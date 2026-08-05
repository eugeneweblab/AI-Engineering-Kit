---
id: typescript/30-engineering-principles
topic: typescript
slug: engineering-principles
title: "TypeScript Engineering Principles"
type: doc
order: 30
status: ready
tags: [typescript, engineering-principles, UserSchema, loadUser, unknown, noUncheckedIndexedAccess, strict, uuid]
related: [typescript/02-type-system, typescript/16-configuration, typescript/17-error-handling, typescript/23-clean-code, typescript/28-best-practices]
when_to_use: "Read before making structural type-design or codebase-wide decisions in a TypeScript project."
---
# TypeScript Engineering Principles

## Purpose

This document defines the non-negotiable engineering principles for writing
TypeScript that stays correct as it grows. It is not a style guide (see
[clean code](23-clean-code.md)) and not a feature tour (see the
[type system](02-type-system.md)). It is the small set of rules that decide
whether the compiler works *for* you or against you. An agent should apply these
when choosing how to model data, configure the project, or shape an API.

## Why It Matters

TypeScript's value is a single promise: if it compiles, a whole class of runtime
errors cannot happen. That promise is only as strong as the weakest escape hatch
in the codebase. One `any`, one unchecked cast, one `strict: false` flag, and the
compiler silently stops proving anything about that path — while still *looking*
type-safe to the next reader. The failures are invisible at author time and
expensive at 3 a.m. These principles exist to keep the type system's guarantees
intact end to end, so that green CI actually means the code is sound.

## Core Principles

- **Make illegal states unrepresentable.** Model data so the compiler rejects
  impossible combinations. A discriminated union beats a bag of optional fields,
  because the bad states never compile in the first place.
- **`strict` is the floor, not a goal.** Every strict flag turns a runtime bug
  into a compile error. Turning one off to "make it build" hides the bug, it does
  not fix it.
- **Types describe runtime reality; validate the boundary.** The compiler trusts
  your annotations. At any I/O edge (network, disk, env, user input) that trust is
  unfounded — parse and validate, then let types flow inward.
- **`any` is a hole in the type system; `unknown` is a locked door.** `any`
  disables checking and spreads. `unknown` forces a narrowing step before use.
- **Infer, don't annotate, when the inference is correct.** Redundant annotations
  drift out of sync with the value they describe. Annotate contracts (function
  signatures, exports); let locals infer.
- **Prefer compile-time proof over runtime defense.** A type that makes a check
  unnecessary is stronger than a check you have to remember to write.

## Best Practices

- Enable `strict: true` plus `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`,
  and `noImplicitOverride`. Treat the tsconfig as production infrastructure (see
  [configuration](16-configuration.md)).
- Validate external data with a schema library (Zod, Valibot, ArkType) and derive
  the static type from the schema, so one source defines both.
- Return `Result`-style unions or typed errors from fallible domain logic instead
  of throwing untyped exceptions across module boundaries (see
  [error handling](17-error-handling.md)).
- Use `readonly` and `as const` by default; make mutability an explicit,
  deliberate choice (see [immutability](20-immutability.md)).
- Narrow `unknown` with user-defined [type guards](12-type-guards.md), never with a
  blind `as` cast.
- Ban `any` in lint (`@typescript-eslint/no-explicit-any`) and forbid
  `@ts-ignore` in favor of `@ts-expect-error` with a comment, so dead suppressions
  fail the build.

## Examples

**Good Example** — illegal states cannot compile; the boundary is validated

```ts
import { z } from "zod";

// A discriminated union: each state carries exactly the fields it needs.
type Request<T> =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ok"; data: T };

const UserSchema = z.object({ id: z.string().uuid(), age: z.number().int() });
type User = z.infer<typeof UserSchema>; // type derived from the validator

function render(req: Request<User>): string {
  switch (req.status) {
    case "loading": return "…";
    case "error":   return req.message;        // .data is not in scope here
    case "ok":      return req.data.id;         // .message is not in scope here
    // no default needed: the union is exhaustively handled
  }
}

async function loadUser(res: Response): Promise<User> {
  return UserSchema.parse(await res.json()); // trust begins only after parse
}
```

**Bad Example** — optional soup and an unchecked cast defeat the compiler

```ts
interface Request<T> {
  status: string;      // any string compiles, including typos
  data?: T;            // present or not — compiler can't tell you which
  message?: string;    // both fields always "maybe there"
}

function render(req: Request<User>): string {
  if (req.status === "ok") return req.data!.id; // "!" asserts a value we never proved
  return req.message ?? "";                     // silently "" when we forgot to set it
}

async function loadUser(res: Response): Promise<User> {
  return (await res.json()) as User; // cast lies: no runtime check at all
}
```

## Common Mistakes

- Reaching for `as` or `!` to silence an error instead of fixing the type that
  caused it — the cast survives long after the assumption stops being true.
- Setting `strict: false` (or leaving `noImplicitAny` off) to unblock a build.
- Trusting `JSON.parse`, `process.env`, or an API response as a typed value
  without validating it.
- Modeling a state machine as several independent optional booleans/fields, so
  contradictory states (`isLoading && isError`) are representable.
- Over-annotating locals, then editing the value and forgetting the annotation,
  leaving a type that lies.
- Using `any` "temporarily" — it propagates through every expression it touches.

## Production Tips

- Fail CI on type errors *and* on `any`/suppression lint rules; a type error that
  only shows in an editor is a type error nobody enforces.
- Run `tsc --noEmit` as a separate CI step from the bundler; bundlers often skip
  type checking for speed.
- When you must cast, isolate it in one narrow, commented adapter function so the
  unsafe assumption has exactly one place to audit.

## AI Review Checklist

- Is `strict` (and ideally `noUncheckedIndexedAccess`) on, with no per-file opt-outs?
- Is every external input validated before it is treated as a typed value?
- Are impossible states unrepresentable (discriminated unions over optional flags)?
- Is `any` absent, and is every `as`/`!` justified by an adjacent runtime check?
- Are errors modeled in the type signature rather than thrown untyped?
- Do exported functions annotate their contracts while locals rely on inference?

## Related

- `knowledge/typescript/02-type-system.md`
- `knowledge/typescript/16-configuration.md`
- `knowledge/typescript/17-error-handling.md`
- `knowledge/typescript/23-clean-code.md`
- `knowledge/typescript/28-best-practices.md`
