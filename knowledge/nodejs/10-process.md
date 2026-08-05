---
id: nodejs/10-process
topic: nodejs
slug: process
title: "Process"
type: doc
order: 10
status: ready
tags: [nodejs, process, process.env, uncaughtException, SIGTERM, unhandledRejection, shutdown, SIGKILL]
related: [nodejs/14-environment, nodejs/16-error-handling, nodejs/26-deployment, nodejs/11-child-process, nodejs/17-logging]
when_to_use: "Read before reading env vars, handling signals, setting exit codes, or catching unhandled errors at the process level."
---
# Process

## Purpose

This document defines how to use the global `process` object correctly: reading
configuration from the environment, handling termination signals, exiting with meaningful
codes, and catching top-level failures (`uncaughtException`, `unhandledRejection`). It is
written so an agent can make a Node process behave predictably under orchestration
(systemd, Docker, Kubernetes) and during deploys.

`process` is the boundary between your code and the operating system. How you treat exit
codes, signals, and env vars determines whether your service restarts cleanly or corrupts
state on the way down.

## Why It Matters

Orchestrators speak in signals and exit codes. A container that ignores `SIGTERM` gets
`SIGKILL`ed after a grace period, dropping in-flight work and connections on every deploy.
A process that exits `0` after a fatal error tells the supervisor "all good" and is never
restarted. And the most dangerous anti-pattern — swallowing `uncaughtException` and
continuing — leaves the process in a corrupted, half-initialized state that produces wrong
results silently. The process boundary is where "it works on my machine" meets production
reality; getting it wrong makes the whole service unreliable regardless of code quality.

## Core Principles

- **Read and validate env at startup, once.** Parse `process.env` into a typed, validated
  config object when the process boots and fail fast if required values are missing —
  do not read `process.env` scattered through the codebase at call time.
- **Handle `SIGTERM` for graceful shutdown.** `SIGTERM` is the orchestrator's "please stop"
  — drain work, close resources, then exit. Ignoring it costs you a `SIGKILL`.
- **Exit codes carry meaning.** Exit `0` for success, non-zero for failure. Supervisors and
  CI branch on this. Never exit `0` from an error path.
- **`uncaughtException`/`unhandledRejection` are for logging then exiting, not recovery.**
  After one fires, the process state is unknown. Log it, then let the process exit so a
  supervisor restarts it clean.
- **`process.env` values are always strings (or `undefined`).** Coerce and validate types
  explicitly; `process.env.PORT` is `"3000"`, not `3000`.

## Best Practices

- Centralize config: one module reads `process.env`, validates it (Zod/`envalid` or a hand-
  written schema), and exports typed values. Everything else imports from there.
- On `SIGTERM` (and `SIGINT` for local dev), run a single idempotent shutdown routine: stop
  accepting work, finish in-flight, close DB/pool/servers, then `process.exit()` after a
  hard-timeout fallback.
- Register `uncaughtException` and `unhandledRejection` handlers that log with full context
  and then exit non-zero; combine with a supervisor that restarts.
- Use `process.exitCode = n` and let the event loop drain, rather than `process.exit(n)`
  which truncates pending I/O (e.g. unflushed logs).
- Never mutate `process.env` at runtime to pass data between modules; use normal imports or
  a config object.
- Read secrets from the environment or a secrets manager, never hard-code them; keep them
  out of logs and error messages.

## Examples

**Good Example** — validated config, graceful shutdown, fail-fast on fatal errors

```js
// config.js — read and validate once, fail fast
function required(name) {
  const v = process.env[name];
  if (!v) throw new Error(`Missing required env var: ${name}`);
  return v;
}
export const config = {
  port: Number(process.env.PORT ?? 3000), // coerce: env values are strings
  databaseUrl: required("DATABASE_URL"),  // crash at boot if absent, not at first query
};

// server.js
let shuttingDown = false;
function shutdown(server) {
  if (shuttingDown) return;               // idempotent: SIGTERM may fire once, SIGINT after
  shuttingDown = true;
  server.close(() => process.exit(0));    // drain, then success exit
  setTimeout(() => process.exit(1), 10_000).unref(); // hard cap so a stuck request can't block
}
process.on("SIGTERM", () => shutdown(server));
process.on("uncaughtException", (err) => {
  logger.fatal(err);                      // log with context...
  process.exit(1);                        // ...then exit; state is untrustworthy now
});
```

**Bad Example** — scattered env reads, swallowed fatal errors, wrong exit code

```js
function handler() {
  const port = process.env.PORT;          // string, read at call time, unvalidated
  connect(process.env.DATABASE_URL);      // undefined at runtime → confusing failure later
}

process.on("uncaughtException", (err) => {
  console.log("ignoring", err);           // process now in unknown/corrupt state, keeps serving
});
// No SIGTERM handler → orchestrator SIGKILLs after grace period, dropping in-flight work.
process.exit(0);                          // exits 0 even on failure → never restarted
```

## Common Mistakes

- Reading `process.env` throughout the code at call time instead of validating once at
  startup, so a missing var surfaces as a cryptic runtime error.
- Forgetting `process.env` values are strings, then doing string math or truthy checks that
  misbehave (`"false"` is truthy).
- No `SIGTERM` handler, so every deploy `SIGKILL`s the process and drops in-flight requests.
- Swallowing `uncaughtException`/`unhandledRejection` and continuing to run in a corrupt
  state.
- Calling `process.exit()` immediately, truncating unflushed logs and pending writes.
- Exiting `0` from an error path, so supervisors and CI think it succeeded.

## Production Tips

- Prefer `process.exitCode = n` plus a natural event-loop drain over `process.exit(n)` so
  logs and metrics flush; reserve immediate `exit` for the shutdown hard-timeout.
- Make the shutdown routine idempotent and guarded — `SIGTERM` then `SIGINT`, or a double
  signal, must not run it twice.
- Load env from a secrets manager or orchestrator-injected variables; do not bake `.env`
  files into images or commit them.

## AI Review Checklist

- Is `process.env` read and validated once at startup into a typed config, not scattered?
- Are env values explicitly coerced from strings to the types the code expects?
- Is there a `SIGTERM` handler that drains work and exits, with a hard-timeout fallback?
- Do `uncaughtException`/`unhandledRejection` handlers log and then exit non-zero (not
  swallow)?
- Do error paths exit non-zero and success paths exit `0`?
- Are secrets read from the environment/secrets manager and kept out of logs?

## Related

- `knowledge/nodejs/14-environment.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/26-deployment.md`
- `knowledge/nodejs/11-child-process.md`
- `knowledge/nodejs/17-logging.md`
