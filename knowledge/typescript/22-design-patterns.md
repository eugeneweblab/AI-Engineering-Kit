---
id: typescript/22-design-patterns
topic: typescript
slug: design-patterns
title: "Design Patterns"
type: doc
order: 22
status: ready
tags: [typescript, design-patterns]
related: [typescript/06-interfaces, typescript/08-generics, typescript/11-unions-and-intersections, typescript/21-functional-programming, typescript/30-engineering-principles]
when_to_use: "Read before introducing a factory, strategy, adapter, or other pattern, or when reviewing an abstraction that may be over-engineered."
---
# Design Patterns

## Purpose

This document defines how to apply design patterns in TypeScript idiomatically: which
classic Gang-of-Four patterns still earn their keep, which the language subsumes, and how
to express them with types instead of ceremony. It is written so an agent reaches for a
pattern only when it removes real duplication or coupling — not to decorate simple code.

A pattern is a named solution to a recurring problem. In TypeScript, first-class
functions, unions, and structural typing already solve many problems that need a whole
class hierarchy in older languages. Use the lightest construct that expresses the intent.

## Why It Matters

Patterns cut both ways. Applied to a real, recurring problem, they make a codebase
predictable — a reviewer sees "strategy" and instantly knows the shape. Applied
speculatively, they add indirection that hides the actual logic behind factories,
managers, and abstract base classes nobody needs, making the code harder to change, not
easier. The skill is knowing when the problem is real. Premature abstraction is as costly
as no abstraction; both make change expensive.

## Core Principles

- **Prefer functions and unions to class hierarchies.** A strategy is often just a
  function type; a state machine is often a discriminated union — no inheritance required.
- **Introduce a pattern to remove concrete pain**, duplication, or a coupling you can name
  — never on the guess that flexibility will be needed later.
- **Program to an interface, not an implementation.** Depend on a narrow type so
  implementations can be swapped and tested; this is dependency inversion.
- **Favor composition over inheritance.** Combine small capabilities; deep inheritance
  trees are rigid and leak base-class details into every subclass.
- **Keep the abstraction narrower than the concretions.** An interface should expose less
  than any implementation, so callers cannot depend on incidental details.

## Best Practices

- Model a **strategy** as a function type (`type Pricer = (o: Order) => number`) and pass
  it in, rather than building a class per algorithm — less code, easier to test.
- Model **state** and variant data as a **discriminated union** with a `kind`/`type` tag;
  `switch` on the tag and let `never` in the default enforce exhaustiveness.
- Use a **factory function** (not necessarily a Factory class) to centralize construction
  when building an object requires non-trivial wiring or validation.
- Use the **adapter** pattern to wrap third-party or legacy APIs behind an interface your
  code owns, so a dependency swap touches one file.
- Reach for **dependency injection** by passing collaborators as constructor/function
  arguments (interface-typed) rather than importing concretes — it is what makes units
  testable without module mocking.
- Prefer the **builder** pattern only for objects with many optional fields and ordering
  constraints; for a handful of fields, an options object is simpler.
- Avoid **singletons** with mutable state; they are global variables in disguise and
  wreck testability. If you need one instance, inject it, do not reach for a global.

## Examples

**Good Example** — strategy as a function, exhaustive union

```ts
// Strategy: just a function type. No class hierarchy, trivially testable and composable.
type ShippingRate = (weightKg: number) => number;

const rates: Record<Tier, ShippingRate> = {
  standard: (w) => 5 + w * 0.5,
  express: (w) => 12 + w * 0.9,
};

// Discriminated union + exhaustive switch: the compiler forces every case to be handled.
type Event =
  | { kind: "created"; id: string }
  | { kind: "shipped"; id: string; at: Date };

function describe(e: Event): string {
  switch (e.kind) {
    case "created": return `order ${e.id} created`;
    case "shipped": return `order ${e.id} shipped at ${e.at.toISOString()}`;
    default: {
      const _exhaustive: never = e; // adding a new kind fails to compile here — safe
      return _exhaustive;
    }
  }
}
```

**Bad Example** — pattern ceremony over a one-liner

```ts
// A factory + abstract class + subclasses to compute two numbers no one will extend.
abstract class ShippingStrategy {
  abstract rate(weightKg: number): number;
}
class StandardStrategy extends ShippingStrategy {
  rate(w: number) { return 5 + w * 0.5; }
}
class ExpressStrategy extends ShippingStrategy {
  rate(w: number) { return 12 + w * 0.9; }
}
class ShippingFactory {
  static create(tier: string): ShippingStrategy {
    if (tier === "express") return new ExpressStrategy();
    return new StandardStrategy(); // silently defaults unknown tiers — hides bugs
  }
}
// Four types and a stringly-typed factory to replace a Record lookup.
```

## Common Mistakes

- Adding a factory/abstract-class hierarchy where a function or union would do.
- Building for hypothetical future flexibility that never arrives ("just in case").
- Using inheritance for code reuse, coupling subclasses to base-class internals.
- Stringly-typed factories that silently default unknown inputs instead of failing.
- Mutable singletons that hold global state and make tests order-dependent.
- Depending on concrete classes instead of narrow interfaces, blocking substitution.
- Non-exhaustive `switch` over a union with no `never` guard, so new cases slip through.

## Production Tips

- When you name a pattern in code, use its conventional name so reviewers recognize it;
  a "Manager" or "Helper" that is really an adapter just hides intent.
- Delete speculative abstraction during review — an interface with a single implementation
  and no test double is usually premature; inline it until a second implementation exists.
- Keep injected dependencies interface-typed and constructed at the composition root
  (main/entry), not scattered `new` calls throughout the codebase.

## AI Review Checklist

- Does each pattern solve a real, present problem (duplication/coupling), not a guess?
- Could a function type or discriminated union replace a class hierarchy here?
- Is code depending on narrow interfaces rather than concrete implementations?
- Is composition preferred over inheritance for reuse?
- Are `switch`es over unions exhaustive, guarded by a `never` default?
- Are there mutable singletons or global state that will break tests?
- Are dependencies injected at a composition root rather than imported as concretes?

## Related

- `knowledge/typescript/06-interfaces.md`
- `knowledge/typescript/08-generics.md`
- `knowledge/typescript/11-unions-and-intersections.md`
- `knowledge/typescript/21-functional-programming.md`
- `knowledge/typescript/30-engineering-principles.md`
