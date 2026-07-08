---
id: typescript/17-error-handling
topic: typescript
slug: error-handling
title: "Error Handling"
type: doc
order: 17
status: ready
tags: [typescript, error-handling]
related: [typescript/12-type-guards, typescript/18-asynchronous-programming, typescript/11-unions-and-intersections, typescript/16-configuration]
when_to_use: "Read before writing a `try/catch`, typing a `catch` binding, or designing how a function reports failure."
---
# Error Handling

## Purpose

This document defines how to represent, propagate, and handle failure in TypeScript: typing
the `catch` binding (which is `unknown`), throwing proper `Error` objects, modeling expected
failures as values (a `Result`/discriminated union) versus throwing for the unexpected, and
handling errors correctly in async code.

The central TypeScript-specific fact: in a `catch (e)` block, `e` has type `unknown`. Anything
can be thrown — a string, `undefined`, a rejected non-`Error`. You must narrow before you can
touch it. Everything else follows from taking that seriously.

## Why It Matters

Swallowed and mistyped errors are among the most damaging bugs because they are *silent*: a
caught-and-ignored exception turns a hard failure into corrupted state that surfaces later,
somewhere unrelated. Assuming `e` is an `Error` and reading `e.message` throws a *second*
error when someone threw a string, masking the first. Conflating expected failures ("user not
found") with bugs ("null pointer") means callers cannot tell a normal outcome from a crash, so
they handle neither well. In async code, a missing `await` or an unhandled rejection escapes
every `try/catch` around it. Good error handling is what separates a system that degrades
gracefully from one that fails in confusing, unrecoverable ways.

## Core Principles

- **`catch` bindings are `unknown` — narrow before use.** Never assume the caught value is an
  `Error`; check with `instanceof` (or a guard) first.
- **Throw `Error` instances, never strings or plain objects.** Only `Error` carries a stack
  trace; throwing a string loses it and breaks every `instanceof` check downstream.
- **Model expected failures as values; throw for the unexpected.** A known outcome (validation
  failed, not found) belongs in a return type the caller must handle; reserve exceptions for
  truly exceptional bugs.
- **Never swallow an error.** Catching without handling, logging, or rethrowing hides bugs.
  Handle it, or let it propagate.
- **Preserve context when rethrowing.** Wrap with `new Error(msg, { cause: e })` so the
  original stack and message survive.

## Best Practices

- Type-check the catch binding: `if (e instanceof Error) { ... }` or a normalizing helper that
  returns a real `Error` for any thrown value.
- Define custom error classes (`class NotFoundError extends Error`) with a stable `name`, and
  set `this.name` in the constructor so logs and `instanceof` both work.
- Use `Error`'s `cause` option (`throw new Error("load failed", { cause: e })`) to chain
  errors without discarding the original.
- For operations that fail routinely and expectedly, return a discriminated `Result`
  (`{ ok: true; value } | { ok: false; error }`) so the compiler forces the caller to handle
  both branches.
- Always `await` (or `.catch`) every promise. Set `tsconfig` `"noUnhandledRejections"` tooling
  / lint rules and enable Node's `--unhandled-rejections=strict` so an escaped rejection is
  fatal in dev, not ignored.
- Catch at the level that can actually recover or add context; do not wrap every call in its
  own `try/catch`. Let a top-level boundary log and translate to a user-facing response.
- Never expose raw error messages or stack traces to end users or API responses; log them,
  return a safe generic message.

## Examples

**Good Example** — narrowed catch, typed failure as a value

```ts
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

async function loadConfig(path: string): Promise<Result<Config>> {
  try {
    const raw = await fs.readFile(path, "utf8"); // awaited: rejection is caught here
    return { ok: true, value: parseConfig(raw) };
  } catch (e) {
    // `e` is `unknown` — narrow before reading any property.
    const message = e instanceof Error ? e.message : String(e);
    return { ok: false, error: `config load failed: ${message}` }; // expected failure as a value
  }
}

const r = await loadConfig("./app.json");
if (!r.ok) return exitWith(r.error); // compiler forces this branch before r.value is reachable
use(r.value);
```

**Bad Example** — assumes `Error`, swallows, drops the async rejection

```ts
function loadConfig(path: string) {
  try {
    const raw = fs.readFile(path, "utf8"); // returns a Promise, never awaited → escapes try/catch
    return parseConfig(raw as any);        // `as any` hides that raw is a Promise, not a string
  } catch (e) {
    console.log(e.message);                // `e` is unknown; if a string was thrown this throws again
    // no rethrow, no return → caller gets `undefined` and a corrupted-state bug later
  }
}
```

## Common Mistakes

- Reading `e.message` / `e.stack` without an `instanceof Error` check — crashes when a non-Error
  is thrown.
- Throwing strings or plain objects, losing the stack trace and breaking `instanceof`.
- Empty or log-only `catch` blocks that swallow the failure and let execution continue in a
  bad state.
- Forgetting `await`, so the rejection escapes the surrounding `try/catch` and becomes an
  unhandled rejection.
- Using exceptions for ordinary control flow (expected "not found"), forcing callers to guess
  which throws are normal.
- Rethrowing a new error without `cause`, discarding the original stack and root cause.
- Leaking internal error details (stack traces, DB messages) to API clients.

## Production Tips

- Centralize error handling at boundaries: one middleware/handler that logs the full error and
  maps it to a safe status/message, so individual handlers stay clean.
- Give each domain error a stable `name` and, where useful, a machine-readable `code`; log
  structured fields, not just a string, so alerts can match on them.
- Run Node with `--unhandled-rejections=strict` in dev/test so an unawaited failing promise
  fails loudly instead of hiding.

## AI Review Checklist

- Is every `catch` binding narrowed (`instanceof Error` or a guard) before its properties are
  used?
- Are only `Error` instances thrown, never strings or plain objects?
- Are expected failures modeled as return values (`Result`/union) rather than exceptions?
- Is every promise `await`ed or `.catch`ed, with no escaped rejections?
- Are errors rethrown with `cause` to preserve the original stack?
- Are internal error details kept out of user-facing/API responses?

## Related

- `knowledge/typescript/12-type-guards.md`
- `knowledge/typescript/18-asynchronous-programming.md`
- `knowledge/typescript/11-unions-and-intersections.md`
- `knowledge/typescript/16-configuration.md`
