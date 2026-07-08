---
id: security/27-best-practices
topic: security
slug: best-practices
title: "Best Practices"
type: doc
order: 27
status: ready
tags: [security, best-practices]
related: [security/28-owasp-top10, security/30-engineering-principles, security/09-input-validation, security/16-secrets-management, security/29-security-review]
when_to_use: "Read when you need a cross-cutting checklist of the security habits every change should honor."
---
# Best Practices

## Purpose

This document is the distilled, cross-cutting set of security habits that apply to
almost every change, regardless of the specific vulnerability class. Where the other
docs go deep on one topic — [XSS](11-xss.md), [JWT](07-jwt.md), [CORS](19-cors.md) —
this one names the durable practices an agent should apply by default, everywhere.

Treat it as the baseline. If a change violates one of these, it needs an explicit,
documented reason, not silence.

## Why It Matters

Most breaches are not exotic; they are the same handful of mistakes repeated —
missing validation, a hardcoded secret, an over-broad permission, a skipped patch.
The [OWASP Top 10](28-owasp-top10.md) has barely changed in a decade because these
fundamentals keep getting skipped under deadline pressure. Practices that are cheap to
apply while writing code are enormously expensive to retrofit after a breach. Encoding
them as defaults — things you do without being asked — is what separates secure-by-habit
engineering from secure-by-luck.

## Core Principles

- **Defense in depth.** No single control is trusted alone. Validate input *and* encode
  output *and* use parameterized queries. Layers survive the failure of any one layer.
- **Least privilege, everywhere.** Every credential, token, container, and DB role gets
  the minimum access it needs. Scope down by default; widen only with justification.
- **Secure by default.** The safe configuration is the one you get with no extra effort:
  deny by default, encrypt by default, private by default.
- **Never trust input; never trust the client.** All external data — bodies, headers,
  query params, files, webhooks — is hostile until validated on the server.
- **Reduce attack surface.** The most secure code is code that isn't there. Fewer
  endpoints, fewer dependencies, fewer permissions, less exposed data.

## Best Practices

- Validate input against an **allowlist** at the trust boundary — see [input validation](09-input-validation.md).
- Use parameterized queries / prepared statements; never build SQL or shell strings by
  concatenation — see [SQL injection](13-sql-injection.md), [command injection](14-command-injection.md).
- Keep secrets out of code and version control; load them from a manager — see [secrets management](16-secrets-management.md).
- Enforce HTTPS/TLS everywhere and set [security headers](22-security-headers.md) (HSTS, CSP, etc.).
- Authenticate, then authorize on **every** request; deny by default — see [authorization](04-authorization.md).
- Keep dependencies patched and pinned; monitor for CVEs — see [dependency security](23-dependency-security.md).
- Fail closed and return generic errors to users; log details server-side only.
- Rate-limit and lock out abusable endpoints — see [rate limiting](21-rate-limiting.md).
- Encode output for its exact context (HTML, attribute, JS, URL) — see [output encoding](10-output-encoding.md).
- Prefer well-reviewed libraries over hand-rolled security code; never invent crypto.

## Examples

**Good Example** — layered defense on a single write endpoint

```ts
router.post("/comments", requireAuth, rateLimit, async (req, res) => {
  // 1. Validate on the server against a strict schema (allowlist).
  const { body } = commentSchema.parse(req.body);           // rejects unknown fields
  // 2. Authorize this specific action (deny by default).
  if (!can(req.user, "comment:create")) return res.sendStatus(403);
  // 3. Parameterized query — no string concatenation into SQL.
  await db.query("INSERT INTO comments (user_id, body) VALUES ($1, $2)",
                 [req.user.id, body]);
  // 4. Output is HTML-encoded at render time, so stored text can't become script.
  res.sendStatus(201);
});
```

**Bad Example** — every layer skipped at once

```ts
router.post("/comments", async (req, res) => {           // no auth, no rate limit
  // Raw, unvalidated input concatenated straight into SQL → injection.
  await db.query(`INSERT INTO comments (user_id, body)
                  VALUES (${req.body.userId}, '${req.body.body}')`);
  // Stored verbatim and later rendered unescaped → stored XSS.
  res.send("ok");
});
```

## Common Mistakes

- Validating on the client only; the server accepts whatever an attacker sends directly.
- Relying on a single control (e.g. "the WAF will catch it") instead of layered defense.
- Broad permissions "to make it work," then never scoping them back down.
- Hardcoding secrets or committing `.env` files to the repo.
- Catching an error and failing *open* — granting access when a check errors out.
- Copying a Stack Overflow snippet that disables a protection (verify=false, CORS `*`) to "fix" a bug.
- Treating security as a final review step instead of a property of each change.

## Production Tips

- Wire these into CI so they're enforced, not remembered: SAST, dependency scanning,
  secret scanning, and lint rules that ban dangerous APIs.
- Make the secure path the easy path — provide validated request wrappers and a query
  builder that is parameterized by construction.
- Keep a short, living "paved road" doc so new code adopts the safe defaults automatically.

## AI Review Checklist

- Is all external input validated on the server against an allowlist?
- Are queries parameterized and shell calls argument-arrayed (no string building)?
- Are secrets loaded from a manager, with none in code or git history?
- Is every request authenticated and authorized, denying by default?
- Is output encoded for its exact rendering context?
- Are security controls layered, so no single failure grants access?
- Do errors fail closed and stay generic to the user?
- Are dependencies patched, pinned, and scanned in CI?

## Related

- `knowledge/security/28-owasp-top10.md`
- `knowledge/security/30-engineering-principles.md`
- `knowledge/security/09-input-validation.md`
- `knowledge/security/16-secrets-management.md`
- `knowledge/security/29-security-review.md`
