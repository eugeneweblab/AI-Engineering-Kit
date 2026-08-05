---
id: rest-api/09-error-handling
topic: rest-api
slug: error-handling
title: "REST API Error Handling"
type: doc
order: 9
status: ready
tags: [rest-api, error-handling]
related: [rest-api/07-status-codes, rest-api/08-validation, rest-api/06-request-response, rest-api/24-security, rest-api/26-monitoring]
when_to_use: "Read before designing how an API reports failures — error bodies, error codes, and exception handling."
---
# REST API Error Handling

## Purpose

This document defines how an API reports failure: the shape of an error response, the
codes clients branch on, and how uncaught exceptions are handled. It is written so an
agent can build error handling that is consistent, machine-parseable, and leaks nothing.

Errors are part of the public contract, not an afterthought. Clients write more code
against your error paths than your happy path, so a stable, documented error format is as
important as the success format.

## Why It Matters

Inconsistent errors force every client to write brittle string-parsing to figure out what
went wrong; a small wording change then breaks them all. Verbose errors leak stack
traces, SQL, internal hostnames, and library versions — a reconnaissance gift to
attackers. And unhandled exceptions that escape as raw `500`s with a stack trace both
break the client and expose internals. A single, disciplined error contract is what makes
an API debuggable for callers and opaque to adversaries at the same time.

## Core Principles

- **One error shape, everywhere.** Every error — validation, auth, not-found, server —
  returns the same JSON structure. Clients parse one format, not ten.
- **Machine-readable code plus human-readable message.** A stable `code`/`type` field is
  what clients branch on; the `message` is for developers reading logs, never for control
  flow and never localized on the server for parsing.
- **Status code and error body agree.** The HTTP status is the primary signal; the body
  refines it — see [status codes](07-status-codes.md).
- **Never leak internals.** No stack traces, SQL, file paths, or dependency versions in a
  response. Log the detail server-side; return a correlation id to the client.
- **Fail closed and predictably.** An unexpected exception becomes a generic `500` with a
  safe body, never a raw crash dump.

## Best Practices

- Adopt a standard envelope. **RFC 9457 Problem Details** (`application/problem+json`) is
  the interoperable default: `type`, `title`, `status`, `detail`, `instance`.
- Include a stable, documented error `code` (or `type` URI) per failure class, plus a
  `traceId`/`instance` that ties the response to server logs.
- For validation, return a list of field-level errors (field, code, message) — see
  [validation](08-validation.md).
- Centralize error handling in one middleware/handler; do not format errors ad hoc in
  each route. Map known domain exceptions to codes there.
- Distinguish *expected* failures (return a modeled error) from *unexpected* ones (log at
  error level, alert, return generic `500`).
- Never expose whether a resource exists to an unauthorized caller — return the same
  `404` you would for a truly missing resource.
- Keep messages generic on security-sensitive paths (auth, payment); log specifics
  internally — see [security](24-security.md).
- Document every error `code` in the OpenAPI spec so clients can handle them.

## Examples

**Good Example** — one envelope, coded, traceable, safe

```ts
// central error middleware — the ONLY place errors become responses
function onError(err, req, res, _next) {
  const traceId = req.id;
  if (err instanceof DomainError) {           // expected, modeled failure
    return res.status(err.status).json({
      type: `/errors/${err.code}`,            // stable, documented, machine-branchable
      title: err.publicMessage,               // safe, generic wording
      status: err.status,
      instance: traceId,                       // ties response to server logs
    });
  }
  log.error({ err, traceId });                 // full detail stays server-side
  return res.status(500).json({                // unexpected → generic, no internals
    type: "/errors/internal", title: "Internal server error",
    status: 500, instance: traceId,
  });
}
```

**Bad Example** — inconsistent, leaky, unparseable

```ts
app.get("/orders/:id", async (req, res) => {
  try {
    const order = await db.find(req.params.id);
    if (!order) return res.status(404).send("not found");   // plain text, no code
    res.json(order);
  } catch (e) {
    // leaks stack trace, SQL, table names; different shape from the 404 above;
    // clients must string-match "not found" vs a raw dump to tell them apart
    res.status(500).json({ error: e.stack });
  }
});
```

## Common Mistakes

- A different error shape per endpoint, so clients cannot handle errors generically.
- No stable machine code — clients parse the human message and break on rewording.
- Leaking stack traces, SQL, or internal paths in the response body.
- Returning `200` with an `error` field instead of a proper `4xx`/`5xx` status.
- Revealing resource existence to unauthorized callers (`403` vs `404` leak).
- Catch-all handlers that swallow errors and return a misleading success.
- No correlation id, making a reported error impossible to find in the logs.

## Production Tips

- Emit a `traceId`/`instance` on every error and propagate it through logs and traces —
  it turns a support ticket into a one-query investigation. See [monitoring](26-monitoring.md).
- Alert on `5xx` rate and on new/unknown error codes appearing in production.
- Add contract tests asserting the exact error envelope and code for each failure path.
- Scrub PII and secrets from error logs; a leaked token in a stack trace is a breach.

## AI Review Checklist

- Does every error return the same documented envelope (e.g. RFC 9457 problem+json)?
- Is there a stable machine-readable `code`/`type` clients can branch on?
- Do all error bodies match their HTTP status (no `200` errors)?
- Are stack traces, SQL, and internal paths kept out of responses?
- Is there one central error handler, with a generic `500` for unexpected failures?
- Does every error carry a correlation id linkable to server logs?
- Do auth/not-found paths avoid leaking resource existence?

## Related

- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/06-request-response.md`
- `knowledge/rest-api/24-security.md`
- `knowledge/rest-api/26-monitoring.md`
