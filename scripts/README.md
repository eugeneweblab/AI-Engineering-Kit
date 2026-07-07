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
