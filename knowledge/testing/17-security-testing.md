---
id: testing/17-security-testing
topic: testing
slug: security-testing
title: "Security Testing"
type: doc
order: 17
status: ready
tags: [testing, security-testing, toBe, toHaveProperty, encodeURIComponent, login]
related: [testing/12-api-testing, testing/04-e2e-testing, testing/21-cicd, testing/25-production-testing, testing/03-integration-testing]
when_to_use: "Read before adding automated tests or pipeline checks that verify a system resists abuse and known vulnerability classes."
---
# Security Testing

## Purpose

This document defines how to test that a system *resists abuse*: authentication and
authorization enforcement, input handling, injection resistance, and known-vulnerable
dependencies. It is the testing view of security — turning "we should be secure" into
automated, repeatable checks. It does not replace a manual audit or penetration test; it
catches the regressions and known classes that must never reach production.

A security test asserts that an attacker's request *fails* — the forbidden action is
denied, the malicious input is rejected, the secret is not leaked. Absence of a crash is
not a pass.

## Why It Matters

Security bugs are silent and total: the app works perfectly for legitimate users while an
attacker reads other tenants' data or escalates to admin. Functional tests never find
these because they only exercise allowed behavior. Worse, security regressions creep in
through ordinary changes — a new endpoint that forgot the authz check, a query built by
string concatenation, a dependency bumped to a vulnerable version. Automated security
tests make the *negative* space — what must be impossible — a first-class, enforced part
of the suite, so an insecure change fails CI instead of shipping.

## Core Principles

- **Test that the attack fails, explicitly.** For every protected action, assert that an
  unauthenticated and an unauthorized actor is denied — with the right status, not a 500.
- **Automate the known classes; leave novel exploits to humans.** SAST, dependency
  scanning, and secret scanning cover the OWASP staples cheaply; a pen-test finds what
  tools cannot.
- **Authorization is per-object, not per-route.** The dangerous bug is a valid user
  reaching *another user's* object (IDOR). Test cross-tenant access directly.
- **Never trust input; prove it.** Feed injection and traversal payloads and assert they
  are neutralized — not merely that nothing crashed.
- **Fail the build on new findings.** A scanner whose output no one gates on is
  documentation, not a control. Break CI on a new high-severity issue.

## Best Practices

- Layer the pipeline: SAST (static analysis) on code, SCA (dependency/CVE scanning) on the
  lockfile, secret scanning on the diff, and DAST (dynamic scanning) against a running
  build. Each catches what the others miss.
- Write per-endpoint authz tests covering the full matrix: anonymous, wrong-user, and
  correct-user — and assert the exact `401`/`403`, not just "not 200."
- Add explicit IDOR tests: user A must receive `403`/`404` for user B's resource IDs.
  This is the single most common and most damaging web vulnerability.
- Test injection resistance with real payloads (SQLi, XSS, command, path traversal) and
  assert the output is escaped or the request rejected — never assert only on status.
- Pin and scan dependencies on every build; fail on known criticals and keep the scanner's
  database current. Most breaches exploit a known, unpatched CVE.
- Scan for committed secrets on every push and rotate anything found — a secret in git
  history is compromised even after deletion.
- Keep security tests deterministic and self-contained so they gate CI reliably; a flaky
  security test gets disabled, which is worse than not having it.

## Examples

**Good Example** — asserts the attack is denied, per object

```ts
import request from "supertest";
import { app } from "../app";

it("denies a user access to another user's order (IDOR)", async () => {
  const tokenA = await login("alice");
  const bobsOrderId = await seedOrderFor("bob");

  const res = await request(app)
    .get(`/orders/${bobsOrderId}`)
    .set("Authorization", `Bearer ${tokenA}`);

  // Assert the forbidden action FAILS with the right status — not merely "no crash".
  expect(res.status).toBe(404);            // 404 avoids confirming the id exists
  expect(res.body).not.toHaveProperty("total"); // and leaks none of Bob's data
});

it("rejects a SQL-injection payload in search", async () => {
  const res = await request(app).get(`/search?q=${encodeURIComponent("'; DROP TABLE users;--")}`);
  expect(res.status).toBe(200);            // parameterized query treats it as literal text
  expect(await usersTableExists()).toBe(true); // prove the injection did nothing
});
```

**Bad Example** — asserts only that nothing broke

```ts
it("search handles weird input", async () => {
  const res = await request(app).get("/search?q='; DROP TABLE users;--");
  // "Not 500" says nothing about whether the injection ran. A vulnerable endpoint that
  // silently executes the payload and returns 200 passes this test.
  expect(res.status).not.toBe(500);
});
```

## Common Mistakes

- Asserting only on status code or "no crash" instead of proving the attack had no effect.
- Testing route-level auth but not per-object authorization, missing IDOR entirely.
- Running scanners whose findings gate nothing, so vulnerabilities accumulate unblocked.
- Feeding sanitized inputs to "security" tests, which then prove nothing about real payloads.
- Testing the happy authorized path and never the anonymous or wrong-user path.
- Letting the dependency-scan database go stale, so new CVEs pass silently.
- Skipping secret scanning and assuming a deleted secret is gone — git history keeps it.

## Production Tips

- Track findings against a policy (for example OWASP ASVS) so coverage is a checklist, not
  a vibe, and gaps are visible.
- Run DAST against ephemeral, production-like builds in CI; run periodic manual
  penetration tests for logic flaws tools cannot model.
- Treat the security suite as release-gating: a new high-severity finding blocks the
  deploy, and exceptions are time-boxed and tracked, never silent.

## AI Review Checklist

- For each protected action, is there a test asserting anonymous and wrong-user requests
  are denied with the correct status?
- Are per-object (IDOR) access attempts tested across tenants/users?
- Do injection tests assert the payload was neutralized, not merely that status was not 500?
- Do SAST, dependency, and secret scanners run in CI and fail the build on new findings?
- Are dependencies pinned and scanned against a current CVE database every build?
- Are security tests deterministic so they can gate the pipeline without flaking?

## Related

- `knowledge/testing/12-api-testing.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/21-cicd.md`
- `knowledge/testing/25-production-testing.md`
- `knowledge/testing/03-integration-testing.md`
