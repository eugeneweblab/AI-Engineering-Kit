---
id: typescript/08-generics
topic: typescript
slug: generics
title: "Generics"
type: doc
order: 8
status: ready
tags: [typescript, generics, unknown, expectTypeError]
related: [typescript/06-interfaces, typescript/07-type-aliases, typescript/09-utility-types, typescript/13-advanced-types]
when_to_use: "Read before writing a function, class, or type that must work over many types while preserving the relationship between input and output types."
---
# Generics

## Purpose

This document defines how to write generics — type parameters that let a function, class,
or type work over many types while preserving the relationship between them. It is written
so an agent can add generics that increase type safety, not decorative `<T>`s that add
noise or hide `any`.

A generic captures a *relationship*: "the return type is the same as the argument type",
"the value type matches the key type". If there is no relationship to preserve, you do not
need a generic.

## Why It Matters

Generics are how a library stays both reusable and type-safe. Without them you must choose
between duplicating a function per type or falling back to `any` — the first bloats the
codebase, the second discards safety. A correct generic lets one implementation serve every
type while the compiler tracks the exact type through every call. A *wrong* generic (an
unused parameter, an unconstrained `T` used like `any`) gives the appearance of safety while
delivering none, which is worse than an honest `unknown`.

## Core Principles

- **A generic must connect two positions.** If a type parameter appears only once in the
  signature, it is doing nothing — replace it with `unknown` or a concrete type.
- **Constrain to the minimum you use.** `<T extends { id: string }>` documents and enforces
  exactly what the function relies on; bare `<T>` promises to work on everything and can
  therefore assume nothing about `T`.
- **Infer, do not annotate.** Let call sites infer type arguments; explicit `<...>` should be
  the exception, not the rule.
- **Push generics down, keep call sites concrete.** Callers should get precise types back
  without writing type arguments.
- **Prefer `unknown` over `any` inside generic bodies.** An unconstrained `T` is not a free
  pass to skip narrowing.

## Best Practices

- Give type parameters meaningful names when there is more than one (`TKey`, `TValue`), and
  a plain `T` only for the single obvious case.
- Add `extends` constraints so the body can safely access members and callers get useful
  errors. Use `extends` with a default (`<T = string>`) when a sensible default exists.
- Use `keyof` and indexed access to relate a key argument to a value type, so a getter
  returns the exact property type rather than a union.
- Do not over-generify. If only one or two concrete types are ever used, a union or an
  overload is simpler to read than a generic with three constrained parameters.
- Combine with [utility types](09-utility-types.md) (`Partial<T>`, `Record<K, V>`) instead of
  re-deriving those shapes by hand.

## Examples

**Good Example** — constrained parameter that preserves the exact type

```ts
// K is constrained to the keys of T, and the return type is the precise property type.
function getProp<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { id: "u1", age: 30 };
const age = getProp(user, "age"); // inferred as number, not string | number
getProp(user, "name");            // ❌ "name" is not a key of user — caught at compile time

// Relationship preserved: the array's element type flows to the callback and result.
function mapArray<T, U>(items: readonly T[], fn: (item: T) => U): U[] {
  return items.map(fn);
}
const lengths = mapArray(["a", "bb"], (s) => s.length); // number[]
```

**Bad Example** — decorative generic that is really `any`

```ts
// T appears only in the parameter, never related to the return — it buys nothing.
function first<T>(items: any[]): T {
  return items[0]; // returns whatever, cast to T the caller guessed — unsound
}
const n = first<number>(["not", "numbers"]); // compiles, n is "number" but actually a string

// Unconstrained T used as if it had an id — no constraint, so this is unsafe.
function idOf<T>(x: T) {
  return (x as any).id; // any leak; caller learns nothing and gets no checking
}
```

## Common Mistakes

- A type parameter used in only one position — it is not preserving a relationship and
  should be `unknown` or a concrete type.
- Adding `<T>` and then casting with `as T`, which fakes safety the compiler never verified.
- Leaving `T` unconstrained but accessing `x.id` inside via `any`, defeating the point.
- Over-parameterizing a function that only ever handles two known types — a union or
  overload reads better.
- Forcing callers to pass explicit type arguments because inference was not set up (put the
  inferable parameter where the compiler can see it).

## Production Tips

- For public library APIs, test generics with `expectTypeError` / `tsd` or `@ts-expect-error`
  fixtures so bad calls stay rejected as the code evolves.
- Provide defaults (`<T = unknown>`) on exported generic types so consumers can reference
  them without always supplying arguments.
- When a generic signature becomes unreadable, extract the constraint into a named
  [type alias](07-type-aliases.md) rather than inlining a long `extends` clause.

## AI Review Checklist

- Does each type parameter appear in at least two positions (input and output/related)?
- Is every parameter constrained to the minimum the body actually requires?
- Are type arguments inferred at call sites rather than written explicitly?
- Is there any `as T` cast that fabricates safety the compiler did not check?
- Would a union or overload be simpler than this generic for the real set of types used?

## Related

- `knowledge/typescript/06-interfaces.md`
- `knowledge/typescript/07-type-aliases.md`
- `knowledge/typescript/09-utility-types.md`
- `knowledge/typescript/13-advanced-types.md`
