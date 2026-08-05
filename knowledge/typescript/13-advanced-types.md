---
id: typescript/13-advanced-types
topic: typescript
slug: advanced-types
title: "Advanced Types"
type: doc
order: 13
status: ready
tags: [typescript, advanced-types, PublicUser, ReturnType, Partial, Omit, loadUser, Parameters]
related: [typescript/08-generics, typescript/09-utility-types, typescript/12-type-guards, typescript/11-unions-and-intersections]
when_to_use: "Read before writing conditional, mapped, or template-literal types, or debugging a deeply nested generic."
---
# Advanced Types

## Purpose

This document covers TypeScript's type-level programming features: conditional types
(`T extends U ? X : Y`), `infer`, mapped types (`{ [K in keyof T]: ... }`), template
literal types, key remapping, and recursive types. These let you *derive* one type from
another so that a single source of truth drives many related types.

Use these tools to remove duplication and encode invariants the compiler can enforce.
They are powerful and easy to overuse — the goal is types that make the code *safer and
clearer*, not a puzzle that only the author can read.

## Why It Matters

Duplicated type definitions drift. When the API response type and the form type and the
database row type are written by hand, one of them is always subtly wrong. Derived types
fix this: change the source, and every dependent type updates and re-checks. Advanced types
also let you catch bugs the value-level code never would — an impossible state can be made
*unrepresentable* rather than merely discouraged. The cost is complexity: a clever type that
takes ten minutes to understand is a liability. Reach for these features when they replace
real duplication or prevent a real class of bug, not to show off.

## Core Principles

- **Derive, don't duplicate.** If type B is "type A but readonly / partial / with one field
  changed", express it with utilities and mapped types so it tracks A automatically.
- **Prefer built-in utilities first.** `Pick`, `Omit`, `Partial`, `Record`, `ReturnType`,
  `Parameters`, `Awaited` cover most needs without custom machinery.
- **Keep type logic shallow and named.** Give each conditional/mapped type a descriptive
  alias; nesting three levels of `extends` inline is unreadable and slow to compile.
- **Constrain generics.** `<T extends object>` documents intent and produces better errors
  than a bare `<T>` that accepts anything.
- **Complexity must pay rent.** Every custom type-level construct should remove duplication
  or make a bad state impossible. If it does neither, delete it.

## Best Practices

- Use conditional types with `infer` to extract a piece of a type (element of an array,
  resolved value of a promise) instead of re-declaring it.
- Use mapped types with key remapping (`as`) to transform property names and types together,
  e.g. generate `on${Capitalize<K>}` event handlers from a props type.
- Use template literal types to model structured strings (route paths, event names, CSS
  units) so typos are compile errors.
- Bound recursive types with a depth or a base case; unbounded recursion hits the compiler's
  instantiation limit and errors with a cryptic message.
- Add `// prettier-ignore` and a comment explaining *what invariant* a gnarly type enforces —
  future readers need the "why", not just the "what".
- Prefer discriminated unions over conditional types when modeling variants; they are simpler
  to consume and narrow (see type guards).

## Examples

**Good Example** — one source type drives the rest

```ts
interface User {
  id: string;
  email: string;
  passwordHash: string;
}

// Derived: a public view that can never leak the hash, tied to `User` at compile time.
type PublicUser = Omit<User, "passwordHash">;

// Derived: extract the resolved value of any async function without re-typing it.
type Resolved<F> = F extends (...args: any[]) => Promise<infer R> ? R : never;

async function loadUser(): Promise<PublicUser> { /* ... */ return {} as PublicUser; }
type Loaded = Resolved<typeof loadUser>; // PublicUser — updates if loadUser's return changes
```

**Bad Example** — hand-duplicated types that silently drift

```ts
interface User { id: string; email: string; passwordHash: string }

// Re-typed by hand; when `User` gains a `role` field this is silently out of date,
// and nothing stops `passwordHash` from being added back and leaked.
interface PublicUser { id: string; email: string }

// A conditional type so nested it is unreadable and reveals no intent.
type Thing<T> = T extends string ? T extends `a${infer _}` ? true : false : T extends number ? never : unknown;
```

## Common Mistakes

- Rewriting a derivable type by hand (`Partial`, `Omit`, `ReturnType`) so it drifts from its
  source the moment either changes.
- Deeply nested inline conditional types that no one can read; extract and name each step.
- Unconstrained recursive types with no base case, hitting "Type instantiation is excessively
  deep and possibly infinite."
- Using `any` inside `infer` positions and losing the very type you meant to extract.
- Building elaborate type-level logic to model variants that a plain discriminated union would
  express more simply.
- Ignoring compile-time cost: pathological types can slow the whole build measurably.

## Production Tips

- Watch `tsc --diagnostics` / editor responsiveness; if type-checking slows, a runaway
  conditional or mapped type is usually the cause. Simplify or cache with a named alias.
- Co-locate derived types with their source type so the dependency is obvious and reviewers
  can verify the derivation.
- Prefer generating types from a schema (Zod's `z.infer`, OpenAPI codegen) over reproducing
  external contracts as advanced types by hand.

## AI Review Checklist

- Is any type that "is another type with a tweak" derived via utilities/mapped types rather
  than duplicated?
- Are complex conditional/mapped types named and commented with the invariant they enforce?
- Are all generics constrained (`extends ...`) rather than bare `<T>` where a constraint
  applies?
- Do recursive types have a clear base case and bounded depth?
- Does each custom type-level construct remove duplication or prevent a bad state — or should
  it be a discriminated union instead?

## Related

- `knowledge/typescript/08-generics.md`
- `knowledge/typescript/09-utility-types.md`
- `knowledge/typescript/12-type-guards.md`
- `knowledge/typescript/11-unions-and-intersections.md`
