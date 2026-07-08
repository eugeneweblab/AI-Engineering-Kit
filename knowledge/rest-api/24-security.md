---
id: rest-api/24-security
topic: rest-api
slug: security
title: "Security"
type: doc
order: 24
status: ready
tags: [rest-api, security]
related: [rest-api/15-authentication, rest-api/16-authorization, rest-api/17-rate-limiting, rest-api/08-validation, rest-api/09-error-handling]
when_to_use: "Read before exposing any REST endpoint to untrusted clients or reviewing an API for security defects."
---
# Security

## Purpose

This document defines how to harden a REST API against attackers at the transport,
request, and response layers. It covers concerns that sit *around* authentication and
authorization: transport security, input handling, injection, secrets, headers, and
data exposure. For identity itself, see [authentication](15-authentication.md) and
[authorization](16-authorization.md); this doc assumes those are in place and focuses on
everything else a hostile client can reach.

## Why It Matters

A REST API is a machine-readable attack surface. Unlike a UI, there is no browser to
sanitize input, no human to slow down a brute-force, and no obscurity — every endpoint,
parameter, and error shape is discoverable. One over-broad response field or one
unvalidated query parameter leaks data or executes code for *every* client at once. The
failure is silent: the API keeps returning `200 OK` while an attacker enumerates users
or exfiltrates rows. Because the blast radius is the whole dataset, API security is held
to a higher bar than internal code. Treat every request as hostile.

## Core Principles

- **Encrypt everything in transit.** Serve only over TLS (HTTPS). Redirect or reject
  plaintext HTTP; a token sent once over HTTP is compromised forever.
- **Validate at the boundary, before use.** Every field — body, query, path, header — is
  untrusted until a schema validates its type, length, and range. See
  [validation](08-validation.md).
- **Never build queries or commands by string concatenation.** Use parameterized queries
  and safe APIs so input can never change the structure of a statement.
- **Return the minimum.** Serialize an explicit allow-list of fields. Default responses
  leak columns you forgot existed (password hashes, internal flags, other users' data).
- **Fail closed and fail quiet.** On any error, deny the action and return a generic
  message. Stack traces and DB errors are a map of your system for an attacker.
- **Authorize every object, every request.** Owning a valid token is not permission to
  touch object `42`. Check ownership on each access to stop IDOR/BOLA.

## Best Practices

- Enforce HTTPS with HSTS (`Strict-Transport-Security`). Set `Content-Type` and reject
  requests whose declared type you do not parse (defends against content sniffing).
- Validate and coerce input with a schema library (Zod, Joi, Pydantic). Reject unknown
  fields rather than ignoring them, so mass-assignment cannot set `isAdmin`.
- Use parameterized queries or an ORM for all data access; never interpolate user input.
- Set security headers: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy`, and a restrictive CORS policy — never `Access-Control-Allow-Origin: *`
  on authenticated endpoints.
- Rate-limit and throttle by client identity and IP to blunt brute-force and scraping.
  See [rate limiting](17-rate-limiting.md).
- Cap request body size and array/pagination limits to prevent resource exhaustion.
- Keep secrets (DB passwords, signing keys, API keys) in a secrets manager and read them
  from the environment — never commit them or return them in responses or logs.
- Log security *events* (auth failures, authz denials, validation rejections) with a
  request id — never log tokens, passwords, or full request bodies.

## Examples

**Good Example** — parameterized query, explicit field allow-list, ownership check

```ts
// GET /accounts/:id — attacker cannot read another user's account or inject SQL.
app.get("/accounts/:id", requireAuth, async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) return res.status(400).json({ error: "Invalid id" });

  // Parameterized: input can never alter the query structure.
  const acct = await db.query(
    "SELECT id, owner_id, name, balance FROM accounts WHERE id = $1",
    [id],
  );
  if (!acct) return res.status(404).json({ error: "Not found" });

  // Object-level authorization: token is not enough — check ownership.
  if (acct.owner_id !== req.user.id) return res.status(404).json({ error: "Not found" });

  // Return an explicit allow-list, never the raw row.
  res.json({ id: acct.id, name: acct.name, balance: acct.balance });
});
```

**Bad Example** — string-built query, whole-row leak, no ownership check

```ts
app.get("/accounts/:id", requireAuth, async (req, res) => {
  // SQL injection: `id` flows straight into the statement.
  const acct = await db.raw(`SELECT * FROM accounts WHERE id = ${req.params.id}`);

  // Leaks every column, including owner_id, internal_notes, kyc_ssn...
  // No ownership check → any authenticated user reads any account (BOLA/IDOR).
  res.json(acct);
});
```

## Common Mistakes

- Trusting a valid token as permission to access any object id (BOLA/IDOR).
- Returning raw ORM objects, leaking fields you never meant to expose.
- Building SQL, shell, or NoSQL queries by concatenating user input.
- `Access-Control-Allow-Origin: *` combined with credentials, exposing the API to any site.
- Echoing exception messages or stack traces in error responses.
- Accepting arbitrary body fields, allowing mass-assignment of privileged attributes.
- Serving tokens or endpoints over HTTP, or omitting HSTS so the first request downgrades.

## Production Tips

- Run an authenticated scanner (OWASP ZAP) and dependency audit (`npm audit`, Snyk) in CI.
- Pen-test the top OWASP API risks explicitly: BOLA, broken auth, excessive data exposure,
  mass assignment, and unrestricted resource consumption.
- Alert on spikes in 401/403 and validation rejections — they signal enumeration attempts.
- Rotate signing keys and API keys on a schedule; support revocation for incident response.

## AI Review Checklist

- Is every endpoint served only over TLS, with HSTS set?
- Is all input validated by a schema, with unknown fields rejected?
- Are all queries parameterized, with no user input concatenated into commands?
- Does each response serialize an explicit field allow-list, not the raw record?
- Is object-level ownership checked on every access, not just token validity?
- Are errors generic, with no stack traces or DB messages leaked?
- Is CORS restricted to known origins, never `*` on authenticated routes?
- Are secrets read from a manager/env and kept out of logs and responses?

## Related

- `knowledge/rest-api/15-authentication.md`
- `knowledge/rest-api/16-authorization.md`
- `knowledge/rest-api/17-rate-limiting.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/09-error-handling.md`
