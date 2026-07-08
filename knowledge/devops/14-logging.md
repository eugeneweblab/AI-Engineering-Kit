---
id: devops/14-logging
topic: devops
slug: logging
title: "Logging"
type: doc
order: 14
status: ready
tags: [devops, logging]
related: [devops/13-observability, devops/12-monitoring, devops/15-alerting, devops/16-security, devops/25-incident-management]
when_to_use: "Read before adding, changing, or reviewing any log statement, or when designing a service's log format and pipeline."
---
# Logging

## Purpose

This document defines how to emit logs that are useful during an incident and safe in
production: what to log, what to never log, and how to structure a line so a machine can
query it. It is written so an agent writes logs that answer "why did this request fail?"
in seconds — not logs that leak secrets, cost a fortune, or say nothing.

Logs are the *why* signal in [observability](13-observability.md): the narrative detail
behind a metric spike or a broken [trace](13-observability.md). They are not a metrics
system (do not count things by grepping logs) and they are not an audit trail unless
built to be one.

## Why It Matters

At 3 a.m. during an outage, logs are often the only record of what a specific request
actually did. If they are unstructured, uncorrelated, or missing the failing case, the
incident stretches for hours. But logging is a double-edged tool: log too much and you
bury the signal and blow the budget; log the wrong field and you write a password,
token, or customer PII into a system that fans it out to third parties and retains it
for years. A single `console.log(user)` can become a compliance breach. Logs are
production code and are held to the same review bar — including "is it safe to write
this?".

## Core Principles

- **Structured, not stringly.** Emit **JSON** (or another machine-parseable format), one
  event per line, with fields — never interpolate values into a prose sentence. The cost
  of prose is that no one can query it under pressure.
- **Never log secrets or PII.** Passwords, tokens, keys, full card numbers, and personal
  data must never reach a log. This is not a style rule; it is a security boundary — see
  [security](16-security.md).
- **Correlate everything.** Every line carries the **trace ID** and **request ID** so a
  single request's story can be reassembled across services and pivoted to its trace.
- **Log levels mean something.** ERROR = a human must look; WARN = degraded but handled;
  INFO = business events; DEBUG = diagnostics. Reserve ERROR for actionable failures or
  it becomes noise.
- **Logs are append-only facts, not control flow.** Never make behavior depend on a log
  call, and never let a logging failure break the request.

## Best Practices

- Emit **structured JSON** with a stable schema: `timestamp`, `level`, `message`,
  `service`, `trace_id`, `request_id`, plus event-specific fields. Downstream tooling
  parses fields, not regexes.
- **Redact at the boundary.** Maintain a deny-list of sensitive keys and scrub them in
  the logger itself, so no individual call site can leak by forgetting.
- Log to **stdout/stderr** and let the platform ship them (the twelve-factor rule).
  Applications should not own log files, rotation, or shipping.
- Include **context, not just an error string**: which user cohort, which route, which
  downstream dependency, and the error type. "DB error" is nearly useless; "timeout
  calling orders-db after 3s on route /checkout" is actionable.
- **Sample high-volume, low-value logs** (health checks, hot-path INFO) and keep all
  errors. Full-fidelity logging of a 50k-rps endpoint is mostly wasted money.
- Make **timestamps UTC and ISO 8601** with millisecond precision, so lines from
  different hosts sort correctly.
- Log **security and audit events** (auth, access changes, admin actions) to a
  separate, tamper-evident stream with longer retention.

## Examples

**Good Example** — structured, correlated, redacted (Node / pino)

```js
// Logger configured once with automatic redaction of known-sensitive paths.
const logger = pino({
  redact: { paths: ["password", "token", "*.authorization", "req.body.card"], censor: "[REDACTED]" },
  formatters: { level: (label) => ({ level: label }) },
});

function handleLogin(req, user) {
  // Fields, not prose: queryable, and trace_id ties this to the metric spike and trace.
  logger.info({
    event: "login_success",
    trace_id: req.traceId,
    request_id: req.id,
    user_id: user.id,          // an ID is fine; the email/password are not
    route: "/login",
  }, "user logged in");
}
```

**Bad Example** — prose, leaked secret, no correlation

```js
function handleLogin(req, user) {
  // Anti-pattern: dumps the whole user object -> writes passwordHash, email, and tokens
  // into the log store, which fans out to third-party log vendors and is retained for years.
  console.log("User logged in: " + JSON.stringify(user));
  // Free-text with no trace_id/request_id -> cannot be joined to the request's trace,
  // and can only be searched by fragile substring matching.
}
```

## Common Mistakes

- Logging entire request/response bodies or user objects, leaking secrets and PII.
- Free-text logs that must be grepped instead of queried by field.
- No trace ID or request ID, so logs cannot be correlated across services.
- Using ERROR for handled, expected conditions, training operators to ignore ERROR.
- Writing to local files and owning rotation instead of emitting to stdout.
- Logging on the hot path with no sampling, producing crippling volume and cost.
- Blocking the request thread on a slow logging sink.

## Production Tips

- Set **retention by stream**: short for DEBUG/INFO, long for audit/security. Retention
  is the main driver of log cost.
- Enforce redaction in **CI** with a lint rule or test that fails if a sensitive key can
  reach the logger, so the boundary cannot regress.
- Emit a **schema version** field; when the log shape changes, downstream parsers can
  adapt instead of silently breaking.

## AI Review Checklist

- Are logs structured (JSON) with a stable field schema, not interpolated prose?
- Is every sensitive value (password, token, key, PII) redacted before it can be logged?
- Does every line include a trace ID and request ID for correlation?
- Are log levels used correctly, with ERROR reserved for actionable failures?
- Does the app log to stdout/stderr rather than owning files and rotation?
- Are high-volume, low-value logs sampled while all errors are kept?
- Are audit/security events on a separate stream with appropriate retention?

## Related

- `knowledge/devops/13-observability.md`
- `knowledge/devops/12-monitoring.md`
- `knowledge/devops/15-alerting.md`
- `knowledge/devops/16-security.md`
- `knowledge/devops/25-incident-management.md`
