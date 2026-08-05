---
id: typescript/05-objects
topic: typescript
slug: objects
title: "Objects"
type: doc
order: 5
status: ready
tags: [typescript, objects, readonly, deactivate, Date, Required, Pick, Partial]
related: [typescript/06-interfaces, typescript/07-type-aliases, typescript/09-utility-types, typescript/20-immutability]
when_to_use: "Read before modeling any object shape, record, or index signature."
---
# Objects

## Purpose

This document covers how to type objects: property shapes, optional and readonly members,
index signatures, excess-property checks, and records. Objects are the primary way data
is modeled, so a precise object type is the foundation of a type-safe module.

TypeScript types an object by its structure — the set of properties and their types. A
well-designed object type makes valid shapes easy to build and invalid ones impossible to
construct. The tools are optionality, `readonly`, index signatures, and utility types;
the discipline is to keep each type as tight as the data it describes.

## Why It Matters

Object types are where structural typing pays off most — and where it fails most quietly.
A property typed too widely (`metadata: any`, `status: string` instead of a union) admits
garbage the compiler should have rejected. A missing `readonly` lets shared state mutate
under callers who assumed it wouldn't. Because objects flow through most functions,
imprecise object types spread imprecision everywhere they go. Tight object types stop bad
data at the point of construction.

## Core Principles

- **Model exactly the shape.** Every property that exists should be typed; no more, no
  fewer. Use literal unions for constrained values (`status: "open" | "closed"`).
- **Make optionality explicit and meaningful.** `field?: T` means "may be absent". Don't
  mark a field optional just to avoid initializing it.
- **`readonly` for data that shouldn't change after creation.** It documents intent and
  lets the compiler catch accidental mutation (see [20-immutability](20-immutability.md)).
- **Index signatures are a last resort.** `Record<string, T>` admits *any* key; prefer a
  known set of properties when the keys are known.
- **Excess-property checks are a feature.** Object literals are checked for extra
  properties — don't defeat this by widening to `any` or casting.

## Best Practices

- Prefer a named `interface` or `type` over inline object types once a shape is reused,
  so the shape has one definition (see [06-interfaces](06-interfaces.md)).
- Use utility types (`Partial`, `Pick`, `Omit`, `Required`, `Readonly`) to derive related
  shapes instead of hand-copying properties, which drift (see [09-utility-types](09-utility-types.md)).
- Use `Record<K, V>` for genuine maps with dynamic keys; use a fixed property set otherwise.
- Prefer object spread (`{ ...a, ...b }`) for immutable updates over in-place mutation.
- Enable `noUncheckedIndexedAccess` so `obj[key]` is typed `T | undefined`, forcing a
  presence check on dynamic access.

## Examples

**Good Example** — precise shape, `readonly`, literal union, derived type

```ts
interface User {
  readonly id: string;              // set at creation, never reassigned
  email: string;
  role: "admin" | "member";         // constrained, not just string
  deactivatedAt?: Date;             // optional means genuinely "may be absent"
}

// Derive the update shape instead of re-declaring it — it can't drift from User.
type UserUpdate = Partial<Omit<User, "id">>;

function deactivate(user: User): User {
  return { ...user, deactivatedAt: new Date() }; // immutable update via spread
}
```

**Bad Example** — wide types, index signature abuse, mutation

```ts
interface User {
  id: string;
  email: string;
  role: string;                 // admits "amdin", "root", anything
  [key: string]: any;           // any key, any value — checking is gone
}

function deactivate(user: User): void {
  user.deactivatedAt = new Date(); // mutates the caller's object in place
}
```

## Common Mistakes

- Typing constrained fields as `string`/`number` instead of a literal union.
- Adding an `[key: string]: any` index signature that disables property checking for the
  whole type.
- Marking fields optional to dodge initialization, hiding that they are actually required.
- Hand-duplicating a shape for updates/DTOs instead of deriving it with utility types,
  letting the copy drift from the original.
- Mutating an object argument in place, surprising callers who share the reference.
- Casting a literal to a wider type to bypass the excess-property check.

## Production Tips

- Pair object types with a runtime validator (e.g., Zod) at system boundaries so the
  declared shape and the actual incoming data cannot diverge.
- Prefer `readonly` arrays and `Readonly<T>` for data returned from a module, so consumers
  cannot mutate internal state through a shared reference.

## AI Review Checklist

- Are constrained properties typed as literal unions rather than bare `string`/`number`?
- Is every property genuinely present typed, with `?` reserved for truly optional fields?
- Is `readonly` applied to properties that must not change after construction?
- Are index signatures avoided when the key set is actually known?
- Are related shapes derived with utility types instead of duplicated?
- Do updates use spread/immutable patterns rather than mutating arguments in place?

## Related

- `knowledge/typescript/06-interfaces.md`
- `knowledge/typescript/07-type-aliases.md`
- `knowledge/typescript/09-utility-types.md`
- `knowledge/typescript/20-immutability.md`
