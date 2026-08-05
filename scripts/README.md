# scripts

Maintenance scripts for the knowledge base. Run from the repo root.

## `inject-frontmatter.py`

Backfills the required YAML frontmatter into every `knowledge/<topic>/*.md` that is
missing it. Idempotent — files that already start with `---` are skipped. `status` is
set to `draft` when the body is an empty scaffold (nothing beyond the `# Title`),
otherwise `ready`.

```bash
python3 scripts/inject-frontmatter.py
```

## `build-index.py`

Reads the frontmatter of every doc and regenerates:

- `knowledge/INDEX.json` — machine-readable index (the agent entrypoint).
- `knowledge/INDEX.md` — human-readable index.

Run it after adding, renaming, or re-statusing any document.

```bash
python3 scripts/build-index.py
```

Both are safe to re-run; they only touch frontmatter and the two INDEX files.

## `check-ready-not-stub.py`

Guardrail linter (read-only). Fails if any doc marked `status: ready` is actually a
stub — it contains a TODO/placeholder marker, or its body is too thin to be real
content, or it is a `type: index` doc that is thin and links nowhere. This prevents the
regression the quality audit found: empty topics marked `ready` that route agents
(which filter `INDEX.json` for ready docs) to dead ends.

```bash
python3 scripts/check-ready-not-stub.py knowledge   # exit 0 = clean, 1 = violations
```

## `check-knowledge.py`

Guardrail linter (read-only). Covers the defect classes that are not visible by
inspection:

| Check | What fails the build |
|---|---|
| structure | a standard topic missing `README`/`00`/`98`/`99`/`100`, or a gap in `01`–`30` |
| frontmatter | `id`/`topic`/`order` disagreeing with the path; empty `status`/`title`/`when_to_use` |
| duplicates | a repeated `id`, a repeated `title`, or two docs claiming the same `order` inside a topic |
| links | a markdown link, a `related:` id, or a `` `knowledge/…md` `` path that does not resolve |
| fences | an unclosed ``` fence |
| code blocks | a block that does not parse as the language its fence claims |
| plan | `docs/structure/` no longer describing the tree: a topic missing from the root tree, a topic with no part in the file list, or a file listed/present without its counterpart |

Blocks are handed to the real parser for their language: `ast.parse` (Python), a
JSONC-tolerant decoder (JSON), PyYAML (YAML), `bash -n` (shell), `php -l` (PHP), and
esbuild (JS/TS/JSX/TSX). PHP and JS/TS are skipped with a printed note when `php` or
`npx` is unavailable.

```bash
python3 scripts/check-knowledge.py knowledge      # exit 0 = clean, 1 = violations
python3 scripts/check-knowledge.py --skip-external  # structure/links only, no php/npx
```

### `codeblock-baseline.json`

Documentation legitimately contains code *fragments* — class-method excerpts, NestJS
parameter decorators, Bad/Good pairs that reuse a name, lists of sibling JSX elements
or function signatures. These never parse standalone and are not defects, so the PHP
and JS/TS checks ignore the blocks listed in this baseline and fail only on a *new*
failure. After intentionally adding or removing such a fragment:

```bash
python3 scripts/check-knowledge.py --update-baseline
```

Review the diff before committing: a baseline that grows without a matching fragment
is a real defect being silenced.

---

All three linters run in CI via `.github/workflows/knowledge-guardrails.yml`, which
also fails the build if `INDEX.json`/`INDEX.md` are out of sync with the frontmatter.
