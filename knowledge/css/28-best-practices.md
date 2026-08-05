---
id: css/28-best-practices
topic: css
slug: best-practices
title: "CSS Best Practices"
type: doc
order: 28
status: ready
tags: [css, best-practices, "--color-danger"]
related: [css/21-architecture, css/29-css-methodologies, css/03-specificity, css/30-engineering-principles, css/99-ai-review-checklist]
when_to_use: "Read before writing or reviewing any stylesheet, and when a codebase's CSS has become hard to change safely."
---
# CSS Best Practices

## Purpose

This document distills the habits that keep CSS maintainable at scale: low specificity,
design tokens, predictable naming, and change-safety. It is the cross-cutting summary that
sits above the individual feature docs — the rules that apply no matter which selector or
property you are using. The aim is CSS you can change confidently a year later without
fear of breaking a page you have never seen.

## Why It Matters

CSS is global by default: every rule can affect every element, and nothing enforces
boundaries. That makes it uniquely prone to rot — small unprincipled additions accumulate
into a codebase where nobody dares delete a rule, `!important` is everywhere, and each fix
causes two regressions. The failure is gradual and social: velocity drops, bugs rise, and
the team stops trusting the stylesheet. Good practices are the boundaries CSS does not give
you for free. They cost a little discipline now and save the project from calcifying.

## Core Principles

- **Keep specificity low and flat.** Style with single classes; avoid ID selectors, deep
  descendant chains, and `!important`. Low specificity keeps overrides possible.
  See [specificity](03-specificity.md).
- **Tokenize decisions.** Colors, spacing, type sizes, and radii live in custom properties,
  not as magic numbers scattered across files. Change once, apply everywhere.
- **Name by intent, not appearance.** `.btn--danger`, not `.btn--red`; the meaning survives
  a redesign, the color does not.
- **Compose, don't override.** Build from small reusable pieces (utilities, components)
  rather than writing a rule then a second rule to undo part of it.
- **Own the cascade.** Use cascade layers and a consistent methodology so the order rules
  apply in is deliberate, not an accident of file order or selector weight.
- **Make styles predictable and local.** A component's styles should not leak out or depend
  on where it is placed. Scope with classes, not element or global selectors.

## Best Practices

- Select with **a single class** for components; reserve descendant selectors for genuine
  structural relationships. Never style on IDs (too specific) or bare tags (too broad).
- Define **design tokens** as custom properties on `:root` (or a theme scope) and reference
  them everywhere: `color: var(--color-text)`, `padding: var(--space-3)`. See
  [css variables](20-css-variables.md).
- Adopt a **naming methodology** (BEM or utility-first) and apply it consistently; the value
  is the consistency, not the specific scheme. See [methodologies](29-css-methodologies.md).
- Use **`@layer`** to order reset / base / components / utilities so specificity conflicts
  resolve by layer, not by escalation. See [architecture](21-architecture.md).
- Use **logical properties and `gap`** for spacing so layouts adapt to direction and need no
  margin-collapsing tricks.
- Prefer **relative/derived values** (`clamp()`, `color-mix()`) over duplicated literals so
  one source drives a scale.
- **Delete dead CSS.** Unused rules are not free — they confuse readers and slow tooling.
  If a class has no markup, remove it.
- **Colocate styles with components** where the build allows, so a component's CSS is found,
  changed, and deleted together with its markup.

## Examples

**Good Example** — tokens, flat specificity, intent naming

```css
:root {
  --color-danger: #c0322b;      /* one source of truth for the token */
  --space-3: 0.75rem;
  --radius-1: 0.375rem;
}

/* Single-class selector, intent-based modifier, all values tokenized. */
.button { padding: var(--space-3); border-radius: var(--radius-1); }
.button--danger {               /* "danger", not "red" — survives a rebrand */
  background: var(--color-danger);
  color: white;
}
```

**Bad Example** — magic numbers, deep selectors, override wars

```css
/* Appearance-based name, hardcoded color repeated in three files. */
.red-btn { background: #c0322b; }

/* Deep, ID-anchored selector: specificity 1,2,1 — almost impossible to override. */
#app .sidebar .panel .red-btn { padding: 11px; border-radius: 6px; }

/* And when it needs to change, the only tool left is the nuke. */
.red-btn { background: #d43f3a !important; } /* debt compounding */
```

## Common Mistakes

- Scattering literal colors and pixel values instead of referencing tokens, so a rebrand
  becomes a find-and-replace across the codebase.
- Naming by appearance (`.blue-box`, `.mt-20`) so the name lies after the next design change.
- Escalating specificity (IDs, deep chains, `!important`) to win overrides, which makes the
  *next* override even harder.
- Styling bare element selectors globally (`div`, `ul`, `a`) so unrelated components collide.
- Leaving unused CSS in place because "it might be needed", growing the file and the confusion.
- Copy-pasting a component's styles and tweaking, instead of composing modifiers, producing
  divergent near-duplicates.

## Production Tips

- Enforce the rules with tooling: **stylelint** for specificity ceilings and disallowed
  units, and a CSS-coverage check to flag unused rules. A rule not linted is a rule not kept.
- Track bundle size; unbounded CSS growth is a smell that composition has broken down.
- When you must break a rule (a deliberate `!important` on a print or utility layer),
  comment *why* — an unexplained escalation reads as a mistake to the next editor.

## AI Review Checklist

- Are components styled with single classes, avoiding IDs, deep chains, and `!important`?
- Are colors, spacing, and sizes referenced from tokens rather than hardcoded literals?
- Are class names intent-based, surviving a color/redesign change?
- Is cascade order controlled with `@layer` and a consistent methodology?
- Is there any unused/dead CSS that should be deleted?
- Are new styles composed from existing pieces rather than duplicating and overriding?

## Related

- `knowledge/css/21-architecture.md`
- `knowledge/css/29-css-methodologies.md`
- `knowledge/css/03-specificity.md`
- `knowledge/css/30-engineering-principles.md`
- `knowledge/css/99-ai-review-checklist.md`
