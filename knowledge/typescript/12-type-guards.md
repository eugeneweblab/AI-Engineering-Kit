---
id: typescript/12-type-guards
topic: typescript
slug: type-guards
title: "Type Guards"
type: doc
order: 12
status: ready
tags: [typescript, type-guards, never, unknown, kind, JSON.parse, area, handle]
related: [typescript/11-unions-and-intersections, typescript/13-advanced-types, typescript/03-type-inference, typescript/17-error-handling]
when_to_use: "Read before narrowing a union, validating unknown input, or writing any `is`/`asserts` predicate."
---
# Type Guards

## Purpose

This document defines how to *narrow* a value from a broad type (a union, `unknown`,
or a supertype) to a specific, safe-to-use type inside a block of code. It covers the
built-in narrowing operators, user-defined predicates (`x is T`), assertion functions
(`asserts x is T`), and the discipline of validating data that crosses a trust boundary.

Narrowing is how you turn "this *could* be a `Cat` or a `Dog`" into "here, the compiler
*knows* it is a `Cat`". Written correctly, guards let the compiler prove the code is
safe. Written carelessly (via `as`), they only *silence* the compiler while the bug
survives.

## Why It Matters

A cast (`value as User`) is a promise you make to the compiler with zero runtime backing.
If the value is not actually a `User`, the cast succeeds anyway and the program blows up
later — often far from the cast, with a confusing stack trace. A type guard replaces that
promise with a runtime *check*: the narrowed type is true because code verified it. At the
edges of a system — HTTP bodies, `JSON.parse`, `localStorage`, message queues — the data is
`unknown` no matter what its declared type says, and only a guard makes it safe to touch.

## Core Principles

- **A guard must actually check what it claims.** A predicate returning `x is User` must
  inspect the fields that make an object a `User`. A guard that lies is worse than a cast —
  it looks safe.
- **Narrow with runtime operators, not `as`.** `typeof`, `instanceof`, `in`, equality, and
  `Array.isArray` narrow *and* execute a real check. `as` narrows nothing at runtime.
- **Prefer discriminated unions over structural guards.** A shared literal `kind` field is
  the cheapest, most reliable thing to switch on.
- **Validate all external data before it enters your types.** Anything from the network,
  disk, or `JSON.parse` is `unknown`; guard it once at the boundary, then trust it inside.
- **Make exhaustiveness a compile error.** A `never` check in the `default`/`else` branch
  forces the compiler to reject an unhandled case when the union grows.

## Best Practices

- Use `typeof` for primitives (`"string"`, `"number"`, `"boolean"`, `"undefined"`,
  `"object"`, `"function"`, `"symbol"`, `"bigint"`) and `instanceof` for class instances.
- Use the `in` operator to distinguish object shapes that lack a discriminant field.
- Give unions a literal discriminant (`kind`, `type`, `status`) and `switch` on it; add a
  `default` branch that assigns to `never` to enforce exhaustiveness.
- Write user-defined guards `function isX(v: unknown): v is X` for reuse; keep the body a
  real structural check, never `return true`.
- Use `asserts v is X` functions when you want to *throw* on failure and narrow the rest of
  the scope, instead of returning a boolean.
- For real validation of external payloads, delegate to a schema library (Zod, Valibot,
  ArkType) whose `.parse`/guard is the source of truth — do not hand-roll deep checks.
- Never widen back: once narrowed, do not reassign the variable to a broader value in the
  same scope, or narrowing is lost.

## Examples

**Good Example** — a predicate that truly checks, plus exhaustive narrowing

```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; side: number };

function isShape(v: unknown): v is Shape {
  // Verify the discriminant AND the payload — this is what makes `v is Shape` honest.
  return (
    typeof v === "object" && v !== null && "kind" in v &&
    ((v as Shape).kind === "circle" || (v as Shape).kind === "square")
  );
}

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.r ** 2;
    case "square": return s.side ** 2;
    default:
      // If a new variant is added, `s` is no longer `never` and this fails to compile.
      const _exhaustive: never = s;
      return _exhaustive;
  }
}
```

**Bad Example** — a lying guard and a silent cast

```ts
function isUser(v: unknown): v is User {
  return true; // claims `v is User` without checking anything — a guaranteed future crash
}

function handle(body: unknown) {
  const user = body as User;        // no runtime check; `body` might be a string
  console.log(user.email.trim());   // throws "Cannot read properties of undefined"
}
```

## Common Mistakes

- Returning `true` (or a partial check) from an `x is T` predicate so it compiles but does
  not verify — a cast in disguise.
- Reaching for `as` at a boundary instead of validating; the type is a fiction until checked.
- Forgetting that `typeof null === "object"`, so `typeof v === "object"` matches `null`.
- Using `value.constructor.name === "Foo"` instead of `instanceof`; it breaks across realms
  and after minification.
- Omitting the `never` exhaustiveness branch, so adding a union member compiles silently and
  falls through at runtime.
- Narrowing inside a closure that is called later — the narrowing does not survive the async
  gap; re-check or capture the narrowed value.

## Production Tips

- Centralize boundary validation: one `parseUser(input: unknown): User` per external shape,
  reused everywhere, so the check exists in exactly one place.
- Prefer a schema library at the edge; its inferred type and its runtime guard cannot drift
  apart, unlike a hand-written predicate paired with a separate `interface`.
- In tests, feed guards malformed input (missing fields, wrong types, `null`) and assert they
  reject it — a guard is only as good as its negative cases.

## AI Review Checklist

- Does every `x is T` predicate perform a real runtime check of `T`'s shape?
- Is external/`unknown` data validated at the boundary rather than cast with `as`?
- Do `typeof v === "object"` checks also guard against `null`?
- Do discriminated-union `switch`es have a `never` exhaustiveness branch?
- Is `instanceof` used for classes instead of `constructor.name` string comparison?
- Are complex payloads validated by a schema library rather than a hand-rolled deep check?

## Related

- `knowledge/typescript/11-unions-and-intersections.md`
- `knowledge/typescript/13-advanced-types.md`
- `knowledge/typescript/03-type-inference.md`
- `knowledge/typescript/17-error-handling.md`
