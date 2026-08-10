---
id: backend/21-security
topic: backend
slug: security
title: "Backend Security"
type: doc
order: 21
status: ready
tags: [backend, security, findUser, Strict-Transport-Security, Content-Security-Policy, X-Content-Type-Options, Content-Type, accepting, untrusted, secrets]
related: [backend/09-validation, backend/10-authentication, backend/11-authorization, backend/12-error-handling, backend/18-database-design]
when_to_use: "Read before exposing an endpoint, accepting user input, handling secrets, or reviewing any code that touches untrusted data."
---
# Backend Security

## Purpose

This document defines the baseline security every backend service must meet: trusting no
input, injection-safe data access, least-privilege access, secret handling, and safe error
output. It is written so an agent can build or review an endpoint without opening a hole
that leaks data or grants unintended access.

This is the backend-wide baseline. Identity-specific rules live in
[authentication](10-authentication.md) and [authorization](11-authorization.md); this
document covers the surface every request crosses regardless of who sent it.

## Why It Matters

Backend services hold the data and the privileges — the database credentials, the payment
keys, the other users' records. A front-end bug annoys one user; a backend security bug
exposes everyone at once, and the service keeps returning `200 OK` while it happens, so the
breach is invisible until it is public. Attackers probe every endpoint automatically, so
"nobody knows this route exists" is never a control. Security has to be a property of the
code, enforced on every path, because a single unguarded input is enough.

## Core Principles

- **Never trust input — validate at the trust boundary.** Every request body, query
  parameter, header, and upload is hostile until validated against a strict schema. See
  [validation](09-validation.md).
- **Separate code from data in every interpreter.** SQL, shell, and templates must receive
  user data as bound parameters, never as concatenated strings. This one rule kills most
  injection classes.
- **Least privilege everywhere.** Each service, database user, and token gets the minimum
  access it needs. A compromised component should reach almost nothing.
- **Deny by default.** Authorization, CORS, and network access start closed and open only
  for explicit, named cases. A missing check must fail safe, not fall through to allow.
- **Never leak internals in responses or logs.** Stack traces, SQL, and secret values are
  attacker intelligence. Return generic errors; log details server-side.

## Best Practices

- Use parameterized queries or an ORM's bound parameters for every database call. Never
  build SQL, shell commands, or file paths by string concatenation of user input.
- Validate and coerce all input against an explicit allowlist schema (Zod, class-validator);
  reject unknown fields rather than ignoring them. Enforce size limits on bodies and uploads.
- Encode output for its sink: HTML-escape for pages, set `Content-Type` and
  `X-Content-Type-Options: nosniff` for APIs, so returned data cannot execute.
- Keep secrets in a secrets manager or environment variables, never in source, logs, or
  version control. Rotate them on a schedule and on any suspected exposure.
- Enforce authorization on every endpoint, checked server-side against the authenticated
  identity — never trust an ID or role sent by the client.
- Enforce TLS in transit and encrypt sensitive data at rest; hash passwords with a memory-
  hard algorithm (Argon2id/bcrypt), never encrypt or store them reversibly.
- Rate-limit public and authentication endpoints to blunt brute-force and abuse.
- Keep dependencies patched; run automated vulnerability scanning (e.g. `npm audit`, SCA) in
  CI and treat criticals as build failures.

## Examples

**Good Example** — parameterized query, generic error

```ts
async function findUser(email: string) {
  // Driver sends the value out-of-band; it can never be parsed as SQL, so ' OR 1=1 --
  // is treated as a literal email string, not code.
  return db.query(`SELECT id, name FROM users WHERE email = $1`, [email]);
}

app.use((err, _req, res, _next) => {
  logger.error(err);                       // full detail stays server-side
  res.status(500).json({ error: "Internal error" }); // no stack, SQL, or internals to client
});
```

**Bad Example** — SQL injection and leaked internals

```ts
async function findUser(email: string) {
  // User input is concatenated into the query: email = "x' OR '1'='1" dumps every row.
  return db.query(`SELECT * FROM users WHERE email = '${email}'`);
}

app.use((err, _req, res, _next) => {
  // Returns the raw error — table names, driver, sometimes secrets — straight to the attacker.
  res.status(500).json({ error: err.message, stack: err.stack });
});
```

## Common Mistakes

- Building SQL, shell, or file paths by concatenating user input (injection).
- Trusting client-supplied IDs, roles, or prices instead of re-checking server-side.
- Returning stack traces, SQL, or exception messages to the client.
- Hardcoded secrets or credentials committed to the repository.
- Missing authorization on an endpoint because "the UI never links to it."
- Validating on the front end only, treating the API as if it were unreachable directly.
- Logging tokens, passwords, or full request bodies containing sensitive data.

## Production Tips

- Add security headers (`Strict-Transport-Security`, `X-Content-Type-Options`,
  `Content-Security-Policy`) and a strict, allowlisted CORS policy.
- Grant the application's database user only the privileges it needs — no `DROP`, no
  superuser — so injection cannot escalate to schema destruction.
- Scan for committed secrets in CI and rotate anything that leaks immediately; assume a
  leaked secret is already compromised.
- Alert on authorization failures and input-validation rejection spikes; they signal active
  probing.

## AI Review Checklist

- Are all database and shell calls parameterized, with no string-concatenated user input?
- Is every input validated against a strict allowlist schema with size limits?
- Is authorization enforced server-side on every endpoint against the authenticated identity?
- Do error responses hide stack traces, SQL, and internal details?
- Are secrets read from a manager/env, never committed or logged?
- Are passwords hashed with Argon2id/bcrypt and data encrypted in transit and at rest?
- Are public and auth endpoints rate-limited, and dependencies scanned in CI?

## Related

- `knowledge/backend/09-validation.md`
- `knowledge/backend/10-authentication.md`
- `knowledge/backend/11-authorization.md`
- `knowledge/backend/12-error-handling.md`
- `knowledge/backend/18-database-design.md`
