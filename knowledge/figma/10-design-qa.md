---
id: figma/10-design-qa
topic: figma
slug: design-qa
title: "Design QA"
type: doc
order: 10
status: ready
tags: [figma, design-qa]
related: []
when_to_use: ""
---
# Design QA

## Purpose

This document defines the standard process for validating an implementation against a Figma design after development.

The objective is to detect visual, structural, responsive, and accessibility differences before code review or client acceptance.

Design QA is a verification phase.

It is not another implementation phase.

---

## Core Principle

Never assume the implementation matches the design.

Always verify it systematically.

Every completed page must pass a Design QA review before it is considered production-ready.

---

## AI Mindset

When reviewing an implementation, behave like a Senior Frontend QA Engineer rather than the original developer.

Do not defend the implementation.

Look for differences.

Assume mistakes exist until proven otherwise.

---

## Design QA Workflow

Every page should be reviewed in the following order:

```
Overall Layout
        ↓
Page Structure
        ↓
Sections
        ↓
Components
        ↓
Typography
        ↓
Spacing
        ↓
Colors
        ↓
Responsive Layout
        ↓
Interactions
        ↓
Accessibility
        ↓
Performance
```

Never review isolated elements first.

Start from the entire page.

---

## Step 1 — Overall Layout

Compare:

- page width;
- overall proportions;
- visual balance;
- whitespace;
- section ordering;
- content hierarchy.

The first visual impression should closely match the design.

---

## Step 2 — Page Structure

Verify:

- correct section order;
- consistent containers;
- expected layout hierarchy;
- semantic HTML landmarks.

Unexpected structural differences usually indicate implementation problems.

---

## Step 3 — Section Review

Review every section independently.

Verify:

- width;
- spacing;
- alignment;
- padding;
- margins;
- background;
- responsiveness.

Sections should be visually independent.

---

## Step 4 — Component Review

Review every reusable component.

Examples:

- buttons;
- cards;
- forms;
- navigation;
- accordions;
- sliders;
- pricing cards;
- testimonials.

Verify that all instances remain consistent.

---

## Step 5 — Typography

Review:

- font family;
- font size;
- font weight;
- line height;
- letter spacing;
- text alignment;
- heading hierarchy.

Typography inconsistencies are among the most common implementation issues.

---

## Step 6 — Spacing

Review:

- section spacing;
- component spacing;
- grid gaps;
- margins;
- padding.

Spacing should follow the design system.

Avoid visual approximations.

---

## Step 7 — Colors

Verify:

- backgrounds;
- text colors;
- borders;
- buttons;
- links;
- icons;
- shadows.

Compare against design tokens rather than screenshots whenever possible.

---

## Step 8 — Responsive Review

Review:

Desktop

↓

Laptop

↓

Tablet

↓

Mobile

Verify:

- layout changes;
- stacking;
- typography;
- spacing;
- navigation;
- touch targets.

Responsive behavior should be intentional.

---

## Step 9 — Interaction Review

Verify every interactive element.

Examples:

- hover;
- focus;
- active;
- disabled;
- loading;
- expanded;
- collapsed.

Review keyboard navigation in addition to pointer interactions.

---

## Step 10 — Accessibility Review

Verify:

- heading hierarchy;
- semantic HTML;
- image alt text;
- focus indicators;
- keyboard navigation;
- labels;
- contrast.

Accessibility is part of design quality.

---

## Step 11 — Performance Review

Verify:

- image optimization;
- lazy loading;
- asset size;
- unnecessary JavaScript;
- unnecessary CSS;
- layout shifts.

Visual quality should not compromise performance.

---

## Severity Levels

Every issue should receive a severity.

## Critical

Examples:

- broken layout;
- inaccessible functionality;
- missing content;
- unusable navigation.

Must be fixed before approval.

---

## Major

Examples:

- incorrect responsive layout;
- missing section;
- incorrect typography;
- incorrect spacing affecting usability.

Should be fixed before approval.

---

## Minor

Examples:

- inconsistent padding;
- small alignment differences;
- incorrect icon size;
- minor border-radius differences.

Should be corrected if practical.

---

## Cosmetic

Examples:

- tiny visual differences;
- insignificant spacing variations;
- decorative inconsistencies.

May be addressed later.

---

## QA Report Format

Every review should include:

## Overall Assessment

Examples:

- Matches Figma closely.
- Minor visual differences detected.
- Significant differences require revision.

---

## Findings

For every issue include:

- severity;
- location;
- description;
- expected result;
- recommended fix.

---

## Positive Findings

List areas implemented correctly.

Examples:

- Excellent responsive behavior.
- Consistent typography.
- Proper semantic HTML.
- Good accessibility.
- Reused existing components.

Good implementations deserve recognition.

---

## Final Recommendation

Choose one:

- Approve
- Approve with minor comments
- Request changes
- Reject implementation

---

## AI Execution Checklist

## Investigation

☐ Compare page structure.

☐ Compare sections.

☐ Compare typography.

☐ Compare spacing.

☐ Compare colors.

☐ Compare responsiveness.

☐ Compare interactions.

☐ Compare accessibility.

---

## Verification

☐ Every difference is documented.

☐ Severity is assigned.

☐ Recommendations are actionable.

☐ Positive findings are included.

☐ Final recommendation is justified.

---

## Common Mistakes

Avoid:

Checking only desktop.

Ignoring spacing.

Ignoring accessibility.

Ignoring hover states.

Ignoring keyboard navigation.

Ignoring responsive layouts.

Accepting visual approximations.

Reviewing implementation without the Figma design.

---

## Completion Criteria

A Design QA review is complete when:

- every section has been reviewed;
- responsive layouts have been verified;
- accessibility has been evaluated;
- issues are categorized by severity;
- a final recommendation is provided;
- the implementation is considered ready for production or returned for revision.

---

## Summary

Design QA is the final engineering safeguard between implementation and production.

A disciplined review process catches visual, structural, responsive, and accessibility issues before they reach users, reducing costly revisions and increasing confidence in every release.