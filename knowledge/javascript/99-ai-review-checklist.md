---
id: javascript/99-ai-review-checklist
topic: javascript
slug: ai-review-checklist
title: "JavaScript AI Review Checklist"
type: doc
order: 99
status: ready
tags: [javascript, ai-review-checklist, res.ok, innerHTML, parseInt, document.write, JSON.parse]
related: [javascript/30-engineering-principles, javascript/100-common-antipatterns, javascript/14-error-handling, javascript/26-security, javascript/23-clean-code]
when_to_use: "Read when reviewing JavaScript code — human-written or AI-generated — before approval."
---
# JavaScript AI Review Checklist

## Purpose

This is the review pass an agent runs over JavaScript before approving it. Each item is a
concrete question with a yes/no answer that can be verified by reading the diff. It
targets the mistakes JavaScript's flexibility invites and that AI-generated code
reproduces most often: silent coercion, unhandled async, mutation of shared state, and
unsafe DOM writes. Treat any "no" as a change request, not a suggestion.

## Why It Matters

Code that passes tests can still be wrong in ways tests do not catch: a swallowed
rejection that only fires under load, an `==` that coerces the wrong value, an
`innerHTML` sink that is fine until user data reaches it. AI-generated JavaScript is
especially prone to plausible-but-unsafe patterns because it optimizes for "looks like
working code." A structured review catches these before they become production incidents.
Reviewing against a fixed list also makes the review reproducible instead of dependent on
whatever the reviewer happened to notice.

## Correctness

**Rules:** [Language Fundamentals](01-language-fundamentals.md) · [This Keyword](16-this-keyword.md)

- [ ] Are all equality comparisons `===` / `!==`, with no reliance on `==` coercion?
- [ ] Are variables declared with `const`/`let` (never `var`), scoped where used?
- [ ] Does every `fetch`/network call check `res.ok` before reading the body?
- [ ] Are number parses (`parseInt`, `Number`) validated for `NaN` before use?
- [ ] Are array/object accesses guarded against `undefined` (optional chaining, defaults)
      where the shape is not guaranteed?

## Async and Concurrency

**Rules:** [Asynchronous JavaScript](08-asynchronous-javascript.md) · [Promises](09-promises.md)

- [ ] Is every promise awaited or its rejection otherwise handled — no floating promises?
- [ ] Are independent async calls parallelized with `Promise.all` instead of serial
      `await` in a loop?
- [ ] Do `catch` blocks handle or rethrow, never swallow silently?
- [ ] Are `async` functions passed to array methods like `forEach` avoided (their
      returned promises are dropped)?

## State and Data

**Rules:** [Objects And Prototypes](05-objects-and-prototypes.md) · [Memory Management](15-memory-management.md)

- [ ] Are function arguments and shared/module-level objects treated as immutable?
- [ ] Is external data (API responses, `JSON.parse`, user input) validated at the
      boundary before use?
- [ ] Are there no accidental global variables (missing declaration, leaked `this`)?

## Security

**Rules:** [Security](26-security.md)

- [ ] Is user-controlled data kept out of `innerHTML`, `eval`, `new Function`, and
      `document.write`?
- [ ] Are secrets and tokens absent from client code and not logged?
- [ ] Are auth tokens in `HttpOnly` cookies rather than `localStorage`?

## Errors and Robustness

**Rules:** [Error Handling](14-error-handling.md)

- [ ] Are thrown values `Error` objects with useful messages, not strings?
- [ ] Are failure paths (not just the happy path) tested?
- [ ] Do error messages avoid leaking internal details (stack traces, queries) to users?

## Clarity

**Rules:** [Clean Code](23-clean-code.md) · [Best Practices](28-best-practices.md)

- [ ] Are functions single-purpose and named for what they do?
- [ ] Is the happy path flat (early returns) rather than deeply nested?
- [ ] Are there no commented-out blocks, dead code, or leftover `console.log`?

## AI Review Checklist

- Did you check every async operation for an unhandled rejection?
- Did you confirm no shared or argument state is mutated?
- Did you verify no user data reaches an HTML/JS sink?
- Did you confirm `===` and `res.ok` are used consistently?
- Did you check that failure paths are tested, not just success?

## Related

- `knowledge/javascript/30-engineering-principles.md`
- `knowledge/javascript/100-common-antipatterns.md`
- `knowledge/javascript/14-error-handling.md`
- `knowledge/javascript/26-security.md`
- `knowledge/javascript/23-clean-code.md`
