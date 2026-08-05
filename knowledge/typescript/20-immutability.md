---
id: typescript/20-immutability
topic: typescript
slug: immutability
title: "Immutability"
type: doc
order: 20
status: ready
tags: [typescript, immutability, readonly, splice, Object.freeze, reverse, localeCompare, method]
related: [typescript/19-collections, typescript/21-functional-programming, typescript/05-objects, typescript/09-utility-types, typescript/28-best-practices]
when_to_use: "Read before modeling state, passing objects across module boundaries, or reviewing code that mutates shared data."
---
# Immutability

## Purpose

This document defines how to use immutability in TypeScript: `readonly`, `const`,
`as const`, `Readonly<T>`, and copy-on-write update patterns. It is written so an agent
can decide what to freeze, express it in the type system, and update state without
mutating data that other code still holds a reference to.

Immutability is not about never changing anything — state does change. It is about
producing a *new* value instead of editing the old one in place, so that no other holder
of the reference is surprised by a change it did not make.

## Why It Matters

Shared mutable state is the root of the hardest bugs: a value read here is silently
edited there, and the two lines are in different files written months apart. In UI code,
in-place mutation defeats reference-equality change detection, so components stop
re-rendering. In concurrent request handlers, a mutated shared object leaks one user's
data into another's response. TypeScript's `readonly` catches these at compile time — but
only shallowly and only if you actually apply it. Immutability makes data flow auditable:
if a function does not return a new value, it did not change anything.

## Core Principles

- **`readonly` is compile-time and shallow.** It stops reassignment of the property, not
  mutation of the object that property points to. Nest `readonly` to go deeper.
- **Update by copying, not by mutating.** Produce a new object/array with the change
  applied; leave the original untouched so existing references stay valid.
- **Model intent in the type.** Mark a parameter `readonly` or `Readonly<T>` when the
  function must not mutate it — the signature becomes a checkable promise.
- **`const` protects the binding, not the value.** `const obj = {}` still lets you mutate
  `obj.x`. Use `readonly`/`as const` for value immutability.
- **Freeze at the boundary, copy in the core.** Deep-freeze untrusted or shared inputs;
  inside pure logic, rely on `readonly` types and copy-on-write.

## Best Practices

- Use `as const` for literal configuration and lookup tables so the values become deeply
  `readonly` and narrowly typed (`"GET" | "POST"` instead of `string`).
- Type function parameters as `readonly T[]` / `Readonly<T>` whenever the body does not
  mutate them — it prevents accidental in-place edits and documents the contract.
- Update immutably with spreads: `{ ...user, name }`, `[...items, next]`,
  `items.filter(...)`, `items.map(...)`. Avoid `push`, `splice`, `sort` (in place), and
  direct assignment on shared data.
- For deep updates, use a library like Immer (`produce`) rather than hand-writing nested
  spreads — deep manual spreads are error-prone and easy to get subtly wrong.
- Use `Object.freeze` for genuinely constant runtime data (feature flags, config) so an
  accidental write throws in strict mode instead of silently corrupting state.
- Prefer `ReadonlyArray`, `ReadonlyMap`, `ReadonlySet` over their mutable forms in public
  APIs so callers cannot mutate your internal state through the reference you handed out.

## Examples

**Good Example** — copy-on-write, readonly contract, narrowed literals

```ts
const ROLES = ["admin", "editor", "viewer"] as const; // deeply readonly, type: literal union
type Role = (typeof ROLES)[number];

// readonly signals: this function will not mutate the array it is given.
function promote(users: readonly User[], id: string): User[] {
  return users.map((u) =>
    u.id === id ? { ...u, role: "admin" as Role } : u, // new object for the changed one
  ); // returns a new array; the caller's original is untouched
}
```

**Bad Example** — in-place mutation of shared data

```ts
const ROLES = ["admin", "editor", "viewer"]; // widened to string[]; ROLES.push(...) allowed

function promote(users: User[], id: string): User[] {
  const user = users.find((u) => u.id === id);
  if (user) user.role = "admin"; // mutates the object every other holder still references
  users.sort((a, b) => a.role.localeCompare(b.role)); // sorts the caller's array in place
  return users; // same reference back — no way to tell what changed
}
```

## Common Mistakes

- Assuming `readonly` is deep — it guards one level; nested objects stay mutable.
- Relying on `const` for value immutability when it only freezes the binding.
- Using `push`, `splice`, or in-place `sort`/`reverse` on an array a caller still holds.
- Hand-writing deep nested spreads and getting one level wrong, dropping sibling fields.
- Returning the same mutated reference, so reference-equality change detection misses it.
- Forgetting `as const`, so `{ method: "GET" }` widens `method` to `string`.
- Freezing shallowly with `Object.freeze` and believing nested objects are protected too.

## Production Tips

- In React/Redux state, treat every update as copy-on-write; in-place mutation is the
  top cause of "the state changed but nothing re-rendered."
- Deep-freeze config objects in development to catch accidental writes early; the freeze
  can be dropped in production builds for performance if profiling justifies it.
- When exposing internal collections from a service, return `readonly` views so callers
  cannot corrupt your invariants through the reference.

## AI Review Checklist

- Are parameters the function does not mutate typed `readonly` / `Readonly<T>`?
- Are updates done by copying (spread/`map`/`filter`) rather than in-place mutation?
- Is `as const` used for literal config and lookup tables that should not widen?
- Is any in-place `sort`/`reverse`/`splice` operating on data a caller still holds?
- For deep updates, is a proven approach (Immer) used instead of fragile manual spreads?
- Do public APIs hand out `readonly` collection types, not mutable internal references?
- Is the code aware that `readonly` and `Object.freeze` are shallow by default?

## Related

- `knowledge/typescript/19-collections.md`
- `knowledge/typescript/21-functional-programming.md`
- `knowledge/typescript/05-objects.md`
- `knowledge/typescript/09-utility-types.md`
- `knowledge/typescript/28-best-practices.md`
