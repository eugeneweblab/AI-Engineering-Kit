---
id: backend/09-validation
topic: backend
slug: validation
title: "Validation"
type: doc
order: 9
status: ready
tags: [backend, validation]
related: [backend/06-api-design, backend/08-domain-modeling, backend/12-error-handling, backend/07-business-logic, backend/21-security]
when_to_use: "Read before accepting any external input — request bodies, query params, webhooks, file uploads, or message payloads."
---
# Validation

## Purpose

This document defines how to check that data entering the system is well-formed and safe
before it is used: request bodies, query parameters, headers, webhooks, and message
payloads. It is written so an agent can validate input at the boundary, precisely and
consistently, without letting malformed or hostile data reach business logic or storage.

Validation is the system's immune boundary. Everything past it should be able to trust
the shape of its data; everything at it must assume the data is wrong or malicious.

## Why It Matters

Every input from outside the process is untrusted — including from your own frontend,
which an attacker can bypass with `curl`. Missing or lenient validation is the root of
injection, corrupted records, crashes on unexpected types, and subtle logic errors that
surface hours later far from the cause. Validating once, at the edge, turns "defend
everywhere" into "trust everywhere inside", which is both safer and simpler. Server-side
validation is mandatory; client-side validation is a UX nicety and provides no security
guarantee whatsoever.

## Core Principles

- **Validate at the boundary, parse into a typed shape.** Don't merely check a raw blob —
  transform it into a trusted, typed value and pass *that* inward. "Parse, don't
  validate": after the edge, the type proves the data is good.
- **Whitelist, don't blacklist.** Define exactly what is allowed (fields, types, ranges,
  enum values) and reject everything else. Blacklists always miss a case.
- **Reject unknown fields.** Strip or fail on properties you didn't declare, so a client
  can't smuggle `isAdmin: true` into an update. The cost is strictness; the payoff is no
  mass-assignment holes.
- **Separate input validation from business rules.** Shape and type belong at the edge;
  "is this allowed given current state" belongs in the domain. See
  [business logic](07-business-logic.md).
- **Fail with actionable, non-leaky errors.** Report which fields failed and why, without
  echoing raw input or internal details. See [error handling](12-error-handling.md).

## Best Practices

- Use a schema library (Zod, Pydantic, JSON Schema, Bean Validation) to declare the
  expected shape once and derive both the runtime check and the static type.
- Coerce and normalize deliberately (trim strings, parse numbers, lowercase emails) at the
  boundary — but only from declared, expected inputs.
- Enforce bounds: max string length, array length, numeric range, allowed enum values.
  Unbounded input is a denial-of-service vector.
- Validate `Content-Type` and body size limits before parsing; reject oversized or wrong
  media types early. See [security](21-security.md).
- For file uploads, validate type by content, not extension, and cap size.
- Return a `400`/`422` with a per-field error list; never a `500` for bad input.
- Validate queue/webhook payloads with the same rigor as HTTP bodies — they are equally
  untrusted.

## Examples

**Good Example** — parse into a typed value, reject the unknown

```ts
import { z } from "zod";

// Declares the ONLY acceptable shape; strict() rejects any extra field.
const CreateUser = z.object({
  email: z.string().email().max(254).transform((s) => s.toLowerCase().trim()),
  age: z.number().int().min(13).max(120),      // bounded range, no floats
  role: z.enum(["member", "editor"]),          // whitelist; "admin" cannot get in
}).strict();

app.post("/users", (req, res) => {
  const parsed = CreateUser.safeParse(req.body);
  if (!parsed.success) {
    // Per-field, actionable, no raw input echoed back.
    return res.status(422).json({ code: "VALIDATION", fields: parsed.error.flatten() });
  }
  createUser(parsed.data); // parsed.data is a trusted, fully-typed value from here on
});
```

**Bad Example** — trusts the blob, mass-assignment hole

```ts
app.post("/users", (req, res) => {
  const b = req.body;
  if (!b.email) return res.status(400).send("email required"); // only checks presence
  // No type check (age could be "banana"), no bounds, no whitelist of fields.
  db.insert("users", b); // spreads the whole body: client sends {isAdmin:true} -> stored
});
```

## Common Mistakes

- Relying on client-side validation for security; it is trivially bypassed.
- Checking presence but not type, range, or format ("it exists" ≠ "it's valid").
- Mass assignment: spreading the whole request body into a model or SQL insert.
- Blacklisting bad values instead of whitelisting good ones.
- No length/size bounds, allowing multi-megabyte fields to exhaust memory.
- Returning a `500` (or a raw exception) instead of a structured `4xx` on bad input.
- Skipping validation on internal channels (queues, webhooks, admin tools).

## Production Tips

- Generate the API's validation schema and its OpenAPI docs from one source so they can't
  drift. See [documentation](24-documentation.md).
- Log validation failure *rates* per endpoint; a sudden spike signals a client bug or an
  attack probing your inputs.
- Fuzz-test boundaries with oversized, wrong-typed, and Unicode-edge inputs in CI.

## AI Review Checklist

- Is every external input validated server-side against a declared schema?
- Are types, ranges, lengths, and enum values checked — not just presence?
- Are unknown/extra fields rejected or stripped (no mass assignment)?
- Is validation a whitelist of allowed values rather than a blacklist?
- Does bad input yield a structured `400`/`422` with per-field detail, never a `500`?
- Are body size and `Content-Type` bounded before parsing?
- Are queue and webhook payloads validated as strictly as HTTP requests?

## Related

- `knowledge/backend/06-api-design.md`
- `knowledge/backend/08-domain-modeling.md`
- `knowledge/backend/12-error-handling.md`
- `knowledge/backend/07-business-logic.md`
- `knowledge/backend/21-security.md`
