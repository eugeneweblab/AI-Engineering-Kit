---
id: typescript/01-language-fundamentals
topic: typescript
slug: language-fundamentals
title: "TypeScript Language Fundamentals"
type: doc
order: 1
status: ready
tags: [typescript, language-fundamentals]
related: [typescript/02-type-system, typescript/03-type-inference, typescript/04-functions, typescript/20-immutability]
when_to_use: "Read before writing variables, control flow, or any everyday TypeScript syntax."
---
# TypeScript Language Fundamentals

## Purpose

This document covers the everyday syntax an agent writes constantly: declaring variables,
literals, operators, control flow, and equality. TypeScript builds on JavaScript
semantics, so getting these right matters regardless of the type layer. The goal is code
that behaves the same at runtime as it reads on the page.

TypeScript adds types on top of JavaScript but changes none of its runtime behavior.
`===`, hoisting, truthiness, and coercion all work exactly as they do in JavaScript. The
type checker helps, but it cannot save you from misunderstanding the underlying language.

## Why It Matters

Most subtle bugs come not from advanced type features but from ordinary JavaScript
footguns that TypeScript inherits: `==` coercion, `var` hoisting, mutating a shared
array, comparing `NaN`. These pass the type checker because they are type-correct; they
are just wrong. An agent that writes disciplined fundamentals produces code that fails
loudly and predictably instead of silently doing the wrong thing.

## Core Principles

- **Prefer immutability by default.** Use `const`; reach for `let` only when a variable
  genuinely reassigns. Never use `var` — its function-scoping and hoisting cause bugs.
- **Compare strictly.** Always use `===` and `!==`. Loose `==` triggers coercion that
  produces surprising results (`0 == ""`, `null == undefined`).
- **Distinguish `null` from `undefined` deliberately.** Pick one to mean "absent" and be
  consistent. `undefined` is "never set"; `null` is "explicitly empty".
- **Do not rely on truthiness for presence checks.** `0`, `""`, and `false` are falsy but
  valid. Check `x == null` or `x === undefined` when you mean "absent".

## Best Practices

- Declare each variable with the narrowest scope it needs; block-scope with `const`/`let`.
- Use template literals (`` `${a}` ``) over string concatenation for readability and to
  avoid accidental `[object Object]` coercions.
- Use optional chaining `?.` and nullish coalescing `??` for absent values. `??` only
  falls through on `null`/`undefined`, unlike `||`, which also falls through on `0`/`""`.
- Prefer `for...of` and array methods (`map`, `filter`, `reduce`) over index loops; they
  avoid off-by-one errors and read as intent.
- Freeze or type-as-`readonly` shared constants so accidental mutation is caught.

## Examples

**Good Example** — strict equality, `const`, nullish coalescing

```ts
const timeoutMs = config.timeoutMs ?? 5000; // only defaults when null/undefined, not when 0

for (const item of items) {
  if (item.status === "active") {  // strict compare, no coercion
    process(item);
  }
}
```

**Bad Example** — loose equality, `var`, `||` swallowing valid zero

```ts
var timeout = config.timeoutMs || 5000; // BUG: a valid 0 becomes 5000

for (var i = 0; i < items.length; i++) {
  if (items[i].status == "active") {   // == coerces; "active\n" or objects surprise you
    process(items[i]);                 // `var i` leaks past the loop
  }
}
```

## Common Mistakes

- Using `||` to supply defaults when `0`, `""`, or `false` are valid inputs — use `??`.
- Using `var`, leaking variables out of their intended block via hoisting.
- Relying on truthiness (`if (count)`) when `0` is a meaningful value.
- Comparing with `==`, letting coercion mask type mismatches the checker would reveal.
- Mutating a `const` array or object and assuming `const` prevented it — `const` only
  blocks reassignment, not mutation (see [20-immutability](20-immutability.md)).

## Production Tips

- Enable ESLint rules `eqeqeq`, `no-var`, and `prefer-const` to enforce these mechanically.
- Turn on `noUncheckedIndexedAccess` so `array[i]` is typed `T | undefined`, forcing you
  to handle out-of-range access instead of trusting it.

## AI Review Checklist

- Are all declarations `const` or `let`, never `var`?
- Is every comparison `===`/`!==` rather than `==`/`!=`?
- Are defaults supplied with `??` where `0`/`""`/`false` are valid values?
- Are presence checks explicit (`== null`) rather than relying on truthiness?
- Is `const` on objects/arrays backed by `readonly` where mutation must be prevented?

## Related

- `knowledge/typescript/02-type-system.md`
- `knowledge/typescript/03-type-inference.md`
- `knowledge/typescript/04-functions.md`
- `knowledge/typescript/20-immutability.md`
