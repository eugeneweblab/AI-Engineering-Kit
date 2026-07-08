---
id: security/02-threat-modeling
topic: security
slug: threat-modeling
title: "Threat Modeling"
type: doc
order: 2
status: ready
tags: [security, threat-modeling]
related: [security/01-security-fundamentals, security/03-authentication, security/04-authorization, security/29-security-review]
when_to_use: "Read when designing a new feature or system, before choosing which security controls to build."
---
# Threat Modeling

## Purpose

This document defines how to decide *what* to defend before writing defensive code.
Threat modeling is the structured act of asking: what are we building, what can go
wrong, and what will we do about it? It turns "be secure" — which is not actionable —
into a concrete list of threats and the specific controls that address them.

Do this at design time. A threat model built after the code is written mostly
documents mistakes; one built before it shapes the design so the mistakes never exist.

## Why It Matters

You cannot defend everything equally, and trying to spreads effort so thin that the
real risks go uncovered. Threat modeling directs effort to where attackers actually
go: the trust boundaries where untrusted data crosses into trusted code. It is the
cheapest security activity per bug prevented, because a design change costs a
conversation while the same fix after launch costs a migration. It also produces a
shared artifact reviewers and future agents can check the code against.

## Core Principles

- **Model the system as data crossing trust boundaries.** Draw where data flows and
  mark every point where it moves from less-trusted to more-trusted (client→server,
  service→service, user→admin). Threats live on those boundaries.
- **Enumerate threats systematically, don't brainstorm.** Use STRIDE per element:
  **S**poofing, **T**ampering, **R**epudiation, **I**nformation disclosure,
  **D**enial of service, **E**levation of privilege. Walking the list finds threats
  intuition skips.
- **Assume a capable, motivated attacker.** Model who would attack this and what they
  can do (an authenticated user, a malicious insider, a network observer), not a
  cartoon hacker. Design for the realistic worst case.
- **Rank by risk, then decide a response.** For each threat, estimate impact ×
  likelihood, then choose: **mitigate** (add a control), **accept** (document why),
  **transfer** (insurance, a provider), or **eliminate** (remove the feature).
- **A threat model is a living document.** Revisit it when the design, data
  sensitivity, or attacker incentives change. A stale model gives false confidence.

## Best Practices

- Time-box it. A one-hour session with a diagram and the STRIDE list catches most
  high-impact issues; perfect is the enemy of done here.
- Focus on the assets that matter: credentials, PII, payment data, and anything that
  grants privilege. Not every field needs a threat.
- Map each identified threat to a concrete control and the doc that governs it (e.g.
  tampering on a JWT → [JWT](07-jwt.md); spoofing at login → [Authentication](03-authentication.md)).
- Record accepted risks explicitly, with the reason and who accepted them. Silent
  acceptance is indistinguishable from an oversight.
- Feed the output into the [Security Review](29-security-review.md): the model is the
  checklist the review runs against.

## Examples

**Good Example** — a STRIDE-driven threat table for a file-download endpoint

```text
Element: GET /files/:id  (authenticated user → object storage)
Trust boundary: client → app server → storage

Threat (STRIDE)          | Risk | Control
-------------------------|------|-------------------------------------------
Spoofing (S)             | High | Require valid session; re-auth on every call
Tampering with :id (T)   | High | Authorize: user must own the file object
Info disclosure (I)      | High | Return 404 (not 403) for others' files
Elevation via ../ (E)    | Med  | Resolve to an ID, never build a filesystem path
Denial of service (D)    | Med  | Rate-limit per user; cap object size
Repudiation (R)          | Low  | Log download events with user id + object id
```

**Bad Example** — a vague, unactionable "assessment"

```text
Security review: The file endpoint should be secure. We use HTTPS and
authentication, so users cannot access files they should not. Looks fine.
```

The bad version names no boundaries, walks no threat list, and produces no control an
agent can implement or a reviewer can verify. It would miss the IDOR (one user reading
another's file by changing `:id`) entirely.

## Common Mistakes

- Skipping the model because "we'll add security later" — later, the design is fixed.
- Modeling only outsider attackers, ignoring authenticated users and insiders (the
  source of most IDOR and privilege bugs).
- Producing prose ("should be secure") instead of a threat→control mapping.
- Listing threats but never assigning a response, so nothing changes in the code.
- Never revisiting the model after the feature grows new endpoints or data.
- Treating the diagram as the deliverable; the deliverable is the list of decisions.

## Production Tips

- Keep threat models in the repo next to the design doc, in version control, so they
  diff with the code they describe.
- Add "threat model updated?" to the PR template for changes that add endpoints or
  handle new sensitive data.
- Turn recurring threats (IDOR, missing rate limit) into reusable checklist items so
  every model does not start from scratch.

## AI Review Checklist

- Are all trust boundaries in the design identified and diagrammed?
- Was STRIDE (or equivalent) walked for each element, not just brainstormed?
- Does every high/medium threat map to a concrete, implemented control?
- Are authenticated-user and insider threats modeled, not just outsiders?
- Are accepted risks documented with a reason and an owner?
- Does the model match the current design, or is it stale?

## Related

- `knowledge/security/01-security-fundamentals.md`
- `knowledge/security/03-authentication.md`
- `knowledge/security/04-authorization.md`
- `knowledge/security/29-security-review.md`
- `knowledge/security/28-owasp-top10.md`
