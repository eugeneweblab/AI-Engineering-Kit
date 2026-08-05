---
id: typescript/100-common-antipatterns
topic: typescript
slug: common-antipatterns
title: "TypeScript Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [typescript, common-antipatterns, toUpperCase, unknown, handle, parse, compute, UserSchema]
related: [typescript/02-type-system, typescript/12-type-guards, typescript/17-error-handling, typescript/23-clean-code, typescript/28-best-practices]
when_to_use: "Read before writing or reviewing TypeScript to avoid common type-safety traps."
---
# TypeScript Common Antipatterns

## Purpose

This document catalogs the TypeScript patterns that compile cleanly but defeat
the type system's guarantees. Each entry states the anti-pattern, *why it is
wrong*, and the concrete fix. An agent should treat any match as a defect to
correct, not a style preference. These are the failures that turn "it type-checks"
into a false sense of safety.

## Why It Matters

Every anti-pattern below has the same shape: it makes the compiler stop proving
something while still looking type-safe to the next reader. The bug does not
appear until runtime, in production, with no compile-time warning. Recognizing
these on sight is the difference between a type system that catches errors and
one that merely decorates them.

## Anti-Patterns

### 1. Using `any` to silence an error

**Why it is wrong:** `any` disables type checking for the value *and everything
it flows into*. One `any` can silently unsound an entire call chain.

**The fix:** Use `unknown` at the boundary and narrow with a [type guard](12-type-guards.md).

```ts
// Bad — payload.user.id is unchecked; a typo compiles, crashes at runtime
function handle(payload: any) { return payload.user.id.toUpperCase(); }

// Good — unknown forces validation before use
function handle(payload: unknown) {
  const { user } = EventSchema.parse(payload); // proven shape
  return user.id.toUpperCase();
}
```

### 2. Casting instead of validating (`as T`)

**Why it is wrong:** `as` is a compile-time assertion with zero runtime effect.
`(await res.json()) as User` claims a shape the compiler never verified.

**The fix:** Parse external data with a schema and derive the type from it.

```ts
// Bad — a lie the compiler believes
const user = (await res.json()) as User;
// Good — the type is a consequence of a real runtime check
const user = UserSchema.parse(await res.json());
```

### 3. The double-cast escape hatch (`x as unknown as T`)

**Why it is wrong:** It exists specifically to bypass the compiler's refusal to
cast between unrelated types. It forces a conversion the type system knows is unsound.

**The fix:** Fix the source type or write a validated adapter. Reserve double-casts
for genuinely typeless interop, isolated and commented.

### 4. Non-null assertion (`!`) to dodge `undefined`

**Why it is wrong:** `arr.find(...)!` asserts a value exists that the type says
might not. When it does not, you get `Cannot read properties of undefined`.

**The fix:** Handle the `undefined` branch, or restructure so the value is proven present.

```ts
// Bad — throws at runtime if no match
const admin = users.find(u => u.role === "admin")!;
// Good — the absent case is explicit
const admin = users.find(u => u.role === "admin");
if (!admin) throw new NoAdminError();
```

### 5. Optional-field soup instead of a discriminated union

**Why it is wrong:** Independent optional fields make contradictory states
representable (`{ loading: true, error: "x", data: {...} }`) and force `!`
everywhere to read them.

**The fix:** Model mutually exclusive states as a discriminated union so illegal
states cannot compile (see [engineering principles](30-engineering-principles.md)).

### 6. Widening literals to `string`/`number`

**Why it is wrong:** `type Status = string` accepts `"loadng"` and every other
typo. The compiler can no longer catch invalid values or exhaustively check them.

**The fix:** Use a string-literal union: `type Status = "loading" | "error" | "ok"`.

### 7. Enums for simple constants

**Why it is wrong:** Numeric `enum`s allow any number to be assigned, and all
`enum`s emit runtime code and have surprising structural-typing behavior.

**The fix:** Prefer `as const` objects or literal unions unless you need a
nominal, iterable enum specifically.

```ts
// Good — no runtime cost, exact values
const Role = { Admin: "admin", User: "user" } as const;
type Role = typeof Role[keyof typeof Role];
```

### 8. Floating promises

**Why it is wrong:** A promise you forget to `await` runs unordered, and its
rejection becomes an unhandled rejection that can crash the process.

**The fix:** Enable `@typescript-eslint/no-floating-promises`; `await` or
explicitly `void` every promise (see [async programming](18-asynchronous-programming.md)).

### 9. Treating `catch` errors as typed

**Why it is wrong:** In TypeScript a caught value is `unknown` — it can be a
string, a number, or anything `throw`n. Accessing `e.message` blindly can throw again.

**The fix:** Narrow before use: `if (e instanceof Error) …` (see [error handling](17-error-handling.md)).

### 10. `@ts-ignore` on an error

**Why it is wrong:** `@ts-ignore` suppresses *whatever* error is on the next line
forever, including new ones introduced later, and hides real regressions.

**The fix:** Use `@ts-expect-error` with a comment — it fails the build if the
error ever disappears, so dead suppressions cannot accumulate.

### 11. Redundant local annotations that drift

**Why it is wrong:** `const n: number = compute()` restates what inference already
knows; when `compute` changes return type, the annotation silently lies or errors
in the wrong place.

**The fix:** Let locals infer; annotate only contracts (exports, function signatures).

## Common Mistakes

- Reaching for the fastest way to make red squiggles disappear (`any`, `as`, `!`,
  `@ts-ignore`) rather than the type that expresses the real constraint.
- Weakening an existing type so new code compiles, degrading safety for every
  other caller.
- Trusting `JSON.parse` / `fetch` results as typed without a runtime parse step.

## AI Review Checklist

- Is there any `any`, or an `as`/`!` without an adjacent runtime check?
- Are external inputs validated, with the type derived from the validator?
- Are mutually exclusive states modeled as discriminated unions, not optional flags?
- Are literal unions/`as const` used instead of `string` widening or numeric enums?
- Are promises always handled, and are `catch` values narrowed from `unknown`?
- Are suppressions `@ts-expect-error` with a reason, never `@ts-ignore`?

## Related

- `knowledge/typescript/02-type-system.md`
- `knowledge/typescript/12-type-guards.md`
- `knowledge/typescript/17-error-handling.md`
- `knowledge/typescript/23-clean-code.md`
- `knowledge/typescript/28-best-practices.md`
