---
id: typescript/23-clean-code
topic: typescript
slug: clean-code
title: "Clean Code"
type: doc
order: 23
status: ready
tags: [typescript, clean-code]
related: [typescript/04-functions, typescript/17-error-handling, typescript/28-best-practices, typescript/30-engineering-principles, typescript/21-functional-programming]
when_to_use: "Read before writing or reviewing everyday application code — naming, function shape, control flow, and readability."
---
# Clean Code

## Purpose

This document defines what clean TypeScript looks like at the level of individual
functions and files: naming, function size, control flow, comments, and the everyday
choices that make code readable. It is written so an agent produces code the next reader
understands on the first pass and can change without fear.

Clean code is not about aesthetics. It is about lowering the cost of the next change.
Code is read far more often than it is written; every minute saved reading it is
multiplied across everyone who touches it after you.

## Why It Matters

Most of a system's cost is in maintenance, and maintenance is dominated by reading code
to understand it before touching it. Unclear names, functions that do five things, and
deep nesting force the reader to hold the whole thing in their head just to make a
one-line change — which is exactly when bugs are introduced. In TypeScript specifically,
weak typing (`any`, loose returns) removes the compiler's ability to help, so clarity has
to come from the code itself. Clean code is the cheapest defect-prevention tool available.

## Core Principles

- **Names carry the meaning.** A name should say what a thing is or does without a comment.
  Rename until the code reads like prose; vague names (`data`, `handle`, `tmp`) are a smell.
- **A function does one thing at one level of abstraction.** If you must scroll to read it,
  or it mixes high-level flow with low-level detail, split it.
- **Return early; keep the happy path un-nested.** Guard clauses at the top flatten
  control flow; deep `if/else` nesting hides the main path.
- **Let types replace comments.** Precise types (`Email`, `readonly User[]`, discriminated
  unions) encode invariants the compiler checks; a comment can lie, a type cannot.
- **Delete dead code and commented-out code.** Version control remembers it; leaving it
  makes readers wonder if it matters.

## Best Practices

- Name booleans and predicates as questions/assertions (`isActive`, `hasAccess`,
  `canEdit`); name functions as verbs (`loadUser`), values as nouns (`user`).
- Keep functions short and focused; a function longer than roughly a screen usually hides
  two or three functions with names waiting to be extracted.
- Limit parameters to a few; past three, pass a typed options object so call sites read
  `move({ from, to, force })` instead of `move(a, b, true)`.
- Replace magic numbers and strings with named `const`s or `as const` unions, so the value
  has a meaning and every use is greppable.
- Prefer `const` over `let`; a `let` signals reassignment, so its absence tells the reader
  the value is stable. Reach for `let` only when you truly reassign.
- Do not use `any`. Reach for `unknown` at boundaries and narrow, so the compiler keeps
  helping; `any` silently disables every check downstream.
- Write comments that explain *why*, not *what*. The code says what; a comment earns its
  place only by explaining a non-obvious reason, trade-off, or constraint.
- Keep nesting shallow — extract a function or use early returns rather than a third level
  of indentation.

## Examples

**Good Example** — intention-revealing names, guard clauses, typed options

```ts
interface TransferInput {
  readonly from: Account;
  readonly to: Account;
  readonly amountCents: number;
}

function transfer({ from, to, amountCents }: TransferInput): Result<Transfer> {
  if (amountCents <= 0) return err("amount must be positive"); // guard: fail fast, flat flow
  if (from.balanceCents < amountCents) return err("insufficient funds");

  // Happy path reads top-to-bottom with no nesting.
  const debited = { ...from, balanceCents: from.balanceCents - amountCents };
  const credited = { ...to, balanceCents: to.balanceCents + amountCents };
  return ok({ debited, credited, amountCents });
}
```

**Bad Example** — vague names, deep nesting, magic numbers, `any`

```ts
function doIt(a: any, b: any, amt: number): any {
  if (amt > 0) {                 // main logic buried three levels deep
    if (a.bal >= amt) {          // "bal"? "a"? what are these
      if (amt < 10000) {         // magic number with no name or reason
        a.bal = a.bal - amt;     // mutates inputs; see immutability doc
        b.bal = b.bal + amt;
        return true;             // returns true | undefined | ...; caller can't rely on it
      }
    }
  }
  // silent fall-through: on failure returns undefined with no reason
}
```

## Common Mistakes

- Vague names (`data`, `obj`, `handle`, `doIt`) that force the reader to open the body.
- Functions that do several things, mixing high-level flow with low-level detail.
- Deep `if/else` nesting instead of early-return guard clauses.
- Magic numbers and string literals scattered instead of named constants.
- Using `any` to silence the compiler, disabling type checking downstream.
- Comments that restate the code (`// increment i`) instead of explaining why.
- Leaving commented-out or dead code that misleads the next reader.
- Long parameter lists of positional args where an options object would read clearly.

## Production Tips

- Enforce the mechanical parts (naming casing, no unused vars, complexity, no `any`) with
  ESLint + `typescript-eslint` so review time is spent on design, not style nits.
- Format with Prettier on save/commit; never spend review comments on whitespace.
- Set `strict: true` (and `noUncheckedIndexedAccess`) in tsconfig — clean code depends on
  the compiler catching what naming discipline cannot.

## AI Review Checklist

- Do names reveal intent without needing a comment to explain them?
- Does each function do one thing at one level of abstraction?
- Is the happy path flat, with early-return guard clauses instead of deep nesting?
- Are magic numbers/strings replaced by named constants or `as const` unions?
- Is `any` absent, with `unknown` + narrowing used at boundaries?
- Is `const` used unless reassignment is genuinely needed?
- Do comments explain *why*, and is there no dead or commented-out code left behind?

## Related

- `knowledge/typescript/04-functions.md`
- `knowledge/typescript/17-error-handling.md`
- `knowledge/typescript/28-best-practices.md`
- `knowledge/typescript/30-engineering-principles.md`
- `knowledge/typescript/21-functional-programming.md`
