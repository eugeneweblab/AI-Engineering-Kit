# cursor integration

This adapter points Cursor at [`../../AGENTS.md`](../../AGENTS.md). Cursor also loads
the root `AGENTS.md` and `.cursor/rules/ai-engineering-kit.mdc` (`alwaysApply: true`)
automatically.

A live compliance run on 2026-08-17 followed the retrieval protocol (git root, grep
`INDEX`/`SIGNALS`, `when_to_use`, owner docs, 98/99/100 checklists) and scored 13/13
on `agent-compliance-v1` output and protocol checks. n=1; the Codex A/B harness
(`scripts/agent-compliance.py run`) does not invoke Cursor, so there is no control arm.

There is nothing else tool-specific to configure yet. Add cursor-only configuration here
if it ever becomes necessary; keep all general engineering knowledge in `knowledge/`.
