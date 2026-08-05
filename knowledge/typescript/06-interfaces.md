---
id: typescript/06-interfaces
topic: typescript
slug: interfaces
title: "Interfaces"
type: doc
order: 6
status: ready
tags: [typescript, interfaces, readonly, UserRepository, unknown, isAdmin, Repository, save]
related: [typescript/07-type-aliases, typescript/05-objects, typescript/08-generics, typescript/11-unions-and-intersections]
when_to_use: "Read before modeling the shape of an object, a public API contract, or a class you expect others to implement or extend."
---
# Interfaces

## Purpose

This document defines how to use `interface` to describe the shape of objects and
the contracts that classes implement. It is written so an agent can pick `interface`
vs [type alias](07-type-aliases.md) deliberately and design contracts that are stable,
extensible, and honestly typed.

An interface is a *named, open contract* for object shape. It answers "what properties
and methods must this thing have?" — not how they are computed. Use it for the public
surface of your code: API payloads, service contracts, and class implementations.

## Why It Matters

Interfaces are the seams of a codebase — the boundaries where one module trusts another.
A loose or dishonest interface (optional where it should be required, `any` where it
should be typed, mutable where it should be `readonly`) lets bugs pass the compiler and
surface at runtime. Because interfaces are consumed in many places, a bad one multiplies
its cost: every implementer and caller inherits the flaw. Getting the contract right once
is cheaper than correcting it after ten call sites depend on it.

## Core Principles

- **Model the contract, not the implementation.** An interface says *what* is provided,
  never *how*. Keep computed logic and private state out of it.
- **Prefer required properties; make optional a deliberate choice.** Every `?` is a branch
  every consumer must handle. Add it only when absence is a real, meaningful state.
- **Default to `readonly` for data you do not own.** Immutable contracts prevent a
  consumer from mutating shared state through a reference.
- **Program to interfaces, not concretions.** Depend on the narrow shape you need, so
  implementations can be swapped and tested with fakes.
- **Interfaces are open (declaration merging); type aliases are closed.** Choose
  `interface` when you want extension via `extends` or library augmentation.

## Best Practices

- Use `interface` for object and class contracts; reach for a [type alias](07-type-aliases.md)
  when you need unions, tuples, mapped, or conditional types — interfaces cannot express those.
- Name interfaces by role, not by a `I`-prefix (`User`, `Repository`, not `IUser`). The
  `I` prefix is noise the compiler already knows.
- Compose with `extends` for is-a relationships; keep each interface focused (interface
  segregation) so implementers are not forced to satisfy methods they do not use.
- Mark unchanging fields `readonly` and array/record fields `readonly` too when the
  consumer must not mutate them.
- Type method signatures precisely — real parameter and return types, never `any`. An
  interface returning `any` disables checking for every caller.
- Use `unknown` (not `any`) for genuinely dynamic values, forcing consumers to narrow.

## Examples

**Good Example** — narrow, honest, immutable contract

```ts
// Contract describes only what a consumer needs, with precise types.
interface UserRepository {
  readonly findById: (id: string) => Promise<User | null>; // null models "not found" honestly
  readonly save: (user: User) => Promise<void>;
}

interface User {
  readonly id: string;      // callers must not reassign identity
  readonly email: string;
  displayName: string;      // mutable by design — profile edits are expected
  role: "admin" | "member"; // literal union, not a loose string
}

// A test double satisfies the contract with no framework needed.
const fakeRepo: UserRepository = {
  findById: async () => null,
  save: async () => {},
};
```

**Bad Example** — dishonest optionals and `any` erase safety

```ts
interface User {
  id?: string;    // id is never really optional — forces pointless null checks everywhere
  email?: string;
  role?: string;  // "any string" — a typo like "Amin" compiles fine
  save?: any;      // any disables checking for every caller of user.save(...)
}

// Consumers now guard against absence that cannot actually occur,
// and role comparisons silently accept invalid values.
function isAdmin(u: User) {
  return u.role === "admin"; // no error if role is "administrator" elsewhere
}
```

## Common Mistakes

- Marking properties optional (`?`) to silence "missing property" errors instead of
  fixing the caller — this pushes null checks onto everyone downstream.
- Using `any` in a method signature, which turns off type checking for all callers.
- Prefixing names with `I` (`IUserService`), adding noise without information.
- Putting a union or tuple where an interface is required — use a type alias instead.
- Fat interfaces that force implementers (and mocks) to satisfy unused members.
- Forgetting `readonly`, letting a consumer mutate objects the producer still holds.

## Production Tips

- For external API payloads, derive interfaces from the schema (OpenAPI, JSON Schema,
  zod) so the type and the runtime validation cannot drift apart.
- Declaration merging is powerful but surprising — reserve `interface` augmentation for
  intentional library extension (e.g. `express.Request`), and comment why.
- Export the interface, not the concrete class, from a module's public entry point so
  consumers depend on the contract.

## AI Review Checklist

- Does every optional property represent a real absent state, not a silenced error?
- Are unchanging fields and consumer-owned data marked `readonly`?
- Are all method signatures precisely typed, with no `any` (use `unknown` if dynamic)?
- Is `interface` used for object/class shape and a type alias used for unions/tuples?
- Are interfaces focused (no unused members forced on implementers)?
- Are string fields with a fixed set of values typed as literal unions, not `string`?

## Related

- `knowledge/typescript/07-type-aliases.md`
- `knowledge/typescript/05-objects.md`
- `knowledge/typescript/08-generics.md`
- `knowledge/typescript/11-unions-and-intersections.md`
