---
id: tailwind/readme
topic: tailwind
slug: readme
title: "Tailwind CSS Engineering Standards"
type: index
order: -1
status: ready
tags: [tailwind, readme, "focus-visible:", "hover:", "dark:"]
related: []
when_to_use: "Read first when starting Tailwind work, to see how this section's docs fit together and how the utility model should be applied."
---
# Tailwind CSS Engineering Standards

## Purpose

This section defines the engineering standards for working with Tailwind CSS: configuring the
theme as a design system, composing utilities without creating unmaintainable markup, and
keeping the generated stylesheet small.

Tailwind's trade is explicit: styling moves into markup, which removes the naming problem and
the dead-CSS problem, and introduces a repetition problem. These standards are mostly about
managing that trade — knowing when a repeated utility string should become a component, and
when a value should become a theme token rather than an arbitrary bracket.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Installation, core concepts, and the utility-first model
- Layout utilities: flexbox, grid, spacing, sizing
- Typography and color
- Responsive design, dark mode, state variants, and pseudo-classes
- Theme customization and design-system alignment
- Component extraction and plugins
- Performance and build optimization
- Framework integration: Next.js and React
- Accessibility, debugging, and production practice

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. [Overview](00-overview.md)
- 01. [Installation](01-installation.md)
- 02. [Core Concepts](02-core-concepts.md)
- 03. [Utility First](03-utility-first.md)
- 30. [Engineering Principles](30-engineering-principles.md)

## Layout

- 04. [Layout](04-layout.md)
- 05. [Flexbox](05-flexbox.md)
- 06. [Grid](06-grid.md)
- 07. [Spacing](07-spacing.md)
- 08. [Sizing](08-sizing.md)

## Visual Design

- 09. [Typography](09-typography.md)
- 10. [Colors](10-colors.md)
- 21. [Design System](21-design-system.md)

## Variants and Responsiveness

- 11. [Responsive Design](11-responsive-design.md)
- 12. [Dark Mode](12-dark-mode.md)
- 13. [State Variants](13-state-variants.md)
- 14. [Pseudo Classes](14-pseudo-classes.md)

## Scaling the Codebase

- 15. [Customization](15-customization.md)
- 16. [Theme](16-theme.md)
- 17. [Components](17-components.md)
- 18. [Plugins](18-plugins.md)
- 28. [Patterns](28-patterns.md)

## Framework Integration

- 23. [Next.js](23-nextjs.md)
- 24. [React](24-react.md)

## Quality and Delivery

- 19. [Performance](19-performance.md)
- 20. [Optimization](20-optimization.md)
- 22. [Accessibility](22-accessibility.md)
- 25. [Debugging](25-debugging.md)
- 26. [Best Practices](26-best-practices.md)
- 27. [Production](27-production.md)
- 29. [Tooling](29-tooling.md)

## Verification

- 98. [Production Checklist](98-production-checklist.md)
- 99. [AI Review Checklist](99-ai-review-checklist.md)
- 100. [Common Antipatterns](100-common-antipatterns.md)

---

## Engineering Principles

Every Tailwind change should satisfy the following principles:

- The theme is the design system. Every color, spacing step, radius, and font size comes from
  configuration, not from an arbitrary value.
- Arbitrary values (`w-[437px]`, `text-[#2563EB]`) are an escape hatch, and each one is a
  question: should this be a token?
- Extract a component when markup repeats, not a CSS class. `@apply` recreates the naming and
  specificity problems Tailwind was adopted to avoid.
- Class names must be statically detectable — a string the compiler cannot see is a style that
  will not exist in production.
- Compose variants rather than writing custom CSS: `hover:`, `focus-visible:`, `dark:`,
  `md:`, `group-*`, `peer-*` cover most of what people hand-write.
- Mobile-first: unprefixed utilities are the small-screen case, and breakpoint prefixes add
  from there.
- Keep utility strings ordered consistently (layout → box → typography → visual → state) so
  diffs stay readable; enforce it with the Prettier plugin rather than by review.
- Accessibility is not covered by utilities — focus indicators, contrast, and semantics remain
  your responsibility.
- Verify the production build, since that is where unused utilities are removed and mistakes
  in detection surface.

---

## Intended Audience

These standards are intended for:

- Frontend Engineers
- Design Engineers
- Fullstack Engineers building UI
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Configure the theme as a design system and consume it through utilities; extract components
rather than classes when markup repeats; keep class names statically detectable; and remember
that Tailwind styles the interface but does not make it accessible.
