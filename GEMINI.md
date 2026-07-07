# GEMINI.md

Agent instructions for this repository live in [`AGENTS.md`](AGENTS.md). Read it first.

Entrypoint for finding knowledge: [`knowledge/INDEX.json`](knowledge/INDEX.json).
Filter to `status: "ready"`, match on `topic`/`tags`/`when_to_use`, then read the
doc at its `path`. Do not cite `draft` stubs as sources.
