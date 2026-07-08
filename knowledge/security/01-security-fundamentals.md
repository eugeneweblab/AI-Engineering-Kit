---
id: security/01-security-fundamentals
topic: security
slug: security-fundamentals
title: "Security Fundamentals"
type: doc
order: 1
status: ready
tags: [security, security-fundamentals]
related: [security/02-threat-modeling, security/03-authentication, security/04-authorization, security/28-owasp-top10]
when_to_use: "Read before writing or reviewing any code that handles untrusted input, secrets, or user identity."
---
# Security Fundamentals

## Purpose

This document defines the principles that every other security doc applies. It is not
about a specific attack or defense — it is the mental model an agent uses to reason
about *any* code that touches untrusted input, secrets, or identity. When a specific
doc is silent on a case, fall back to these principles.

## Why It Matters

Most breaches are not exotic. They come from ordinary code that trusted something it
should not have: an unvalidated parameter, a default password, an over-broad
permission, an error message that leaked a secret. A developer who internalizes a few
principles catches these before they ship, without memorizing every attack. The cost of
applying the principles is small friction now; the cost of skipping them is a breach
later, when the fix is public and expensive.

## Core Principles

- **Least privilege.** Every component, credential, and user gets the minimum access
  needed, for the minimum time. A leaked read-only token is a smaller incident than a
  leaked admin token.
- **Defense in depth.** Assume any single control will fail. Layer independent
  controls so one bypass is not total compromise. Validation *and* parameterized
  queries *and* least-privilege DB grants.
- **Fail closed.** When a check cannot complete — an exception, a timeout, a missing
  config — deny access. An error must never fall through to "allowed".
- **Never trust the client.** Anything the client controls (headers, cookies, hidden
  fields, JS validation) is attacker-controlled. Re-validate and re-authorize on the
  server, every time.
- **Reduce the attack surface.** Every endpoint, dependency, feature flag, and open
  port is something to defend. The safest code is code that does not exist.
- **Secure by default.** New features start closed and opt-in, not open and opt-out.
  A default of "public" will not get tightened later.
- **Complete mediation.** Check authorization on every access to a protected resource,
  not once at the entry point. Do not cache "allowed" past the point it can change.

## Best Practices

- Validate input against an allowlist of what is *permitted*, not a denylist of what is
  known-bad. Denylists are always incomplete.
- Keep secrets out of code and logs; load them from a secrets manager at runtime. See
  [Secrets Management](16-secrets-management.md).
- Make security failures loud and observable: log the *event* (who, what, when) but
  never the secret itself.
- Use vetted libraries for crypto, auth, and parsing. Custom implementations fail in
  ways you cannot see or test.
- Separate the code that decides *whether* an action is allowed from the code that
  *performs* it, so the check cannot be accidentally skipped.
- Keep the trusted computing base small: fewer privileged code paths are easier to
  review and harder to get wrong.

## Examples

**Good Example** — fail closed, least privilege, server-side authority

```ts
function getDocument(user: User, docId: string): Document {
  const doc = repo.find(docId);
  if (!doc) throw new NotFoundError();      // do not leak existence to non-owners

  // Authorize on every access; deny unless explicitly permitted (fail closed).
  if (!canRead(user, doc)) {
    throw new ForbiddenError();             // no data returned on the failure path
  }
  return doc;
}
```

**Bad Example** — trusts the client, fails open

```ts
function getDocument(req: Request): Document {
  // Trusting a client-supplied role — attacker sets header "x-role: admin".
  const isAdmin = req.headers["x-role"] === "admin";

  try {
    const doc = repo.find(req.query.docId);
    if (isAdmin) return doc;                // over-broad, client-controlled
    return doc;                             // and it returns the doc anyway — fails open
  } catch {
    return repo.find(req.query.docId);      // error path bypasses every check
  }
}
```

## Common Mistakes

- Enforcing rules only in the UI or client JS, then trusting the client on the server.
- Denylist validation ("block `<script>`") instead of allowlisting valid input.
- Catch-all error handlers that return data or "allow" on the failure path.
- One authorization check at login, then trusting the session for actions it never
  covered.
- Broad, long-lived credentials because scoping them "was easier".
- Leaking internal detail (stack traces, SQL, whether a record exists) in errors.

## Production Tips

- Bake the principles into review: a PR that adds an endpoint must state its authz
  model and its input contract.
- Run automated scanners (SAST, dependency audit) in CI so surface growth is visible.
- Default every new config, bucket, and role to closed; require an explicit, reviewed
  change to open it.

## AI Review Checklist

- Is every trust boundary re-validated on the server, never on client-supplied claims?
- Does every failure path (exception, timeout, missing config) deny rather than allow?
- Is input allowlisted, not denylisted?
- Do credentials and permissions follow least privilege and expire?
- Are independent controls layered so one bypass is not total compromise?
- Do errors avoid leaking secrets, internals, or record existence?

## Related

- `knowledge/security/02-threat-modeling.md`
- `knowledge/security/03-authentication.md`
- `knowledge/security/04-authorization.md`
- `knowledge/security/28-owasp-top10.md`
- `knowledge/security/16-secrets-management.md`
