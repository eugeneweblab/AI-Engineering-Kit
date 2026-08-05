---
id: typescript/99-ai-review-checklist
topic: typescript
slug: ai-review-checklist
title: "TypeScript AI Review Checklist"
type: doc
order: 99
status: ready
tags: [typescript, ai-review-checklist, unknown, Pick, Partial, Omit, never, JSON.parse]
related: [typescript/12-type-guards, typescript/17-error-handling, typescript/23-clean-code, typescript/28-best-practices, typescript/100-common-antipatterns]
when_to_use: "Read before reviewing a TypeScript pull request or AI-generated TypeScript."
---
# TypeScript AI Review Checklist

## Purpose

This is the checklist an agent runs when reviewing TypeScript — its own output or
a human's. Each item is a concrete, verifiable question with a clear failure
signal, ordered so the highest-leverage type-safety checks come first. Reviewing
against this list catches the defects that pass the compiler but violate the
intent of a typed codebase.

## Why It Matters

Code that compiles is not code that is correct. TypeScript can be quietly
defeated — a cast, an `any`, a validated-looking value that was never validated —
and the compiler will still print green. Generated code is especially prone to
"looks-typed" patterns that assert instead of prove. A disciplined review pass is
where those escape hatches get caught before they reach production and rot into
silent runtime failures.

## Type Soundness

**Rules:** [Type System](02-type-system.md) · [Type Guards](12-type-guards.md)

- [ ] No `any` (explicit or implicit); boundary values use `unknown` and are narrowed.
- [ ] Every `as` cast and `!` assertion has an adjacent runtime check that justifies it.
- [ ] No double-cast escape hatch (`x as unknown as T`) without an explicit, sound reason.
- [ ] Discriminated unions are used where states are mutually exclusive, not optional-field bags.
- [ ] `switch`/exhaustive logic over unions has a `never` default or is provably total.

## Boundaries & Validation

**Rules:** [Interfaces](06-interfaces.md) · [Library Design](27-library-design.md)

- [ ] API responses, `JSON.parse`, env vars, and user input are schema-validated before typed use.
- [ ] The static type at a boundary is *derived from* the validator, not asserted alongside it.
- [ ] No structural type is trusted across a network/process boundary without parsing.

## Errors & Async

**Rules:** [Error Handling](17-error-handling.md) · [Asynchronous Programming](18-asynchronous-programming.md)

- [ ] No floating promises; every async call is awaited or explicitly handled.
- [ ] `catch (e)` treats `e` as `unknown` and narrows before accessing properties.
- [ ] Fallible functions signal failure in their return type, not via undeclared throws.
- [ ] No `async` function that swallows errors or returns before an awaited side effect completes.

## API & Types

**Rules:** [Generics](08-generics.md) · [Utility Types](09-utility-types.md)

- [ ] Exported functions/types have explicit, intentional signatures — not inferred-and-leaked internals.
- [ ] `readonly`/`as const` are used for data that should not mutate.
- [ ] Utility types (`Pick`, `Omit`, `Partial`) are used instead of hand-duplicated shapes.
- [ ] Generic parameters are actually constrained and used; no `<T>` that could be `unknown`.
- [ ] Enum-like values use string-literal unions or `as const` objects unless a real enum is needed.

## Clarity

**Rules:** [Clean Code](23-clean-code.md) · [Best Practices](28-best-practices.md)

- [ ] Names describe intent; types are not widened to `string`/`number` where a literal union fits.
- [ ] No dead `@ts-expect-error` (it would fail the build) and no unexplained suppressions.
- [ ] The change does not weaken an existing type to make new code compile.

## How To Use

For each item, find the evidence in the diff. If you cannot point to the line
that satisfies it, treat the item as failing. Report failures with the file,
line, the rule violated, and the concrete fix — mirror the format in
[common anti-patterns](100-common-antipatterns.md). Passing items need no comment.

## Related

- `knowledge/typescript/12-type-guards.md`
- `knowledge/typescript/17-error-handling.md`
- `knowledge/typescript/23-clean-code.md`
- `knowledge/typescript/28-best-practices.md`
- `knowledge/typescript/100-common-antipatterns.md`
