---
description: Rules for Python/shell tooling under scripts/.
paths: ["scripts/**"]
---

# scripts/ rules

Apply when writing or editing files under `scripts/`.

1. **Stdlib-only Python 3.** No third-party imports (no `pyyaml`,
   `requests`, etc.). Parse YAML frontmatter with a minimal in-repo parser.
   If a dependency seems necessary, stop and raise it as a design question
   instead of adding `requirements.txt`.
2. **Explicit exit codes.** `0` on success, `1` on validation/data error,
   `2` reserved for hook contracts. Every error path prints a `file:line:
   message` diagnostic to stderr before exiting.
3. **Deterministic output.** Same input → same bytes. No timestamps or
   non-sorted iteration in generated files.
4. **Tests are required.** Each script ships matching cases under
   `scripts/tests/`, runnable via `python3 -m unittest discover scripts/tests`.
   Cover every documented failure mode with a fixture.
5. **Shell scripts use `set -euo pipefail`** and a leading `#!/usr/bin/env bash`.
6. **No network calls** unless the script's sole purpose is a sync/fetch step,
   in which case behind a `--dry-run` flag for tests.
7. **Generated artifacts are never edited by hand** — they are rebuilt and
   diff-checked in CI.
