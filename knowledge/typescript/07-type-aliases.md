---
id: typescript/07-type-aliases
topic: typescript
slug: type-aliases
title: "Type Aliases"
type: doc
order: 7
status: ready
tags: [typescript, type-aliases, UserId, loadUser, PublicUser, unknown, Pick, Omit]
related: [typescript/06-interfaces, typescript/11-unions-and-intersections, typescript/13-advanced-types, typescript/09-utility-types]
when_to_use: "Read before naming a union, tuple, function type, or any composed/derived type, or when deciding between type alias and interface."
---
# Type Aliases

## Purpose

This document defines how to use `type` aliases to name any type — unions, tuples,
function types, primitives, and types derived from other types. It is written so an agent
can name types deliberately, choose `type` vs [interface](06-interfaces.md) correctly,
and build composed types that stay honest.

A type alias is a *name for a type expression*. Unlike an [interface](06-interfaces.md),
which only describes object shape, a type alias can name anything the type system can
express, and it is *closed* (no declaration merging).

## Why It Matters

A well-named type turns an opaque expression into documentation the compiler enforces.
`type UserId = string` communicates intent and, with branding, prevents mixing a user id
with an order id. Type aliases are where a codebase's domain vocabulary lives; sloppy
ones (`type Data = any`, giant unnamed inline unions) erase that vocabulary and let
category errors compile. Because aliases are referenced widely, one imprecise alias
weakens every site that uses it.

## Core Principles

- **Name the concept, then reuse the name.** If a shape or union appears twice, alias it
  once. Repetition drifts; a single alias stays consistent.
- **Use `type` for what interfaces cannot express** — unions, intersections, tuples,
  function types, mapped and conditional types, and primitive aliases.
- **Aliases are transparent, not nominal.** `type Meters = number` is still just `number`;
  the compiler will accept any number. Use *branding* when you need real distinctness.
- **Keep aliases derived, not duplicated.** Build new types from existing ones with
  [utility types](09-utility-types.md) so they update automatically when the source changes.
- **Closed by design.** Type aliases cannot be reopened or merged — prefer them when you
  do *not* want library augmentation.

## Best Practices

- Choose `interface` for object/class contracts you expect to extend or implement; choose
  `type` for unions, tuples, function signatures, and derived types. Applied consistently,
  this makes intent readable at a glance.
- Alias domain primitives (`type Email = string`) and, where mixing them is a real risk,
  brand them so the compiler rejects a raw `string`.
- Derive request/response variants from a single source type with `Omit`, `Pick`, and
  `Partial` rather than hand-writing parallel shapes that can diverge.
- Name function types when they recur (`type Handler = (e: Event) => void`) instead of
  repeating the signature inline.
- Avoid deeply nested inline unions in signatures — alias them so errors and hovers read
  cleanly.

## Examples

**Good Example** — named union, branded primitive, derived type

```ts
// A branded primitive: structurally still a string, but nominally distinct.
type UserId = string & { readonly __brand: "UserId" };
const asUserId = (s: string) => s as UserId;

// A named discriminated union — the domain's set of states, in one place.
type Result<T> =
  | { readonly ok: true; value: T }
  | { readonly ok: false; error: string };

interface User { id: UserId; email: string; passwordHash: string }

// Derived, not duplicated: PublicUser tracks User automatically.
type PublicUser = Omit<User, "passwordHash">;

function loadUser(id: UserId): Result<PublicUser> { /* ... */ }
loadUser("raw-string"); // ❌ compile error: plain string is not a UserId
```

**Bad Example** — untyped alias and duplicated shapes drift

```ts
type Data = any;                 // alias that names nothing and disables checking

// Two hand-written shapes that must stay in sync — and won't.
type User = { id: string; email: string; passwordHash: string };
type PublicUser = { id: string; email: string }; // add a field to User → this silently omits it

// Bare string ids: nothing stops passing an orderId where a userId is required.
function loadUser(id: string): Data { /* ... */ }
```

## Common Mistakes

- Aliasing to `any` (`type Json = any`) — the name looks safe but checking is off. Use
  `unknown` or a real recursive `Json` type.
- Hand-writing a "public" variant of a type instead of deriving it with `Omit`/`Pick`,
  so the two drift apart on the next edit.
- Assuming `type Meters = number` prevents passing a raw number — it does not without
  branding.
- Using a type alias for an object contract you intend to `extends`/`implements` widely,
  where an interface would compose more clearly.
- Giant inline unions repeated across signatures instead of one named alias.

## Production Tips

- Represent parsed JSON as `unknown` and narrow with a validator (zod, valibot); export
  the inferred type as the alias so runtime and compile-time shapes cannot diverge.
- Brand ids and money/units at system boundaries where confusing them causes real bugs;
  the `as`-cast cost is paid once in a constructor helper.
- Prefer `import type { X }` for type-only aliases so bundlers can strip them cleanly.

## AI Review Checklist

- Is each alias a real concept reused more than once, not a one-off inline type?
- Are `type` and `interface` chosen by capability (unions/tuples vs extendable shape)?
- Are derived variants built with utility types, not hand-duplicated?
- Do domain primitives that are easy to confuse use branding, not bare `string`/`number`?
- Is there any `type X = any`? Replace with `unknown` or a precise type.

## Related

- `knowledge/typescript/06-interfaces.md`
- `knowledge/typescript/11-unions-and-intersections.md`
- `knowledge/typescript/13-advanced-types.md`
- `knowledge/typescript/09-utility-types.md`
