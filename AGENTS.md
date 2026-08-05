# AGENTS.md — How AI agents should use this repository

This repository (**AI Engineering Kit**) is a knowledge base that gives AI coding
agents the shared engineering context experienced teams rely on. It is **not** a
prompt library. Treat it as reference material you consult before and during work.

This file is the canonical entrypoint for **every** AI tool (Claude Code, Cursor,
Codex, Copilot, Gemini CLI, Cline, …). Tool-specific pointers under `agents/` all
redirect here.

---

## Start here (retrieval protocol)

Follow this loop for any coding task:

1. **Gather context first.** Understand the existing project, its architecture,
   naming, and patterns before writing code. Reuse over recreate.
2. **Locate relevant knowledge.** Open [`knowledge/INDEX.json`](knowledge/INDEX.json)
   (machine-readable) or [`knowledge/INDEX.md`](knowledge/INDEX.md) (human-readable).
   Filter to `status: "ready"`, match on `topic` / `tags` / `when_to_use`, then read
   the doc at its `path`.
3. **Apply the process.** For end-to-end tasks, follow the matching guide in
   [`knowledge/workflows/`](knowledge/workflows/) and the principles in
   [`knowledge/engineering/`](knowledge/engineering/) and [`knowledge/ai/`](knowledge/ai/).
4. **Self-verify before finishing.** Run the topic's `98-production-checklist.md`
   and `99-ai-review-checklist.md`, and re-read `100-common-antipatterns.md` to
   confirm you did not introduce a known mistake. Each themed section of those
   checklists opens with a **Rules:** line naming the documents the items came
   from — when a check fails, that is where the explanation and the fix are.

Never invent guidance that contradicts a `ready` document. If no `ready` doc covers
the topic, say so and rely on general engineering judgment — do not treat a `draft`
stub (`status: draft`) as authoritative.

---

## The document metadata contract

Every topic document begins with YAML frontmatter. Agents should read it instead of
guessing from filenames:

```yaml
---
id: nextjs/03-app-router      # stable unique id (topic/basename)
topic: nextjs                 # owning topic (folder name)
slug: app-router              # topic-scoped slug
title: "Next.js App Router"   # human title (first H1)
type: doc                     # doc | index
order: 3                      # canonical ordering within the topic
status: ready                 # ready | draft  ← authoritative only when "ready"
tags: [nextjs, app-router]    # retrieval keywords
related: []                   # ids of related docs
when_to_use: ""               # one line: when this doc applies (fill as content lands)
---
```

**`status` is the most important field:**

- `ready` — complete, verified, safe to rely on and generate code from.
- `draft` — scaffold only: frontmatter plus an empty `# Title`, no body yet. Exists to
  reserve the structure. **Do not cite it as a source.** These are where new content
  goes next. (Detect drafts by `status: draft` — not by file contents.)

Filenames use a fixed numeric prefix (`00`…`30`, then `98`, `99`, `100`). Because
`100` sorts before `11` lexically, **order docs by the `order` field, not by
filename** — the index already does this for you.

---

## Repository map

| Path | What it holds |
|------|---------------|
| `knowledge/INDEX.json` / `INDEX.md` | Generated index of every doc — **your entrypoint**. |
| `knowledge/<topic>/` | Standard topics (`00-overview` → `30-…`, `98/99/100`). |
| `knowledge/engineering/` | Cross-cutting engineering principles (custom structure). |
| `knowledge/ai/` | How AI should gather context, plan, generate, verify (custom). |
| `knowledge/workflows/` | Step-by-step task guides (fix a bug, add an endpoint, …). |
| `knowledge/engineering/WRITING_STANDARD.md` | **Canonical** writing standard for all docs. |
| `knowledge/TEMPLATE.md` | Scaffold (incl. required frontmatter) for a new doc. |
| `agents/<tool>/` | Tool-specific integration notes — all redirect here. |
| `docs/structure/` | Frozen canonical structure spec and file list. |
| `scripts/` | `inject-frontmatter.py`, `build-index.py` (regenerate metadata/index). |

---

## Non-negotiables

- **Understand before implementing.** Read the relevant `ready` docs first.
- **Reuse over recreate.** Prefer existing components, patterns, and conventions.
- **Stay in scope.** Fix the task; do not make unrelated changes.
- **Consistency over cleverness.** Match the surrounding code and this KB's guidance.
- **Verify.** Run the checklists; do not claim done without evidence.

---

## Extending the knowledge base

When you add or edit a doc:

1. Follow [`knowledge/engineering/WRITING_STANDARD.md`](knowledge/engineering/WRITING_STANDARD.md)
   and start from [`knowledge/TEMPLATE.md`](knowledge/TEMPLATE.md).
2. Fill a `draft` stub with real content and flip `status` to `ready`; set
   `when_to_use` and `related`.
3. Regenerate the index: `python3 scripts/build-index.py`.
4. Keep the canonical filenames/numbering from `docs/structure/canonical-file-list.md`, and
   add the file to that list when you create one — the numeric prefix is the document's
   `order` and must be unique within its topic.
5. Verify before you finish: `python3 scripts/check-knowledge.py knowledge`. It resolves
   every cross-link and parses every fenced code block in the language its fence claims,
   so a wrong tag or an unrunnable example fails loudly instead of shipping.
