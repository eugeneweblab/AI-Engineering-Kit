---
id: javascript/30-engineering-principles
topic: javascript
slug: engineering-principles
title: "JavaScript Engineering Principles"
type: doc
order: 30
status: ready
tags: [javascript, engineering-principles]
related: [javascript/23-clean-code, javascript/14-error-handling, javascript/08-asynchronous-javascript, javascript/28-best-practices, javascript/24-testing]
when_to_use: "Read before making a JavaScript design decision or reviewing code for long-term maintainability."
---
# JavaScript Engineering Principles

## Purpose

This document defines the engineering principles that separate JavaScript code that
merely runs from JavaScript code that survives in production. It is not a style guide
(see [clean code](23-clean-code.md)) and not a language reference (see
[language fundamentals](01-language-fundamentals.md)); it is the set of reasoning rules
an agent applies when choosing *how* to structure logic, handle failure, and manage
state. Follow these when a decision has more than one plausible answer.

## Why It Matters

JavaScript gives you enormous freedom — dynamic typing, mutable objects, implicit
coercion, and asynchrony everywhere. That freedom is why the same feature can be written
ten ways, nine of which will break under load, refactoring, or an unexpected input.
Principles are the constraint that makes the tenth choice automatic. Code written without
them works on the happy path in the author's browser and fails silently in production:
a rejected promise nobody caught, a shared object mutated across requests, a `==`
comparison that coerced a `0` into `false`. Principles pay for themselves the first time
someone else — or the author six months later — has to change the code without re-reading
all of it.

## Core Principles

- **Make the implicit explicit.** JavaScript will coerce, hoist, and default silently.
  Use `===`, declare variables where they are used, and name your data shapes. Ambiguity
  the language tolerates is a bug the reader will not see.
- **Prefer immutability; isolate the mutation you keep.** Treat function inputs as
  read-only. Shared mutable state is the root cause of the hardest JavaScript bugs
  because the mutation and the symptom are far apart in time and code.
- **Every async operation can fail — model the failure.** A promise is a value that may
  reject. Unhandled rejection is not an edge case; it is the default outcome of ignoring
  it. Handle or propagate, never swallow.
- **Push side effects to the edges.** Keep the core of a module pure — input to output,
  no I/O, no globals. Effects (network, DOM, storage, time) belong in a thin, testable
  outer layer.
- **Fail loud in development, degrade safely in production.** A thrown error you can see
  in a test is worth ten silent `catch {}` blocks that hide the bug from you and leak it
  to the user.
- **Design for the reader, optimize for the profiler.** Write the clear version first.
  Only trade clarity for speed against a measured [performance](25-performance.md) number,
  never a guess.

## Best Practices

- Use `const` by default, `let` when reassignment is real, never `var`. The declaration
  keyword communicates intent to the next reader before they read the body.
- Return early to keep the happy path flat. Deep nesting hides the one branch that
  matters.
- Keep functions single-purpose and small enough to hold in your head. If you cannot name
  it precisely, it does too much.
- Prefer pure functions and pass dependencies in as arguments so behavior is testable
  without mocks of globals like `Date`, `fetch`, or `window`.
- Use `async`/`await` over raw `.then()` chains for sequential logic, and `Promise.all`
  for independent work you want to run concurrently — do not `await` in a loop when the
  iterations are independent.
- Validate data at the boundary (API responses, user input, `JSON.parse`). Inside the
  trusted core, assume the shape is correct so you are not defensively checking everywhere.
- Throw `Error` objects (or subclasses), never strings — stack traces and `instanceof`
  checks depend on it. See [error handling](14-error-handling.md).

## Examples

**Good Example** — pure core, explicit failure, effects at the edge

```js
// Pure: no I/O, no shared state — trivially testable, safely reusable.
function nextRetryDelay(attempt, baseMs = 200) {
  return Math.min(baseMs * 2 ** attempt, 10_000); // explicit cap, no magic surprises
}

// Effectful edge: the only place that touches the network and time.
async function fetchWithRetry(url, maxAttempts = 3) {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`); // fetch does NOT reject on 4xx/5xx
      return await res.json();
    } catch (err) {
      if (attempt === maxAttempts - 1) throw err;         // last try: propagate, do not swallow
      await sleep(nextRetryDelay(attempt));
    }
  }
}
```

**Bad Example** — hidden mutation, swallowed failure, coercion trap

```js
const defaults = { retries: 3, tags: [] };

function configure(overrides) {
  Object.assign(defaults, overrides); // mutates the shared default for EVERY future caller
  return defaults;
}

async function load(url) {
  try {
    const res = await fetch(url);
    if (res.status == "200") return res.json(); // "200" coercion + only one status handled
  } catch {
    return null; // swallows the error: the caller cannot tell "empty" from "broken"
  }
}
```

## Common Mistakes

- Mutating a function argument or a module-level object, then debugging a symptom that
  appears three modules away.
- Using `==` and letting `0`, `""`, `null`, and `undefined` coerce into the wrong branch.
- `await`-ing inside a `for` loop for independent requests, turning parallel work into a
  serial waterfall.
- `catch {}` (or `catch (e) { console.log(e) }`) that hides a failure instead of handling
  or rethrowing it.
- Assuming `fetch` rejects on `404`/`500` — it only rejects on network failure; you must
  check `res.ok`.
- Reaching for globals (`window`, `Date.now`, `localStorage`) inside core logic, making
  it impossible to test deterministically.

## Production Tips

- Enable a linter (ESLint) with `no-floating-promises` / `no-misused-promises` (via
  `@typescript-eslint` or `eslint-plugin-promise`) so unhandled async is a build error,
  not a production incident.
- Add a global `unhandledrejection` (browser) / `unhandledRejection` (Node) handler that
  reports to your error tracker — it is the safety net, not the design.
- Freeze true constants with `Object.freeze` so accidental mutation throws in strict mode
  instead of silently corrupting shared state.

## AI Review Checklist

- Are function inputs treated as read-only, with no mutation of arguments or shared
  module state?
- Is every `await` / promise either handled or deliberately propagated — no swallowed
  `catch`?
- Are independent async operations run concurrently with `Promise.all` rather than in a
  serial loop?
- Is `===` used everywhere, with no reliance on implicit coercion?
- Is core logic free of I/O and globals, with side effects isolated at the edges?
- Are errors thrown as `Error` objects and `fetch` responses checked with `res.ok`?

## Related

- `knowledge/javascript/23-clean-code.md`
- `knowledge/javascript/14-error-handling.md`
- `knowledge/javascript/08-asynchronous-javascript.md`
- `knowledge/javascript/28-best-practices.md`
- `knowledge/javascript/24-testing.md`
