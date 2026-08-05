---
id: accessibility/readme
topic: accessibility
slug: readme
title: "Accessibility Engineering Standards"
type: index
order: -1
status: ready
tags: [accessibility, readme, button, prefers-color-scheme, prefers-reduced-motion]
related: []
when_to_use: "Read first when starting accessibility work, to see how this section's docs fit together and which one covers the component you are building."
---
# Accessibility Engineering Standards

## Purpose

This section defines the engineering standards for building interfaces usable by everyone:
semantic structure, keyboard operability, assistive-technology support, and the WCAG criteria
those requirements come from.

The premise throughout is that accessibility is a property of the markup and interaction
model, not a layer applied afterwards. A `div` with a click handler cannot be made accessible
by adding attributes — it has to become a `button`. Retrofitting is expensive precisely
because the fix is usually structural.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Fundamentals and the POUR principles
- Semantic HTML, ARIA, and document structure
- Keyboard navigation and focus management
- Screen readers and live regions
- Component patterns: forms, dialogs, tables, media, images
- Visual concerns: color and contrast, typography, layout, motion
- Responsive accessibility
- Testing with axe and Lighthouse, and manual verification
- WCAG, legal requirements, remediation, and documentation

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. [Overview](00-overview.md)
- 01. [Accessibility Fundamentals](01-accessibility-fundamentals.md)
- 02. [POUR Principles](02-pour-principles.md)
- 23. [WCAG](23-wcag.md)
- 30. [Engineering Principles](30-engineering-principles.md)

## Structure and Semantics

- 03. [Semantic HTML](03-semantic-html.md)
- 07. [ARIA](07-aria.md)
- 06. [Screen Readers](06-screen-readers.md)
- 19. [Live Regions](19-live-regions.md)

## Interaction

- 04. [Keyboard Navigation](04-keyboard-navigation.md)
- 05. [Focus Management](05-focus-management.md)
- 16. [Dialogs](16-dialogs.md)

## Components

- 08. [Forms](08-forms.md)
- 18. [Error Messages](18-error-messages.md)
- 09. [Images](09-images.md)
- 15. [Media](15-media.md)
- 17. [Tables](17-tables.md)

## Visual Design

- 10. [Color and Contrast](10-color-and-contrast.md)
- 11. [Typography](11-typography.md)
- 12. [Layout](12-layout.md)
- 13. [Responsive Accessibility](13-responsive-accessibility.md)
- 14. [Motion and Animation](14-motion-and-animation.md)

## Verification in Practice

- 20. [Testing Tools](20-testing-tools.md)
- 21. [Axe](21-axe.md)
- 22. [Lighthouse](22-lighthouse.md)
- 24. [Accessibility Testing](24-accessibility-testing.md)
- 25. [Remediation](25-remediation.md)

## Applied Guidance

- 26. [Legal Requirements](26-legal-requirements.md)
- 27. [Best Practices](27-best-practices.md)
- 28. [Real-World Patterns](28-real-world-patterns.md)
- 29. [Documentation](29-documentation.md)

## Verification

- 98. [Production Checklist](98-production-checklist.md)
- 99. [AI Review Checklist](99-ai-review-checklist.md)
- 100. [Common Antipatterns](100-common-antipatterns.md)

---

## Engineering Principles

Every interface should satisfy the following principles:

- Use the native element. Its role, keyboard behavior, and focus handling come for free and
  are correct in every browser and assistive technology.
- No ARIA is better than bad ARIA — an incorrect role overrides working semantics.
- Everything operable by mouse must be operable by keyboard, in a logical order, with a
  visible focus indicator.
- Never remove focus outlines without replacing them.
- Meaning must survive without color, without sound, and without motion.
- Every input has a persistent label; a placeholder is not a label.
- Announce state changes to assistive technology, not just visually.
- Respect user preferences: `prefers-reduced-motion`, `prefers-color-scheme`, zoom, and
  browser font size.
- Automated scans catch roughly a third of real defects — keyboard and screen-reader passes
  are not optional.
- Accessibility decisions belong in the design phase; flag omissions in the design rather
  than inventing them in code.

---

## Intended Audience

These standards are intended for:

- Frontend Engineers
- Designers and Design Engineers
- QA and Accessibility Specialists
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Accessibility comes from correct structure and interaction, not from attributes added late.
Use native elements, keep everything keyboard-operable with visible focus, never rely on color
or motion alone, and verify manually because scanners see only part of the problem.
