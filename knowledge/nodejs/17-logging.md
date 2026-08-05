---
id: nodejs/17-logging
topic: nodejs
slug: logging
title: "Node.js Logging"
type: doc
order: 17
status: ready
tags: [nodejs, logging]
related: [nodejs/16-error-handling, nodejs/27-monitoring, nodejs/18-security, nodejs/14-environment, nodejs/26-deployment]
when_to_use: "Read before adding logging to a service or reviewing what and how an app logs."
---
# Node.js Logging

## Purpose

This document defines how to log in a Node.js service: structured output, log levels,
correlation across requests, and what must never appear in a log. Logs are the primary way you
understand a running system after the fact, so this doc treats logging as a first-class
production concern, not a debugging afterthought.

Logging records *what happened*; [error handling](16-error-handling.md) decides *what to do*
about it; [monitoring](27-monitoring.md) aggregates and alerts on the result. This doc covers
the first.

## Why It Matters

In production you cannot attach a debugger — logs are your only window into what the process
did. Unstructured `console.log` lines are unqueryable at scale: when an incident hits and you
need "every error for request X in the last hour," free-text strings across thousands of pods
are useless. Structured, leveled, correlated logs turn that same question into a one-line
query. Just as important, logs are a security surface: one careless line that prints a password
or token leaks it into every log sink, backup, and third-party aggregator forever.

## Core Principles

- **Log structured JSON, not string concatenation.** Machine-parseable key/value objects are
  queryable and filterable; interpolated strings are not.
- **Use a real logger, not `console.log`.** `console.*` is synchronous and can block the
  [event loop](02-event-loop.md) under load. Use `pino` (or `winston`) with async transports.
- **Use levels deliberately.** `error` (needs attention), `warn` (suspicious, handled),
  `info` (business events), `debug` (developer detail, off in prod). The level is a filter, not
  decoration.
- **Correlate everything.** Attach a request/trace id to every log line for a request so you can
  reconstruct one request's full path across services.
- **Never log secrets or PII.** Passwords, tokens, API keys, card numbers, and personal data
  never go to logs — redact at the logger boundary, not case by case.
- **Log to stdout/stderr; let the platform route.** A twelve-factor process does not manage log
  files, rotation, or shipping — the container/platform does.

## Best Practices

- Configure a **single logger instance** with a base context (service name, version, env) and
  create **child loggers** per request that bind the request id.
- Set the **level from configuration** (`LOG_LEVEL`), defaulting to `info` in production and
  `debug` in development. See [environment](14-environment.md).
- Use **automatic redaction** (pino's `redact` paths) for known-sensitive fields so a new call
  site cannot accidentally leak them.
- Log **errors as objects** (`logger.error({ err })`), not `err.message` — you want the stack,
  name, and cause, which structured serializers preserve.
- Emit **JSON in production** and pretty-printed logs only in local development; never pretty-
  print in prod (it is slower and breaks parsers).
- Keep log volume proportional to value: do not log every successful health check at `info`, and
  do not put high-cardinality data in messages when it belongs in fields.

## Examples

**Good Example** — structured, leveled, correlated, redacted

```js
import pino from "pino";

const logger = pino({
  level: config.logLevel, // driven by env, not hardcoded
  redact: ["req.headers.authorization", "*.password", "*.token"], // secrets never printed
  base: { service: "api", version: config.version },
});

app.use((req, res, next) => {
  // Child logger binds a request id so every line for this request is correlatable.
  req.log = logger.child({ reqId: req.id });
  next();
});

app.post("/users", async (req, res) => {
  req.log.info({ email: req.body.email }, "creating user"); // structured fields, no password
  try {
    const user = await createUser(req.body);
    req.log.info({ userId: user.id }, "user created");
    res.json(user);
  } catch (err) {
    req.log.error({ err }, "create user failed"); // full error object → stack preserved
    res.status(500).json({ error: "internal error", reqId: req.id });
  }
});
```

**Bad Example** — unstructured, synchronous, leaky

```js
app.post("/users", async (req, res) => {
  // console.log is sync (can block under load) and unqueryable free text.
  console.log("creating user " + JSON.stringify(req.body)); // logs the raw PASSWORD
  try {
    const user = await createUser(req.body);
    console.log("done"); // no id, no context: impossible to correlate later
    res.json(user);
  } catch (err) {
    console.log("error: " + err.message); // stack and error type discarded
    res.status(500).json({ error: err.message }); // leaks internals to the client
  }
});
```

## Common Mistakes

- Logging passwords, tokens, or full request bodies, leaking secrets into every sink.
- Using `console.log`, which is synchronous and produces unstructured, unqueryable output.
- Logging `err.message` instead of the error object, losing the stack and cause.
- No request/correlation id, making it impossible to trace one request across services.
- Hardcoding the log level instead of driving it from configuration.
- Writing and rotating log files inside the app instead of logging to stdout.
- Pretty-printing JSON in production, slowing the app and breaking log parsers.

## Production Tips

- Ship stdout JSON to a central platform (Loki, ELK, Datadog) and build alerts on `error`-level
  rates in [monitoring](27-monitoring.md).
- Propagate the correlation id via a header (e.g. `traceparent`/`x-request-id`) so it spans
  service boundaries.
- Sample high-volume `debug`/`info` logs under load to control cost without losing `error`s.
- Flush logs on shutdown so the last lines before a crash are not lost.

## AI Review Checklist

- Is logging structured JSON via a real logger, not `console.log`?
- Is every request correlated with a request/trace id via a child logger?
- Are secrets and PII redacted at the logger boundary, never printed?
- Are errors logged as objects so the stack and cause survive?
- Is the log level driven by configuration, with `info` default in production?
- Does the app log to stdout and leave routing/rotation to the platform?

## Related

- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/27-monitoring.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/14-environment.md`
- `knowledge/nodejs/26-deployment.md`
