---
id: accessibility/23-wcag
topic: accessibility
slug: wcag
title: "WCAG"
type: doc
order: 23
status: ready
tags: [accessibility, wcag]
related: [accessibility/02-pour-principles, accessibility/26-legal-requirements, accessibility/20-testing-tools, accessibility/21-axe, accessibility/27-best-practices]
when_to_use: "Read before citing a conformance level, agreeing to an accessibility acceptance criterion, or scoping a compliance target."
---
# WCAG

## Purpose

This document defines the Web Content Accessibility Guidelines (WCAG) — the international
standard that every accessibility requirement in this knowledge base ultimately maps to.
It explains WCAG's structure (principles → guidelines → success criteria), the meaning of
conformance levels A/AA/AAA, which version and level to target in 2026, and how to read a
success criterion so you know exactly what "passes."

WCAG is the vocabulary you use to make accessibility *verifiable*. "Make it accessible"
is not a spec; "meet WCAG 2.2 Level AA" is. This document lets an agent translate a
requirement into concrete, testable success criteria.

## Why It Matters

WCAG is not just guidance — it is the standard written into law. The EU Accessibility Act
(in force June 2025), the US ADA / Section 508, and the UK/EU EN 301 549 all reference
WCAG, almost always **Level AA**, as the conformance bar. Getting the version and level
right is therefore both an engineering and a legal decision (see
[legal requirements](26-legal-requirements.md)). Just as important, WCAG turns a fuzzy
goal into a finite list of pass/fail criteria you can test, assign, and sign off — which
is the only way accessibility work becomes trackable rather than aspirational.

## Core Principles

- **POUR is the top of the tree.** Every criterion sits under one of four principles:
  **P**erceivable, **O**perable, **U**nderstandable, **R**obust (see
  [POUR principles](02-pour-principles.md)). If you cannot place a requirement under one,
  question it.
- **Three levels, cumulative.** **A** = minimum/blocking, **AA** = the standard bar most
  laws require, **AAA** = enhanced and often impractical site-wide. AA includes all of A.
- **AA is the target.** Aim for WCAG **2.2 Level AA** in 2026 unless a contract or law
  names otherwise. AAA is applied selectively to critical flows, not mandated everywhere.
- **Success criteria are testable statements.** Each SC (e.g. 1.4.3 Contrast) has a
  precise pass condition. Conformance means meeting *every* applicable A and AA criterion,
  not most of them.
- **Newest applicable version wins.** WCAG is backward-compatible; 2.2 adds criteria to
  2.1. Target the latest version your obligations reference — 2.2 as of 2026.

## Best Practices

- State the target explicitly in acceptance criteria: **"WCAG 2.2 AA"**, and cite the
  specific SC numbers a feature must meet (e.g. 1.4.3, 2.4.7, 2.5.8), so "done" is testable.
- Know the criteria your work touches most: **1.1.1** (non-text alt), **1.4.3**
  (contrast 4.5:1 text / 3:1 large), **1.4.11** (non-text contrast 3:1), **2.1.1**
  (keyboard), **2.4.7** (focus visible), **4.1.2** (name/role/value), **4.1.3** (status
  messages). These recur across nearly every UI.
- Learn the WCAG 2.2 additions and apply them: **2.4.11 Focus Not Obscured**, **2.5.7
  Dragging Movements** (offer a non-drag alternative), **2.5.8 Target Size (Minimum)**
  (24×24 CSS px), **3.3.7 Redundant Entry**, **3.3.8 Accessible Authentication**.
- Map each criterion to *how* it is verified — automated (axe covers ~a third), manual
  keyboard, or screen reader — because most SCs are not machine-checkable.
- Use the official **Understanding** and **Techniques** documents for the exact pass
  condition rather than paraphrasing; wording precision decides conformance.
- Do not claim conformance from tools alone. A conformance claim requires that every
  applicable A/AA criterion is met and verified, most of them by a human.

## Examples

**Good Example** — a requirement pinned to specific, testable criteria

```markdown
Acceptance criteria — "Add to cart" button (target: WCAG 2.2 AA)
- 1.4.3  Text contrast ≥ 4.5:1 against its background        [automated + manual]
- 1.4.11 Button/border contrast ≥ 3:1                        [automated]
- 2.1.1  Operable with keyboard alone (Enter/Space)          [manual keyboard]
- 2.4.7  Visible focus indicator when tabbed to              [manual keyboard]
- 2.5.8  Hit target ≥ 24×24 CSS px                           [manual/measured]
- 4.1.2  Exposes name, role="button", and pressed state      [screen reader]
# Each line is a pass/fail check with a named verification method.
```

**Bad Example** — an untestable, unpinned target

```markdown
Acceptance criteria — "Add to cart" button
- Must be "fully accessible" and "compliant"   <!-- no version, no level -->
- Passes Lighthouse                            <!-- a subset score, not conformance -->
# No success criteria, no verification method: nobody can prove this done or not-done.
```

## Common Mistakes

- Saying "accessible" or "compliant" without naming a version and level — nothing to test.
- Targeting AAA blanket-wide; several AAA criteria are impractical or conflicting across a
  whole site, so it stalls delivery. Apply AAA to critical paths only.
- Assuming Level A is enough; law and contracts almost always require AA.
- Citing an outdated version (2.0/2.1) when 2.2 is the current, backward-compatible target.
- Believing automated tools prove WCAG conformance — they cover a minority of criteria.
- Treating criteria as guidelines to "consider" rather than pass/fail requirements to meet.

## Production Tips

- Keep a living conformance matrix: each applicable SC, its status, and how it was
  verified. This is what an audit or a legal request will ask for.
- Reference SC numbers in code review and PR templates for accessibility-relevant changes
  so the standard is enforced continuously, not at an end-of-cycle audit.
- When a criterion cannot be met, document the specific SC, the barrier, and the planned
  remediation — a known, tracked gap is defensible; an untracked one is not.

## AI Review Checklist

- Is the conformance target stated as a specific version and level (WCAG 2.2 AA)?
- Are requirements pinned to named success criteria with a verification method each?
- Is Level AA (not just A) met for every applicable criterion?
- Are the WCAG 2.2 additions (2.4.11, 2.5.7, 2.5.8, 3.3.7, 3.3.8) considered where relevant?
- Is conformance verified by manual testing, not inferred from tool scores alone?
- Are known gaps documented by SC number with a remediation plan?

## Related

- `knowledge/accessibility/02-pour-principles.md`
- `knowledge/accessibility/26-legal-requirements.md`
- `knowledge/accessibility/20-testing-tools.md`
- `knowledge/accessibility/21-axe.md`
- `knowledge/accessibility/27-best-practices.md`
