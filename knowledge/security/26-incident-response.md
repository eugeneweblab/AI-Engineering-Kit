---
id: security/26-incident-response
topic: security
slug: incident-response
title: "Incident Response"
type: doc
order: 26
status: ready
tags: [security, incident-response, clearCookie, logout, send]
related: [security/25-monitoring, security/16-secrets-management, security/03-authentication, security/23-dependency-security, security/29-security-review]
when_to_use: "Read before writing runbooks, break-glass procedures, or breach-handling code paths."
---
# Incident Response

## Purpose

This document defines how to respond when a security control has failed: a breach,
a leaked secret, an exploited vulnerability, or active abuse. It covers the phases of
response and the code-level affordances — kill switches, revocation, forced logout —
that make a fast response possible.

Incident response is not a document you write after the fire starts. It is a capability
you build in advance: the ability to detect (via [monitoring](25-monitoring.md)),
contain, eradicate, and recover — calmly, under pressure, without making it worse.

## Why It Matters

During an incident, the two ways to lose are moving too slowly and moving recklessly.
Slow response lets an attacker exfiltrate more, pivot deeper, and destroy evidence.
Reckless response — deleting the compromised host before imaging it, rotating the wrong
key, tipping off the attacker — destroys the forensic trail and can worsen the breach.
A rehearsed plan and pre-built controls (revocation, isolation) collapse the decision
time from hours to minutes, and that time difference is usually the difference between
a contained event and a headline. The engineering decisions made *before* an incident
determine how badly it goes.

## Core Principles

- **Contain before you clean.** Stop the bleeding — isolate the host, revoke the token,
  disable the account — before investigating root cause. Contained damage is bounded damage.
- **Preserve evidence.** Snapshot and image before you wipe. Logs, memory, and disk are
  the only record of what happened; destroying them blinds the investigation.
- **Assume secrets are burned.** If a credential *may* have leaked, rotate it. Treating
  "maybe" as "no" is how breaches recur.
- **Communicate on a known-clean channel.** If the corporate systems may be compromised,
  coordinate out-of-band. Don't discuss the breach where the attacker can read it.
- **One incident commander.** A single owner drives decisions; everyone else executes.
  Committees are slow, and speed is the whole point.

## Best Practices

- Build **revocation into the design**: server-side session invalidation, token
  denylists, and per-user forced logout. You cannot revoke what you never built to revoke.
- Provide a **kill switch** per risky feature (flag-gated) so a compromised path can be
  disabled without a full deploy.
- Keep an up-to-date runbook: who to call, how to rotate each secret, how to isolate a
  service, how to enable read-only mode.
- Rotate leaked [secrets](16-secrets-management.md) immediately and confirm the old value
  is rejected everywhere — rotation without invalidation is theater.
- Practice with tabletop exercises and game days so the first real incident is not the
  first rehearsal.
- Define severity levels and escalation paths in advance; ambiguity wastes minutes you
  don't have.
- Write a blameless post-incident review that fixes the *systemic* cause, not the person.

## Examples

**Good Example** — a built-in containment control, ready before the incident

```ts
// Break-glass: revoke every active session for a user in one call.
// This exists BEFORE any incident so responders can act in seconds.
async function revokeAllSessions(userId: string, reason: string) {
  await sessions.deleteByUser(userId);        // server-side sessions gone immediately
  await tokenDenylist.addUserTokens(userId);  // outstanding JWTs rejected until expiry
  logger.warn({ event: "ir.session.revoked", userId, reason, ts: nowUtc() });
}
// A feature flag lets us disable the exploited endpoint without a deploy:
if (!flags.isEnabled("checkout.coupon")) return res.status(503).send("temporarily disabled");
```

**Bad Example** — no revocation, evidence destroyed, secret not rotated

```ts
// "Logout" only clears the client cookie; the server session is still valid,
// so a stolen token keeps working through the entire incident.
function logout(res) { res.clearCookie("sid"); }

// During the incident, an engineer deletes the compromised container to "clean up"
// — destroying memory and disk evidence — and never rotates the leaked API key,
// so the attacker simply reconnects an hour later.
```

## Common Mistakes

- No server-side revocation, so "logging everyone out" is impossible mid-breach.
- Wiping or terminating compromised hosts before imaging them, erasing all forensics.
- Assuming a possibly-leaked secret is fine because there is "no proof" it was used.
- Discussing the incident on the same systems the attacker may control.
- No named incident commander, so decisions stall in a group chat.
- Post-mortems that assign blame to a person instead of fixing the system that allowed it.
- Notifying regulators/customers late because no one knew the legal clock (e.g. 72-hour) had started.

## Production Tips

- Maintain a printed/offline copy of the runbook and contact tree — the incident may
  take down the systems that host them.
- Pre-authorize break-glass access with strong audit logging, so responders don't wait
  on approvals mid-incident but every use is reviewed after.
- Integrate secret-scanning and dependency alerts ([dependency security](23-dependency-security.md))
  as incident *triggers*, not just reports.
- Track detection-to-containment time as a metric; drive it down deliberately.

## AI Review Checklist

- Can every user session be revoked server-side and forcibly logged out?
- Is there a per-feature kill switch (flag) to disable an exploited path without a deploy?
- On a possible secret leak, is rotation triggered and the old value confirmed rejected?
- Does the runbook name an incident commander, escalation path, and rotation steps?
- Are compromised hosts imaged/snapshotted before being wiped?
- Are security detections wired to actually page an on-call human?
- Is there a defined severity model and a breach-notification legal clock?

## Related

- `knowledge/security/25-monitoring.md`
- `knowledge/security/16-secrets-management.md`
- `knowledge/security/03-authentication.md`
- `knowledge/security/23-dependency-security.md`
- `knowledge/security/29-security-review.md`
