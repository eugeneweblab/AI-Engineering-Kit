---
id: typescript/00-overview
topic: typescript
slug: overview
title: "TypeScript Overview"
type: doc
order: 0
status: ready
tags: [typescript, overview, strict, unknown, isInteger, toFixed]
related: [typescript/02-type-system, typescript/03-type-inference, typescript/16-configuration, typescript/28-best-practices, typescript/100-common-antipatterns]
when_to_use: "Read first when starting any TypeScript work, to orient yourself before diving into a specific document."
---
# TypeScript Overview

## Purpose

This document is the map for the `typescript` topic. It explains what TypeScript is,
what these documents cover, and the order in which an agent should read them. It is not
a concept doc — it points to the concept docs. Read it first, then jump to the specific
document your task needs.

TypeScript is JavaScript with a static type system checked at compile time and erased at
runtime. The runtime is still JavaScript; the value TypeScript adds is a compiler that
catches type errors before code ships. Everything in this topic exists to help an agent
use that compiler correctly rather than fighting it or silencing it.

## Why It Matters

Type errors are the most common class of runtime bug in JavaScript: `undefined is not a
function`, `cannot read property of null`, silent `NaN` propagation. TypeScript moves
those failures from production to the editor. But the compiler only helps if the types
are honest. A codebase full of `any`, `as` casts, and `@ts-ignore` has the syntax of
TypeScript with the safety of JavaScript — worse, because it lies. These documents exist
to keep the type layer honest, so the green checkmark actually means something.

## Core Principles

- **Types describe reality, not wishes.** A type must match what a value actually is at
  runtime. A cast that isn't true is a bug the compiler can no longer catch.
- **Prefer inference; annotate boundaries.** Let the compiler infer local types; write
  explicit types at public boundaries (function signatures, exports, module edges).
- **`strict` mode is the floor, not a goal.** Every rule here assumes `strict: true`.
  Code that only compiles with strictness off is out of scope.
- **Make illegal states unrepresentable.** Use unions, literals, and narrow types so the
  compiler rejects bad states instead of your runtime code checking for them.

## Best Practices

- Read [02-type-system](02-type-system.md) before designing any data model, and
  [03-type-inference](03-type-inference.md) before deciding what to annotate.
- Enable `strict` and treat every new warning as a defect (see [16-configuration](16-configuration.md)).
- Reach for narrow types first (unions, literals, `readonly`) and widen only when a
  concrete use forces it. Widening later is cheap; narrowing later breaks callers.
- Keep `any` out of the codebase; use `unknown` at untyped boundaries and narrow it.

## How These Documents Fit Together

Read roughly in order; each layer builds on the one before.

- **Foundations** — [01-language-fundamentals](01-language-fundamentals.md) covers
  syntax, variables, and control flow. [02-type-system](02-type-system.md) and
  [03-type-inference](03-type-inference.md) explain how types are declared and deduced.
- **Building blocks** — [04-functions](04-functions.md) and [05-objects](05-objects.md)
  cover the two shapes almost all code takes. [06-interfaces](06-interfaces.md) and
  [07-type-aliases](07-type-aliases.md) name those shapes.
- **Composition** — [08-generics](08-generics.md), [09-utility-types](09-utility-types.md),
  [10-enums-and-literals](10-enums-and-literals.md), [11-unions-and-intersections](11-unions-and-intersections.md),
  and [12-type-guards](12-type-guards.md) let types combine and narrow.
- **Systems** — [14-modules](14-modules.md), [16-configuration](16-configuration.md),
  [17-error-handling](17-error-handling.md), and [18-asynchronous-programming](18-asynchronous-programming.md)
  cover how code is organized and run.
- **Craft** — [20-immutability](20-immutability.md) through
  [28-best-practices](28-best-practices.md) and the checklists
  ([98](98-production-checklist.md), [99](99-ai-review-checklist.md),
  [100](100-common-antipatterns.md)) cover quality and review.

## Examples

**Good Example** — honest types the compiler can enforce

```ts
// A union makes the two states explicit; the compiler forces callers to handle both.
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

function parsePort(raw: string): Result<number> {
  const n = Number(raw);
  return Number.isInteger(n) ? { ok: true, value: n } : { ok: false, error: "not an int" };
}
```

**Bad Example** — types that lie, defeating the whole topic

```ts
// `as any` tells the compiler to stop checking; the runtime shape is unverified.
function parsePort(raw: string): number {
  return (raw as any).toFixed(); // compiles, then throws at runtime
}
```

## Common Mistakes

- Treating TypeScript as "JavaScript with annotations" and reaching for `any` under
  deadline pressure — this discards the entire benefit.
- Skipping the foundational docs and copying advanced patterns without understanding
  inference, causing types that don't narrow.
- Turning off `strict` to make errors go away instead of fixing the underlying type.

## AI Review Checklist

- Is `strict` mode on, and does the code compile clean under it?
- Are public boundaries explicitly typed while locals rely on inference?
- Is `any` absent, with `unknown` used at untyped edges?
- Do the types match runtime reality, with no unjustified `as` casts?

## Related

- `knowledge/typescript/02-type-system.md`
- `knowledge/typescript/03-type-inference.md`
- `knowledge/typescript/16-configuration.md`
- `knowledge/typescript/28-best-practices.md`
- `knowledge/typescript/100-common-antipatterns.md`
