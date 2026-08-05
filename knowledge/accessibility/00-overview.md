---
id: accessibility/00-overview
topic: accessibility
slug: overview
title: "Accessibility Overview"
type: doc
order: 0
status: ready
tags: [accessibility, overview]
related: [accessibility/01-accessibility-fundamentals, accessibility/02-pour-principles, accessibility/03-semantic-html, accessibility/07-aria, accessibility/23-wcag]
when_to_use: "Read first when starting any UI work, to see how the accessibility docs fit together and where to go next."
---
# Accessibility Overview

## Purpose

This document is the map for the `accessibility` topic. It orients an agent to what
accessibility (often abbreviated **a11y**) means in practice, names the standard we
target, and points to the sibling docs that cover each concern in depth. Read it once
to know *where* a rule lives; read the specific doc to know the rule.

Accessibility means building interfaces that people can perceive and operate regardless
of vision, hearing, motor ability, or cognitive load — including users of screen readers,
keyboards, switch devices, magnification, and voice control. Our target standard is
**WCAG 2.2 Level AA**, the level referenced by most laws and procurement rules as of 2026.

## Why It Matters

Accessibility is not a feature you bolt on at the end; it is a property of the markup and
interaction model you choose from the first line. Retrofitting is expensive because the
fixes are structural — swapping a `<div>` soup for semantic elements, rebuilding a custom
widget's keyboard model, reworking focus order. Getting it right early costs almost nothing
extra. Getting it wrong locks out real users, invites legal action (ADA, Section 508,
European Accessibility Act), and — because keyboard and semantics also drive automated
tests and SEO — degrades quality across the board. An accessible app is a more robust app.

## Core Principles

- **Semantics first, ARIA second.** Native HTML elements carry role, state, and keyboard
  behavior for free. Reach for ARIA only to describe what HTML cannot. See
  [semantic HTML](03-semantic-html.md) and [ARIA](07-aria.md).
- **Everything works from the keyboard.** If it works with a mouse only, it is broken.
  See [keyboard navigation](04-keyboard-navigation.md).
- **Focus is always visible and always sensible.** Users must see where they are and
  never get trapped. See [focus management](05-focus-management.md).
- **The DOM is the source of truth for the accessibility tree.** Screen readers announce
  what the markup says, not what the pixels show. See [screen readers](06-screen-readers.md).
- **Test with tools *and* with a keyboard and a screen reader.** Automated checks catch
  ~40% of issues; the rest need manual verification. See [testing](24-accessibility-testing.md).

## How These Docs Fit Together

- **Foundations** — start here: [fundamentals](01-accessibility-fundamentals.md) (who
  we build for, the assistive-tech landscape) and [POUR principles](02-pour-principles.md)
  (the four pillars of WCAG: Perceivable, Operable, Understandable, Robust).
- **Structure & interaction** — [semantic HTML](03-semantic-html.md),
  [keyboard navigation](04-keyboard-navigation.md), [focus management](05-focus-management.md),
  [screen readers](06-screen-readers.md), and [ARIA](07-aria.md).
- **Content patterns** — [forms](08-forms.md), [images](09-images.md),
  [color and contrast](10-color-and-contrast.md), [dialogs](16-dialogs.md),
  [live regions](19-live-regions.md), [error messages](18-error-messages.md).
- **Verification & compliance** — [testing](24-accessibility-testing.md),
  [axe](21-axe.md), [Lighthouse](22-lighthouse.md), [WCAG](23-wcag.md),
  and [legal requirements](26-legal-requirements.md).

## Best Practices

- Decide the target conformance level (**WCAG 2.2 AA**) at project start and treat it as
  a definition of done, not a stretch goal.
- Build with real HTML controls (`button`, `a`, `input`, `select`); resort to custom
  widgets only when the platform offers no equivalent — and then follow the ARIA
  Authoring Practices patterns exactly.
- Add an accessibility check to CI (axe-core) so regressions fail the build, and pair it
  with a manual keyboard-and-screen-reader pass each release.
- Write accessibility acceptance criteria into tickets so it is scoped, not discovered.

## Common Mistakes

- Treating accessibility as a late-stage audit rather than a design constraint.
- Assuming an automated scan that passes means the page is accessible — it only means the
  machine-detectable subset passed.
- Copying ARIA attributes from tutorials without understanding the role's required states
  and keyboard contract, producing widgets that announce lies.
- Testing only in the developer's own browser with a mouse.

## AI Review Checklist

- Is there a stated target conformance level, and does the change meet it?
- Does the change use native semantic elements before reaching for ARIA?
- Is every interactive element reachable and operable by keyboard alone?
- Is focus visible and ordered logically after the change?
- Was the change verified with an automated tool *and* a manual keyboard pass?

## Related

- `knowledge/accessibility/01-accessibility-fundamentals.md`
- `knowledge/accessibility/02-pour-principles.md`
- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/23-wcag.md`
