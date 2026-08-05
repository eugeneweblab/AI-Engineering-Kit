---
id: rest-api/08-validation
topic: rest-api
slug: validation
title: "REST API Validation"
type: doc
order: 8
status: ready
tags: [rest-api, validation, CreateUser, safeParse, email, strict, object]
related: [rest-api/09-error-handling, rest-api/07-status-codes, rest-api/06-request-response, rest-api/24-security, rest-api/21-openapi]
when_to_use: "Read before accepting any client-supplied input into an endpoint — body, query, path, or headers."
---
# REST API Validation

## Purpose

This document defines how an API validates incoming data before it reaches business
logic or storage. It is written so an agent can build an endpoint that rejects malformed
and malicious input cleanly, with useful errors, and never processes data it has not
verified.

Validation is the boundary between the hostile outside world and your trusted internal
model. Everything past this boundary should be safe to assume well-formed; everything at
it should assume nothing.

## Why It Matters

Unvalidated input is the root of most API failures: injection, corrupted records,
`500`s from type errors deep in the stack, and silent data drift. The damage is not
contained to one request — a single bad row can poison reports, break other consumers,
and be impossible to reconstruct later. Validation is cheap at the door and ruinously
expensive once bad data is persisted. Reject early, at the edge, with a clear reason.

## Core Principles

- **Validate at the boundary, once, completely.** Do all structural and semantic checks
  on entry so inner layers can trust their inputs. Scattered ad-hoc checks leak.
- **Allowlist, never denylist.** Define exactly what is valid (fields, types, ranges,
  enum values) and reject everything else. Trying to enumerate bad input always misses a
  case.
- **Reject unknown fields.** An unexpected field is a client bug or an attack; failing on
  it catches typos and prevents mass-assignment of fields the client should not set.
- **Validation is not authorization.** Verifying a value is *well-formed* says nothing
  about whether this caller may *use* it. Do both, separately.
- **Report every error at once.** Return the full list of validation failures in one
  response so the client fixes them in a single round trip, not one at a time.

## Best Practices

- Use a schema (Zod, Pydantic, JSON Schema, class-validator) as the single source of
  truth; do not hand-roll `if` checks scattered across handlers.
- Validate all input surfaces: body, query parameters, path parameters, and relevant
  headers. Query and path params are strings until you parse and constrain them.
- Enforce types, required/optional, length and range bounds, formats (email, UUID, URL),
  and enum membership. Cap array lengths and string sizes to prevent resource exhaustion.
- Coerce and normalize deliberately (trim whitespace, lowercase emails) — but decide the
  policy explicitly; silent coercion hides bugs.
- Return `422 Unprocessable Content` for well-formed JSON that fails business rules, and
  `400 Bad Request` for malformed/unparseable input — see [status codes](07-status-codes.md).
- Never build SQL, shell, or HTML from raw input; use parameterized queries regardless of
  validation — see [security](24-security.md).
- Keep the schema and the OpenAPI contract in sync so the documented shape *is* the
  enforced shape — see [openapi](21-openapi.md).

## Examples

**Good Example** — schema-driven, strict, all errors at once

```ts
import { z } from "zod";

const CreateUser = z.object({
  email: z.string().email(),
  age: z.number().int().min(13).max(120),      // typed + bounded
  role: z.enum(["member", "admin"]),           // allowlist of valid values
}).strict();                                    // unknown fields are rejected

function handler(req, res) {
  const parsed = CreateUser.safeParse(req.body);
  if (!parsed.success) {
    // 422: well-formed JSON, failed the rules; every issue returned together
    return res.status(422).json({ errors: parsed.error.issues });
  }
  createUser(parsed.data);  // inner layers receive fully-trusted, typed data
}
```

**Bad Example** — trust first, check later

```ts
function handler(req, res) {
  const { email, age, role } = req.body;   // types unknown, fields unbounded
  if (!email) return res.status(400).send("email required"); // stops at first error
  // no email format check, no age bounds, no role allowlist
  // unknown fields (e.g. isAdmin) pass straight through → mass assignment
  db.query(`INSERT INTO users (email) VALUES ('${email}')`);  // injection
}
```

## Common Mistakes

- Validating only the body and trusting query/path params or headers.
- Denylisting "bad" characters instead of allowlisting valid input.
- Accepting unknown fields, enabling mass assignment (`isAdmin: true`).
- Returning the first error only, forcing clients into fix-retry loops.
- Treating a passed validation as authorization ("the id is a valid UUID" ≠ "you own it").
- No length/size caps, letting a giant array or string exhaust memory.
- Duplicating validation logic in handlers instead of one shared schema.

## Production Tips

- Generate types from the schema (or the schema from types) so the compiler enforces the
  same shape the runtime does.
- Fuzz endpoints with malformed and boundary inputs in CI; assert `4xx`, never `5xx`.
- Log validation-failure *counts and field names* to spot broken clients or probing —
  never log the raw rejected values if they may contain secrets.
- Keep error messages specific about *what* is wrong but never echo back unsanitized input
  into an HTML/error surface.

## AI Review Checklist

- Is every input surface (body, query, path, headers) validated against a schema?
- Does the schema reject unknown fields (`.strict()` or equivalent)?
- Are types, ranges, lengths, formats, and enum values all enforced?
- Are all validation errors returned together, with a `422`/`400` as appropriate?
- Are queries parameterized regardless of validation?
- Is validation kept distinct from authorization?
- Does the enforced schema match the documented OpenAPI contract?

## Related

- `knowledge/rest-api/09-error-handling.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/06-request-response.md`
- `knowledge/rest-api/24-security.md`
- `knowledge/rest-api/21-openapi.md`
