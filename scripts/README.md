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

Wired into CI via `.github/workflows/knowledge-guardrails.yml`, which also fails the
build if `INDEX.json`/`INDEX.md` are out of sync with the docs' frontmatter.
