---
id: prompts/readme
topic: prompts
slug: readme
title: "Prompts"
type: index
order: -1
status: ready
tags: [prompts, readme]
related: []
when_to_use: "Read first to find a reusable prompt for an AI-assisted task."
---
# Prompts

## Purpose

Reusable prompts for tasks that recur: reviewing a change, investigating a bug, refactoring
without changing behavior.

These are starting points to adapt, not incantations. A prompt that works is mostly context —
what the code does, what constrains it, what "done" means — and only slightly phrasing.

---

## What's Here

| Prompt | Use for |
|---|---|
| [01. Code Review](01-code-review.md) | Reviewing a diff for defects before merge |
| [02. Bug Investigation](02-bug-investigation.md) | Finding a root cause from a reproducible failure |
| [03. Refactoring](03-refactoring.md) | Restructuring code without changing behavior |

---

## What Makes a Prompt Work

**Context beats phrasing.** The stack, the constraint, and the definition of done matter more
than any wording. Most of that belongs in a committed instructions file rather than in each
prompt — see [Tools — AI Coding Tools](../tools/26-ai-coding-tools.md).

**State the whole task up front.** A complete specification in the first message produces
better results than the same information revealed across several turns.

**Ask for the outcome, not the procedure.** Enumerating steps constrains the approach to what
you already thought of. Say what "done" looks like and what must not change.

**Say what you do not want changed.** Scope expansion — adjacent refactors, extra
abstractions, defensive error handling for impossible cases — is the most common complaint,
and one sentence prevents it.

**Do not shout.** Emphasis stacked on every instruction (`CRITICAL`, `MUST`, `ALWAYS`) makes
none of it stand out, and instructions written to overcome an older model's reluctance now
over-apply.

---

## What Not to Put in a Prompt

- **Secrets, credentials, or production data.** Anything sent has left your machine; rotate
  what leaks rather than deleting the message.
- **Instructions to think step by step**, or to use a scratchpad. Current models reason
  without being told, and the instruction mostly adds tokens.
- **A restatement of general programming knowledge.** Say what is specific to this codebase.

---

## Related Topics

- [Tools — AI Coding Tools](../tools/26-ai-coding-tools.md) — where persistent context belongs.
- [AI — Context Gathering](../ai/01-context-gathering.md) and [AI — Task Planning](../ai/02-task-planning.md) — the reasoning process these prompts trigger.
- [Figma — AI Prompting Standard](../figma/12-ai-prompts.md) — the design-to-code equivalent.
- [Engineering — Code Review](../engineering/02-code-review.md) — what a review is for.

---

## Summary

A good prompt is mostly context, states the whole task at once, describes the outcome rather
than the procedure, and says explicitly what must not change. Keep the durable parts in a
committed instructions file and the task-specific parts here.
