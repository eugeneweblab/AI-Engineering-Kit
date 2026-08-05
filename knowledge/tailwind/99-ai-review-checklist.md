---
id: tailwind/99-ai-review-checklist
topic: tailwind
slug: ai-review-checklist
title: "Tailwind CSS AI Review Checklist"
type: doc
order: 99
status: ready
tags: [tailwind, ai-review-checklist, "focus-visible:", "dark:", w-full, justfy-center, gap-4, flexx]
related: [tailwind/26-best-practices, tailwind/30-engineering-principles, tailwind/100-common-antipatterns, tailwind/22-accessibility, tailwind/98-production-checklist]
when_to_use: "Read when reviewing a diff or PR that adds or changes Tailwind markup, before approving it."
---
# Tailwind CSS AI Review Checklist

## Purpose

A focused checklist for reviewing Tailwind CSS (v4) markup in a pull request. Each item is
a yes/no question an agent can answer by reading the diff. It targets the mistakes that
pass tests and render fine but degrade consistency, accessibility, and bundle size over
time. Pair it with the ship-time [production-checklist](98-production-checklist.md).

## Design Tokens & Values

**Rules:** [Theme](16-theme.md) · [Design System](21-design-system.md)

- [ ] Do new colors, spacing, and radii use theme tokens instead of arbitrary values like
      `p-[7px]` or `text-[#3b82f6]`?
- [ ] If an arbitrary value is present, is it genuinely one-off, or should it become a
      token in `@theme`?
- [ ] Are values on-scale (`p-2`, `gap-4`) rather than off-scale magic numbers that only
      approximate the scale?
- [ ] Are raw hex/rgb colors avoided in favor of named palette or brand tokens?

## Structure & Reuse

**Rules:** [Components](17-components.md) · [Patterns](28-patterns.md)

- [ ] Is repeated markup (buttons, cards, badges) extracted into a component rather than
      copy-pasted with drift?
- [ ] Is `@apply` avoided except for third-party markup that cannot be componentized?
- [ ] When a component accepts `className`, is `tailwind-merge` used so overrides win
      instead of duplicating conflicting utilities?
- [ ] Are class strings built safely (`cn`/`clsx`) rather than string-concatenated in ways
      that could drop or duplicate classes?

## Responsiveness

**Rules:** [Responsive Design](11-responsive-design.md)

- [ ] Are styles mobile-first — base unprefixed, `md:`/`lg:` layered on top — rather than
      desktop-first with overrides?
- [ ] Does the change avoid fixed pixel widths that break on small screens (prefer
      `max-w-*`, `w-full`, grid/flex)?
- [ ] Are breakpoints from the standard set, not one-off arbitrary media queries?

## State & Interactivity

**Rules:** [State Variants](13-state-variants.md) · [Pseudo Classes](14-pseudo-classes.md)

- [ ] Are interactive elements given `hover:`, `focus-visible:`, and `disabled:` states as
      appropriate?
- [ ] Is `focus-visible:` used (not `focus:`) so keyboard focus shows without a mouse-click
      ring?
- [ ] Is the default focus outline preserved or intentionally replaced — never silently
      removed?

## Dark Mode

**Rules:** [Dark Mode](12-dark-mode.md)

- [ ] If the app supports dark mode, does every new surface/text/border include a `dark:`
      variant?
- [ ] Are the `dark:` color choices actually readable (adequate contrast), not just
      inverted?

## Accessibility

**Rules:** [Accessibility](22-accessibility.md)

- [ ] Do foreground/background pairs meet WCAG AA contrast in both themes?
- [ ] Is information conveyed by more than color (icon, text, shape) for status/errors?
- [ ] Do motion utilities honor `motion-reduce:`?

## Correctness & Hygiene

**Rules:** [Best Practices](26-best-practices.md) · [Debugging](25-debugging.md)

- [ ] Are all class names valid (no typos like `flexx`, `justfy-center` that silently do
      nothing)?
- [ ] Is class order consistent with `prettier-plugin-tailwindcss` output?
- [ ] Are conflicting utilities (`block hidden`, `p-2 p-4`) absent, so intent is
      unambiguous?

## Related

- `knowledge/tailwind/26-best-practices.md`
- `knowledge/tailwind/30-engineering-principles.md`
- `knowledge/tailwind/100-common-antipatterns.md`
- `knowledge/tailwind/22-accessibility.md`
- `knowledge/tailwind/98-production-checklist.md`
