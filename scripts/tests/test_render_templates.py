"""Tests for harness-layer/sync/render-templates.py.

Renders a 3-repo fixture manifest (one repo per tech: terraform, python,
java/spring) with the REAL templates and rule sources, and snapshot-compares
against scripts/tests/fixtures/render_golden/. Regenerate goldens after an
intentional template/rule change with:

    python3 scripts/tests/test_render_templates.py --regen

Skills are faked in the fixture so pk.sh changes don't churn the snapshots.
"""

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN = Path(__file__).resolve().parent / "fixtures" / "render_golden"

spec = importlib.util.spec_from_file_location(
    "render_templates", REPO_ROOT / "harness-layer" / "sync" / "render-templates.py")
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)

FIXTURE_MANIFEST = """\
version: "1.0"

product_areas:

  fixture-infra:
    description: "Fixture terraform area"
    repos:
      - name: tf-vpc
        role: networking
        tech: [terraform]
        deploy_target: aws
        depends_on: []

  fixture-apps:
    description: "Fixture application area"
    repos:
      - name: py-events
        tech: [python]
        deploy_target: lambda
        depends_on: [tf-vpc]

      - name: java-api
        tech: [java, spring-boot]
        deploy_target: eks
        depends_on: [tf-vpc]

deprecated:
  - name: old-tf
    reason: "fixture deprecated repo"
"""

SURVEY_JAVA_API = """\
# java-api survey report

## Build & test

- `./gradlew build` (verified from bitbucket-pipelines.yml)
- `./gradlew test`

## Other

ignored section
"""


def build_fixture_root(tmp):
    """Fixture team-os root: real templates+rules, fake skills, fixture manifest."""
    root = Path(tmp) / "team-os"
    hl = root / "harness-layer"
    (hl / "rules").mkdir(parents=True)
    for t in rt.TEMPLATES:
        shutil.copy(REPO_ROOT / "harness-layer" / t, hl / t)
    for r in (REPO_ROOT / "harness-layer" / "rules").glob("*.rule.md"):
        shutil.copy(r, hl / "rules" / r.name)
    skill = hl / "skills" / "platform-graph"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("fixture skill\n", encoding="utf-8")
    (hl / "surveys").mkdir()
    (hl / "surveys" / "java-api.md").write_text(SURVEY_JAVA_API, encoding="utf-8")
    (root / "repo-manifest.yaml").write_text(FIXTURE_MANIFEST, encoding="utf-8")
    return root


def render_fixture():
    with tempfile.TemporaryDirectory() as tmp:
        return rt.render_all(build_fixture_root(tmp))


class TestRenderFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rendered = render_fixture()

    def test_snapshot_matches_golden(self):
        self.assertTrue(GOLDEN.is_dir(),
                        "golden dir missing — run test_render_templates.py --regen")
        golden = {p.relative_to(GOLDEN).as_posix(): p.read_text(encoding="utf-8")
                  for p in GOLDEN.rglob("*") if p.is_file()}
        self.assertEqual(sorted(golden), sorted(self.rendered))
        for rel in golden:
            self.assertEqual(golden[rel], self.rendered[rel], f"drift in {rel}")

    def test_deprecated_repo_not_rendered(self):
        self.assertFalse(any(p.startswith("old-tf/") for p in self.rendered))

    def test_tech_matched_rules(self):
        self.assertIn("tf-vpc/.claude/rules/terraform.md", self.rendered)
        self.assertIn("tf-vpc/.github/instructions/terraform.instructions.md",
                      self.rendered)
        self.assertNotIn("tf-vpc/.claude/rules/java-spring.md", self.rendered)
        self.assertIn("py-events/.claude/rules/python-lambda.md", self.rendered)
        self.assertIn("java-api/.claude/rules/java-spring.md", self.rendered)
        self.assertNotIn("java-api/.claude/rules/terraform.md", self.rendered)

    def test_survey_injected_else_todo(self):
        self.assertIn("./gradlew build", self.rendered["java-api/AGENTS.md"])
        self.assertNotIn("ignored section", self.rendered["java-api/AGENTS.md"])
        self.assertIn("TODO(verify): build/test commands not yet surveyed",
                      self.rendered["py-events/AGENTS.md"])

    def test_dependents_computed(self):
        self.assertIn("- py-events", self.rendered["tf-vpc/AGENTS.md"])
        self.assertIn("- java-api", self.rendered["tf-vpc/AGENTS.md"])

    def test_generated_header_on_all_non_skill_files(self):
        for rel, content in self.rendered.items():
            if "/.claude/skills/" in rel:
                continue
            # header is line 1, or the first line after a frontmatter block
            head = "\n".join(content.split("\n")[:6])
            self.assertIn("# GENERATED — edit in team-os/harness-layer/", head,
                          f"missing GENERATED header in {rel}")

    def test_agents_under_line_budget(self):
        for rel, content in self.rendered.items():
            if rel.endswith("/AGENTS.md"):
                self.assertLess(content.count("\n") + 1, rt.AGENTS_LINE_BUDGET, rel)

    def test_skills_copied_verbatim(self):
        self.assertEqual(self.rendered["java-api/.claude/skills/platform-graph/SKILL.md"],
                         "fixture skill\n")


class TestRendererErrors(unittest.TestCase):
    def test_unresolved_placeholder_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_root(tmp)
            tpl = root / "harness-layer" / "AGENTS.md.tmpl"
            tpl.write_text(tpl.read_text(encoding="utf-8") + "\n{{nope}}\n",
                           encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                rt.render_all(root)
            self.assertIn("unresolved placeholder {{nope}}", str(ctx.exception))

    def test_missing_manifest_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_root(tmp)
            (root / "repo-manifest.yaml").unlink()
            with self.assertRaises(ValueError):
                rt.render_all(root)


class TestRealManifest(unittest.TestCase):
    """T3.1 Verify criterion: harness-api renders < 100 lines from the real manifest."""

    def test_real_render_harness_api(self):
        rendered = rt.render_all(REPO_ROOT)
        agents = rendered["harness-api/AGENTS.md"]
        self.assertLess(agents.count("\n") + 1, 100)
        self.assertIn("## Platform knowledge graph", agents)

    def test_check_mode_exits_zero(self):
        self.assertEqual(rt.main(["--check"]), 0)


def regen():
    rendered = render_fixture()
    if GOLDEN.exists():
        shutil.rmtree(GOLDEN)
    for rel, content in rendered.items():
        target = GOLDEN / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    print(f"regenerated {len(rendered)} golden files under {GOLDEN}")


if __name__ == "__main__":
    if "--regen" in sys.argv:
        regen()
    else:
        unittest.main()
