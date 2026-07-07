# Contributing Guide

This guide covers the **process**. For writing style and document shape, see the
single sources of truth:

- [`engineering/WRITING_STANDARD.md`](engineering/WRITING_STANDARD.md) — how to write.
- [`TEMPLATE.md`](TEMPLATE.md) — required frontmatter and section order.
- [`../AGENTS.md`](../AGENTS.md) — how agents consume this knowledge base.

---

## Adding or editing a document

1. Keep the canonical filename and numbering from
   [`../docs/structure/canonical-file-list.md`](../docs/structure/canonical-file-list.md).
   Most files already exist as `draft` stubs — fill them, don't create new numbers.
2. Start from `TEMPLATE.md`. Every document MUST have the frontmatter block.
3. Write per `WRITING_STANDARD.md`. One topic per document. Explain *why*, not only *how*.
4. Flip `status: draft → ready` only when the Definition of Done is met.
5. Update `when_to_use` and `related` so agents can find and connect the doc.
6. Regenerate the index: `python3 scripts/build-index.py` (commit `INDEX.json` +
   `INDEX.md` with your change).

---

## Rules

- Write in English.
- Examples must compile, use modern syntax, and avoid deprecated APIs.
- Do not duplicate content — cross-reference the canonical document.
- Do not include project-specific hacks or outdated APIs.
- Prefer updating an existing document over creating a new one.

---

## Frontmatter is required

Every document under `knowledge/<topic>/` carries machine-readable frontmatter
(see `TEMPLATE.md`). It powers `INDEX.json`, which is how AI agents locate docs.
A document without valid frontmatter will not appear correctly in the index.

Missing frontmatter can be backfilled with `python3 scripts/inject-frontmatter.py`
(idempotent — it skips files that already have it).
