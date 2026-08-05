---
id: javascript/18-iterators-and-generators
topic: javascript
slug: iterators-and-generators
title: "Iterators And Generators"
type: doc
order: 18
status: ready
tags: [javascript, iterators-and-generators, for...of, take, yield, constructor, close, TypeError]
related: [javascript/17-es6-features, javascript/09-promises, javascript/08-asynchronous-javascript, javascript/15-memory-management, javascript/19-symbols]
when_to_use: "Read before building custom iterable data structures, lazy sequences, or streaming/async pipelines."
---
# Iterators And Generators

## Purpose

This document defines how to produce and consume sequences in JavaScript using the
**iteration protocols**, **generator functions** (`function*`), and their async
counterparts (`async function*`). It covers how `for...of`, spread, and destructuring
find values, and how to expose a data structure as iterable without materializing every
element up front.

An *iterator* is any object with a `next()` method returning `{ value, done }`. An
*iterable* is any object with a `[Symbol.iterator]()` method that returns an iterator.
Generators are the ergonomic way to author both.

## Why It Matters

Iterators are the contract behind `for...of`, `...spread`, `Array.from`, destructuring,
`Map`/`Set` construction, and `Promise.all`. Getting the protocol right makes your type
work everywhere those features do; getting it wrong produces silent `undefined` or an
"is not iterable" `TypeError`. Generators also enable **lazy evaluation** — computing
values on demand instead of building a full array — which is the difference between
streaming a million-row file and running out of memory. Because iteration is pull-based,
it composes: a generator can wrap another generator with near-zero overhead.

## Core Principles

- **Iterable vs iterator are different roles.** An iterable *produces* iterators;
  an iterator *is consumed once*. Keep them separate so one collection supports many
  concurrent `for...of` loops.
- **Iterators are single-use and stateful.** Once `done: true`, an iterator stays
  exhausted. Never share one iterator across two consumers.
- **`return` and `throw` are part of the protocol.** A well-behaved iterator releases
  resources in a `return()` method so early `break` still runs cleanup.
- **Generators pause and resume.** Execution suspends at each `yield` and resumes on the
  next `next()`, preserving local state — no manual index bookkeeping.
- **`yield*` delegates.** It forwards iteration to another iterable and returns that
  inner generator's final value, enabling composition and recursion.
- **Laziness is the point.** Prefer generators when the sequence is large, infinite, or
  expensive so callers pay only for what they consume.

## Best Practices

- Make a data structure iterable by defining `[Symbol.iterator]()` as a generator method
  — it is the shortest correct implementation and handles `done` for you.
- Return a *fresh* iterator from `[Symbol.iterator]()` on every call so the collection is
  re-iterable; never `return this` from a stateful iterator.
- Use `async function*` and `for await...of` for sources that yield over time (paginated
  APIs, streams). Do not fake async iteration by resolving arrays of promises.
- Free resources in `finally` inside a generator — it runs on exhaustion, `break`,
  `return()`, and thrown errors, so file handles and cursors always close.
- Guard against infinite generators at the consumer with a `take(n)` helper; never
  `[...infiniteGen]` or `Array.from(infiniteGen)`.
- Reach for the native protocol before a library. `for...of` + generators cover most
  lazy-pipeline needs without a dependency.

## Examples

**Good Example** — re-iterable collection and a lazy, resource-safe pipeline

```js
class Range {
  constructor(start, end) { this.start = start; this.end = end; }

  // A fresh generator per call → the range can be iterated many times.
  *[Symbol.iterator]() {
    for (let i = this.start; i < this.end; i++) yield i;
  }
}

// Lazy: nothing runs until the consumer pulls. Composes by delegation.
function* map(iterable, fn) {
  for (const x of iterable) yield fn(x);
}
function* take(iterable, n) {
  if (n <= 0) return;
  let i = 0;
  for (const x of iterable) { yield x; if (++i >= n) return; }
}

const r = new Range(0, 1_000_000);
console.log([...take(map(r, x => x * x), 3)]); // [0, 1, 4] — only 3 squares computed
console.log([...r]);                            // [0..] works again: fresh iterator

// Async source with guaranteed cleanup on early break.
async function* readPages(client) {
  let cursor = null;
  try {
    do {
      const page = await client.fetch(cursor);
      yield* page.items;      // delegate: yield each item, not the page
      cursor = page.next;
    } while (cursor);
  } finally {
    await client.close();     // runs even if the consumer breaks early
  }
}
```

**Bad Example** — single-use "iterable", eager work, leaked resources

```js
class Range {
  constructor(start, end) { this.i = start; this.end = end; }
  // Returns `this`: the object IS its own iterator, so it exhausts permanently.
  [Symbol.iterator]() { return this; }
  next() {
    return this.i < this.end
      ? { value: this.i++, done: false }
      : { value: undefined, done: true };
  }
}
const r = new Range(0, 3);
[...r];            // [0, 1, 2]
[...r];            // [] — already exhausted, silent wrong answer

function squaresUpTo(n) {
  const out = [];
  for (let i = 0; i < n; i++) out.push(i * i); // eager: builds whole array in memory
  return out;
}
squaresUpTo(1e9);  // OOM even though the caller only wanted the first few
```

## Common Mistakes

- Returning `this` from `[Symbol.iterator]()` on a stateful object, making it single-use.
- Sharing one iterator between two loops and getting interleaved or empty results.
- Spreading or `Array.from`-ing an infinite/large generator, hanging or exhausting memory.
- Forgetting `try/finally` in a generator that holds a cursor, socket, or file handle.
- Using a plain `function` and manual `{ value, done }` where a `function*` is simpler
  and less error-prone.
- Mixing async and sync protocols — a normal generator that `yield`s promises is not an
  async iterator and won't work with `for await...of` correctly.

## Production Tips

- For streaming transforms, generators beat accumulating arrays: constant memory,
  early termination, and backpressure via the async protocol.
- Node streams are async iterables — `for await (const chunk of readable)` is the modern,
  cleaner alternative to `data`/`end` event handlers.
- Profile before optimizing: generator call overhead is small but nonzero; for tight
  numeric loops over a fixed array, a plain `for` loop can be faster.

## AI Review Checklist

- Does `[Symbol.iterator]()` return a *fresh* iterator so the value is re-iterable?
- Are iterator objects never shared across concurrent consumers?
- Do generators holding resources clean up in a `finally` block?
- Is any potentially infinite generator bounded by `take`/`break` at the consumer?
- Are time-based sources implemented as `async function*` consumed with `for await...of`?
- Is `yield*` used to delegate instead of manually re-yielding a nested loop?

## Related

- `knowledge/javascript/17-es6-features.md`
- `knowledge/javascript/09-promises.md`
- `knowledge/javascript/08-asynchronous-javascript.md`
- `knowledge/javascript/15-memory-management.md`
- `knowledge/javascript/19-symbols.md`
