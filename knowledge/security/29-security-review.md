---
id: security/29-security-review
topic: security
slug: security-review
title: "Security Review"
type: doc
order: 29
status: ready
tags: [security, security-review]
related: [security/28-owasp-top10, security/27-best-practices, security/02-threat-modeling, security/09-input-validation, security/04-authorization]
when_to_use: "Read before reviewing a pull request or design for security, or defining a review gate."
---
# Security Review

## Purpose

This document defines how to review code and designs for security — the systematic
pass an agent or engineer makes to find vulnerabilities *before* they ship. It gives
a repeatable method (trace the data, question the trust boundaries) rather than a
vague instruction to "look for security issues."

A security review is not a re-read of the diff hoping something jumps out. It is a
directed search for specific, known failure modes at specific, known locations.

## Why It Matters

Vulnerabilities are cheapest to fix at review time and most expensive after a breach —
often by a factor of hundreds. Yet most reviews focus on style and logic and glance
past security, because reviewers don't know *where* to look. A structured review closes
that gap: it turns "did anyone check this for security?" — a question that usually gets
an uncomfortable silence — into a documented, repeatable gate. For an AI agent, the
review method is the difference between rubber-stamping a diff and actually catching
the injection hidden in it.

## Core Principles

- **Follow the data.** Trace every piece of external input from where it enters to
  where it is used (a query, a template, a shell, a file path). Vulnerabilities live on
  that path.
- **Question every trust boundary.** Where does untrusted become trusted? That crossing
  must have validation, authorization, or encoding — verify it does.
- **Assume the diff is incomplete.** A change to one endpoint may weaken another. Review
  the *effect*, not just the lines.
- **Prove the negative path.** Don't just confirm the happy path works — confirm the
  attack path fails (wrong user, malformed input, missing token).
- **A finding needs a concrete exploit.** "This looks insecure" is not a finding.
  "An attacker can pass id=2 to read another user's record" is.

## Best Practices

- Review against the [OWASP Top 10](28-owasp-top10.md) categories explicitly — walk the
  list, don't freestyle.
- Check that all external input is validated server-side against an allowlist — see [input validation](09-input-validation.md).
- Verify authorization on every object access, not just authentication — see [authorization](04-authorization.md).
- Grep the diff for dangerous patterns: string-built SQL/shell, `eval`, `dangerouslySetInnerHTML`,
  `verify=false`, `CORS: *`, hardcoded secrets, disabled auth.
- Confirm secrets are absent from code, config, and test fixtures.
- Check error handling fails closed and does not leak stack traces or internals.
- For new endpoints, confirm rate limiting, auth, and input schema are all present.
- Require a [threat model](02-threat-modeling.md) for changes that add a new trust boundary
  (new external input, new integration, new auth path).
- Automate the mechanical checks (SAST, secret scan, dependency scan) so human review
  focuses on logic and authorization — machines miss intent, humans miss volume.

## Examples

**Good Example** — a review comment that names the exploit and the fix

```md
🔴 Security — Broken Access Control (A01)
File: routes/orders.ts:42
`getOrder(req.params.id)` loads the order by id with no ownership check.
Exploit: an authenticated user changes the URL id and reads any customer's order (IDOR).
Fix: `if (order.userId !== req.user.id) return res.sendStatus(403);` before returning.
Blocking until resolved.
```

**Bad Example** — a non-actionable review comment

```md
This part looks a bit unsafe, maybe add some validation?
<!-- No location, no exploit, no concrete fix. The author can't act on it,
     so it gets waved through and the vulnerability ships. -->
```

## Common Mistakes

- Reviewing style and logic but never explicitly asking "what's the security impact?"
- Confirming the feature works without ever testing the attack path.
- Vague findings ("looks insecure") that can't be acted on and get dismissed.
- Reviewing only the changed lines, missing that the change weakens a caller elsewhere.
- Trusting that "the framework handles it" without verifying the specific control is on.
- Letting automated scanner passes stand in for reasoning about authorization and design.

## Production Tips

- Make security review a required gate on changes touching auth, payments, PII, file
  upload, or deserialization — label those PRs so they can't skip it.
- Keep a short repo-specific review checklist next to the code; generic checklists get ignored.
- Track findings by OWASP category over time to see which weaknesses recur, then fix the
  root cause (better defaults, safer wrappers) rather than the symptom.

## AI Review Checklist

- Was each piece of external input traced from entry to sink (query, template, shell, path)?
- Does every trust-boundary crossing validate, authorize, or encode as appropriate?
- Is authorization checked per object, not just authentication?
- Was the diff grepped for dangerous patterns (string-built SQL/shell, eval, disabled TLS/CORS, secrets)?
- Does each finding include a concrete exploit and a concrete fix?
- Were the attack/negative paths verified to fail, not just the happy path?
- Was the change checked against the OWASP Top 10 categories?

## Related

- `knowledge/security/28-owasp-top10.md`
- `knowledge/security/27-best-practices.md`
- `knowledge/security/02-threat-modeling.md`
- `knowledge/security/09-input-validation.md`
- `knowledge/security/04-authorization.md`
