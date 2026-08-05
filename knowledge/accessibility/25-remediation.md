---
id: accessibility/25-remediation
topic: accessibility
slug: remediation
title: "Remediation"
type: doc
order: 25
status: ready
tags: [accessibility, remediation, save, Modal, Button]
related: [accessibility/24-accessibility-testing, accessibility/23-wcag, accessibility/03-semantic-html, accessibility/07-aria, accessibility/27-best-practices]
when_to_use: "Read before fixing an existing product's accessibility defects, triaging an audit report, or planning a remediation backlog."
---
# Remediation

## Purpose

This document defines how to fix an existing product that fails accessibility
requirements: how to triage findings, prioritize by user impact, choose durable fixes
over patches, and avoid re-introducing the same defects. It assumes the code already
ships and you cannot start over — the constraint that makes remediation different from
building accessibly the first time.

Remediation consumes the output of [accessibility testing](24-accessibility-testing.md)
and an audit against [WCAG](23-wcag.md), and turns it into merged fixes.

## Why It Matters

An audit report is a liability, not a fix. Until findings are resolved, the gap between
"we know" and "we did" is exactly the window a legal complaint or a locked-out user lives
in. Remediation is also where teams do the most damage: under deadline pressure they
reach for an ARIA band-aid (`role="button"` on a `<div>`) that silences the scanner while
leaving the control broken for real users. Doing remediation well means fixing the
*cause*, so the defect does not reappear the next sprint in a slightly different form.

Prioritization matters because backlogs are finite. A blocker that stops a screen-reader
user from checking out outranks a decorative image missing `alt=""`, even though a tool
may report them as the same severity.

## Core Principles

- **Fix the root, not the symptom.** Prefer a native element or a corrected structure
  over an ARIA override. ARIA is the last resort, not the first. See [ARIA](07-aria.md).
- **Prioritize by user impact, not tool severity.** Rank by "can the user complete the
  task?" — blockers first, then friction, then polish.
- **Fix the pattern once, not the instance many times.** Most violations trace to a
  shared component; repair it there and hundreds of pages heal at once.
- **Verify with assistive tech.** A change is "done" when a keyboard and screen-reader
  user can complete the flow — not when the scanner turns green.
- **Prevent regression.** Every fix ships with a test so the defect cannot return silently.

## Best Practices

- Triage findings into **blocker / serious / moderate / minor** by task impact, then
  sequence work by the number of users and flows affected.
- Start with **primary user journeys** (sign-up, search, checkout, core task). Fixing a
  rarely visited page before the checkout flow is misallocated effort.
- Replace custom widgets with **semantic HTML** first (`<button>`, `<a>`, `<label>`,
  `<nav>`) — it deletes whole classes of defects instead of patching them.
- Batch fixes by **shared component**: one corrected `Button` or `Modal` resolves every
  usage. Track which components are the highest-leverage repairs.
- Re-test each fix with **keyboard + screen reader**, and add an automated assertion so
  CI catches a regression. See [testing](24-accessibility-testing.md).
- When a full fix is not yet possible, document an **accessible alternative** and a dated
  plan — but treat that as debt, not a resolution.
- Feed root causes back into [best practices](27-best-practices.md) and component
  templates so new code does not recreate the same bugs.

## Examples

**Good Example** — root-cause fix using the native element

```html
<!-- Before: a div pretending to be a button. Not focusable, no key handling,
     no role announced. ARIA alone cannot restore all of this reliably. -->
<div class="btn" onclick="save()">Save</div>

<!-- After: the platform gives focusability, Enter/Space activation, the correct
     role and state, and disabled semantics for free. One change, defect class gone. -->
<button type="button" class="btn" onclick="save()">Save</button>
```

**Bad Example** — patching the symptom to pass the scanner

```html
<!-- Adds a role to silence the "element has no role" rule, but the div is still
     not in the tab order and still ignores the keyboard. The tool goes green;
     the keyboard user still cannot activate it. Symptom hidden, cause intact. -->
<div class="btn" role="button" onclick="save()">Save</div>
<!-- Now someone will "fix" it further with tabindex + keydown handlers,
     re-implementing everything <button> already does. -->
```

## Common Mistakes

- Fixing whatever the tool lists first instead of ranking by user impact.
- Layering ARIA onto broken markup instead of switching to the right native element.
- Repairing one page at a time when a shared component is the real source.
- Declaring a fix done on a green scan without a keyboard or screen-reader check.
- Shipping fixes with no test, so the next refactor silently reintroduces the defect.
- Treating a documented "accessible alternative" as a permanent solution rather than debt.
- Remediating symptoms without updating templates, guaranteeing the bug returns in new code.

## Production Tips

- Maintain a remediation backlog with impact rating, affected component, and a link to a
  reproduction; it makes prioritization defensible and progress measurable.
- When you fix a shared component, search the codebase for the anti-pattern it replaced
  and migrate all callers in the same effort to prevent drift.
- Record recurring root causes; a spike in one category is a signal to fix a template or
  add a lint rule, not to keep filing tickets.

## AI Review Checklist

- Are findings prioritized by **user impact**, with blockers on primary flows fixed first?
- Does each fix address the **root cause** (native element, correct structure) over ARIA?
- Were **shared components** fixed once rather than patched per instance?
- Was each fix **verified with a keyboard and screen reader**, not just a rescan?
- Does every fix ship with a **test** that prevents regression?
- Are temporary "accessible alternatives" tracked as **dated debt**, not closed as done?
- Were root causes fed back into templates or lint rules to stop recurrence?

## Related

- `knowledge/accessibility/24-accessibility-testing.md`
- `knowledge/accessibility/23-wcag.md`
- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/27-best-practices.md`
