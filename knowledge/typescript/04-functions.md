---
id: typescript/04-functions
topic: typescript
slug: functions
title: "Functions"
type: doc
order: 4
status: ready
tags: [typescript, functions]
related: [typescript/03-type-inference, typescript/08-generics, typescript/17-error-handling, typescript/18-asynchronous-programming]
when_to_use: "Read before writing or reviewing any function signature, callback, or overload."
---
# Functions

## Purpose

This document covers how to type functions well: parameters, return types, optional and
default parameters, overloads, and callbacks. Functions are the contracts of a codebase —
their signatures are what callers depend on — so precise, honest function types matter
more than almost anything else.

A function's signature is its API. TypeScript lets you make that API precise: which
arguments are required, what shapes they take, what comes back, and what can go wrong.
The body is private; the signature is a promise. Keep the promise narrow and truthful.

## Why It Matters

A loose signature (`(...args: any[]) => any`) type-checks everything and protects nothing:
callers pass wrong arguments and find out at runtime. An over-loose return type forces
every caller to guard against cases that can't happen. Because signatures propagate — one
function's return feeds the next's argument — a single sloppy type degrades everything
downstream. Precise signatures are the highest-leverage typing an agent can do.

## Core Principles

- **Annotate parameters and return types at the boundary.** Explicit signatures fix the
  contract and make the function self-documenting (see [03-type-inference](03-type-inference.md)).
- **Prefer narrow parameter types.** Accept the least the function needs. `(user: {id:
  string})` is better than `(user: User)` if only the id is used — it accepts more callers.
- **Prefer specific return types.** Return the most precise type you can. Returning a wide
  type pushes needless narrowing onto every caller.
- **Model failure in the type, not by throwing silently.** Return `T | undefined` or a
  `Result` union when absence/failure is expected (see [17-error-handling](17-error-handling.md)).
- **Keep parameter lists short.** More than ~3 positional params: use an options object,
  which is self-documenting and order-independent.

## Best Practices

- Use default parameters (`x = 0`) over `x?: number` when a sensible default exists — it
  removes the `undefined` case from the body entirely.
- Type callbacks precisely; avoid `Function` and `any`. `(item: T, index: number) => void`
  tells the caller exactly what they receive.
- Use generics to relate input and output types instead of `any`: `identity<T>(x: T): T`
  preserves the caller's type (see [08-generics](08-generics.md)).
- Avoid overloads when a union or generic expresses the same thing more simply; reserve
  overloads for genuinely distinct argument/return shape pairings.
- For async functions, type the resolved value; the compiler wraps it in `Promise<T>`.

## Examples

**Good Example** — narrow inputs, precise return, options object, failure in the type

```ts
interface FetchOpts { retries?: number; timeoutMs?: number }

// Accepts only what it needs (a url + opts); returns the exact success/failure shape.
async function fetchJson<T>(
  url: string,
  { retries = 3, timeoutMs = 5000 }: FetchOpts = {},
): Promise<{ ok: true; data: T } | { ok: false; status: number }> {
  const res = await withTimeout(fetch(url), timeoutMs);
  return res.ok ? { ok: true, data: (await res.json()) as T } : { ok: false, status: res.status };
}
```

**Bad Example** — `any` params, wide return, boolean-blind flags

```ts
// any defeats checking; the return type forces every caller to guard everything.
async function fetchJson(url: any, retries: any, useCache: boolean, parse: boolean): Promise<any> {
  // positional booleans: call sites read fetchJson(u, 3, true, false) — unreadable
  const res = await fetch(url);
  return res.json();
}
```

## Common Mistakes

- Typing parameters or returns as `any`, so the signature protects nothing.
- Long positional parameter lists with booleans, making call sites unreadable and
  order-fragile — use an options object.
- Widening the return type (`Promise<any>`, `object`) and pushing narrowing onto callers.
- Using `x?: T` when a default value would be cleaner and eliminate the `undefined` branch.
- Overusing overloads where a single generic or union signature is clearer.
- Forgetting that an `async` function's declared return is auto-wrapped in `Promise<T>`.

## Production Tips

- Enable `@typescript-eslint/explicit-function-return-type` for exported functions so
  return contracts never drift silently.
- Prefer pure functions (output depends only on input) where practical — they are trivial
  to type, test, and reason about.

## AI Review Checklist

- Do public functions have explicit parameter and return types, both as narrow as possible?
- Are parameters typed to the minimum shape the function actually uses?
- Is expected failure/absence modeled in the return type rather than thrown silently?
- Are there 4+ positional params or boolean flags that should be an options object?
- Are callbacks and generics used instead of `any`/`Function` to relate types?

## Related

- `knowledge/typescript/03-type-inference.md`
- `knowledge/typescript/08-generics.md`
- `knowledge/typescript/17-error-handling.md`
- `knowledge/typescript/18-asynchronous-programming.md`
