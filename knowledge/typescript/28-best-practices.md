---
id: typescript/28-best-practices
topic: typescript
slug: best-practices
title: "TypeScript Best Practices"
type: doc
order: 28
status: ready
tags: [typescript, best-practices]
related: [typescript/02-type-system, typescript/12-type-guards, typescript/17-error-handling, typescript/23-clean-code, typescript/16-configuration]
when_to_use: "Read before writing or reviewing everyday TypeScript to apply the type-safety practices that prevent whole classes of bugs."
---
# TypeScript Best Practices

## Purpose

This document collects the day-to-day practices that make TypeScript deliver on its
promise: catching bugs at compile time instead of in production. These are the habits that
separate "JavaScript with some annotations" from genuinely type-safe code. Each rule
exists to remove a specific class of runtime error.

Where other docs go deep on one subject, this one is the practical baseline an agent
should apply to every file, every day.

## Why It Matters

TypeScript only pays off when its guarantees are real. Every `any`, every unchecked cast,
every disabled compiler flag punches a hole in the safety net — and holes compound. A
codebase that is "mostly typed" gives false confidence: reviewers trust the types, but the
types no longer reflect reality. The practices here keep the type system honest, so a
green compile actually means something. The alternative is the worst of both worlds: the
ceremony of types with none of the safety.

## Core Principles

- **`strict` is the floor, not a preference.** Enable all strict flags. Each one you
  disable is a category of null/undefined/implicit-any bug you have chosen to keep.
- **`unknown` over `any`.** `unknown` forces you to narrow before use; `any` disables
  checking and spreads silently through the program.
- **Model the domain in types.** Encode invariants (non-empty, validated, branded) so the
  compiler enforces them; do not rely on comments and discipline.
- **Let inference work, annotate the boundaries.** Annotate function parameters, return
  types, and public APIs; let locals be inferred. See [type inference](03-type-inference.md).
- **Narrow, don't assert.** Prove a type with a guard; only cast when you truly know more
  than the compiler and cannot express it otherwise.

## Best Practices

- Turn on `strict`, plus `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`, in
  `tsconfig`. See [configuration](16-configuration.md).
- Type function return values explicitly on public and exported functions so an accidental
  widening is caught at the definition, not the call site.
- Replace `any` with `unknown` at boundaries and narrow with type guards. See
  [type guards](12-type-guards.md).
- Use discriminated unions to model states with a `kind`/`type` tag, so `switch` is
  exhaustively checked (add a `never` default). See [type system](02-type-system.md).
- Prefer `readonly` and `as const` for data that should not mutate; immutability removes a
  class of aliasing bugs. See [immutability](20-immutability.md).
- Handle `null`/`undefined` explicitly with `?.`, `??`, and narrowing — not with `!`
  non-null assertions, which silently reintroduce the crash `strict` prevents.
- Type errors as `unknown` in `catch` and narrow before use; never assume `catch (e: any)`.
  See [error handling](17-error-handling.md).
- Name types for domain concepts (branded types, unions) instead of passing bare `string`
  and `number` that any value satisfies.
- Keep `eslint` with `@typescript-eslint` in CI and fix warnings; do not litter
  `// @ts-ignore`. Prefer `// @ts-expect-error` with a reason when a suppression is truly
  needed, because it fails if the error disappears.

## Examples

**Good Example** — exhaustive union, narrowing, no assertions

```ts
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "square":
      return shape.side ** 2;
    default:
      // If a new variant is added, `shape` is not `never` here → compile error.
      const _exhaustive: never = shape;
      throw new Error(`Unhandled shape: ${_exhaustive}`);
  }
}

function parse(input: unknown): number {
  // Narrow `unknown` with a guard instead of asserting `input as number`.
  if (typeof input === "number") return input;
  throw new TypeError("Expected a number");
}
```

**Bad Example** — `any`, non-null assertion, silent widening

```ts
// `any` disables checking; every downstream use is unprotected.
function area(shape: any): number {
  if (shape.kind === "circle") return Math.PI * shape.radius ** 2;
  // A missing case returns undefined at runtime, typed as number — a lie.
  return shape.side ** 2;
}

function firstName(user?: User) {
  return user!.name; // `!` reintroduces the exact null crash strict mode caught
}
```

## Common Mistakes

- Disabling `strict` (or individual strict flags) to make errors go away.
- Reaching for `any` where `unknown` plus a guard would preserve safety.
- Non-null assertions (`!`) to silence null errors instead of handling the null case.
- `// @ts-ignore` that hides a real error and never gets revisited.
- `catch (e: any)` and using `e.message` without checking `e` is an `Error`.
- Passing bare `string`/`number` for domain values, so any value type-checks.
- Non-exhaustive `switch` over a union with no `never` guard, silently missing new cases.

## Production Tips

- Fail CI on `tsc --noEmit` and on new lint warnings in changed files.
- Track and drive down the count of `any`/`@ts-ignore` over time; make new ones require
  justification in review.
- Adopt strict flags incrementally in legacy code (file-by-file) rather than never.

## AI Review Checklist

- Is `strict` (and `noUncheckedIndexedAccess`) enabled and unbroken?
- Are boundaries typed with `unknown` and narrowed, with no stray `any`?
- Are non-null assertions (`!`) absent, with nulls handled explicitly?
- Do unions have exhaustive handling backed by a `never` check?
- Are caught errors typed `unknown` and narrowed before use?
- Are `@ts-ignore` suppressions replaced by `@ts-expect-error` with a reason, or removed?

## Related

- `knowledge/typescript/02-type-system.md`
- `knowledge/typescript/12-type-guards.md`
- `knowledge/typescript/17-error-handling.md`
- `knowledge/typescript/23-clean-code.md`
- `knowledge/typescript/16-configuration.md`
