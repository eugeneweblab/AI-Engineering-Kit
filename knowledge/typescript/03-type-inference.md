---
id: typescript/03-type-inference
topic: typescript
slug: type-inference
title: "Type Inference"
type: doc
order: 3
status: ready
tags: [typescript, type-inference, entries]
related: [typescript/02-type-system, typescript/04-functions, typescript/10-enums-and-literals, typescript/28-best-practices]
when_to_use: "Read before deciding whether to annotate a value or let the compiler infer its type."
---
# Type Inference

## Purpose

This document explains when to let TypeScript infer a type and when to write one
explicitly. Inference is one of TypeScript's best features: it keeps code concise while
staying fully typed. But inference has rules — widening, contextual typing, `const` vs
`let` — and knowing them is the difference between a precise type and a uselessly broad
one.

The guiding rule: **infer internally, annotate at boundaries.** Let the compiler deduce
local variable and return types; write explicit types where code meets other code
(exported functions, public APIs, module edges).

## Why It Matters

Over-annotating is noisy and, worse, can be *wrong* — an explicit type that drifts from
the value it describes is a lie the compiler now trusts. Under-annotating at boundaries
lets inference leak implementation details into a public contract, so a small internal
change silently alters the exported type and breaks callers. Getting inference right
keeps code both concise and stable: precise where it counts, quiet everywhere else.

## Core Principles

- **Trust inference for locals.** `const x = 5` is already `5`; annotating it `: number`
  adds noise and *widens* it. Redundant annotations obscure, they don't clarify.
- **Annotate function boundaries.** Give exported functions explicit parameter and return
  types so the contract is fixed and doesn't shift when the body changes.
- **`const` narrows, `let` widens.** `const s = "GET"` infers the literal `"GET"`; `let s
  = "GET"` infers `string`. Use `as const` to keep literals in objects and arrays.
- **Contextual typing flows inward.** In `arr.map(x => ...)`, `x` is inferred from `arr`.
  Don't re-annotate what context already provides.

## Best Practices

- Let local `const`/`let` types be inferred; annotate only when inference is wrong or
  ambiguous (e.g., an empty array `const xs: string[] = []`).
- Always write explicit return types on exported/public functions. This catches accidental
  return-type changes at the definition rather than at distant call sites.
- Use `as const` for literal config objects and tuples so their narrow types survive.
- When an inferred type is too wide (e.g., `string` where you need a union), narrow with
  `as const` or an explicit literal type rather than casting later.

## Examples

**Good Example** — infer locals, annotate the boundary, `as const` for literals

```ts
// Explicit return type fixes the public contract; params annotated at the boundary.
export function toQuery(params: Record<string, string>): string {
  const pairs = Object.entries(params); // inferred [string, string][] — no annotation needed
  return pairs.map(([k, v]) => `${k}=${v}`).join("&");
}

const methods = ["GET", "POST"] as const; // type: readonly ["GET", "POST"], not string[]
type Method = (typeof methods)[number];    // "GET" | "POST"
```

**Bad Example** — redundant annotations, missing boundary type, lost literals

```ts
export function toQuery(params: Record<string, string>) { // no return type: contract can drift
  const pairs: [string, string][] = Object.entries(params); // redundant, just noise
  return pairs.map(([k, v]: [string, string]) => `${k}=${v}`).join("&"); // context already types this
}

const methods = ["GET", "POST"]; // inferred string[]; the literal union is lost
```

## Common Mistakes

- Annotating every local variable, adding noise and risking an annotation that lies.
- Omitting return types on exported functions, letting the public type shift silently
  when the implementation changes.
- Forgetting `as const`, so a literal config widens to `string`/`number` and loses its
  precise union (see [10-enums-and-literals](10-enums-and-literals.md)).
- Re-annotating callback parameters that contextual typing already infers correctly.
- Initializing with `[]` or `null` and letting it infer `any[]`/`any`, then never narrowing.

## Production Tips

- Enable the ESLint rule `@typescript-eslint/explicit-module-boundary-types` to require
  return types on exported functions automatically.
- Hover types in your editor before annotating — if the inferred type is already correct
  and precise, an explicit annotation only adds a maintenance burden.

## AI Review Checklist

- Do exported/public functions have explicit return types?
- Are local variables left to inference unless inference is genuinely wrong or empty?
- Is `as const` used where literal unions or tuples must be preserved?
- Are there redundant annotations that merely restate what the compiler already infers?
- Are empty-array/`null` initializers narrowed instead of inferring `any`?

## Related

- `knowledge/typescript/02-type-system.md`
- `knowledge/typescript/04-functions.md`
- `knowledge/typescript/10-enums-and-literals.md`
- `knowledge/typescript/28-best-practices.md`
