---
id: accessibility/29-documentation
topic: accessibility
slug: documentation
title: "Accessibility Documentation"
type: doc
order: 29
status: ready
tags: [accessibility, documentation]
related: [accessibility/26-legal-requirements, accessibility/24-accessibility-testing, accessibility/25-remediation, accessibility/27-best-practices, accessibility/23-wcag]
when_to_use: "Read before writing an accessibility statement, a VPAT/ACR, component a11y notes, or documenting a known accessibility gap."
---
# Accessibility Documentation

## Purpose

This document defines what accessibility documentation a product needs, who reads it, and
how to write it so it is truthful and useful rather than decorative. It covers the
outward-facing accessibility statement and ACR/VPAT, and the inward-facing component notes
and known-issues log that keep a team's conformance honest between releases.

Documentation is the connective tissue between [legal requirements](26-legal-requirements.md)
(what you must claim), [testing](24-accessibility-testing.md) (what you verified), and
[remediation](25-remediation.md) (what remains).

## Why It Matters

Undocumented conformance is unfalsifiable — and in a dispute or a procurement review, an
unfalsifiable claim is worthless. Buyers, auditors, and regulators do not run your test
suite; they read your ACR, your statement, and your known-issues log. Those documents are
the evidence that conformance is real and current.

Internally, documentation is how accessibility survives staff turnover and refactors. A
component's keyboard model and ARIA contract, written down, is a design constraint the next
developer must respect; left in one person's head, it is a regression waiting to happen.
Honest documentation also builds trust: an accurate "known gap with a fix date" reads far
better — legally and reputationally — than an overreaching "fully accessible."

## Core Principles

- **Claim only what you tested.** Every conformance statement must trace to a dated test or
  audit. Aspirational claims are liabilities, not marketing.
- **Be specific and testable.** Name the standard, version, level, scope, and date. "We
  care about accessibility" documents nothing.
- **Disclose gaps honestly.** A dated, tracked known-issue is a sign of maturity; a hidden
  one is a landmine. Include the accessible alternative where one exists.
- **Keep it current.** A conformance document is only as true as its last review. Re-date it
  when you re-assess, and treat a stale claim as an inaccurate one.
- **Write for the reader.** Statements for users and buyers, ACR/VPAT for procurement,
  component notes for developers. Each audience needs different detail.

## Best Practices

- Publish an **accessibility statement** with: the target standard (e.g., WCAG 2.2 AA),
  scope, date last assessed, known limitations, and a **contact** for reporting barriers.
- Maintain an **ACR (Accessibility Conformance Report), commonly a VPAT**, mapping each
  applicable success criterion to *Supports / Partially Supports / Does Not Support* with
  notes. Enterprise and government buyers require it.
- Keep a **known-issues log** in the repo: each entry has impact, affected area, a
  reproduction, an accessible alternative if any, and a target fix release.
- Document each shared component's **accessibility contract**: its role, keyboard model,
  required props (labels), and states — so consumers use it correctly and reviewers can check it.
- Record the **test method** behind a claim (tools, screen readers, browsers, date) so the
  evidence is reproducible, not a bare assertion.
- **Version and date** every document; when you re-audit, update the date even if nothing
  changed, so readers know it was reviewed.

## Examples

**Good Example** — a component accessibility note a reviewer can enforce

```markdown
## <Combobox> accessibility contract
- Role: WAI-ARIA combobox; `aria-expanded` reflects the listbox state.
- Name: REQUIRED — pass `label` or `aria-label`; the component throws in dev if absent.
- Keyboard: Down/Up move the active option; Enter selects; Escape closes and keeps the text.
- Announcements: result count is announced via a `polite` live region on each query.
- Verified: NVDA+Firefox, VoiceOver+Safari — 2026-06-30. Known gaps: none.
```

**Bad Example** — a statement that documents nothing and overclaims

```markdown
## Accessibility
Our product is 100% accessible and fully WCAG compliant.
<!-- No version, no level, no scope, no date, no test method, no contact.
     "100%" and "fully" are almost certainly false, so a single real defect
     turns this from marketing into evidence against you. -->
```

## Common Mistakes

- Publishing "fully accessible" / "100% compliant" claims that any single defect disproves.
- Stating conformance with no standard version, level, scope, date, or test method.
- Hiding known issues instead of disclosing them with an alternative and a fix date.
- Letting the statement and ACR go stale while the product keeps changing.
- Documenting conformance for users but keeping no component contracts for developers.
- Having no ACR/VPAT ready when an enterprise or government buyer asks.
- Recording a claim with no reproducible evidence behind it.

## Production Tips

- Store the statement, ACR/VPAT, and known-issues log in the repo, versioned, so they change
  in the same pull requests as the code they describe and never drift.
- Generate part of the component contract from tests: if the keyboard test enumerates the
  keys, the doc can cite it, keeping documentation and behavior in lockstep.
- Add "update the accessibility docs" to the definition of done for any change that alters a
  documented behavior, so the paper trail stays accurate by process, not memory.

## AI Review Checklist

- Does the **accessibility statement** name standard, version, level, scope, date, and a contact?
- Is an **ACR/VPAT** maintained and current, mapping criteria to support levels with notes?
- Are **known issues** disclosed with impact, an accessible alternative, and a fix target?
- Does every conformance claim trace to a **dated, reproducible test method**?
- Do shared components have a documented **accessibility contract** (role, keyboard, name, states)?
- Are the documents **versioned and dated**, and updated alongside the code they describe?

## Related

- `knowledge/accessibility/26-legal-requirements.md`
- `knowledge/accessibility/24-accessibility-testing.md`
- `knowledge/accessibility/25-remediation.md`
- `knowledge/accessibility/27-best-practices.md`
- `knowledge/accessibility/23-wcag.md`
