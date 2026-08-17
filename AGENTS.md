# AGENTS.md — How AI agents should use this repository

This repository (**AI Engineering Kit**) is a knowledge base that gives AI coding
agents the shared engineering context experienced teams rely on. It is **not** a
prompt library. Treat it as reference material you consult before and during work.

This file is the shared source of project guidance. Tool-specific pointers under
`agents/` redirect here, but automatic loading is a property of each tool and version,
not something this repository can guarantee. The integration matrix records what has
actually been tested; an unverified adapter is a pointer, not evidence of compliance.

---

## Start here (retrieval protocol)

First resolve the repository root. A coding agent may be launched from a nested
directory, so paths under `knowledge/` must never be interpreted relative to the current
directory by accident:

```bash
git rev-parse --show-toplevel
cd <the-path-printed-above>
```

If the repository root does not contain this `AGENTS.md` and `knowledge/`, stop and
report that the kit is not installed in the project. Do not silently continue while
claiming to have consulted it.

Follow this loop for any coding task:

1. **Gather context first.** Understand the existing project, its architecture,
   naming, and patterns before writing code. Reuse over recreate.
2. **Locate relevant knowledge. Query the index; do not read it.**
   [`knowledge/INDEX.json`](knowledge/INDEX.json) is ~310k tokens and
   [`knowledge/SIGNALS.json`](knowledge/SIGNALS.json) ~260k. Loading either wastes a
   context window and most of them will not fit. Both are formatted one entry per
   line so a search returns exactly the entry you need — a symbol lookup costs about
   thirty tokens:

   ```bash
   # An API name from the diff -> the documents that govern it
   grep -A5 '"revalidateTag":' knowledge/SIGNALS.json

   # A symptom or subject -> candidate documents (INDEX.md is 30k, still worth grepping)
   grep -i -B2 -A2 'serialization' knowledge/INDEX.json
   grep -i 'transactions' knowledge/INDEX.md

   # One document's metadata, without the other 1438
   grep -A8 '"id": "nextjs/10-caching"' knowledge/INDEX.json
   ```

   Read a document in full only once you have chosen it. Filter to `status: "ready"`,
   then match **in this order** — each step is stronger
   evidence than the one after it, and a later step must not outrank an earlier one:

   1. **A signal from the repository or the diff.** A file that identifies the stack,
      or an API name that appears in the change. This is evidence, not inference.
   2. **`when_to_use`.** The one field written to answer "does this document apply to
      what I am doing".
   3. **`topic` and `tags`.** They narrow a set; they do not pick a winner.
   4. **Words in the title or slug.** Weakest, and often coincidental — "block" in a
      task about blocking a merge matches `block-editor`, which is about something
      else entirely. Use this only to break a tie.

   Then read the doc at its `path`.

   [`knowledge/SIGNALS.json`](knowledge/SIGNALS.json) inverts this lookup. Its
   `stack` list maps a file that identifies a stack or a variant — `app/**/page.tsx`
   versus `pages/_app.tsx`, a theme with `theme.json` versus one without — to the
   documents that govern it, so the applicable rule set is determined by the
   repository rather than guessed. Treat that list as the starting set, not the
   complete set: also resolve symbols from the files you will edit (`timeout-minutes`,
   `lock_timeout`, `SET NX`). Its `symbols` index maps an API name to the
   documents that state its rules.

   **Match from the code, not only from the task description.** After the topic and
   slug, `tags` lists the API names, directives, and configuration keys a document
   governs — `revalidateTag`, `add_filter`, `DISABLE_WP_CRON`, `autovacuum_freeze_max_age`.
   When a symbol in the diff appears in a doc's `tags`, that doc states the rules for
   it, and it is a more reliable match than guessing the topic from the ticket.
3. **Apply the process.** For end-to-end tasks, follow the matching guide in
   [`knowledge/workflows/`](knowledge/workflows/) and the principles in
   [`knowledge/engineering/`](knowledge/engineering/) and [`knowledge/ai/`](knowledge/ai/).
4. **Self-verify before finishing.** Run the topic's `98-production-checklist.md`
   and `99-ai-review-checklist.md`, and re-read `100-common-antipatterns.md` to
   confirm you did not introduce a known mistake. Each themed section of those
   checklists opens with a **Rules:** line naming the documents the items came
   from — when a check fails, that is where the explanation and the fix are.

Never silently contradict a `ready` document. If existing code and a `ready` document
disagree, treat that as repository drift: the code is evidence of current behaviour,
while the document states intended policy. Surface the conflict, inspect history/tests,
and follow the explicit task or confirmed project intent. Do not copy either source
blindly. If no `ready` doc covers the topic, say so and rely on general engineering
judgment — do not treat a `draft` stub (`status: draft`) as authoritative.

## Instruction authority

This repository cannot override instructions supplied by the agent platform. Resolve
conflicts in this order:

1. Platform/system/developer safety and execution policy.
2. Explicit user instruction for the current task.
3. The closest project instruction file that applies to the edited path.
4. A `ready` knowledge document that owns the rule (`defers_to` resolves overlaps).
5. Verified repository behaviour, architecture, tests, and conventions.
6. General model knowledge.

When levels 2–5 disagree materially, do not hide the disagreement. State the evidence,
the selected authority, and any assumption that still needs confirmation.

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
type: doc                     # doc | index | checklist | antipatterns | workflow
                              # | template | playbook | prompt | snippet | example
order: 3                      # canonical ordering within the topic
status: ready                 # ready | draft  ← authoritative only when "ready"
maturity: validated           # unverified | reviewed | validated
tags: [nextjs, app-router,    # topic, slug, then the API names this doc governs
       generateStaticParams, notFound]
applies_to: [app-router]      # optional: the variant this doc is specific to
related: []                   # ids of related docs
defers_to: ""                 # optional: when two topics cover one subject,
                              # the doc that owns the rule
when_to_use: ""               # one line: when this doc applies (fill as content lands)
verified_against: "Next.js 16.0" # required for reviewed/validated guidance
source_urls: ["https://nextjs.org/docs/..."]
last_reviewed: "2026-08-17"
review_after: "2026-11-17"
---
```

`applies_to` and `defers_to` appear only when they say something. `applies_to`
names the variant a document is specific to — App Router caching rules are not
"mostly right" on the Pages Router, they are wrong — so a document carrying it
should be skipped unless `SIGNALS.stack` matched that variant in this repository.
No matched variant means skip it: Prisma migration rules do not apply to a folder
of raw SQL. `defers_to` names the document that owns the rule when two topics
cover one subject; the deferring document still applies, but it does not override
the owner.

**`status` controls whether a document may be used; `maturity` states how strongly
its correctness has been established:**

- `ready` — structurally complete and eligible for retrieval; consult `maturity`
  before treating its claims as verified evidence.
- `draft` — scaffold only: frontmatter plus an empty `# Title`, no body yet. Exists to
  reserve the structure. **Do not cite it as a source.** These are where new content
  goes next. (Detect drafts by `status: draft` — not by file contents.)

`maturity: unverified` means complete prose that has not yet been checked against
named primary sources; `reviewed` means a human checked the rule and sources;
`validated` additionally means examples or behaviour were exercised mechanically.
Prefer the highest-maturity applicable owner. A `ready` but `unverified` document is
guidance, not proof; state that limitation for version-sensitive decisions.

Filenames use a fixed numeric prefix (`00`…`30`, then `98`, `99`, `100`). Because
`100` sorts before `11` lexically, **order docs by the `order` field, not by
filename** — the index already does this for you.

---

## Repository map

| Path | What it holds |
|------|---------------|
| `knowledge/INDEX.json` / `INDEX.md` | Generated index of every doc — **your entrypoint**. |
| `knowledge/SIGNALS.json` | Generated: repository file → applicable docs, and API symbol → the docs that govern it. |
| `knowledge/<topic>/` | Standard topics (`00-overview` → `30-…`, `98/99/100`). |
| `knowledge/engineering/` | Cross-cutting engineering principles (custom structure). |
| `knowledge/ai/` | How AI should gather context, plan, generate, verify (custom). |
| `knowledge/workflows/` | Step-by-step task guides (fix a bug, add an endpoint, …). |
| `knowledge/engineering/WRITING_STANDARD.md` | **Canonical** writing standard for all docs. |
| `knowledge/TEMPLATE.md` | Scaffold (incl. required frontmatter) for a new doc. |
| `agents/<tool>/` | Tool-specific integration notes — all redirect here. |
| `docs/structure/` | Frozen canonical structure spec and file list. |
| `scripts/` | `build-index.py`, `build-signals.py` (regenerate), `check-knowledge.py` (verify). |

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
3. Regenerate the generated files: `python3 scripts/build-index.py` and
   `python3 scripts/build-signals.py`.
4. Keep the canonical filenames/numbering from `docs/structure/canonical-file-list.md`, and
   add the file to that list when you create one — the numeric prefix is the document's
   `order` and must be unique within its topic.
5. Verify before you finish: `python3 scripts/check-knowledge.py knowledge`. It resolves
   every cross-link and parses every fenced code block in the language its fence claims,
   so a wrong tag or an unrunnable example fails loudly instead of shipping.
