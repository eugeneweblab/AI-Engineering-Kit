---
id: typescript/02-type-system
topic: typescript
slug: type-system
title: "Type System"
type: doc
order: 2
status: ready
tags: [typescript, type-system, never, unknown, strictNullChecks, area, strict, noImplicitAny]
related: [typescript/03-type-inference, typescript/11-unions-and-intersections, typescript/12-type-guards, typescript/16-configuration]
when_to_use: "Read before designing any data model or deciding how strictly to type a value."
---
# Type System

## Purpose

This document explains how TypeScript's type system works: structural typing, the
special types (`any`, `unknown`, `never`, `void`), narrowing, and strict mode. Understand
this before designing types, because the type system's rules determine which designs the
compiler can actually enforce.

TypeScript is *structurally* typed: two types are compatible if their shapes match, not
because they share a name. Types exist only at compile time and are fully erased before
the code runs — you cannot inspect a type at runtime. Every guarantee the type system
gives you is a compile-time guarantee, and only as strong as the honesty of your types.

## Why It Matters

The type system is the entire reason to use TypeScript. Used well, it makes whole
categories of bugs impossible to write. Used carelessly — with `any`, blanket casts, or
`strict` disabled — it becomes decoration that gives false confidence. The difference
between a type system that catches bugs and one that hides them is a handful of
disciplines applied consistently. Because types are erased at runtime, a wrong type is
never caught later; it just produces a crash the compiler swore couldn't happen.

## Core Principles

- **Structural, not nominal.** Compatibility is by shape. A value satisfies a type if it
  has the required members, regardless of how it was declared.
- **`unknown` over `any`, always.** `any` disables checking and infects everything it
  touches. `unknown` is the safe top type: you must narrow it before use.
- **`never` is the empty set.** It means "cannot happen". Use it for exhaustiveness
  checks so adding a new union case becomes a compile error, not a silent gap.
- **Narrow, don't cast.** Prefer runtime checks (`typeof`, `in`, guards) that the
  compiler understands over `as` assertions, which the compiler trusts blindly.
- **`strict` is non-negotiable.** `strictNullChecks` alone eliminates most null bugs.

## Best Practices

- Never write `any`. At untyped boundaries (JSON, third-party data) type as `unknown` and
  validate before use (see [12-type-guards](12-type-guards.md)).
- Model optional and absent values with `T | undefined` or `T | null`, and let
  `strictNullChecks` force you to handle them.
- Add a `never` exhaustiveness check in every `switch` over a union, so the compiler flags
  any case you forgot when the union grows.
- Reserve `as` for cases the compiler genuinely cannot verify (e.g., `as const`, or a
  validated `unknown`), and comment why the assertion is sound.
- Use `readonly` and `as const` to make immutability part of the type, not a convention.

## Examples

**Good Example** — `unknown` at the boundary, `never` for exhaustiveness

```ts
type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.r ** 2;
    case "square": return s.side ** 2;
    default: {
      const _exhaustive: never = s; // compile error if a new Shape kind is added
      return _exhaustive;
    }
  }
}

function parse(raw: unknown): Shape {
  if (typeof raw === "object" && raw !== null && "kind" in raw) return raw as Shape; // narrowed, then asserted
  throw new Error("invalid shape");
}
```

**Bad Example** — `any` erases safety, no exhaustiveness

```ts
function area(s: any): number {   // any: no member is checked
  if (s.kind === "circle") return Math.PI * s.r ** 2;
  return s.side ** 2;             // silently wrong for an unknown kind; s.side may be undefined
}
```

## Common Mistakes

- Using `any` (or an untyped `catch` variable) and losing all downstream checking.
- Casting with `as` to silence an error instead of narrowing to prove the type.
- Omitting the `never` default case, so new union members compile with unhandled paths.
- Disabling `strictNullChecks`, letting `undefined` flow anywhere unchecked.
- Assuming a type exists at runtime (e.g., `instanceof MyInterface`) — types are erased.

## Production Tips

- Turn on `noImplicitAny` and `useUnknownInCatchVariables` so untyped values surface as
  errors rather than silent `any`.
- For external data, pair the type system with a runtime validator (e.g., Zod) so the
  compile-time type and the runtime shape cannot drift.

## AI Review Checklist

- Is `any` absent, with `unknown` used and narrowed at every untyped boundary?
- Does every `switch` over a union have a `never` exhaustiveness default?
- Are `as` casts justified and commented, not used to silence real errors?
- Is `strict` (including `strictNullChecks`) enabled and passing?
- Are optional/absent values modeled explicitly rather than assumed present?

## Related

- `knowledge/typescript/03-type-inference.md`
- `knowledge/typescript/11-unions-and-intersections.md`
- `knowledge/typescript/12-type-guards.md`
- `knowledge/typescript/16-configuration.md`
