---
id: frontend/03-design-systems
topic: frontend
slug: design-systems
title: "Design Systems"
type: doc
order: 3
status: ready
tags: [frontend, design-systems]
related: [frontend/02-component-driven-development, frontend/15-styling, frontend/16-css-architecture, frontend/09-accessibility]
when_to_use: "Read before creating shared UI primitives, defining design tokens, or building a component library."
---
# Design Systems

## Purpose

This document defines how to build and consume a design system: design tokens, a
library of shared primitives, and the contract that keeps a product visually and
behaviorally consistent as many people build many screens. It lets an agent add to
or use a design system without fragmenting it.

A design system is not a folder of components. It is a single source of truth for
visual decisions (color, spacing, type, motion) plus the primitives that encode
them, so that consistency is the default rather than an act of discipline.

## Why It Matters

Without a design system, every screen re-decides padding, color, and focus behavior.
The result is dozens of subtly different buttons, inconsistent spacing, and
accessibility handled ad hoc — sometimes right, often not. Fixing a color or a
focus ring means editing hundreds of files.

With tokens and primitives, a change to a brand color or a focus style is one edit
that propagates everywhere. Consistency, accessibility, and theming (light/dark)
become properties of the system instead of per-screen chores.

## Core Principles

- **Tokens are the source of truth.** Colors, spacing, radii, type, and motion are
  named values, not literals scattered in components. Components reference tokens.
- **Never hardcode a raw value in a component.** `#3b82f6` and `13px` are bugs;
  `color-primary` and `space-3` are the contract.
- **Primitives encode accessibility once.** Focus rings, contrast, hit targets, and
  ARIA live in the shared component so consumers cannot get them wrong.
- **Semantic tokens over raw tokens.** Expose `color-surface`, `color-text`, not
  `gray-100`; the semantic layer is what makes theming a single switch.
- **The system is versioned and additive.** Breaking a primitive breaks every
  consumer; changes are backward-compatible or explicitly versioned.

## Best Practices

- Define tokens in one place (CSS custom properties or a tokens file) and derive
  themes by overriding semantic tokens, not by rewriting components.
- Build primitives (`Button`, `Input`, `Stack`, `Text`) that consume only tokens;
  application code composes primitives and never reaches for raw CSS values.
- Bake accessible defaults into primitives: visible focus, adequate contrast,
  minimum 44px touch targets, correct roles. See [accessibility](09-accessibility.md).
- Support theming via a `data-theme` attribute or `prefers-color-scheme`, resolved
  through semantic tokens so no component needs a theme conditional.
- Document each primitive's props, states, and do/don't usage so consumers reuse
  instead of forking. See [styling](15-styling.md) and [CSS architecture](16-css-architecture.md).

## Examples

**Good Example** — semantic tokens, theme by override

```css
:root {
  --gray-900: #111827;  --gray-50: #f9fafb;  --blue-600: #2563eb; /* raw tokens */
  /* Semantic tokens: what components actually reference. */
  --color-surface: var(--gray-50);
  --color-text:    var(--gray-900);
  --color-accent:  var(--blue-600);
}
:root[data-theme="dark"] {
  --color-surface: var(--gray-900);  /* dark mode = override semantics, nothing else */
  --color-text:    var(--gray-50);
}
```

```tsx
// Button consumes tokens only; it works in every theme with zero changes.
export function Button({ children, ...props }) {
  return (
    <button
      className="btn"                          // .btn { background: var(--color-accent) }
      style={{ color: "var(--color-surface)" }} // never a literal hex here
      {...props}
    >
      {children}
    </button>
  );
}
```

**Bad Example** — hardcoded values, no theming path

```tsx
// Raw hex and pixel literals baked into the component. Dark mode is impossible
// without editing this (and every other) component, and the blue drifts from the
// blue used three files over. The design system has already fragmented.
function Button({ children }) {
  return (
    <button style={{ background: "#2f7bf6", color: "#fafafa", padding: "13px" }}>
      {children}
    </button>
  );
}
```

## Common Mistakes

- Hardcoding colors, spacing, or font sizes in components instead of using tokens.
- Exposing only raw tokens (`gray-100`), so theming requires touching every component.
- Forking a primitive to change one detail instead of adding a supported variant.
- Handling focus, contrast, and ARIA per screen rather than once in the primitive.
- Letting application code drop to raw HTML/CSS, bypassing the system entirely.
- No versioning, so a "small" primitive change silently breaks distant screens.

## Production Tips

- Lint against raw color/size literals in application code to keep everything on
  tokens.
- Generate tokens from a single source (e.g. a JSON/`style-dictionary` file) if the
  same values feed CSS, native, and design tools.
- Add visual-regression tests to primitives; they are the highest-leverage code in
  the app.

## AI Review Checklist

- Do components reference semantic tokens instead of raw hex/pixel literals?
- Is theming achieved by overriding semantic tokens, not by per-component conditionals?
- Do shared primitives encode focus, contrast, and hit-target accessibility?
- Are new variations added as supported props rather than forked components?
- Is application code composing primitives instead of dropping to raw CSS?

## Related

- `knowledge/frontend/02-component-driven-development.md`
- `knowledge/frontend/15-styling.md`
- `knowledge/frontend/16-css-architecture.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/10-responsive-design.md`
