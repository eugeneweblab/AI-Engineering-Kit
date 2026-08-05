---
id: security/98-production-checklist
topic: security
slug: production-checklist
title: "Security Production Checklist"
type: doc
order: 98
status: ready
tags: [security, production-checklist]
related: [security/27-best-practices, security/28-owasp-top10, security/16-secrets-management, security/22-security-headers, security/25-monitoring, security/99-ai-review-checklist]
when_to_use: "Read before shipping any service to production or signing off a release that changes an auth, data, or network surface."
---
# Security Production Checklist

## Purpose

This is the go-live gate for security. Every item is a verifiable yes/no fact about the
system you are about to ship — not a principle to ponder. If any box cannot be checked
truthfully, the release is not ready. Use it as the final pass after the feature-level
guidance in the sibling docs has been applied.

## Why It Matters

Most breaches exploit boring, known gaps: a default credential, a missing header, an
unpatched dependency, a debug endpoint left open. These are invisible in a passing test
suite and a working demo. A checklist converts tribal knowledge into a repeatable gate so
the same hole is never shipped twice. Run it every release, not once — configuration drifts
and new endpoints appear.

## How To Use

- Copy this list into the release PR or ticket and check each box against the actual
  deployed configuration, not the intended one.
- An unchecked box is a blocker or an explicit, signed-off risk acceptance — never a silent skip.
- "N/A" is allowed only with a one-line reason (e.g., "no file uploads in this service").

## Authentication and Sessions

- [ ] Passwords are hashed with Argon2id or bcrypt and a per-user salt; no fast/reversible hashes.
- [ ] Login, signup, password-reset, and MFA endpoints are rate-limited and lockout-protected.
- [ ] Session IDs regenerate on login and privilege change; logout revokes server-side.
- [ ] Session cookies are `HttpOnly`, `Secure`, and `SameSite=Lax` or `Strict`.
- [ ] Tokens are not stored in `localStorage` or exposed to client-side JavaScript.
- [ ] JWTs are verified for signature, algorithm, issuer, audience, and expiry before trust.
- [ ] MFA is available and enforced for administrative accounts.

## Authorization

- [ ] Every endpoint enforces an explicit authorization check; default is deny.
- [ ] Object-level access is checked (the requester owns/may access *this* record, not just the type).
- [ ] Role/permission checks happen server-side, never trusting a client-supplied role or flag.
- [ ] There are no debug, admin, or actuator endpoints reachable without authentication.

## Input, Output, and Injection

- [ ] All external input is validated against an allowlist schema at the boundary.
- [ ] Database access uses parameterized queries or an ORM; no string-concatenated SQL.
- [ ] Shell/OS calls avoid the shell or use argument arrays; no interpolated command strings.
- [ ] Output is context-encoded (HTML, attribute, JS, URL) to prevent XSS.
- [ ] File uploads validate type by content, cap size, store outside the web root, and randomize names.

## Transport and Headers

- [ ] HTTPS is enforced everywhere with HSTS; HTTP redirects to HTTPS.
- [ ] TLS is 1.2+ with modern ciphers; no expired or self-signed certs in production.
- [ ] A Content-Security-Policy is set and does not use `unsafe-inline`/`unsafe-eval` for scripts.
- [ ] Security headers are present: `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`/frame-ancestors.
- [ ] CORS allows only known origins; it is not `*` on any authenticated endpoint.

## Secrets and Configuration

- [ ] No secrets, keys, or tokens are committed to the repo or baked into images/logs.
- [ ] Secrets come from a secrets manager or injected env vars, not source files.
- [ ] All default and vendor credentials have been changed or disabled.
- [ ] Debug mode, verbose stack traces, and source maps are disabled in production.
- [ ] Error responses to clients are generic; details go to server logs only.

## Dependencies and Supply Chain

- [ ] A dependency vulnerability scan runs in CI and blocks known-critical findings.
- [ ] Dependencies are pinned with a lockfile; builds are reproducible.
- [ ] Base images are minimal, current, and pulled by digest, not floating tags.

## Data Protection

- [ ] Sensitive data at rest is encrypted; PII is minimized and access-logged.
- [ ] Backups exist, are encrypted, and a restore has been tested.
- [ ] PII/secrets are scrubbed from logs, analytics, and error trackers.

## Monitoring and Response

- [ ] Security-relevant events (auth failures, lockouts, authz denials) are logged and alertable.
- [ ] Log timestamps are UTC and logs are tamper-evident / centralized.
- [ ] There is a documented, reachable path to revoke sessions and rotate keys during an incident.
- [ ] An owner and runbook exist for the top plausible incidents.

## Common Mistakes

- Checking boxes against the code or intent instead of the live deployed configuration.
- Running the checklist once at launch and never again as endpoints and config drift.
- Treating "N/A" as a free skip with no recorded reason.
- Passing CI green as equivalent to secure — most items here are not covered by unit tests.

## AI Review Checklist

- Did I verify each item against actual production config, not assumptions?
- Is every unchecked item either fixed or an explicit, signed-off risk?
- Do new endpoints added this release each appear under the relevant section?
- Are there any debug/default-credential/verbose-error gaps that a demo would hide?

## Related

- `knowledge/security/27-best-practices.md`
- `knowledge/security/28-owasp-top10.md`
- `knowledge/security/16-secrets-management.md`
- `knowledge/security/22-security-headers.md`
- `knowledge/security/25-monitoring.md`
- `knowledge/security/99-ai-review-checklist.md`
