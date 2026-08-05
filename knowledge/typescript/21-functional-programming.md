---
id: typescript/21-functional-programming
topic: typescript
slug: functional-programming
title: "TypeScript Functional Programming"
type: doc
order: 21
status: ready
tags: [typescript, functional-programming, applyDiscount, BadRequest, readonly, checkout, load, save]
related: [typescript/20-immutability, typescript/19-collections, typescript/04-functions, typescript/08-generics, typescript/17-error-handling]
when_to_use: "Read before structuring business logic as data transformations, composing functions, or reviewing code for hidden side effects."
---
# TypeScript Functional Programming

## Purpose

This document defines how to apply functional programming in TypeScript: pure functions,
composition, higher-order functions, and modeling effects and failure as values. It is
written so an agent can structure logic as predictable transformations that are trivial
to test, rather than as tangled procedures that reach out and mutate the world.

Functional programming here is a discipline, not a dogma. The goal is to push side
effects (I/O, mutation, randomness, time) to the edges and keep the core a set of pure
functions — inputs in, value out, nothing else touched.

## Why It Matters

A pure function is the cheapest thing in software to reason about and to test: same
input, same output, no setup, no mocks, no order dependence. Code that mixes computation
with side effects is the opposite — you cannot test the calculation without also standing
up a database, and a bug could live in the logic or the plumbing. Hidden mutation and
shared state are what make large codebases fragile: a change here breaks something there
with no visible link. Keeping the core pure shrinks the surface where surprises can hide.

## Core Principles

- **A pure function has no side effects and depends only on its arguments.** No mutation
  of inputs, no I/O, no reads of mutable outer state. This is what makes it testable.
- **Push effects to the edges.** Do I/O at the boundary, pass plain data into pure logic,
  and apply the result at the boundary again. The middle stays pure.
- **Prefer expressions over statements.** Return a value; avoid accumulating into mutable
  variables. `map`/`filter`/`reduce` over an explicit mutating loop where readable.
- **Model failure and absence as values.** Return `T | undefined` or a `Result` type
  instead of throwing for expected outcomes, so the compiler forces callers to handle it.
- **Compose small functions.** Build behavior by combining single-purpose functions;
  each is independently testable and nameable.

## Best Practices

- Keep functions single-purpose and total — for every input in the type, they return a
  defined output. A function that throws on some valid inputs is not total; widen the
  return type to reflect the real outcomes.
- Do not mutate arguments. Take `readonly` inputs and return new values (see
  [immutability](20-immutability.md)); mutation inside a "pure" helper is a silent trap.
- Use higher-order functions (`map`, `filter`, `reduce`, custom combinators) but name the
  callback when it is non-trivial — a deeply nested anonymous chain is not more readable.
- Prefer a `Result<T, E>` (or discriminated `{ ok: true } | { ok: false }`) for expected
  failures in a pipeline; reserve `throw` for programmer errors and truly exceptional I/O.
- Avoid shared mutable module-level state. If you need memoization or a cache, make it
  explicit and bounded, not a hidden global that breaks referential transparency.
- Keep currying and point-free style for genuinely reusable combinators; do not obfuscate
  ordinary business logic with clever composition the next reader must decode.

## Examples

**Good Example** — pure core, effects at the edge, failure as a value

```ts
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

// Pure: no I/O, no mutation, total over its input. Trivial to unit-test.
function applyDiscount(order: Readonly<Order>, code: string): Result<Order> {
  const pct = DISCOUNTS[code];
  if (pct === undefined) return { ok: false, error: "unknown code" }; // failure as value
  return { ok: true, value: { ...order, total: order.total * (1 - pct) } }; // new object
}

// Effect lives at the boundary; the pure function above is called with plain data.
async function checkout(id: string, code: string) {
  const order = await orders.load(id);            // I/O at the edge
  const result = applyDiscount(order, code);      // pure computation in the middle
  if (!result.ok) throw new BadRequest(result.error);
  await orders.save(result.value);                // I/O at the edge
}
```

**Bad Example** — hidden I/O and mutation inside "logic"

```ts
let lastCode = ""; // shared mutable state: makes the function order-dependent

async function applyDiscount(order: Order, code: string): Promise<void> {
  lastCode = code;                       // side effect on module state
  const pct = await db.query(code);      // I/O buried in what should be pure logic
  order.total = order.total * (1 - pct); // mutates the caller's object in place
  console.log("applied", order.id);      // side effect; can't test without capturing stdout
  // returns nothing and throws on unknown code — caller can't tell success from failure
}
```

## Common Mistakes

- Mutating an argument inside a function that reads as pure, surprising the caller.
- Doing I/O (DB, `fetch`, `console`) in the middle of computation, making it untestable
  without heavy mocking.
- Relying on shared module-level mutable state, breaking referential transparency.
- Throwing for expected outcomes (validation, not-found) instead of returning a value.
- Over-abstracting with point-free/curried code that obscures simple business rules.
- Building giant `reduce`s where a named helper or a plain loop would read better.
- Treating `map`/`forEach` with a mutating callback as "functional" — it is not pure.

## Production Tips

- Keep the pure core in modules with zero I/O imports; it makes unit tests fast and lets
  you exercise edge cases without fixtures.
- Prefer a small, well-typed `Result` helper over pulling in a heavy FP framework unless
  the team already knows one — unfamiliar abstractions slow reviews more than they help.
- When adopting a library (Effect, fp-ts, Remeda), standardize on one; mixing FP idioms
  across a codebase raises the cost of every review.

## AI Review Checklist

- Are core business functions pure — no mutation of inputs, no I/O, no outer state reads?
- Are side effects (I/O, logging, randomness, time) confined to the boundary?
- Are expected failures modeled as return values (`Result`/`undefined`), not thrown?
- Are arguments treated as `readonly` and never mutated in place?
- Is there any shared mutable module-level state breaking referential transparency?
- Is composition used to clarify, not to obfuscate ordinary logic?
- Can each function be unit-tested with plain inputs and no mocks?

## Related

- `knowledge/typescript/20-immutability.md`
- `knowledge/typescript/19-collections.md`
- `knowledge/typescript/04-functions.md`
- `knowledge/typescript/08-generics.md`
- `knowledge/typescript/17-error-handling.md`
