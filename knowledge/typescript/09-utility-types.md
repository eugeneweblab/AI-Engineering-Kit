---
id: typescript/09-utility-types
topic: typescript
slug: utility-types
title: "Utility Types"
type: doc
order: 9
status: ready
tags: [typescript, utility-types, Pick, Omit, Required, Partial, PublicUser, Readonly, return, payload, view]
related: [typescript/07-type-aliases, typescript/08-generics, typescript/13-advanced-types, typescript/06-interfaces]
when_to_use: "Read before deriving one type from another — a public view of a model, a partial update payload, a lookup map, or a function's return type."
---
# Utility Types

## Purpose

This document defines how to use TypeScript's built-in utility types — `Partial`, `Pick`,
`Omit`, `Record`, `Required`, `Readonly`, `ReturnType`, `Parameters`, `Awaited`,
`NonNullable`, and friends — to *derive* types from existing ones instead of hand-writing
parallel shapes. It is written so an agent keeps derived types in sync with their source
automatically.

Utility types are pre-built [generic](08-generics.md) transformations. The core idea: define
a shape once, then compute every variant of it. When the source changes, every derived type
updates for free.

## Why It Matters

The most common source of type drift is duplication: a `User` model, a `CreateUserInput`, a
`PublicUser`, and an `UpdateUserPatch` all written by hand. Add a field to `User` and three
other types silently fall out of date — the compiler cannot warn you, because it does not know
they were meant to match. Utility types remove the duplication: the variants are *computed*
from the source, so they cannot drift. This is one of the highest-leverage safety tools in
the language.

## Core Principles

- **Derive, never duplicate.** If a type is "`User` but without X" or "`User` but all
  optional", express that with a utility type so it tracks the source.
- **Know each utility's exact effect.** `Omit` removes keys, `Pick` keeps them, `Partial`
  makes all optional, `Required` makes all required, `Readonly` freezes at the type level.
- **`Partial` for patches, `Required` for guarantees.** Use `Partial` on update payloads;
  use `Required` to assert a fully-populated object after validation.
- **`Record<K, V>` for maps, not index signatures written by hand.** It is clearer and lets
  you constrain the key set with a union.
- **Compose utilities.** `Readonly<Pick<User, "id" | "email">>` is normal and preferred over a
  bespoke interface.

## Best Practices

- Build API view types from the model: `type PublicUser = Omit<User, "passwordHash">`. Adding
  a secret field to `User` then requires you to consciously expose it.
- Build update payloads with `Partial<Pick<User, ...editable keys>>` so only intended fields
  are patchable and all are optional.
- Extract types from values you already have: `ReturnType<typeof createStore>` and
  `Parameters<typeof fn>` avoid re-declaring a function's shape.
- Unwrap promises with `Awaited<ReturnType<typeof fetchUser>>` instead of hand-writing the
  resolved type.
- Strip nullability with `NonNullable<T>` after you have narrowed, rather than casting.
- Prefer `Readonly<T>` / `readonly T[]` on data crossing a boundary to signal "do not mutate".

## Examples

**Good Example** — one source of truth, everything derived

```ts
interface User {
  id: string;
  email: string;
  displayName: string;
  passwordHash: string; // secret
}

// Public view: computed, so a new secret field is excluded until explicitly added.
type PublicUser = Omit<User, "passwordHash">;

// Update payload: only these keys, all optional — patch semantics for free.
type UserPatch = Partial<Pick<User, "email" | "displayName">>;

// A typed lookup keyed by a fixed union — no loose index signature.
type UsersById = Record<string, PublicUser>;

// Types pulled from existing functions instead of re-declared.
async function fetchUser(id: string): Promise<User> { /* ... */ }
type Fetched = Awaited<ReturnType<typeof fetchUser>>; // User
```

**Bad Example** — parallel shapes that drift on the next edit

```ts
interface User { id: string; email: string; displayName: string; passwordHash: string }

// Hand-written duplicates. Add a "role" field to User and these are now wrong,
// with zero compiler warning that they were meant to mirror User.
interface PublicUser { id: string; email: string; displayName: string }
interface UserPatch { email?: string; displayName?: string }

// Loose map: any string key, any-ish value, and passwordHash could leak in.
const usersById: { [k: string]: any } = {};
```

## Common Mistakes

- Re-declaring a "public" or "input" interface by hand instead of deriving it, guaranteeing
  future drift.
- Confusing `Omit` and `Pick` (or `Partial` and `Required`) — verify direction against the
  intended result.
- Using `Omit` with a typo'd key: `Omit<User, "passwordHsh">` silently omits nothing. Prefer
  `Pick` of an allow-list where leaking a field is dangerous.
- Reaching for `Record<string, any>` where a precise value type or key union is known.
- Forgetting `Awaited` and typing a promise's resolved value by hand, which drifts from the
  async function.

## Production Tips

- For "public" DTOs, prefer `Pick` (allow-list) over `Omit` (deny-list) for security-relevant
  types: a new secret field is excluded by default rather than exposed by default.
- `Readonly<T>` is shallow; for deep immutability use a `DeepReadonly` helper or freeze at
  runtime — do not assume nested objects are protected.
- When a derivation chain gets long, name the intermediate steps with
  [type aliases](07-type-aliases.md) so hovers and errors stay legible.

## AI Review Checklist

- Is every "variant" type (public/input/patch) derived from its source, not hand-written?
- For security-sensitive DTOs, is `Pick` (allow-list) used rather than `Omit` (deny-list)?
- Are function-derived types (`ReturnType`, `Parameters`, `Awaited`) used instead of
  re-declared signatures?
- Is `Record<K, V>` used with a precise value type (and constrained key set where possible)?
- Are boundary data types marked `Readonly`/`readonly` where mutation would be a bug?

## Related

- `knowledge/typescript/07-type-aliases.md`
- `knowledge/typescript/08-generics.md`
- `knowledge/typescript/13-advanced-types.md`
- `knowledge/typescript/06-interfaces.md`
