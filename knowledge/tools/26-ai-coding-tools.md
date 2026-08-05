---
id: tools/26-ai-coding-tools
topic: tools
slug: ai-coding-tools
title: "AI Coding Tools"
type: doc
order: 26
status: ready
tags: [tools, ai-coding-tools]
related: [tools/25-editor-setup, tools/16-git-hooks, tools/27-dependency-management, ai/00-ai-engineering-principles, engineering/02-code-review]
when_to_use: "Read before adopting an AI coding assistant on a project — writing project instructions, connecting tools, setting review expectations, and deciding what the assistant must not touch."
---
# AI Coding Tools

## Purpose

This document defines how to work with AI coding assistants as engineering tooling: what context to give them, how to connect them to a project's real systems, what to keep out of their reach, and where human review remains mandatory.

The scope is *using* an assistant to build software. Building an application that calls an LLM is a different topic — see [AI — AI Engineering Principles](../ai/00-ai-engineering-principles.md).

## Why It Matters

An assistant's output quality is dominated by the context it receives, not by the prompt. Given a repository with no conventions written down, it infers conventions from whatever file it happened to read — and produces code that works but does not belong. Given the project's actual constraints, it produces code a reviewer can merge.

The second reason is the failure mode this tooling introduces: plausible-looking code that a reviewer skims because it *reads* correct. That risk is managed with the same gates as any other contributor's code, not with vigilance.

## Core Principles

- **Context beats prompting.** A committed instructions file that states the stack, conventions, and constraints improves every session; a clever one-off prompt improves one.
- **The assistant is a contributor, not an oracle.** Its output goes through the same review, CI, and test gates as anyone else's.
- **Verification is the human's job.** Generated code that passes tests can still be wrong about intent — and an assistant is not a substitute for understanding the change you are shipping.
- **Grant capability deliberately.** Read access, write access, shell access, and network access are separate decisions with different blast radii.
- **Never paste secrets into a prompt.** Anything sent to a model has left your machine. Rotate what leaks; do not just delete the message.

## Project Instructions

The highest-leverage artifact is a committed instructions file. Claude Code reads `CLAUDE.md` from the project root; the vendor-neutral `AGENTS.md` convention is read by several tools. Point one at the other rather than maintaining two:

```markdown
<!-- CLAUDE.md -->
This project's agent instructions live in [AGENTS.md](AGENTS.md). Read it first.
```

What earns its place in that file — the things the model cannot infer:

```markdown
## Stack
Next.js 15 (App Router), TypeScript strict, Tailwind, Prisma + PostgreSQL.
PHP 8.3 for the WordPress plugin under `wp/`.

## Conventions
- Server Components by default; `"use client"` only where interactivity requires it.
- Data access goes through `src/server/db/`, never Prisma directly in a component.
- Money is stored in integer cents. Never a float.

## Constraints
- `src/generated/` is generated — never edit by hand; run `pnpm codegen`.
- The `orders` table is replicated downstream; schema changes need a migration plan.

## Verify before claiming done
pnpm verify   # typecheck + lint + test
```

What does not: general programming knowledge, framework documentation, or restatements of what good code looks like. Every line is read on every session and is paid for in context.

Keep it short enough that it stays accurate. A 500-line instructions file drifts from the codebase within a month, and stale instructions are worse than none.

## Connecting Tools and Data

**MCP (Model Context Protocol)** is the standard for giving an assistant access to systems beyond the filesystem — issue trackers, databases, documentation, monitoring. Servers are configured per project, so the capability set is reviewable:

```json
// .mcp.json — committed; credentials come from the environment
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "DATABASE_URL": "${LOCAL_DATABASE_URL}" }
    }
  }
}
```

Two rules keep this safe. Point database servers at a **local or read-only** connection, never production — the same discipline as [Database Tools](24-database-tools.md). And treat each server as a dependency: it runs code on your machine with your credentials.

**Skills** package task-specific instructions the assistant loads when relevant — a `SKILL.md` plus supporting files, in the repository. Use them for procedures that recur and have a right answer: the release checklist, the migration process, how this project writes tests. They cost nothing until they are relevant, which makes them a better home for detail than the always-loaded instructions file.

**Hooks** run your own commands at defined points in the assistant's loop — formatting after an edit, blocking a command pattern, logging tool calls. This is where enforcement belongs: a rule the assistant is asked to follow is a request, while a hook that rejects the edit is a gate.

## Working Effectively

**Give the whole task up front.** Current models plan better with a complete specification than with a task revealed across several turns — state the goal, the constraints, and what "done" means in the first message rather than course-correcting incrementally.

**Ask for a plan on non-trivial work.** Reviewing an approach costs a minute; reviewing a finished implementation of the wrong approach costs an hour.

**Keep sessions scoped.** One task per session. A session that has drifted through three unrelated problems carries all of that context into the fourth.

**Point at the constraint, not the symptom.** "This must not do an N+1 query — the list is paginated at 200" produces a better result than "make it faster".

**Let it verify itself.** An assistant that can run the test suite and the type checker catches its own errors before you see them. That is the strongest argument for a single `verify` script — see [Task Runners](19-task-runners.md).

## Review and Verification

Generated code gets reviewed as code. What deserves particular attention:

- **Invented APIs.** A method that does not exist, called plausibly. The type checker and tests catch most of this — which is why both must be in the loop.
- **Silent scope expansion.** Refactors, renames, or "improvements" adjacent to the actual request. Read the whole diff, not the part you asked for.
- **Weakened checks.** A failing test edited into passing, a type assertion added to silence an error, an `eslint-disable` inserted rather than fixing the cause.
- **Dependencies added casually.** A new package for something the standard library does — see [Dependency Management](27-dependency-management.md).
- **Confident wrongness in unfamiliar areas.** The output reads the same whether the model is certain or guessing. Domain-specific logic — pricing, tax, permissions, anything regulated — needs the same scrutiny as a new hire's first PR in that area.

CI is the backstop: type checks, tests, lint, and security scanning apply identically regardless of who or what wrote the code. If a gate can be skipped by a human, it can be skipped by an assistant.

## What to Keep Out

```gitignore
# Never in a prompt, a context file, or a committed config:
.env
*.pem
credentials.json
```

Beyond secrets, exercise judgment about production data: customer records pasted in for debugging are a disclosure, and an anonymized sample answers the same question.

For sensitive repositories, restrict capability at the tool level rather than by instruction — read-only where write is not needed, no shell where shell is not needed, no network where network is not needed.

## Cost and Context

Two properties of how these tools bill are worth understanding, because both are controllable:

- **Context is the cost driver.** Long sessions, large files read in full, and verbose instructions all accumulate. Starting a fresh session for a new task is usually cheaper than continuing a long one.
- **Prompt caching is a prefix match.** Stable content at the front of a conversation — the instructions file, tool definitions — is cached and reread cheaply; anything that changes invalidates everything after it. This is another argument for keeping instructions files stable rather than regenerating them per session.

## Examples

**Good Example** — the repository carries the context, and the output is verified

```markdown
<!-- AGENTS.md at the repository root: read by the agent before it starts. -->
# Working in this repository

- Package manager is pnpm. Never run `npm install`.
- `pnpm verify` must pass before you claim a task is done: typecheck, lint,
  unit tests, build.
- Amounts are integer cents. Never introduce a float for money.
- Services return `Result`, never throw across a service boundary.
- No new dependencies without an ADR in docs/adr/.
```

```bash
# The agent's claim is checked by the same command a human would run,
# and by the same command CI runs — not by reading the diff and agreeing.
pnpm verify
git diff --stat                # is the diff the size the task implied?
git diff -- src/lib/money.ts   # did it touch anything it was told not to?
```

**Bad Example** — accept plausible output because it reads well

```ts
// Generated, reviewed by eye, merged. Every line is idiomatic and the function
// name is right, so nothing looked wrong.
export function applyDiscount(totalCents: number, percent: number): number {
  // Floating-point arithmetic on money, in a codebase whose one written rule
  // is that amounts are integer cents. Off by a penny on ~3% of orders.
  return totalCents * (1 - percent / 100);
}
```

Generated code fails in a specific way: it is fluent, conventional, and wrong about the things
only this repository knows. Fluency is not evidence — run the checks.

---

## Common Mistakes

- No instructions file, so conventions are re-inferred every session.
- An instructions file so long it goes stale and nobody updates it.
- Restating general programming knowledge in project instructions.
- Reviewing generated diffs more loosely than human ones.
- Secrets or production data pasted into prompts.
- MCP servers pointed at production databases.
- Rules stated as instructions where a hook could enforce them.
- No single verify command, so the assistant cannot check its own work.
- Treating a passing test suite as proof the change is correct.
- Accepting scope expansion because the extra changes look reasonable.

## Production Tips

- Put the instructions file under review like any other project convention — it is documentation that executes.
- Add a hook that runs the formatter after edits; it removes an entire category of review comment.
- Use skills for repeatable procedures and keep the always-loaded instructions file minimal.
- When an assistant repeatedly makes the same mistake, fix the context rather than repeating the correction — that is what the instructions file and skills are for.
- Keep model choice deliberate: reach for the most capable model on hard, long-horizon work, and a faster one on mechanical tasks. For current model identifiers, pricing, and capabilities, consult the provider's documentation rather than memory — this area changes faster than any document can track.

## AI Review Checklist

- Does the project have a committed instructions file, and is it current?
- Does it state stack, conventions, and constraints rather than general knowledge?
- Is there one command that verifies the project end to end?
- Are MCP servers scoped to non-production data, with credentials from the environment?
- Are project rules enforced by hooks where enforcement is possible?
- Does generated code go through the same review and CI gates as any other change?
- Is anything sensitive at risk of reaching a prompt?

## Related

- `knowledge/tools/25-editor-setup.md`
- `knowledge/tools/16-git-hooks.md`
- `knowledge/tools/27-dependency-management.md`
- `knowledge/ai/00-ai-engineering-principles.md`
- `knowledge/engineering/02-code-review.md`
