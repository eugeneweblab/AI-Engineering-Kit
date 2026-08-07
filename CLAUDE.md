# CLAUDE.md

This project's agent instructions live in [`AGENTS.md`](AGENTS.md). Read it first.

**TL;DR for coding tasks:** detect the stack from the repository via
[`knowledge/SIGNALS.json`](knowledge/SIGNALS.json) → find a `ready` doc via
[`knowledge/INDEX.json`](knowledge/INDEX.json) (filter `status: "ready"`; `when_to_use`
says when a doc applies, `tags` and `SIGNALS.symbols` match API names straight from the
diff) → follow the matching [`knowledge/workflows/`](knowledge/workflows/) guide →
self-verify with the topic's `98`/`99`/`100` checklists, whose sections name the rule
behind each item.

Skip a doc whose `applies_to` names a variant the repository does not use — App Router
rules are wrong on the Pages Router, not merely inexact. When two topics cover one
subject, `defers_to` names the one that owns the rule.

Never treat a `draft` stub (`status: draft` — frontmatter, empty body) as an
authoritative source.
