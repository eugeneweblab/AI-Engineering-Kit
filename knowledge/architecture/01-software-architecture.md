---
id: architecture/01-software-architecture
topic: architecture
slug: software-architecture
title: "Software Architecture"
type: doc
order: 1
status: ready
tags: [architecture, software-architecture]
related: [architecture/02-system-design, architecture/03-clean-architecture, architecture/26-architecture-decision-records, architecture/28-best-practices, architecture/30-engineering-principles]
when_to_use: "Read before making any decision that will be expensive to reverse — module boundaries, data ownership, or a new dependency between components."
---
# Software Architecture

## Purpose

This document defines what software architecture *is* in practice and how to reason about
it: identifying the decisions that are expensive to change, drawing component boundaries,
and directing dependencies. It is written so an agent can make a structural decision
deliberately rather than by accident, and defend it later.

Architecture is not diagrams and it is not the framework you chose. Architecture is the set
of design decisions that are costly to reverse once code depends on them.

## Why It Matters

The cost of a change grows with the number of things that depend on it. A function body is
cheap to rewrite; a module boundary that ten features cross is not; the choice of which
service owns which data is nearly permanent. Because agents generate code quickly, they can
cement a bad boundary across a codebase in minutes — and every later feature inherits it.
Spending a few minutes to place a boundary correctly saves weeks of untangling. The whole
discipline is about front-loading the decisions that are painful to undo.

## Core Principles

- **Separate the expensive-to-change from the cheap-to-change.** Isolate stable business
  rules from volatile details (frameworks, databases, third-party APIs) so the volatile
  parts can churn without touching the core. This is the single most important move.
- **Dependencies point toward stability.** A component may depend on something more stable
  than itself, never on something more volatile. Use interfaces to invert any dependency
  that violates this.
- **High cohesion, low coupling.** Things that change together belong together; things that
  change independently belong apart. Measure a boundary by how often a change forces edits
  on both sides — frequent cross-cutting edits mean the boundary is wrong.
- **Make the important decisions explicit and few.** A good architecture names a handful of
  load-bearing decisions and leaves everything else free. Over-specifying rigidifies the
  system; under-specifying invites chaos.
- **Optimize for the readers, not the writer.** Code is read and modified far more than it
  is written. Structure serves the people (and agents) who arrive later.

## Best Practices

- Before adding a dependency between two modules, ask which is more stable. If the arrow
  points the wrong way, invert it with an interface owned by the stable side. The cost is
  one indirection; the benefit is the stable side never recompiles when the detail changes.
- Keep business rules free of framework and I/O types. A domain function should not import
  your HTTP framework or ORM — if it does, the rule is now coupled to a detail.
- Choose the simplest structure that satisfies today's constraints plus one realistic step
  of growth. Do not architect for hypothetical 100x scale you cannot yet justify.
- Record load-bearing decisions as [ADRs](26-architecture-decision-records.md) with the
  alternatives considered and the trade-off accepted. Undocumented decisions get reversed
  by the next person who does not see the reasoning.
- Revisit boundaries when they generate friction. Architecture is a set of hypotheses;
  treat repeated cross-boundary churn as evidence to redraw the line.

## Examples

**Good Example** — business rule depends on an abstraction it owns

```ts
// domain/pricing.ts — pure, no framework or I/O imports
interface ExchangeRates {
  rate(from: string, to: string): number; // owned by the domain
}

// The rule is stable; the rate source (HTTP, cache, file) can change freely.
export function totalInUsd(items: Item[], rates: ExchangeRates): number {
  return items.reduce((sum, i) => sum + i.price * rates.rate(i.currency, "USD"), 0);
}
```

**Bad Example** — business rule coupled to a volatile detail

```ts
import { httpClient } from "../infra/http"; // domain now depends on transport

export async function totalInUsd(items: Item[]): Promise<number> {
  let sum = 0;
  for (const i of items) {
    // A pricing rule reaching out over HTTP: untestable without a network,
    // and a change to the rates vendor forces edits inside core logic.
    const rate = await httpClient.get(`/fx/${i.currency}/USD`);
    sum += i.price * rate.data.value;
  }
  return sum;
}
```

## Common Mistakes

- Confusing architecture with tools: "we use microservices/GraphQL" describes technology,
  not boundaries or dependency direction.
- Letting framework or database types leak into business logic, welding the core to a
  detail that will eventually change.
- Big-upfront-design that specifies everything, producing a rigid system that resists the
  first real requirement.
- No-design-at-all, where boundaries emerge accidentally from import order and deadlines.
- Adding abstraction with no volatility behind it — an interface with exactly one
  implementation that will never have a second is just indirection tax.

## Production Tips

- Enforce dependency direction mechanically (lint rules like `no-restricted-imports`, or
  module-boundary tools) so violations fail CI instead of accumulating silently.
- Keep an up-to-date component diagram and an ADR log in the repo; a design no one can read
  is not a shared design.

## AI Review Checklist

- Do dependencies point from volatile components toward stable ones?
- Are business rules free of framework, ORM, and transport imports?
- Is each new abstraction justified by real, expected variation — not speculation?
- Does each module have high internal cohesion and few outward dependencies?
- Are the load-bearing decisions captured as [ADRs](26-architecture-decision-records.md)?

## Related

- `knowledge/architecture/02-system-design.md`
- `knowledge/architecture/03-clean-architecture.md`
- `knowledge/architecture/26-architecture-decision-records.md`
- `knowledge/architecture/28-best-practices.md`
- `knowledge/architecture/30-engineering-principles.md`
