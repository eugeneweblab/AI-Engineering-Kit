---
id: typescript/19-collections
topic: typescript
slug: collections
title: "Collections"
type: doc
order: 19
status: ready
tags: [typescript, collections, array.includes, Record, noUncheckedIndexedAccess, for...in, for...of, groups, looks, elements]
related: [typescript/20-immutability, typescript/21-functional-programming, typescript/08-generics, typescript/25-performance, typescript/05-objects]
when_to_use: "Read before choosing a data structure or writing code that iterates, transforms, groups, or looks up elements."
---
# Collections

## Purpose

This document defines how to choose and use collections in TypeScript: arrays,
`Map`, `Set`, `Record`, and the typed transformation methods over them. It is written so
an agent picks the right structure for the access pattern and iterates with types that
stay honest about what a lookup can return.

The default reflex — "use an array/object for everything" — produces O(n) lookups and
`undefined` bugs. Choosing `Map` or `Set` when the access pattern calls for it is a
correctness and performance decision, not a style preference.

## Why It Matters

The wrong collection turns linear code into quadratic code that only bites at scale, long
after the test suite passed on ten rows. Using a plain object as a keyed store silently
inherits prototype keys and coerces every key to a string, so numeric keys and the string
`"__proto__"` become landmines. And TypeScript, by default, lies about index access:
`arr[i]` and `record[key]` are typed as `T`, not `T | undefined`, so the compiler hides
the exact `undefined` that crashes at runtime. Getting collections right removes a whole
class of "works on my machine" defects.

## Core Principles

- **Match the structure to the access pattern.** Ordered/indexed → array. Keyed lookup by
  a dynamic key → `Map`. Uniqueness / membership test → `Set`. Fixed known keys → object
  or `Record`.
- **Enable `noUncheckedIndexedAccess`.** It makes `arr[i]` and `record[k]` return
  `T | undefined`, forcing you to handle the miss the runtime already has.
- **Prefer `Map` over an object for a dynamic dictionary.** `Map` has real keys of any
  type, a `.size`, safe iteration order, and no prototype pollution.
- **Transform, do not mutate, in application logic.** `map`/`filter`/`reduce` return new
  arrays and keep data flow easy to follow; mutate only in tight measured hot paths.
- **Type the element, and the empty case.** A collection's element type must include the
  possibility of "not found" wherever a lookup can fail.

## Best Practices

- Use `Set` for membership checks and deduplication (`[...new Set(items)]`) instead of
  `array.includes` in a loop, which is O(n²).
- Use `Map` when keys are dynamic, non-string, or numerous; use `Record<K, V>` only for a
  known, closed set of keys.
- Reach for `Object.groupBy` / `Map.groupBy` (ES2024) to group items instead of hand-
  rolling a reduce; they are clearer and correctly typed as partial.
- Prefer `for...of` for iterating values and `map.entries()` for key/value pairs. Avoid
  `for...in` on arrays — it iterates enumerable keys, including inherited ones.
- Chain `filter`/`map` for readability at normal sizes; collapse to a single `reduce` or
  a `for...of` loop only when profiling shows the intermediate arrays matter.
- Keep collections homogeneous — `Array<User>`, not `Array<User | string | null>`. A
  mixed array pushes type-narrowing cost onto every consumer.
- Use `readonly T[]` / `ReadonlyMap` / `ReadonlySet` for parameters you do not mutate, so
  the signature documents intent and the compiler enforces it.

## Examples

**Good Example** — right structure, safe access, no mutation

```ts
// Set for O(1) membership; Map for keyed lookup with a typed miss.
function activeUsersByRole(users: readonly User[], activeIds: Set<string>) {
  const byRole = new Map<Role, User[]>();
  for (const user of users) {
    if (!activeIds.has(user.id)) continue;       // O(1) membership, not array.includes
    const bucket = byRole.get(user.role) ?? [];  // .get returns User[] | undefined — handled
    bucket.push(user);
    byRole.set(user.role, bucket);
  }
  return byRole; // caller reads by role in O(1)
}
```

**Bad Example** — object-as-map, O(n²) lookup, hidden undefined

```ts
function activeUsersByRole(users: User[], activeIds: string[]) {
  const byRole: Record<string, User[]> = {};
  for (const user of users) {
    if (!activeIds.includes(user.id)) continue; // O(n) inside O(n) → O(n²)
    byRole[user.role].push(user);               // byRole[role] is undefined on first hit → crash
    // "__proto__" as a role would corrupt the prototype chain
  }
  return byRole;
}
```

## Common Mistakes

- Using `array.includes` inside a loop where a `Set` would give O(1) membership.
- Using a plain object as a dynamic dictionary, inheriting prototype keys and string-only
  keys instead of using `Map`.
- Leaving `noUncheckedIndexedAccess` off, so `arr[i]`/`record[k]` hide their `undefined`.
- Reading `record[key].field` without checking the key exists, crashing on a miss.
- `for...in` over an array, iterating indices as strings plus inherited keys.
- Mutating a shared array with `push`/`splice` when a `map`/`filter` copy was expected.
- Building deeply nested intermediate arrays in a hot path where a single loop suffices.

## Production Tips

- Prefer `Map`/`Set` for caches and indexes in long-lived processes, but bound their size
  (LRU or TTL) — an unbounded `Map` used as a cache is a memory leak.
- When serializing, remember `Map` and `Set` do not survive `JSON.stringify` as-is;
  convert to arrays/objects explicitly at the boundary.
- For very large numeric arrays in hot paths, consider typed arrays (`Float64Array`) to
  cut memory and GC pressure.

## AI Review Checklist

- Does the structure match the access pattern (array/`Map`/`Set`/`Record`)?
- Is `noUncheckedIndexedAccess` enabled, and are index/lookup misses handled?
- Are membership checks done with `Set`, not `array.includes` in a loop?
- Is a dynamic dictionary a `Map`, not a plain object vulnerable to prototype keys?
- Are collection parameters `readonly` when the function does not mutate them?
- Are `Map`/`Set` converted explicitly when crossing a JSON boundary?
- Are cache-like `Map`s bounded so they cannot grow without limit?

## Related

- `knowledge/typescript/20-immutability.md`
- `knowledge/typescript/21-functional-programming.md`
- `knowledge/typescript/08-generics.md`
- `knowledge/typescript/25-performance.md`
- `knowledge/typescript/05-objects.md`
