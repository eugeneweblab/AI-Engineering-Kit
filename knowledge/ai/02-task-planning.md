---
id: ai/02-task-planning
topic: ai
slug: task-planning
title: "Task Planning"
type: doc
order: 2
status: ready
tags: [ai, task-planning]
related: [ai/01-context-gathering, ai/03-code-generation, engineering/04-task-execution]
when_to_use: "Read before planning an AI-assisted task and prior to making any code changes."
---
# Task Planning

## Purpose

This document defines how an AI coding agent should plan work before making any modifications to a project.

Context gathering (the previous step) answers *what exists*. Planning answers *what will change, in what order, and how each change will be proven correct*. The output of this step is a concrete, reviewable artifact: a numbered, file-scoped plan — not a vague intention.

Planning reduces unnecessary changes, improves implementation quality, and minimizes the risk of regressions.

Implementation should always be the result of a plan—not the beginning of one.

For a non-trivial task, present the plan to the user for approval *before* editing any file. A plan is cheap to revise; a wrong implementation is expensive to unwind.

---

## Core Principle

Think first.

Code second.

Every engineering task should have an implementation plan before any file is modified.

The larger the task, the more detailed the plan should be.

---

## Planning Workflow

Always follow the same planning sequence.

```
Receive Task
      ↓
Understand Requirements
      ↓
Gather Context
      ↓
Identify Impact
      ↓
Design Solution
      ↓
Validate Plan
      ↓
Implement
```

Never skip planning because a task appears simple.

---

## Step 1 — Understand the Goal

Determine exactly what needs to be accomplished.

Identify:

- business objective;
- expected behavior;
- success criteria;
- technical constraints;
- out-of-scope items.

Do not assume hidden requirements.

---

## Step 2 — Break the Task Into Smaller Problems

Large tasks should never be implemented as one large change.

Decompose by **vertical slice**, not by horizontal layer. A layer-first breakdown ("do all the DB, then all the API, then all the UI") produces long-lived broken states where nothing works until the last step. A slice-first breakdown produces a sequence of independently verifiable, shippable increments.

Bad decomposition — horizontal, nothing works until the end:

```
1. Add every column to every table
2. Write every backend service method
3. Wire up every API route
4. Build every UI screen
5. Write all the tests at the end
```

Good decomposition — vertical, each slice is demonstrable on its own:

```
Feature: "Implement user profile editing"

Slice 1 — Edit display name (thinnest end-to-end path)
  DB: no change (column exists)
  API: PATCH /users/:id accepts { displayName }
  UI: inline edit field on profile page
  Test: PATCH persists; page reflects new name
  → Demoable. Ship or checkpoint here.

Slice 2 — Edit email (adds a new validation concern)
  API: reuse PATCH /users/:id, add email format + uniqueness check
  UI: reuse the inline edit field component from Slice 1
  Test: duplicate email rejected with 409

Slice 3 — Avatar upload (adds a new subsystem: storage)
  ...
```

Order the slices so the **thinnest end-to-end path ships first**. Each later slice adds exactly one new concern (a validation rule, a subsystem, a new field), which keeps every review small and every regression easy to localize.

---

## Step 3 — Identify Affected Areas

List every part of the project that may be impacted.

Examples:

- components;
- pages;
- services;
- APIs;
- database;
- authentication;
- configuration;
- tests;
- documentation.

Understanding impact reduces unexpected regressions.

---

## Step 4 — Record the Reuse Decision

The searching itself belongs to context gathering. Planning's job is to *commit the decision in writing* so the implementation cannot silently drift into a greenfield rewrite.

For each planned unit, the plan must resolve to one of three verdicts, and name the concrete artifact:

| Unit | Verdict | Artifact |
|------|---------|----------|
| Inline edit field | Reuse | `src/components/InlineEdit.tsx` |
| Email uniqueness check | Extend | add rule to `validators/user.ts` |
| Storage adapter | Create | none exists — new `services/storage.ts` |

A `Create` verdict is a claim that *no existing artifact fits*, and it should be justified in the plan, because "Create" is the verdict most likely to be wrong. If you cannot name the file you searched and rejected, you have not searched hard enough to justify creating a new one.

---

## Step 5 — Evaluate Risks

Every task has potential risks.

Examples:

- breaking existing functionality;
- API compatibility;
- performance regressions;
- security implications;
- accessibility issues;
- deployment risks;
- migration requirements.

Risks should be identified before implementation begins.

---

## Step 6 — Define Implementation Order

Determine the safest order of execution.

Prefer dependencies before consumers.

Example:

1. Database changes
2. Backend logic
3. API
4. Frontend
5. Tests
6. Documentation

Avoid constantly switching between unrelated parts of the project.

---

## Step 7 — Define Verification

Every plan should attach a **runnable check to each step**, not a single vague "test at the end". The strongest plans pair each change with the exact command or observation that proves it, so verification is mechanical rather than a judgment call.

Bad — verification deferred and unspecified:

```
Step 5: Test everything works.
```

Good — verification is per-step and executable:

```
Step 2: PATCH /users/:id accepts { email }
  Verify: npx jest users.controller.spec -t "updates email"
          curl -X PATCH localhost:3000/users/1 -d '{"email":"dup@x.com"}'
          → expect 409

Step 3: Existing avatars unchanged after migration
  Verify: SELECT count(*) FROM users WHERE avatar_url IS NOT NULL;
          → same count before and after
```

Prefer checks that a machine can run and read the result of. A verification step you cannot execute is a hope, not a plan.

---

## Planning Questions

Before implementation answer:

What problem am I solving?

Why does this problem exist?

Which files are affected?

Which files should NOT be modified?

Can existing code be reused?

Which architectural decisions must be respected?

How will I verify the implementation?

What could break?

---

## AI Execution Checklist

## Before Planning

- Read the entire task.
- Identify missing information.
- Clarify ambiguous requirements.
- Understand business goals.

---

## During Planning

- Inspect repository structure.
- Search similar implementations.
- Identify reusable code.
- Determine affected modules.
- Estimate implementation risk.
- Define implementation order.
- Define verification strategy.

---

## Before Implementation

- The task is fully understood.
- Context has been collected.
- Existing architecture is understood.
- Risks are documented.
- A verification strategy exists.
- The smallest possible implementation has been identified.

Only after completing every applicable step should implementation begin.

---

## Anti-patterns

Avoid:

Starting implementation immediately.

Planning while coding.

Creating unnecessary abstractions.

Ignoring existing implementations.

Changing architecture without necessity.

Combining unrelated tasks.

Planning only the happy path.

Ignoring rollback considerations.

---

## AI Responsibilities

During planning AI should:

Explain its reasoning.

Identify uncertainties.

State assumptions explicitly.

Recommend alternative approaches when appropriate.

Highlight potential risks.

Prefer existing project patterns over new ones.

Planning should be transparent.

---

## Example Planning Output

A good plan is file-scoped and step-ordered, and every step carries its reuse verdict and its verification. This is the artifact to present for approval before touching code — copy this shape:

Good:

```
## Plan: Add profile avatar upload

Goal
  Users can upload a profile image (≤2 MB, jpeg/png). Existing avatars unchanged.
Out of scope
  Image cropping, CDN resizing.

Affected files
  services/storage.ts        (create)
  validators/image.ts        (reuse — already validates mime + size)
  users.controller.ts        (extend — add POST /users/:id/avatar)
  ProfilePage.tsx            (extend — add <FileUpload/>, reuse existing component)

Steps (in dependency order)
  1. storage.ts: putObject() wrapping the existing S3 client in lib/s3.ts
       Verify: npx jest storage.spec -t "putObject uploads"
  2. users.controller.ts: POST /users/:id/avatar → validators/image.ts → storage
       Verify: curl upload of 3 MB file → 413; valid png → 200 + url
  3. ProfilePage.tsx: wire <FileUpload/> to the new endpoint
       Verify: manual — upload shows new avatar; reload persists
  4. Migration check: existing users retain avatar_url
       Verify: row count with avatar_url unchanged before/after

Risks
  - Auth: endpoint must reject uploads for other users' :id (add ownership guard).
  - Storage: bucket write permission required in staging env.

Rollback
  Endpoint is additive; revert the 3 files. No schema change to undo.
```

Poor:

```
I'll add avatar upload.
```

The second example contains no engineering thinking: no file scope, no ordering, no reuse verdicts, no per-step verification, and no rollback — nothing a reviewer can approve or a future agent can resume.

---

## Examples

**Good Example** — a plan with an order, a boundary, and a verification step

```text
Task: add rate limiting to the public API.

Findings from context gathering
  - Redis is already a dependency (src/lib/redis.ts), used for sessions.
  - Route handlers live in src/app/api/**; there is no shared middleware today.
  - CONTRIBUTING.md requires new middleware to be covered by an integration test.

Plan
  1. src/lib/rate-limit.ts — sliding-window counter on the existing Redis client.
  2. src/middleware.ts — apply to /api/* only; skip static assets via the matcher.
  3. Return 429 with Retry-After; document the header in docs/api.md.
  4. Integration test: 11th request within the window returns 429.

Explicitly out of scope
  - Per-plan limits (needs the billing model, which does not exist yet).
  - Rate limiting the tRPC routes — different transport, separate ticket.

Open question
  - Limit per IP or per API key? Keys exist but are optional today.
    → Proceeding with IP, noted in the PR description; trivial to change.
```

**Bad Example** — start editing and decide as you go

```text
Task: add rate limiting to the public API.

→ opened src/middleware.ts, added a counter in a module-level Map
→ noticed it resets on deploy, switched to Redis
→ noticed it also caught /_next/static, added an exclusion
→ while there, refactored the auth check "since it was nearby"
→ tests failed; changed the test to match the new behaviour
```

The diff now contains three unrelated changes, the auth refactor was never requested, and a
failing test was edited rather than explained. The open question about IP versus API key was
never surfaced, so it was answered silently by whoever typed first.

---

## Summary

Planning is an engineering activity, not administrative overhead.

A good implementation plan reduces defects, improves consistency, simplifies code review, and enables AI coding agents to make predictable engineering decisions.

## Related

- `knowledge/ai/01-context-gathering.md`
- `knowledge/ai/03-code-generation.md`
- `knowledge/engineering/04-task-execution.md`
