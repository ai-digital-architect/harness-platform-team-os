"""Tests for impact.py (transitive closure of dependents).

Fixture manifest reproduces the EKS chain:
  harness-terraform-data -> harness-terraform-integration
    -> {harness-terraform-eks-blue, harness-terraform-eks-green}
  harness-terraform-route53 depends on harness-terraform-data
    and harness-terraform-eks-blue.
Run: python3 -m unittest discover scripts/tests
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import impact

EKS_MANIFEST = """\
version: "1.0"

product_areas:

  infrastructure:
    description: "Terraform modules (EKS chain fixture)"
    repos:
      - name: harness-terraform-data
        tech: [terraform]
        depends_on: []

      - name: harness-terraform-integration
        tech: [terraform]
        depends_on: [harness-terraform-data]

      - name: harness-terraform-eks-blue
        tech: [terraform]
        depends_on: [harness-terraform-integration]

      - name: harness-terraform-eks-green
        tech: [terraform]
        depends_on: [harness-terraform-integration]

      - name: harness-terraform-route53
        tech: [terraform]
        depends_on: [harness-terraform-data, harness-terraform-eks-blue]
"""

CYCLE_MANIFEST = """\
version: "1.0"

product_areas:

  loops:
    description: "cycle fixture"
    repos:
      - name: repo-a
        depends_on: [repo-b]

      - name: repo-b
        depends_on: [repo-a]
"""


class ImpactBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write_manifest(self, text=EKS_MANIFEST):
        (self.root / "repo-manifest.yaml").write_text(text, encoding="utf-8")

    def run_impact(self, repo):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = impact.main([repo, "--root", str(self.root)])
        return code, out.getvalue(), err.getvalue()


class TestEksChain(ImpactBase):
    def test_data_impacts_full_chain(self):
        self.write_manifest()
        code, out, err = self.run_impact("harness-terraform-data")
        self.assertEqual(code, 0, err)
        impacted = out.splitlines()
        self.assertIn("harness-terraform-integration", impacted)
        self.assertIn("harness-terraform-eks-blue", impacted)
        self.assertIn("harness-terraform-eks-green", impacted)
        self.assertIn("harness-terraform-route53", impacted)

    def test_output_is_sorted_and_exact(self):
        self.write_manifest()
        _, out, _ = self.run_impact("harness-terraform-data")
        impacted = out.splitlines()
        self.assertEqual(impacted, sorted(impacted))
        self.assertEqual(impacted, [
            "harness-terraform-eks-blue",
            "harness-terraform-eks-green",
            "harness-terraform-integration",
            "harness-terraform-route53",
        ])

    def test_integration_impacts_eks_and_route53_but_not_data(self):
        self.write_manifest()
        code, out, _ = self.run_impact("harness-terraform-integration")
        self.assertEqual(code, 0)
        impacted = out.splitlines()
        self.assertEqual(impacted, [
            "harness-terraform-eks-blue",
            "harness-terraform-eks-green",
            "harness-terraform-route53",
        ])
        self.assertNotIn("harness-terraform-data", impacted)


class TestEdgeCases(ImpactBase):
    def test_unknown_repo_exits_1_with_stderr(self):
        self.write_manifest()
        code, out, err = self.run_impact("no-such-repo")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("unknown repo 'no-such-repo'", err)
        self.assertIn("repo-manifest.yaml:1: error:", err)

    def test_repo_with_no_dependents_prints_nothing(self):
        self.write_manifest()
        code, out, err = self.run_impact("harness-terraform-route53")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "")

    def test_cycle_does_not_hang(self):
        self.write_manifest(CYCLE_MANIFEST)
        code, out, _ = self.run_impact("repo-a")
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), ["repo-b"])

    def test_missing_manifest_exits_1(self):
        code, out, err = self.run_impact("harness-terraform-data")
        self.assertEqual(code, 1)
        self.assertIn("repo-manifest.yaml not found", err)

    def test_no_args_exits_1_with_usage(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = impact.main([])
        self.assertEqual(code, 1)
        self.assertIn("usage:", err.getvalue())


class TestGraphJsonEdges(ImpactBase):
    def test_graph_json_depends_on_edges_extend_closure(self):
        self.write_manifest()
        knowledge = self.root / "knowledge"
        knowledge.mkdir()
        graph = {
            "nodes": [{"id": "dependencies/route53-consumers", "type": "dependency",
                       "title": "x", "status": "draft"}],
            "edges": [{"from": "dependencies/route53-consumers", "rel": "depends-on",
                       "to": "harness-terraform-route53"}],
        }
        (knowledge / "graph.json").write_text(json.dumps(graph), encoding="utf-8")
        code, out, err = self.run_impact("harness-terraform-data")
        self.assertEqual(code, 0, err)
        self.assertIn("dependencies/route53-consumers", out.splitlines())

    def test_invalid_graph_json_exits_1(self):
        self.write_manifest()
        knowledge = self.root / "knowledge"
        knowledge.mkdir()
        (knowledge / "graph.json").write_text("{not json", encoding="utf-8")
        code, _, err = self.run_impact("harness-terraform-data")
        self.assertEqual(code, 1)
        self.assertIn("cannot read graph.json", err)


if __name__ == "__main__":
    unittest.main()
