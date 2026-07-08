---
id: typescript/11-unions-and-intersections
topic: typescript
slug: unions-and-intersections
title: "Unions And Intersections"
type: doc
order: 11
status: ready
tags: [typescript, unions-and-intersections]
related: [typescript/10-enums-and-literals, typescript/12-type-guards, typescript/07-type-aliases, typescript/13-advanced-types]
when_to_use: "Read before modeling a value that can be one of several shapes (union) or must satisfy several contracts at once (intersection), especially state machines and API results."
---
# Unions And Intersections

## Purpose

This document defines how to compose types with unions (`A | B`, "one of") and intersections
(`A & B`, "all of"), with emphasis on *discriminated unions* — the primary tool for modeling
values that vary by state. It is written so an agent can make illegal states unrepresentable
and narrow safely rather than casting.

A union is a value that is **exactly one** of several types. An intersection is a value that is
**simultaneously all** of several types. Most real modeling power comes from *discriminated*
unions: a set of shapes distinguished by a shared literal tag.

## Why It Matters

Most bugs in stateful code come from representing several mutually exclusive states as one loose
object with optional fields — `{ loading?: boolean; data?: T; error?: E }` — where nonsense
combinations (`loading` *and* `error`) are representable and therefore eventually occur. A
discriminated union makes each state a distinct shape, so the impossible combinations cannot be
constructed and the compiler forces you to handle each case. This converts a category of runtime
"how did we get here?" bugs into compile errors. Intersections, used carelessly, do the opposite —
combining conflicting properties into `never` — so they demand equal care.

## Core Principles

- **Model "one of N states" as a discriminated union**, not one object with optional fields. A
  shared literal tag (`kind`, `status`, `type`) makes states mutually exclusive.
- **Narrow, do not cast.** Use the discriminant, `typeof`/`instanceof`, or a
  [type guard](12-type-guards.md) to prove which member you have. `as` throws away the check.
- **Unions widen the requirement; intersections widen the guarantee.** With `A | B` you may only
  touch members common to both until you narrow; with `A & B` you get everything from both.
- **Exhaustiveness is enforceable.** A `never` default in a `switch` over the discriminant turns
  an unhandled new state into a compile error.
- **Beware conflicting intersections.** Intersecting incompatible property types yields `never`,
  a silent bug generator.

## Best Practices

- Give every union member a shared, unique literal discriminant so narrowing is a single tag
  check. Prefer `kind`/`type`/`status` consistently across the codebase.
- Model async and result states as unions: `{ status: "loading" } | { status: "ok"; data: T } |
  { status: "error"; error: E }`. The data only exists in the state where it is valid.
- Access union-specific fields only inside a narrowed branch; the compiler will otherwise reject
  it, which is the safety working as intended.
- Use intersections to *compose* capabilities (`Timestamped & Identifiable`), not to merge
  overlapping-but-conflicting shapes.
- Add an `assertNever` default to every discriminant `switch` to lock in exhaustiveness.

## Examples

**Good Example** — discriminated union makes bad states impossible

```ts
// Each state is a distinct shape; data/error exist only where they are meaningful.
type Fetch<T> =
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; message: string };

function render<T>(state: Fetch<T>): string {
  switch (state.status) {
    case "loading": return "…";
    case "success": return `ok: ${JSON.stringify(state.data)}`; // data available here only
    case "error":   return `error: ${state.message}`;
    default:
      return assertNever(state); // new state → compile error until handled
  }
}
function assertNever(x: never): never { throw new Error(`Unhandled: ${JSON.stringify(x)}`); }

// Intersection composes capabilities without conflict.
type Entity = { id: string } & { createdAt: Date };
```

**Bad Example** — optional-field blob and a lossy cast

```ts
// All fields optional → illegal combinations are representable and unavoidable.
interface Fetch<T> { loading?: boolean; data?: T; error?: string }

function render<T>(state: Fetch<T>): string {
  if (state.loading && state.error) return "???"; // impossible-yet-reachable state
  return `ok: ${(state as { data: T }).data}`;     // cast lies: data may be undefined → crash
}

// Conflicting intersection silently collapses to never.
type Bad = { id: string } & { id: number }; // id: never — nothing can satisfy it
```

## Common Mistakes

- Representing mutually exclusive states as one object with optional fields, allowing
  `loading && error` and forcing defensive checks everywhere.
- Casting with `as` to reach a member's field instead of narrowing on the discriminant.
- Omitting the shared discriminant, so narrowing requires brittle `in`/property probing.
- No `never` default, so a newly added union member is silently unhandled.
- Intersecting types with a conflicting property and getting `never` without noticing.
- Accessing a union-only property outside its narrowed branch and reaching for `!`/`as` to
  silence the (correct) error.

## Production Tips

- Mirror server API responses as discriminated unions keyed on a status/type field so client
  code must handle each variant; pair with a runtime validator so the tag is trusted.
- For a value that is "one of a fixed set of *tags*" with no payload, a
  [literal union](10-enums-and-literals.md) is enough; add payloads to make it discriminated.
- If an intersection unexpectedly becomes `never`, hover the type — conflicting members are the
  usual cause; refactor to a union or reconcile the property types.

## AI Review Checklist

- Are mutually exclusive states modeled as a discriminated union, not optional fields?
- Does every union member share a unique literal discriminant (`kind`/`type`/`status`)?
- Is narrowing done via the discriminant/type guard rather than `as` casts?
- Does every `switch` over the discriminant have a `never` default for exhaustiveness?
- Are union-specific fields accessed only inside a narrowed branch?
- Do any intersections silently resolve to `never` from conflicting properties?

## Related

- `knowledge/typescript/10-enums-and-literals.md`
- `knowledge/typescript/12-type-guards.md`
- `knowledge/typescript/07-type-aliases.md`
- `knowledge/typescript/13-advanced-types.md`
