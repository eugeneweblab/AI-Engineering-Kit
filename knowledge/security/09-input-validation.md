---
id: security/09-input-validation
topic: security
slug: input-validation
title: "Input Validation"
type: doc
order: 9
status: ready
tags: [security, input-validation, CreateUser, strict, email, object]
related: [security/10-output-encoding, security/11-xss, security/13-sql-injection, security/14-command-injection]
when_to_use: "Read before accepting any external data — request bodies, query params, headers, uploads, or webhooks."
---
# Input Validation

## Purpose

This document defines how to validate untrusted input at the boundary of the system: HTTP
bodies, query strings, headers, path parameters, file uploads, webhooks, and messages from
other services. Validation answers "is this data well-formed and within the shape I expect?"
before any code acts on it.

Validation is a *first* line of defense, not the only one. It reduces the attack surface and
catches malformed data early, but it does not replace context-specific defenses like
parameterized queries or [output encoding](10-output-encoding.md). Do both.

## Why It Matters

Every injection class — SQLi, command injection, XSS, path traversal, SSRF, deserialization
— starts with input the code was not prepared for. When you validate at the boundary, a
whole category of malformed or hostile input never reaches the vulnerable sink. The failure
mode of *missing* validation is that unexpected data flows deep into the system and detonates
somewhere far from where it entered, making the bug hard to trace and easy to exploit.
Validation shrinks the set of values your code must handle to the set it was actually
designed for.

## Core Principles

- **Allowlist, do not denylist.** Define what is *valid* and reject everything else.
  Denylists (blocking `<script>`, `../`, `;`) always miss a variant — encodings, unicode
  look-alikes, new payloads. The cost of allowlisting is spelling out the shape; the payoff
  is that unknown attacks fail closed.
- **Validate at the trust boundary, once, server-side.** Client-side checks are UX, not
  security — they are trivially bypassed. Re-validate on the server for every request.
- **Parse, don't just check.** Convert input into a typed, constrained value (a `number`,
  an `enum`, a validated `Email`) so the rest of the code cannot receive a bad value at all.
- **Validation is not sanitization.** Validation *rejects* bad input; encoding/escaping makes
  input *safe for a specific sink*. Rejecting `<` on input breaks legitimate data and still
  fails to protect the sink. Escape at output instead.
- **Fail closed with a generic error.** On invalid input, reject the request; do not "clean"
  it and proceed with a guessed value.

## Best Practices

- Validate **type, range, length, format, and allowed set** for every field. A string field
  needs a max length; a number needs bounds; a status needs an enum.
- Use a schema validator (e.g. `zod`, `pydantic`, JSON Schema) and reject unknown/extra keys
  (`strict`) so attackers cannot smuggle fields your handler forgot to ignore.
- Validate structure and semantics, then hand the typed result to context-specific defenses:
  parameterized queries for SQL, argument arrays for shell, encoding for HTML.
- Canonicalize before validating (normalize unicode, decode once, resolve paths) so a check
  and its later use see the same bytes. Reject input that decodes more than once.
- Bound collection sizes and nesting depth to stop resource-exhaustion via huge or deeply
  nested payloads.
- Validate `Content-Type` and enforce a request-body size limit before parsing.

## Examples

**Good Example** — schema parse into a typed, constrained value

```ts
import { z } from "zod";

const CreateUser = z.object({
  email: z.string().email().max(254),               // format + length bound
  age: z.number().int().min(13).max(120),           // type + range
  role: z.enum(["member", "admin"]),                // allowlist of valid values
}).strict();                                        // reject unknown keys

function handler(body: unknown) {
  const input = CreateUser.parse(body); // throws on any malformed field → fails closed
  // `input` is now a typed value the rest of the code can trust to be in-shape.
  return users.create(input);
}
```

**Bad Example** — denylist string-scrubbing, trusts the client

```ts
function handler(body: any) {
  // Denylist: strips one pattern, misses `<img onerror>`, unicode, double-encoding.
  const name = body.name.replace(/<script>/gi, "");
  // No type/length check → a 5 MB string or an object where a string was expected.
  // No allowlist on role → client sends role:"admin" and is trusted verbatim.
  return users.create({ name, role: body.role });
}
```

## Common Mistakes

- Relying on client-side validation and skipping the server check.
- Denylisting "bad characters" instead of allowlisting valid shapes.
- Accepting extra/unknown fields, letting attackers set properties the handler didn't expect
  (mass assignment).
- Confusing validation with output safety — validating then still concatenating into SQL/HTML.
- No length or size bounds, enabling resource-exhaustion and buffer-style abuse.
- Validating a value, then re-decoding it before use so the checked and used bytes differ.
- Coercing invalid input to a default and continuing instead of rejecting.

## Production Tips

- Centralize schemas so request and internal-message shapes are validated the same way and
  are reviewable in one place.
- Log validation *failures* with the field and rule that failed (not the raw payload if it
  may contain secrets); alert on spikes that indicate probing.
- Return `400` with a stable, generic error shape — do not echo the offending value back
  verbatim into an error page (that becomes an XSS/reflection vector).

## AI Review Checklist

- Is every external field validated for type, range, length, format, and allowed set?
- Is validation done server-side, at the boundary, regardless of client checks?
- Does the schema reject unknown/extra keys to prevent mass assignment?
- Is this allowlist-based rather than a denylist of "bad" characters?
- Is validation paired with a context-specific sink defense (parameterized query, encoding)?
- Are body size, collection length, and nesting depth bounded?
- Is invalid input rejected with a generic error rather than silently "cleaned"?

## Related

- `knowledge/security/10-output-encoding.md`
- `knowledge/security/11-xss.md`
- `knowledge/security/13-sql-injection.md`
- `knowledge/security/14-command-injection.md`
