---
id: ai/01-context-gathering
topic: ai
slug: context-gathering
title: "Context Gathering"
type: doc
order: 1
status: ready
tags: [ai, context-gathering, CurrentUser, UserRepository, CreateOrderDto, formatPrice, formatCurrency]
related: [ai/02-task-planning, engineering/05-context-first-development, workflows/02-fix-a-bug]
when_to_use: "Read before gathering context for any AI-assisted coding task."
---
# Context Gathering

## Purpose

This document defines how an AI coding agent should gather context before making engineering decisions.

The quality of generated code is directly proportional to the quality of the collected context.

AI should spend more effort understanding the project than generating code.

---

## Core Principle

Never generate code using only the user's request.

The user's request is only one source of information.

Engineering decisions should also be based on:

- project architecture;
- existing code;
- documentation;
- configuration;
- dependencies;
- established conventions.

---

## Context Priority

Always gather context in the following order.

## Level 1 — User Request

Understand:

- what is requested;
- expected outcome;
- constraints;
- explicit requirements;
- implicit assumptions.

Questions should be asked whenever requirements are incomplete.

---

## Level 2 — Repository Structure

Understand the repository before searching inside it.

Start by mapping the tree while ignoring noise directories, then read the manifest that pins the stack:

```bash
# Map the source tree without node_modules/vendor/build noise
rg --files --hidden -g '!.git' \
  | rg -v 'node_modules|vendor|dist|build|\.next|coverage' \
  | sed 's|/[^/]*$||' | sort -u | head -50

# Identify the stack from the manifest, not from guessing
cat package.json | jq '{name, scripts, dependencies, devDependencies}'
```

Read the folder layout as a signal of the architecture. A `src/modules/*/` layout with per-module controllers and services implies a modular (often NestJS) architecture; a `app/` directory with `page.tsx`/`layout.tsx` implies the Next.js App Router; a flat `pkg/` and `cmd/` split implies Go. Match your output to the layout you observe — do not impose a layout the repo does not use.

The repository often reveals architectural decisions before any documentation does.

---

## Level 3 — Existing Implementation

Before creating anything new, find the nearest existing implementation and copy its shape. The goal is to locate a sibling that already solves the same *category* of problem, then mirror its structure, imports, and error handling.

Two-phase search: first find the file, then read it whole.

```bash
# Phase 1 — locate: which files define a pattern like the one you need?
# Example: adding a new REST controller — find the existing ones.
rg -l --type ts 'export class \w+Controller' src/

# Example: adding a data-fetching hook — find the existing hooks.
rg -l "^export function use[A-Z]" src/ -g '*.ts' -g '*.tsx'

# Phase 2 — read the closest match end-to-end, including its imports and test.
# Never skim; the imports reveal the project's chosen libraries and helpers.
```

When you have a candidate, also open its co-located test. The test is the executable specification of the convention: it shows how the module is instantiated, what is mocked, and what the expected error shape is. Reproducing the test style is as important as reproducing the source style.

Existing implementations are the strongest source of engineering context — a matching sibling file resolves naming, layering, error handling, and testing questions in a single read.

---

## Level 4 — Configuration

Inspect configuration files.

Examples:

- package.json
- tsconfig.json
- composer.json
- eslint.config.js
- prettier.config.js
- next.config.js
- nest-cli.json
- wp-config.php
- docker-compose.yml

Configuration often explains architectural decisions.

---

## Level 5 — Documentation

Read available documentation.

Examples:

- README
- architecture documents
- ADRs
- playbooks
- contribution guides
- coding standards

Documentation explains decisions that code alone cannot.

---

## Level 6 — Dependencies

Determine which libraries are already available before reaching for a new one.

Check the manifest and the lockfile — the lockfile lists transitive packages that are installed and importable even though they are not direct dependencies:

```bash
# Is a date library already present? Prefer it over adding another.
jq '.dependencies + .devDependencies | keys[]' package.json \
  | rg -i 'date|dayjs|luxon|moment'

# Confirm it is actually resolvable, not just declared.
rg -c "from 'dayjs'|require\\('dayjs'\\)" src/ | head
```

Before proposing `npm install <x>`, state which existing dependency you checked and why it does not cover the need. For example: "The repo already uses `zod` for validation, so I will validate the new payload with `zod` rather than adding `joi`."

Never introduce a new dependency before verifying whether the project already contains an appropriate solution. Additional dependencies increase maintenance and audit cost.

---

## Repository Investigation

Before implementation, AI should answer:

What technologies are used?

How is the project organized?

Which architectural pattern is followed?

How are files named?

How are components organized?

How are services organized?

How is state managed?

How are errors handled?

How are tests written?

How is styling implemented?

If these questions cannot be answered, additional investigation is required.

---

## Searching Strategy

Never stop after the first search result. Use a *widen-then-narrow* loop: start with a broad symbol search across the whole repo, then narrow to the directory and file that own the concern.

Search by **symbol and usage**, not by guessed folder name. Folder conventions vary; a symbol search finds the code wherever it actually lives.

```bash
# Widen: where is authentication handled at all?
rg -i 'auth|jwt|session|passport|bearer' -l

# Narrow: how is the current user actually resolved in requests?
rg -n 'getCurrentUser|@CurrentUser|req\.user|useSession' -g '*.ts' -g '*.tsx'

# Trace a symbol both ways: definition and every call site.
rg -n 'class UserRepository'            # definition
rg -n 'new UserRepository|UserRepository\b'   # usages that show how it is wired
```

Prefer AST- or symbol-aware navigation when it is available (LSP "go to definition" / "find references", or a symbol search tool) over plain text search — it resolves re-exports and aliases that grep misses. Fall back to `rg` when no language server is present.

Good: search for the symbol `PrismaService`, find its provider registration, then follow imports to see how repositories consume it.

Bad: assume database code lives in `db/` because that is where a previous project kept it, search only that folder, find nothing, and conclude the project has no data layer.

Large repositories often contain multiple valid implementations — after finding one, run the same search once more to confirm it is the canonical pattern and not an outlier.

---

## Detect Existing Conventions

Before writing code, identify conventions for:

Naming

Folder organization

Imports

Error handling

Logging

Testing

Comments

Documentation

Formatting

Architecture

Detect conventions from evidence, not assumption. A few targeted reads settle most questions:

```bash
# Naming: are files kebab-case, PascalCase, or camelCase?
rg --files -g '*.ts' src/ | sed 's|.*/||' | head -20

# Imports: alias paths or relative? Read the tsconfig paths map.
jq '.compilerOptions.paths' tsconfig.json

# Formatting/lint rules are machine-readable — obey them literally.
cat .prettierrc .eslintrc* eslint.config.* 2>/dev/null
```

Follow existing conventions unless there is a clear engineering reason not to. When two files disagree, follow the newer or more frequently referenced one, and note the ambiguity.

---

## Missing Context

If important context is unavailable, AI should explicitly identify what is missing.

Examples:

"I could not determine how authentication is implemented."

"No existing component follows this pattern."

"The repository does not appear to contain testing guidelines."

Missing context should be communicated before implementation.

---

## When To Ask Questions

AI should ask questions when:

requirements are ambiguous;

multiple implementations are equally valid;

repository conventions are unclear;

business rules are missing;

implementation affects security;

implementation affects public APIs;

implementation changes architecture.

Questions reduce incorrect assumptions.

---

## Context Checklist

Before implementation verify:

- I understand the requested outcome.
- I understand the repository structure.
- I inspected similar implementations.
- I identified project conventions.
- I checked configuration.
- I reviewed documentation.
- I searched for reusable code.
- I understand the affected architecture.
- I identified possible side effects.
- I know which files should change.

Implementation should not begin until every applicable item has been completed.

---

## Anti-patterns

Avoid:

Generating code after reading only one file.

Creating new components without searching the repository.

Ignoring existing architecture.

Adding dependencies unnecessarily.

Assuming coding conventions.

Using examples from unrelated projects instead of repository code.

Treating every task as a greenfield implementation.

---

## Worked Example — "Add a `POST /orders` endpoint"

This is what disciplined context gathering looks like as a trace, before writing a single line of the new endpoint.

```bash
# 1. Confirm the stack and how routes are defined.
jq '.dependencies | keys[]' package.json | rg -i 'express|fastify|nestjs|next'
#   → @nestjs/core → this is a NestJS app; endpoints are controllers, not route files.

# 2. Find the nearest sibling: an existing write endpoint to mirror.
rg -l 'export class \w+Controller' src/ | rg -i 'user|product'
#   → src/products/products.controller.ts

# 3. Read that controller AND its service AND its test end-to-end.
#    Observed: DTOs validated with class-validator, service injected via constructor,
#    errors thrown as NotFoundException, tests use Test.createTestingModule.

# 4. Check for a reusable orders domain before creating one.
rg -ni 'order' src/ -l
#   → src/orders/orders.module.ts already exists with a service but no create method.

# 5. Confirm validation library so the new DTO matches convention.
jq '.dependencies | keys[]' package.json | rg 'class-validator|zod'
#   → class-validator — use decorators, not zod, for the CreateOrderDto.
```

Before / after the same task, the difference is entirely in the context step:

Bad — skips gathering:

> Generates a new `src/routes/orders.ts` Express-style route file with manual `req.body` parsing and a `res.status(500)` catch-all — none of which matches the NestJS project.

Good — acts on gathered context:

> Adds `createOrder` to the existing `OrdersService`, a `CreateOrderDto` using `class-validator` decorators, a controller method that throws `BadRequestException`, and a spec mirroring `products.controller.spec.ts`.

The Good result is not more clever code. It is code that a reviewer cannot distinguish from the rest of the repository, because it was derived from the repository.

---

## Examples

**Good Example** — find the existing answer before writing a new one

```bash
# Does this already exist? Search by behaviour, not by the name you would pick.
rg -n "formatCurrency|toCurrency|formatPrice" src/
rg -n "Intl.NumberFormat" src/

# How does this codebase already solve the adjacent problem?
rg -n --files-with-matches "export function use[A-Z]" src/hooks/ | head

# What does the project itself say about the rule?
sed -n '1,80p' CONTRIBUTING.md
rg -n "currency|money|price" docs/
```

```text
Found before writing anything:
  src/lib/format.ts        formatCurrency(cents, locale) — already handles rounding
  src/lib/money.ts         Money type; amounts are integer cents everywhere
  CONTRIBUTING.md          "never store amounts as floats"

Conclusion: the task is to call the existing helper from the new component,
not to add a second formatter. Scope shrank from ~80 lines to 3.
```

**Bad Example** — start from the request and infer the rest

```ts
// Written without searching. A formatter already existed three directories away,
// and this one disagrees with it: it takes a float, rounds differently, and
// hardcodes the locale the rest of the app takes from the user.
export function formatPrice(price: number): string {
  return '£' + price.toFixed(2);
}
```

The result compiles, passes review if the reviewer is also unaware, and produces prices that
differ by a penny from every other screen — a defect that surfaces in accounting, not in tests.

---

## Summary

Context gathering is the highest return activity in AI-assisted software development.

The best AI agents are not those that generate code the fastest.

They are the ones that understand the repository the best before generating a single line of code.

## Related

- `knowledge/ai/02-task-planning.md`
- `knowledge/engineering/05-context-first-development.md`
- `knowledge/workflows/02-fix-a-bug.md`
