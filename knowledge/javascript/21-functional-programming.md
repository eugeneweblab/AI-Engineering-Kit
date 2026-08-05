---
id: javascript/21-functional-programming
topic: javascript
slug: functional-programming
title: "JavaScript Functional Programming"
type: doc
order: 21
status: ready
tags: [javascript, functional-programming, pipe, structuredClone, Object.freeze, applyDiscount, reverse, compose]
related: [javascript/04-functions, javascript/03-scope-and-closures, javascript/22-design-patterns, javascript/23-clean-code, javascript/28-best-practices]
when_to_use: "Read before writing data-transformation logic, shared state, or composing pipelines of small functions."
---
# JavaScript Functional Programming

## Purpose

This document defines the functional style in JavaScript: **pure functions**,
**immutability**, **higher-order functions**, and **composition**. It shows how to model
logic as data transformations rather than mutations, and when the functional approach is
the right default versus when it costs more than it returns.

Functional programming here means practical FP for application code — not category
theory. The goal is predictable, testable, composable functions, not purity for its own
sake.

## Why It Matters

Most hard bugs come from **shared mutable state**: something changed a value another part
of the code assumed was stable. Pure functions eliminate that class of bug by design — the
same input always yields the same output, with no hidden reads or writes. That property
makes code trivially testable (no mocks, no setup), safely parallelizable, and easy to
reason about locally. JavaScript is well suited to this style: functions are first-class,
and `map`/`filter`/`reduce` express transformations declaratively. The cost is real,
though — deep immutability and heavy composition can allocate more and obscure control
flow, so apply the style where it pays.

## Core Principles

- **Pure functions have no side effects.** Given the same arguments they return the same
  result and touch nothing outside themselves — no I/O, no mutation, no clock/random.
- **Data is immutable.** Produce new values instead of mutating inputs; callers keep the
  values they passed in.
- **Functions are values.** Pass them, return them, and store them — higher-order
  functions abstract over behavior, not just data.
- **Composition over control flow.** Build complex transforms by chaining small,
  single-purpose functions rather than nesting conditionals.
- **Push side effects to the edges.** Keep the core pure; concentrate I/O, mutation, and
  logging in a thin outer shell where they're easy to see and test.
- **Prefer expressions over statements.** `map`/`filter`/`reduce` and ternaries state
  *what* you want; imperative loops state *how* and hide intent.

## Best Practices

- Write functions that take inputs and return outputs; avoid reading or writing module
  or object state from inside a transform.
- Copy before you change: spread (`{...obj}`, `[...arr]`) or `structuredClone` for deep
  copies; treat function arguments as read-only.
- Use `map`/`filter`/`reduce`/`flatMap` for collection transforms; reach for a plain loop
  only when you need early exit or measured performance.
- Compose with small helpers (`pipe`, `compose`) so data flows left-to-right and each
  step is independently testable.
- Prefer parameters over closures-over-mutable-state; a function that closes over a
  variable that others mutate is not pure.
- Freeze shared constants with `Object.freeze` (note: shallow) to catch accidental
  mutation of configuration in development.
- Do not over-apply: for a single hot numeric loop or a simple mutation local to one
  scope, an imperative version is clearer and faster — the trade-off there favors it.

## Examples

**Good Example** — pure transforms, immutable data, effects at the edge

```js
// Pure: no mutation, deterministic, testable without any setup.
const applyDiscount = (rate) => (item) => ({ ...item, price: item.price * (1 - rate) });
const isInStock = (item) => item.stock > 0;
const sumPrices = (items) => items.reduce((total, i) => total + i.price, 0);

const pipe = (...fns) => (x) => fns.reduce((acc, fn) => fn(acc), x);

const priceInStock = pipe(
  (cart) => cart.filter(isInStock),
  (cart) => cart.map(applyDiscount(0.1)),
  sumPrices,
);

const cart = [{ price: 100, stock: 2 }, { price: 50, stock: 0 }];
const total = priceInStock(cart); // 90
saveInvoice(total);               // the ONLY side effect, at the outer edge
console.log(cart[0].price);       // 100 — original data untouched
```

**Bad Example** — hidden mutation and side effects tangled into the core

```js
let runningTotal = 0;             // shared mutable state → order-dependent, untestable

function processCart(cart) {
  for (const item of cart) {
    if (item.stock > 0) {
      item.price = item.price * 0.9; // MUTATES the caller's data in place
      runningTotal += item.price;    // writes external state as a side effect
      console.log("charged", item);  // I/O buried inside the calculation
    }
  }
  return runningTotal;             // second call returns wrong number (state leaks)
}

const cart = [{ price: 100, stock: 2 }];
processCart(cart);
processCart(cart);                 // double-discounts + wrong total; cart corrupted
```

## Common Mistakes

- Mutating an argument (array `push`/`sort`, object assignment) and surprising the caller.
- Relying on shared module-level state, making results order-dependent and tests flaky.
- Assuming `Object.freeze` is deep — nested objects remain mutable.
- Chaining `map`/`filter`/`map` over huge arrays, creating many intermediate copies where
  one `reduce` or a lazy generator would do.
- Calling a function "pure" while it reads `Date.now()`, `Math.random()`, or a global.
- Over-abstracting with point-free composition until the code is unreadable — clarity wins.

## Production Tips

- `Array.prototype.sort` and `reverse` mutate in place; copy first (`[...arr].sort()`) in
  functional code.
- For large datasets, replace `map().filter().map()` chains with a single `reduce` or a
  lazy generator pipeline to avoid intermediate allocations.
- Reach for a library (Immer, Ramda) only when hand-written immutability becomes the
  bottleneck for readability; native spread/`structuredClone` covers most cases.

## AI Review Checklist

- Do transformation functions avoid mutating their arguments?
- Are side effects (I/O, logging, network) pushed to the edges, out of the core logic?
- Is any function called "pure" actually free of clock/random/global reads?
- Are `map`/`filter`/`reduce` used for transforms, with loops reserved for early exit?
- Is deep immutability handled (spread/clone), not assumed from a shallow `freeze`?
- Is the functional style justified here, versus a clearer imperative version?

## Related

- `knowledge/javascript/04-functions.md`
- `knowledge/javascript/03-scope-and-closures.md`
- `knowledge/javascript/22-design-patterns.md`
- `knowledge/javascript/23-clean-code.md`
- `knowledge/javascript/28-best-practices.md`
