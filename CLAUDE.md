# CLAUDE.md

This project's agent instructions live in [`AGENTS.md`](AGENTS.md). Read it first.

**TL;DR for coding tasks:** gather context → find a `ready` doc via
[`knowledge/INDEX.json`](knowledge/INDEX.json) (filter `status: "ready"`, match
`tags`/`when_to_use`) → follow the matching [`knowledge/workflows/`](knowledge/workflows/)
guide → self-verify with the topic's `98`/`99`/`100` checklists.

Never treat a `draft` stub (`status: draft` — frontmatter, empty body) as an
authoritative source.
