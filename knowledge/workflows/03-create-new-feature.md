---
id: workflows/03-create-new-feature
topic: workflows
slug: create-new-feature
title: "Workflow — Create a New Feature"
type: doc
order: 3
status: ready
tags: [workflows, create-new-feature, ExportButton, unparse, createObjectURL, Blob, scope, open]
related: [engineering/04-task-execution, ai/02-task-planning, workflows/07-add-api-endpoint]
  - engineering/05-context-first-development
  - engineering/00-engineering-principles
  - architecture/00-overview
  - architecture/11-api-first
  - architecture/25-documentation
  - security/04-authorization
  - performance/00-overview
  - accessibility/00-overview
  - testing/98-production-checklist
when_to_use: "Follow this workflow when implementing a new feature in an existing project."
---
# Workflow — Create a New Feature

## Purpose

This workflow defines the standard engineering process for implementing a new feature in an existing software project.

A new feature should integrate naturally into the existing system without introducing unnecessary complexity, duplication, or architectural inconsistencies.

The objective is to deliver maintainable functionality that follows the project's engineering standards.

---

## Goal

Deliver a feature that:

- satisfies the business requirements;
- follows the existing architecture;
- reuses existing code whenever possible;
- minimizes technical debt;
- is safe to review, test, and maintain.

---

## Workflow Overview

```
Receive Requirements
        ↓
Understand Business Goal
        ↓
Analyze Existing System
        ↓
Identify Reusable Code
        ↓
Design Implementation
        ↓
Estimate Impact
        ↓
Implement Incrementally
        ↓
Verify
        ↓
Document
        ↓
Complete
```

---

## Step 1 — Understand the Requirements

Read the complete specification.

Determine:

- business objective;
- expected user behavior;
- acceptance criteria;
- technical constraints;
- dependencies;
- assumptions.

If any requirement is unclear, resolve it before implementation.

Gather context deliberately before writing any code — see
[`../engineering/05-context-first-development.md`](../engineering/05-context-first-development.md).
When requirements imply a non-trivial trade-off (build vs. reuse, sync vs. async, new
dependency vs. existing tooling), record the reasoning using
[`../engineering/01-decision-framework.md`](../engineering/01-decision-framework.md).

---

## Step 2 — Understand the Existing System

Investigate how similar functionality is implemented.

Review:

- architecture;
- folder structure;
- reusable components;
- services;
- utilities;
- APIs;
- coding conventions;
- testing strategy.

Every feature should feel native to the project.

Relevant knowledge topics:

- [`../architecture/00-overview.md`](../architecture/00-overview.md) — how the system is layered and where new behavior belongs.
- [`../react/22-folder-structure.md`](../react/22-folder-structure.md) — conventions for locating components, hooks, and modules in a React codebase.

---

## Step 3 — Search Before Creating

Before creating new code, search for reusable implementations.

Examples:

Components

Services

Utilities

Hooks

Validation

Layout containers

Configuration

Constants

Types

Prefer extension over duplication.

Reuse before creating is a core engineering principle — see
[`../engineering/00-engineering-principles.md`](../engineering/00-engineering-principles.md)
for the DRY and single-responsibility guidance that governs this step.

---

## Step 4 — Design the Implementation

Create a technical plan.

Identify:

- affected modules;
- new modules;
- reusable code;
- data flow;
- API changes;
- database changes;
- configuration changes;
- testing requirements.

The implementation plan should be understandable before coding begins.

Relevant knowledge topics:

- [`../architecture/03-clean-architecture.md`](../architecture/03-clean-architecture.md) — keeping business logic independent of frameworks and I/O.
- [`../architecture/11-api-first.md`](../architecture/11-api-first.md) — designing the contract before the implementation when the feature exposes or consumes an API.

---

## Step 5 — Estimate Impact

Determine what could be affected.

Review:

- public APIs;
- authentication;
- authorization;
- shared components;
- existing workflows;
- performance;
- accessibility;
- SEO (if applicable);
- analytics;
- caching.

Every feature has consequences beyond its own code.

Consult the relevant knowledge topic for each area of impact:

- Authentication and authorization — [`../security/03-authentication.md`](../security/03-authentication.md) and [`../security/04-authorization.md`](../security/04-authorization.md).
- Performance and caching — [`../performance/00-overview.md`](../performance/00-overview.md) and [`../performance/08-caching.md`](../performance/08-caching.md).
- Accessibility — [`../accessibility/00-overview.md`](../accessibility/00-overview.md).
- SEO (for user-facing pages) — [`../seo/00-overview.md`](../seo/00-overview.md).

---

## Step 6 — Implement Incrementally

Implement in small logical steps.

Recommended order:

Infrastructure

↓

Data layer

↓

Business logic

↓

API

↓

UI

↓

Interactions

↓

Validation

↓

Tests

↓

Documentation

Avoid implementing the entire feature in one large change.

When the feature introduces a new HTTP surface, design the resources and error contract
first — see [`../rest-api/03-resource-design.md`](../rest-api/03-resource-design.md) and
[`../rest-api/09-error-handling.md`](../rest-api/09-error-handling.md). For error handling
inside the UI layer, follow
[`../react/19-error-handling.md`](../react/19-error-handling.md).

---

## Step 7 — Verify Functionality

Verify:

- happy path;
- edge cases;
- invalid input;
- permissions;
- loading states;
- empty states;
- error handling.

The feature is not complete until every important scenario has been reviewed.

Choose the right level of test coverage for each concern:

- [`../testing/02-unit-testing.md`](../testing/02-unit-testing.md) — business logic and pure functions.
- [`../testing/04-e2e-testing.md`](../testing/04-e2e-testing.md) — the happy path and critical user flows end to end.
- [`../testing/17-security-testing.md`](../testing/17-security-testing.md) — permission and input-validation checks.

---

## Step 8 — Review Integration

Confirm the feature integrates naturally.

Review:

- navigation;
- shared layouts;
- design consistency;
- API compatibility;
- performance impact;
- accessibility;
- responsive behavior.

The feature should feel like part of the product—not an addition.

Relevant knowledge topics:

- [`../accessibility/13-responsive-accessibility.md`](../accessibility/13-responsive-accessibility.md) — responsive behavior that stays accessible across breakpoints.
- [`../performance/29-performance-review.md`](../performance/29-performance-review.md) — confirming the change did not regress load or runtime performance.

---

## Step 9 — Update Documentation

When appropriate update:

- README;
- API documentation;
- architecture documentation;
- environment variables;
- configuration guides;
- developer documentation.

Documentation is part of implementation.

For conventions on what to document and where, see
[`../architecture/25-documentation.md`](../architecture/25-documentation.md). Non-obvious
design trade-offs made during the feature should be captured as an Architecture Decision
Record — [`../architecture/26-architecture-decision-records.md`](../architecture/26-architecture-decision-records.md).

---

## AI Execution Checklist

## Investigation

☐ Read the complete requirements.

☐ Understand the business goal.

☐ Review existing architecture.

☐ Search for similar implementations.

☐ Identify reusable code.

☐ Identify affected modules.

---

## Planning

☐ Create an implementation plan.

☐ Estimate risks.

☐ Define implementation order.

☐ Define verification strategy.

---

## Implementation

☐ Modify only required files.

☐ Preserve architecture.

☐ Reuse existing code.

☐ Avoid duplicate functionality.

☐ Keep responsibilities separated.

---

## Verification

☐ Verify all acceptance criteria.

☐ Verify edge cases.

☐ Verify permissions.

☐ Verify responsive behavior.

☐ Verify accessibility.

☐ Verify tests.

☐ Update documentation if necessary.

---

## Manual Verification

Before completing the feature:

- complete every acceptance criterion;
- verify user flows;
- verify navigation;
- verify responsive layouts;
- verify browser console contains no errors;
- verify network requests behave correctly;
- verify logs contain no unexpected warnings.

---

## Examples

**Good Example** — the feature is shaped by what the codebase already does

```text
Feature: export orders as CSV

Context first
  - src/lib/export/to-csv.ts exists; the invoices page already uses it.
  - Exports stream from a Route Handler (src/app/api/invoices/export/route.ts).
  - CONTRIBUTING.md: no new dependencies without an ADR.

Plan
  1. src/app/api/orders/export/route.ts — mirrors the invoices route.
  2. Reuse toCsv; add the orders column map beside the invoices one.
  3. Stream from the repository, not from the paginated page query.
  4. Integration test: 4,000 seeded orders produce 4,001 lines.

Out of scope (stated, not silently dropped)
  - XLSX export — asked for "eventually"; separate ticket.
  - Column selection UI — not requested.
```

```ts
// The implementation is unremarkable on purpose: a reviewer who knows the
// invoices route already knows this one.
export async function GET(request: NextRequest) {
  const session = await auth();
  if (!session) return new Response('Unauthorized', { status: 401 });

  const rows = ordersRepository.streamAllForUser(session.userId);   // not the page query
  return new Response(toCsvStream(rows, ORDER_COLUMNS), {
    headers: {
      'content-type': 'text/csv; charset=utf-8',
      'content-disposition': 'attachment; filename="orders.csv"',
    },
  });
}
```

**Bad Example** — the feature is shaped by the first idea

```tsx
'use client';
import { unparse } from 'papaparse';       // new dependency, no ADR

export function ExportButton({ orders }: { orders: Order[] }) {
  // `orders` is the current page — 20 of 4,000. The export is silently
  // incomplete, and it will be trusted for months before anyone notices.
  const download = () => {
    const csv = unparse(orders);
    window.open(URL.createObjectURL(new Blob([csv], { type: 'text/csv' })));
  };
  return <button onClick={download}>Export CSV</button>;
}
```

---

## Common Mistakes

Avoid:

Starting implementation without understanding the business problem.

Creating duplicate components.

Ignoring existing architecture.

Combining feature development with refactoring.

Introducing unnecessary dependencies.

Changing unrelated files.

Skipping verification.

Treating documentation as optional.

---

## Completion Criteria

The workflow is complete only if:

- all requirements are satisfied;
- existing architecture is respected;
- reusable code has been used where appropriate;
- verification is complete;
- documentation is accurate;
- regression risk is acceptable;
- self-review has been completed.

---

## Expected AI Output

After completing this workflow, the AI should be able to explain:

- the business objective;
- the implementation strategy;
- reused components and services;
- newly created modules;
- affected files;
- verification performed;
- remaining risks or assumptions.

---

## Self-Verification — Topic Checklists

Before marking the feature complete, run the `98`/`99`/`100` checklists for every knowledge
topic the feature touched. Start with the topics that dominate the change:

- Architecture — [`../architecture/98-production-checklist.md`](../architecture/98-production-checklist.md), [`../architecture/99-ai-review-checklist.md`](../architecture/99-ai-review-checklist.md), [`../architecture/100-common-antipatterns.md`](../architecture/100-common-antipatterns.md).
- Testing — [`../testing/98-production-checklist.md`](../testing/98-production-checklist.md), [`../testing/99-ai-review-checklist.md`](../testing/99-ai-review-checklist.md), [`../testing/100-common-antipatterns.md`](../testing/100-common-antipatterns.md).
- Security — [`../security/98-production-checklist.md`](../security/98-production-checklist.md), [`../security/99-ai-review-checklist.md`](../security/99-ai-review-checklist.md), [`../security/100-common-antipatterns.md`](../security/100-common-antipatterns.md).

If the feature includes UI, also close with the React and accessibility checklists —
[`../react/98-production-checklist.md`](../react/98-production-checklist.md),
[`../react/99-ai-review-checklist.md`](../react/99-ai-review-checklist.md),
[`../accessibility/98-production-checklist.md`](../accessibility/98-production-checklist.md),
and [`../accessibility/99-ai-review-checklist.md`](../accessibility/99-ai-review-checklist.md).

---

## Summary

A successful feature is not measured by the amount of new code.

It is measured by how naturally it integrates into the existing product while remaining maintainable, consistent, and easy to extend.

## Related

- `knowledge/engineering/04-task-execution.md`
- `knowledge/ai/02-task-planning.md`
- `knowledge/workflows/07-add-api-endpoint.md`
