---
id: accessibility/26-legal-requirements
topic: accessibility
slug: legal-requirements
title: "Legal Requirements"
type: doc
order: 26
status: ready
tags: [accessibility, legal-requirements]
related: [accessibility/23-wcag, accessibility/24-accessibility-testing, accessibility/25-remediation, accessibility/29-documentation, accessibility/02-pour-principles]
when_to_use: "Read before deciding which conformance target to build to, scoping a compliance effort, or answering what standard a product legally owes."
---
# Legal Requirements

## Purpose

This document maps the accessibility laws that turn [WCAG](23-wcag.md) from a best
practice into an obligation, and explains what an engineering team must actually do to
satisfy them. It is a practitioner's orientation, not legal advice: it tells an agent
which standard to build to and why, so conformance is a design input rather than a
post-launch surprise.

Laws almost always point *back* to WCAG as the technical yardstick, so the concrete
target is a WCAG level and version — most commonly **WCAG 2.1 or 2.2, Level AA**.

## Why It Matters

Accessibility is enforced by law across major markets, and enforcement is active. In the
United States, thousands of ADA web-accessibility lawsuits are filed every year; a demand
letter arrives with no warning and settles for real money regardless of intent. In the
EU, the **European Accessibility Act** became enforceable on **28 June 2025**, extending
requirements to private-sector e-commerce, banking, and digital services. "We didn't know"
is not a defense, and a green scanner is not a compliance record.

Building to the standard from the start is dramatically cheaper than remediating under a
legal deadline. Treating the target as a real requirement — with an owner, a test, and a
paper trail — is what converts legal exposure into a solved engineering problem.

## Core Principles

- **WCAG is the de facto legal standard.** Nearly every law references WCAG success
  criteria. Build to a named version and level; "accessible" without a target is untestable.
- **AA is the working baseline.** Most regulations require Level AA. Treat AA as the floor
  and A as non-negotiable; pursue AAA selectively where the audience demands it.
- **Know your jurisdiction and sector.** The exact law depends on where you operate and
  what you sell — public sector, e-commerce, and finance carry the strictest duties.
- **Conformance is continuous.** Compliance is a state you maintain per release, not a
  certificate you earn once. Every change can break it.
- **Document conformance.** A tested, dated record ([documentation](29-documentation.md))
  is your evidence; undocumented conformance is indistinguishable from none in a dispute.

## Best Practices

- Adopt **WCAG 2.2 Level AA** as the default target unless a specific law names another
  version; it supersets 2.1 AA and covers the criteria regulators cite today.
- Identify the laws that apply before you design. Common ones:
  - **ADA (US)** — courts apply it to commercial websites and apps; WCAG AA is the yardstick.
  - **Section 508 (US federal)** — WCAG 2.0 AA via the 2017 refresh; required for procurement.
  - **ADA Title II (US state/local government)** — DOJ rule requires WCAG 2.1 AA, phasing in
    through 2026–2027.
  - **EN 301 549 (EU)** — the harmonized standard behind the EAA and public-sector directive;
    tracks WCAG AA.
  - **AODA (Ontario)** and **Accessibility Canada (ACA)** — WCAG AA for covered organizations.
- Maintain an **Accessibility Conformance Report (ACR / VPAT)** stating what you conform to
  and where gaps remain; procurement and enterprise buyers require it.
- Publish an **accessibility statement** with your target standard, a contact for barriers,
  and the date last assessed. It is both good faith and, in some jurisdictions, expected.
- Re-assess on a schedule and after major releases; a conformance claim decays as the
  product changes.

## Examples

**Good Example** — a concrete, testable, dated conformance claim

```markdown
# Accessibility Statement

This application conforms to **WCAG 2.2 Level AA**.

- Last audited: 2026-05-12 (automated axe-core + manual NVDA/VoiceOver review)
- Known gaps: the legacy report export is partially conformant; fix tracked as A11Y-482,
  targeted for the 2026-08 release. An accessible CSV alternative is available today.
- Report a barrier: accessibility@example.com — we respond within 5 business days.
```

**Bad Example** — a vague claim that satisfies no law and proves nothing

```markdown
# Accessibility

We care deeply about accessibility and our site is fully accessible to everyone.
<!-- No standard, no version, no level, no date, no scope, no contact.
     Untestable, unverifiable, and — because "fully accessible" is almost
     never true — actively misleading in a dispute. -->
```

## Common Mistakes

- Claiming "accessible" or "ADA compliant" with no WCAG version and level named.
- Assuming a passing automated scan constitutes legal compliance; it covers ~40% of criteria.
- Ignoring the EAA because the company is US-based, despite serving EU customers.
- Treating conformance as a launch milestone and never re-assessing after changes.
- Publishing an overreaching "fully accessible" statement that a single defect contradicts.
- Having no documented ACR/VPAT when an enterprise or government buyer requests one.
- Confusing "we ran a tool" with "we have evidence of conformance we can produce."

## Production Tips

- Store the ACR/VPAT and audit reports in the repo or a known location, dated and
  versioned, so they can be produced on request without a scramble.
- Assign an owner for the conformance target the same way you assign a security owner;
  an unowned requirement is an unmet one.
- When counsel names a specific standard for your market, encode it as the CI test target
  so the legal requirement and the automated gate are literally the same thing.

## AI Review Checklist

- Is the conformance target a **named WCAG version and level** (e.g., 2.2 AA), not "accessible"?
- Have the **applicable laws** for the product's jurisdictions and sectors been identified?
- Does an **accessibility statement** exist with target, scope, contact, and assessment date?
- Is an **ACR/VPAT** maintained and current for procurement and enterprise buyers?
- Is conformance **re-assessed** on a schedule and after major releases, not just at launch?
- Are conformance claims **supported by documented, dated evidence**, not just a tool run?

## Related

- `knowledge/accessibility/23-wcag.md`
- `knowledge/accessibility/24-accessibility-testing.md`
- `knowledge/accessibility/25-remediation.md`
- `knowledge/accessibility/29-documentation.md`
- `knowledge/accessibility/02-pour-principles.md`
