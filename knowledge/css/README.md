---
id: css/readme
topic: css
slug: readme
title: "CSS Engineering Standards"
type: index
order: -1
status: ready
tags: [css, readme]
related: []
when_to_use: "Read first when starting any CSS work, to see how this section's docs fit together."
---
# CSS Engineering Standards

## Purpose

This section defines the engineering standards for writing CSS that is predictable,
debuggable, and cheap to change. CSS looks forgiving — a wrong value rarely throws, the page
just renders slightly off — and that forgiveness is exactly why it drifts into
unmaintainable state. CSS is also global by default, so a change that fixes one component can
silently break another three screens away, with no compiler to catch it.

The docs teach rules that win by structure rather than by brute-force `!important`, layouts
that adapt without magic numbers, and selectors that survive a redesign. They move from the
foundations of the cascade, through box and layout, visual detail, adaptation, and the
architecture and quality practices that keep styling editable over years.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- CSS fundamentals: the cascade, selectors, specificity
- The box model, positioning, flexbox, and grid
- Sizing, spacing, typography, colors, and backgrounds
- Borders, transforms, transitions, and animations
- Responsive design, media queries, and container queries
- CSS variables, architecture, and methodologies
- Performance, accessibility, and print styles
- Modern CSS, browser compatibility, and debugging

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. Overview
- 01. CSS Fundamentals
- 02. Selectors
- 03. Specificity
- 30. Engineering Principles

## Box & Layout

- 04. Box Model
- 05. Positioning
- 06. Flexbox
- 07. Grid
- 08. Sizing
- 09. Spacing

## Visual Detail

- 10. Typography
- 11. Colors
- 12. Backgrounds
- 13. Borders
- 14. Transforms
- 15. Transitions
- 16. Animations

## Adaptation

- 17. Responsive Design
- 18. Media Queries
- 19. Container Queries

## Scale & Quality

- 20. CSS Variables
- 21. Architecture
- 22. Performance
- 23. Accessibility
- 24. Print Styles
- 29. CSS Methodologies

## Practice

- 25. Modern CSS
- 26. Browser Compatibility
- 27. Debugging
- 28. Best Practices

## Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every CSS change should satisfy the following principles:

- Treat the cascade as the model — understand source order, specificity, and inheritance
  before reaching for overrides.
- Style by intent, targeting a component's role with a class, not its DOM position.
- Prefer flow and modern layout to manual pixel math; let the browser do the arithmetic.
- Keep specificity low and flat so rules override predictably.
- Add intent with a class rather than raising specificity or reaching for `!important`.
- Design layouts that adapt without magic numbers.
- Verify a change holds up across the breakpoints and containers a component lives in.
- Consult the specific doc for the property or behavior being changed.

---

## Intended Audience

These standards are intended for:

- Frontend Engineers
- UI and Design-System Engineers
- Fullstack Engineers
- Web Designers who write code
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps stylesheets predictable and cheap to change, so styling stays
editable across redesigns instead of becoming code everyone is afraid to touch.
