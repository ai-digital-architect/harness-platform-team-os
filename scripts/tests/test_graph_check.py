"""Tests for graph_check.py and build_index.py.

Each documented failure mode gets a fixture node, built in a temp root so
graph.json/INDEX.md writes never touch the real knowledge/ tree.
Run: python3 -m unittest discover scripts/tests
"""

import datetime
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_index
import graph_check

MANIFEST = """\
product_areas:
  - name: infrastructure
    repos:
      - name: harness-terraform-data
        depends_on: []
      - name: harness-terraform-eks-blue
        depends_on: [harness-terraform-data]
"""


def make_node(root, rel, frontmatter, body=""):
    path = root / "knowledge" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n\n{body}", encoding="utf-8")
    return path


def valid_fm(rel_id, ntype="convention", extra=""):
    return (f"id: {rel_id}\ntype: {ntype}\ntitle: A node\nstatus: draft\n{extra}")


class GraphCheckBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "knowledge").mkdir()
        self.addCleanup(self._tmp.cleanup)

    def run_check(self, write=True):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = graph_check.run(self.root, write=write)
        return code, out.getvalue(), err.getvalue()

    def write_manifest(self):
        (self.root / "repo-manifest.yaml").write_text(MANIFEST, encoding="utf-8")


class TestEmptyGraph(GraphCheckBase):
    def test_empty_graph_exits_zero(self):
        code, _, _ = self.run_check()
        self.assertEqual(code, 0)

    def test_empty_graph_writes_empty_graph_json(self):
        self.run_check()
        graph = json.loads((self.root / "knowledge" / "graph.json").read_text())
        self.assertEqual(graph, {"nodes": [], "edges": []})


class TestValidNodes(GraphCheckBase):
    def test_valid_node_passes_and_lands_in_graph_json(self):
        make_node(self.root, "conventions/terraform-patterns.md",
                  valid_fm("conventions/terraform-patterns"))
        code, _, err = self.run_check()
        self.assertEqual(code, 0, err)
        graph = json.loads((self.root / "knowledge" / "graph.json").read_text())
        self.assertEqual(graph["nodes"][0]["id"], "conventions/terraform-patterns")

    def test_template_files_excluded(self):
        make_node(self.root, "workflows/_template.md", "this is: not valid frontmatter\n")
        code, _, _ = self.run_check()
        self.assertEqual(code, 0)

    def test_edge_to_node_id_resolves(self):
        make_node(self.root, "conventions/terraform-patterns.md",
                  valid_fm("conventions/terraform-patterns"))
        make_node(self.root, "workflows/upgrade.md",
                  valid_fm("workflows/upgrade", "workflow",
                           "edges:\n  - {rel: governed-by, to: conventions/terraform-patterns}\n"))
        code, _, err = self.run_check()
        self.assertEqual(code, 0, err)

    def test_edge_to_manifest_repo_resolves(self):
        self.write_manifest()
        make_node(self.root, "dependencies/d.md",
                  valid_fm("dependencies/d", "dependency",
                           "edges:\n  - {rel: depends-on, to: harness-terraform-data}\n"))
        code, _, err = self.run_check()
        self.assertEqual(code, 0, err)

    def test_workflow_repos_become_ordered_touches_edges(self):
        self.write_manifest()
        make_node(self.root, "workflows/upgrade.md",
                  valid_fm("workflows/upgrade", "workflow",
                           "repos:\n  - harness-terraform-data\n  - harness-terraform-eks-blue\n"))
        code, _, err = self.run_check()
        self.assertEqual(code, 0, err)
        graph = json.loads((self.root / "knowledge" / "graph.json").read_text())
        touches = [e for e in graph["edges"] if e["rel"] == "touches"]
        self.assertEqual([e["to"] for e in sorted(touches, key=lambda e: e["order"])],
                         ["harness-terraform-data", "harness-terraform-eks-blue"])


class TestFailureModes(GraphCheckBase):
    def assert_error(self, err_substring):
        code, _, err = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn(err_substring, err)
        return err

    def test_missing_required_field(self):
        make_node(self.root, "conventions/x.md",
                  "id: conventions/x\ntype: convention\nstatus: draft\n")  # no title
        self.assert_error("missing required field: title")

    def test_id_path_mismatch(self):
        make_node(self.root, "conventions/x.md", valid_fm("conventions/WRONG"))
        self.assert_error("does not match path-derived id")

    def test_unknown_type(self):
        make_node(self.root, "conventions/x.md", valid_fm("conventions/x", "saga"))
        self.assert_error("type 'saga' not in")

    def test_unknown_status(self):
        make_node(self.root, "conventions/x.md",
                  "id: conventions/x\ntype: convention\ntitle: T\nstatus: maybe\n")
        self.assert_error("status 'maybe' not in")

    def test_unknown_edge_rel(self):
        make_node(self.root, "conventions/a.md", valid_fm("conventions/a"))
        make_node(self.root, "conventions/x.md",
                  valid_fm("conventions/x", "convention",
                           "edges:\n  - {rel: blesses, to: conventions/a}\n"))
        self.assert_error("edge rel 'blesses' not in closed vocabulary")

    def test_dangling_edge_target(self):
        self.write_manifest()
        make_node(self.root, "conventions/x.md",
                  valid_fm("conventions/x", "convention",
                           "edges:\n  - {rel: governed-by, to: conventions/ghost}\n"))
        self.assert_error("edge target 'conventions/ghost' resolves to neither")

    def test_malformed_edge(self):
        make_node(self.root, "conventions/x.md",
                  valid_fm("conventions/x", "convention",
                           "edges:\n  - {rel: governed-by}\n"))
        self.assert_error("edge must be a mapping with rel and to")

    def test_unresolved_wikilink(self):
        self.write_manifest()
        make_node(self.root, "conventions/x.md", valid_fm("conventions/x"),
                  body="See [[conventions/ghost]] for details.\n")
        err = self.assert_error("wikilink [[conventions/ghost]] resolves to neither")
        self.assertRegex(err, r"x\.md:\d+: error")

    def test_workflow_repo_missing_from_manifest(self):
        self.write_manifest()
        make_node(self.root, "workflows/w.md",
                  valid_fm("workflows/w", "workflow", "repos:\n  - no-such-repo\n"))
        self.assert_error("workflow repo 'no-such-repo' not found in repo-manifest.yaml")

    def test_broken_frontmatter_reports_file_line(self):
        (self.root / "knowledge" / "bad.md").write_text("no frontmatter here\n", encoding="utf-8")
        err = self.assert_error("missing frontmatter")
        self.assertIn("bad.md:1:", err)

    def test_graph_json_not_written_on_error(self):
        make_node(self.root, "conventions/x.md", valid_fm("conventions/WRONG"))
        self.run_check()
        self.assertFalse((self.root / "knowledge" / "graph.json").exists())


class TestManifestAbsentWarnings(GraphCheckBase):
    def test_workflow_repos_skipped_with_warning(self):
        make_node(self.root, "workflows/w.md",
                  valid_fm("workflows/w", "workflow", "repos:\n  - anything-goes\n"))
        code, _, err = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("skipping workflow repos check", err)

    def test_edge_to_possible_repo_warns_not_errors(self):
        make_node(self.root, "dependencies/d.md",
                  valid_fm("dependencies/d", "dependency",
                           "edges:\n  - {rel: depends-on, to: some-repo}\n"))
        code, _, err = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("warning", err)


class TestFrontmatterParser(unittest.TestCase):
    def test_flow_map_with_nested_list(self):
        data, _, _ = graph_check.parse_frontmatter(
            "---\nverify_against:\n  - {repo: x, paths: [\"*.tf\", \"*.py\"]}\n---\n")
        self.assertEqual(data["verify_against"],
                         [{"repo": "x", "paths": ["*.tf", "*.py"]}])

    def test_flow_list_scalar(self):
        data, _, _ = graph_check.parse_frontmatter("---\nowners: [infra-team, dev]\n---\n")
        self.assertEqual(data["owners"], ["infra-team", "dev"])

    def test_key_line_numbers(self):
        _, key_lines, _ = graph_check.parse_frontmatter("---\nid: a\ntype: b\n---\n")
        self.assertEqual(key_lines["type"], 3)

    def test_unbalanced_flow_raises_with_line(self):
        with self.assertRaises(graph_check.FrontmatterError) as ctx:
            graph_check.parse_frontmatter("---\nedges:\n  - {rel: x, to: [a}\n---\n")
        self.assertEqual(ctx.exception.line, 3)


class TestBuildIndex(GraphCheckBase):
    def run_index(self, today="2026-06-11"):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = build_index.main(["--root", str(self.root), "--today", today])
        return code, err.getvalue()

    def test_empty_graph_index(self):
        code, err = self.run_index()
        self.assertEqual(code, 0, err)
        text = (self.root / "knowledge" / "INDEX.md").read_text()
        self.assertIn("Graph health: n/a (0 nodes).", text)
        self.assertIn("No nodes yet.", text)

    def test_grouped_by_type_with_health(self):
        make_node(self.root, "conventions/fresh.md",
                  valid_fm("conventions/fresh", "convention", "last_verified: 2026-06-01\n"))
        make_node(self.root, "workflows/stale.md",
                  valid_fm("workflows/stale", "workflow", "last_verified: 2025-01-01\n"))
        code, err = self.run_index()
        self.assertEqual(code, 0, err)
        text = (self.root / "knowledge" / "INDEX.md").read_text()
        self.assertIn("Graph health: 50% verified within 60 days (1 of 2 nodes).", text)
        self.assertIn("## workflow", text)
        self.assertIn("## convention", text)
        self.assertLess(text.index("## workflow"), text.index("## convention"))
        self.assertIn("| [workflows/stale](workflows/stale.md) | A node | draft | 2025-01-01 |", text)

    def test_deterministic_output(self):
        make_node(self.root, "conventions/a.md", valid_fm("conventions/a"))
        self.run_index()
        first = (self.root / "knowledge" / "INDEX.md").read_bytes()
        self.run_index()
        self.assertEqual(first, (self.root / "knowledge" / "INDEX.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
