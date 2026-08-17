# GitHub Copilot instructions

This repository's full agent guidance is in [`AGENTS.md`](../AGENTS.md).
Resolve the Git root first and run every lookup under `knowledge/` from there, even when
the current directory is nested.

When answering or generating code:

1. Consult [`knowledge/INDEX.json`](../knowledge/INDEX.json); use only docs with
   `status: "ready"`. `when_to_use` states when a document applies; `tags` and `topic`
   narrow it.
2. Use [`knowledge/SIGNALS.json`](../knowledge/SIGNALS.json) to work from the code:
   `stack` maps a repository file to the documents that govern it, `symbols` maps an API
   name in the diff to the documents that state its rules.
3. Skip a document whose `applies_to` names a variant this repository does not use.
4. Reuse existing patterns; stay in scope; prefer consistency over cleverness.
5. Verify against the topic's `98-production-checklist.md`,
   `99-ai-review-checklist.md`, and `100-common-antipatterns.md`. Each section of those
   checklists opens with a **Rules:** line naming the document behind its items.

Ignore `draft` stubs (`status: draft`, empty body) — they are placeholders, not sources.
