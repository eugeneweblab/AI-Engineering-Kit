---
id: javascript/02-execution-context
topic: javascript
slug: execution-context
title: "Execution Context"
type: doc
order: 2
status: ready
tags: [javascript, execution-context, total]
related: [javascript/00-overview, javascript/01-language-fundamentals, javascript/03-scope-and-closures, javascript/04-functions, javascript/16-this-keyword]
when_to_use: "Read before debugging hoisting, temporal-dead-zone, or 'undefined before assignment' errors."
---
# Execution Context

## Purpose

This document explains what the JavaScript engine does *before and during* running your
code: how it creates an execution context, hoists declarations, sets up the temporal dead
zone (TDZ), and binds `this`. It lets an agent explain why a variable is `undefined`,
why a `let` access throws a `ReferenceError`, and why one function is callable before its
definition while another is not.

## Why It Matters

Every line of JavaScript runs inside an execution context, and the engine builds that
context in two phases: a *creation* phase that registers declarations, then an
*execution* phase that runs statements top to bottom. Hoisting, the TDZ, and the value of
`this` are all decided in the creation phase. Code that assumes strictly top-to-bottom
execution mispredicts these, producing `undefined` values, "cannot access before
initialization" errors, and a `this` that points somewhere unexpected. Understanding the
two phases turns these from mysteries into predictions.

## Core Principles

- **Two phases per context.** Creation: allocate the environment, register bindings, set
  `this`. Execution: run statements and assign values.
- **`function` declarations are fully hoisted.** Both name and body are available before
  their line, so they can be called earlier in the same scope.
- **`var` is hoisted and initialized to `undefined`.** The name exists early but holds no
  value until its assignment line runs.
- **`let`/`const`/`class` are hoisted but not initialized.** They sit in the TDZ from the
  top of the block until their declaration; touching them there throws.
- **`this` is set when the context is created, by how the function is called** — not by
  where it is defined (except arrow functions, which inherit `this`).

## Best Practices

- Declare before use, always. Relying on hoisting to call code above its definition makes
  order fragile; the TDZ punishes it for `let`/`const`.
- Prefer `const`, then `let`; never `var`. `var`'s function-scoping and `undefined`
  hoisting cause exactly the bugs the TDZ was designed to prevent.
- Put `function` declarations at the top of their scope if you rely on calling them early,
  so the hoisting is visible rather than implicit.
- Do not read a `let`/`const` binding above its declaration line — it is a guaranteed TDZ
  `ReferenceError`, not `undefined`.
- Know that arrow functions capture the surrounding `this` at definition; regular
  functions receive `this` from the call site. Choose deliberately (see
  [the `this` keyword](16-this-keyword.md)).

## Examples

**Good Example** — declare before use, predictable values

```js
"use strict";

function total(items) {
  let sum = 0;                 // declared before first use, no TDZ risk
  for (const item of items) {  // block-scoped, fresh binding per iteration
    sum += item.price;
  }
  return sum;
}

// `total` is a function declaration → hoisted, so this call is safe:
console.log(total([{ price: 10 }, { price: 5 }])); // 15
```

**Bad Example** — hoisting and TDZ traps

```js
function report() {
  console.log(count);   // undefined — `var count` is hoisted but not yet assigned
  var count = 5;

  console.log(rate);    // ReferenceError — `rate` is in the temporal dead zone
  let rate = 0.2;

  // Reads like it runs top to bottom, but the engine registered both names first.
}
```

## Common Mistakes

- Expecting a `var` read before its assignment to throw; it silently yields `undefined`.
- Expecting a `let`/`const` read before its declaration to yield `undefined`; it throws a
  TDZ `ReferenceError`.
- Calling a function *expression* (`const f = () => {}`) before its line — the binding is
  in the TDZ, unlike a function *declaration*.
- Assuming `this` is fixed by where a function is written; for regular functions it is
  fixed by how it is called, and a detached method loses its receiver.
- Using `var` in a loop and capturing the same binding in every closure (see
  [Scope and Closures](03-scope-and-closures.md)).

## AI Review Checklist

- Is every variable declared before it is read, with no reliance on `var` hoisting?
- Are `let`/`const` accesses always below their declaration (no TDZ reads)?
- Are function *expressions* defined before they are called?
- Is the value of `this` correct for each call site, and are arrow vs. regular functions
  chosen deliberately?
- Is `var` avoided in favor of `const`/`let`?

## Related

- `knowledge/javascript/00-overview.md`
- `knowledge/javascript/01-language-fundamentals.md`
- `knowledge/javascript/03-scope-and-closures.md`
- `knowledge/javascript/04-functions.md`
- `knowledge/javascript/16-this-keyword.md`
