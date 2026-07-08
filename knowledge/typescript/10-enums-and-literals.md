---
id: typescript/10-enums-and-literals
topic: typescript
slug: enums-and-literals
title: "Enums And Literals"
type: doc
order: 10
status: ready
tags: [typescript, enums-and-literals]
related: [typescript/11-unions-and-intersections, typescript/07-type-aliases, typescript/12-type-guards, typescript/06-interfaces]
when_to_use: "Read before modeling a fixed set of named values — a status, a role, a mode, a variant tag — and when deciding between an enum and a literal union."
---
# Enums And Literals

## Purpose

This document defines how to model a fixed set of named values in TypeScript: literal types,
literal unions, `as const`, and `enum`. It is written so an agent picks the representation that
is type-safe, tree-shakeable, and honest about runtime behavior — and knows when `enum` is the
wrong tool.

A literal type is a single exact value (`"admin"`, `200`, `true`). A literal *union*
(`"admin" | "member"`) is the idiomatic way to model a closed set. An `enum` is a runtime
construct that also emits JavaScript — a different trade-off you should choose deliberately.

## Why It Matters

Modeling a fixed set as a plain `string` lets typos (`"Amin"`) and invalid states compile,
then fail at runtime in the one branch nobody tested. A closed set — literal union or enum —
turns those into compile errors and unlocks exhaustiveness checking, so adding a new case
forces every `switch` to handle it. The wrong choice also has runtime cost: numeric and
regular `enum`s emit code and reverse-mappings that resist tree-shaking and can produce
surprising values. Getting this right prevents a class of "impossible" runtime bugs.

## Core Principles

- **Prefer literal unions to `enum` for most cases.** They are erased at compile time (zero
  runtime cost), tree-shakeable, and interoperate directly with JSON string values.
- **Avoid numeric `enum`s.** Their reverse mapping and implicit numbering (`Status.Active`
  === `0`) invite bugs; a `0` value is also falsy. If you must use `enum`, make it string-valued.
- **Use `as const` to derive a union from data.** One array/object of allowed values gives you
  both the runtime list and the type, kept in sync.
- **Make illegal states unrepresentable.** A closed set is the foundation of discriminated
  unions and exhaustive handling.
- **Exhaustiveness is a feature — enforce it.** A `never` default case turns "unhandled new
  variant" into a compile error.

## Best Practices

- Model status/role/mode as a literal union: `type Role = "admin" | "member" | "guest"`.
- When you need the values at runtime (to iterate, validate, or render a dropdown), define the
  list once with `as const` and derive the type: `type Role = typeof ROLES[number]`.
- If you use `enum` (e.g. for an existing API), make it a **string enum** and prefer
  `const enum` only when you understand the inlining and isolatedModules caveats.
- Add an `assertNever(x: never)` default in every `switch` over a closed set so new cases
  cannot be silently ignored.
- Validate external strings against the set at the boundary (a `Set` membership check or a
  schema) before treating them as the union type.

## Examples

**Good Example** — `as const` list, derived union, exhaustive switch

```ts
// One source of truth: runtime values AND the type stay in sync.
const ROLES = ["admin", "member", "guest"] as const;
type Role = (typeof ROLES)[number]; // "admin" | "member" | "guest"

function isRole(x: string): x is Role {
  return (ROLES as readonly string[]).includes(x); // boundary validation
}

function homePath(role: Role): string {
  switch (role) {
    case "admin":  return "/admin";
    case "member": return "/app";
    case "guest":  return "/welcome";
    default:
      // If a new role is added to ROLES, this line fails to compile until handled.
      return assertNever(role);
  }
}
function assertNever(x: never): never { throw new Error(`Unhandled: ${x}`); }
```

**Bad Example** — numeric enum and bare string invite silent bugs

```ts
enum Status { Active, Inactive, Banned } // Active === 0 (falsy!), reverse-mapped, emits code

function label(s: Status) {
  if (!s) return "active"; // ❌ meant "=== Active", but Active is 0 → always true for Active
  return "other";
}

// Elsewhere, status modeled as a plain string: typos compile.
function setRole(role: string) { /* "Amin" is accepted, fails deep in the app */ }
```

## Common Mistakes

- Numeric `enum`s whose first member is `0` and thus falsy, breaking truthiness checks.
- Relying on numeric `enum` reverse mapping (`Status[0]`), which bloats output and confuses
  readers.
- Typing a closed set as `string`, allowing typos and invalid values to compile.
- No `never` default in a `switch`, so adding a variant silently skips a branch.
- Duplicating the allowed-values list in code and in the type instead of deriving one from the
  other with `as const`.
- Trusting an external string as the union type without validating it at the boundary.

## Production Tips

- For values that appear in JSON, on the wire, or in a database, use string literal unions —
  they serialize as-is and need no mapping layer.
- `const enum` is fully inlined and disappears at runtime, but breaks under `isolatedModules`
  and some bundlers; prefer `as const` unions unless a dependency requires the enum.
- Pair the union with a runtime validator (zod `z.enum(ROLES)`) so compile-time and
  boundary-time agree on the allowed set.

## AI Review Checklist

- Is the fixed set a literal union (or string enum), never a bare `string`?
- Are numeric `enum`s avoided, or at least converted to string enums?
- When runtime values are needed, are they derived from one `as const` list via `typeof[number]`?
- Does every `switch` over the set have a `never` default for exhaustiveness?
- Are external strings validated against the set before being used as the union type?

## Related

- `knowledge/typescript/11-unions-and-intersections.md`
- `knowledge/typescript/07-type-aliases.md`
- `knowledge/typescript/12-type-guards.md`
- `knowledge/typescript/06-interfaces.md`
