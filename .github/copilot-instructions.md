# GitHub Copilot instructions

This repository's full agent guidance is in [`AGENTS.md`](../AGENTS.md).

When answering or generating code:

1. Consult [`knowledge/INDEX.json`](../knowledge/INDEX.json); use only docs with
   `status: "ready"`, matched by `topic` / `tags` / `when_to_use`.
2. Reuse existing patterns; stay in scope; prefer consistency over cleverness.
3. Verify against the topic's `98-production-checklist.md`,
   `99-ai-review-checklist.md`, and `100-common-antipatterns.md`.

Ignore `draft` stubs (`status: draft`, empty body) — they are placeholders, not sources.
