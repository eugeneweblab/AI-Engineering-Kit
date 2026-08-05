---
id: security/28-owasp-top10
topic: security
slug: owasp-top10
title: "OWASP Top 10"
type: doc
order: 28
status: ready
tags: [security, owasp-top10, getInvoice, ForbiddenError, findById]
related: [security/27-best-practices, security/04-authorization, security/13-sql-injection, security/24-supply-chain-security, security/29-security-review]
when_to_use: "Read when triaging a design or PR against the industry-standard list of the most common web risks."
---
# OWASP Top 10

## Purpose

This document maps the OWASP Top 10 — the industry-standard list of the most impactful
web application security risks — to the deeper docs in this knowledge base. Use it as a
triage index: given a feature, walk the ten categories and ask "could this change
introduce that risk?" The list referenced here is **OWASP Top 10:2025**, which
supersedes the 2021 edition.

The Top 10 is not a compliance checkbox; it is a prioritized reminder of where real
applications actually break. Most breaches map to one of these ten.

## Why It Matters

The categories barely move between editions — Broken Access Control has led three
editions running — because organizations keep making the same mistakes. That stability
is the point: these are not edge cases, they are the *default* failure modes of web
software. An agent that internally checks every change against these ten will prevent
the large majority of exploitable bugs before they ship. Ignoring the list means
rediscovering, the hard way, risks that the industry catalogued years ago.

## Core Principles

- **Access control is the #1 risk — treat every object reference as an attack.** Most
  breaches are authorization failures, not exotic exploits.
- **Prevention beats detection for these categories.** Every item on this list has a
  well-known, cheap-to-apply preventive control. Apply it by default.
- **Categories overlap; defense is layered.** Injection, misconfiguration, and design
  flaws often coexist. Fixing one is not fixing the request.
- **"Not on the list" is not "safe."** The Top 10 is a floor, not a ceiling — it omits
  many real risks by design.

## Best Practices

The 2025 categories, each with the failure, why it is wrong, and the fix:

- **A01 Broken Access Control** — a user reaches data or actions they should not.
  *Wrong:* trusting a client-supplied id or hidden field. *Fix:* authorize every
  request server-side, deny by default, check ownership on each object. See [authorization](04-authorization.md).
- **A02 Security Misconfiguration** — insecure defaults, verbose errors, open admin
  panels, permissive [CORS](19-cors.md). *Wrong:* shipping framework defaults and debug
  mode to prod. *Fix:* harden by default; set [security headers](22-security-headers.md); disable debug.
- **A03 Software Supply Chain Failures** — a compromised or vulnerable dependency,
  build tool, or artifact. *Wrong:* unpinned deps and unverified build inputs. *Fix:*
  pin, verify, and scan — see [supply chain security](24-supply-chain-security.md), [dependency security](23-dependency-security.md).
- **A04 Cryptographic Failures** — sensitive data exposed by weak or missing crypto.
  *Wrong:* HTTP in transit, plaintext at rest, home-grown ciphers. *Fix:* TLS
  everywhere, vetted algorithms, managed keys — see [encryption](17-encryption.md), [HTTPS](18-https.md).
- **A05 Injection** — untrusted input interpreted as code (SQL, shell, LDAP, XSS).
  *Wrong:* string concatenation into an interpreter. *Fix:* parameterize and encode —
  see [SQL injection](13-sql-injection.md), [command injection](14-command-injection.md), [XSS](11-xss.md).
- **A06 Insecure Design** — the flaw is in the design, not the code; no amount of clean
  implementation fixes it. *Wrong:* skipping threat modeling. *Fix:* model threats and
  build security requirements up front — see [threat modeling](02-threat-modeling.md).
- **A07 Authentication Failures** — weak credentials, guessable sessions, no MFA,
  credential stuffing. *Wrong:* fast hashes, no lockout, forgeable tokens. *Fix:* strong
  hashing, MFA, rate limits — see [authentication](03-authentication.md), [session management](06-session-management.md).
- **A08 Software or Data Integrity Failures** — trusting unverified updates, plugins,
  or deserialized data. *Wrong:* auto-updating from an unsigned source. *Fix:* verify
  signatures, sign artifacts, avoid unsafe deserialization — see [supply chain security](24-supply-chain-security.md).
- **A09 Logging & Alerting Failures** — attacks go unseen because nothing is logged or
  alerted. *Wrong:* no audit trail, no alerts. *Fix:* log security events and alert on
  anomalies — see [monitoring](25-monitoring.md), [incident response](26-incident-response.md).
- **A10 Mishandling of Exceptional Conditions** — errors, timeouts, and edge cases
  handled insecurely (failing open, leaking stack traces). *Wrong:* granting access on
  error. *Fix:* fail closed, return generic errors, handle every branch deliberately.

## Examples

**Good Example** — closing the #1 risk, Broken Access Control

```ts
// Authorize the specific object, not just "is logged in".
async function getInvoice(user, invoiceId) {
  const inv = await invoices.findById(invoiceId);
  if (!inv || inv.ownerId !== user.id) throw new ForbiddenError(); // ownership check
  return inv;                                                      // deny by default
}
```

**Bad Example** — classic IDOR (Insecure Direct Object Reference)

```ts
// Any authenticated user can read ANY invoice by changing the id in the URL:
// the code checks authentication but never authorization/ownership.
async function getInvoice(user, invoiceId) {
  return invoices.findById(invoiceId); // A01 Broken Access Control
}
```

## Common Mistakes

- Treating the Top 10 as a checklist to pass once, rather than a lens for every change.
- Focusing on injection (A05) while ignoring access control (A01), the more common breach.
- Assuming a framework's defaults are secure (A02) without hardening them.
- Ignoring supply chain (A03) because "we didn't write that code" — you still ship it.
- Confusing authentication (A07) with authorization (A01) and fixing the wrong one.

## Production Tips

- Tag security findings and tickets with their OWASP category to reveal recurring weak spots.
- Map your SAST/DAST tooling output to these categories so coverage gaps are visible.
- Re-baseline against the newest edition when OWASP publishes it; categories do shift.

## AI Review Checklist

- A01: Is every object access authorized by ownership/role, server-side?
- A02: Are prod configs hardened (no debug, no default creds, strict CORS/headers)?
- A03/A08: Are dependencies and build artifacts pinned, scanned, and signature-verified?
- A04/A05: Is data encrypted in transit and at rest, and is all input parameterized/encoded?
- A06: Was the feature threat-modeled before implementation?
- A07: Are auth, MFA, hashing, and rate limiting in place?
- A09: Are security events logged and alerted on?
- A10: Do error and edge-case paths fail closed and stay generic?

## Related

- `knowledge/security/27-best-practices.md`
- `knowledge/security/04-authorization.md`
- `knowledge/security/13-sql-injection.md`
- `knowledge/security/24-supply-chain-security.md`
- `knowledge/security/29-security-review.md`
