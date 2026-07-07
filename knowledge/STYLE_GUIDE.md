# Style Guide

The canonical writing standard for this repository is
**[`engineering/WRITING_STANDARD.md`](engineering/WRITING_STANDARD.md)** — it is the
single source of truth for tone, structure, examples, naming, and Definition of Done.

To create or edit a document:

1. Start from [`TEMPLATE.md`](TEMPLATE.md) (required frontmatter + section order).
2. Write per [`engineering/WRITING_STANDARD.md`](engineering/WRITING_STANDARD.md).
3. Set `status: ready` only when the Definition of Done is met.
4. Regenerate the index: `python3 scripts/build-index.py`.

## Quick reference

- One `#` H1 per document (the title). Use `##` / `###` for sections.
- Filenames: lowercase `kebab-case`, named after the topic, not the format.
- Always use fenced code blocks with a language.
- Keep examples short; prefer a good/bad pair.
- Cross-reference the canonical doc instead of duplicating explanations.
