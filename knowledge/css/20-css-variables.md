---
id: css/20-css-variables
topic: css
slug: css-variables
title: "CSS Variables"
type: doc
order: 20
status: ready
tags: [css, css-variables]
related: [css/21-architecture, css/11-colors, css/18-media-queries, css/23-accessibility, css/29-css-methodologies]
when_to_use: "Read before defining design tokens, building a theme system (dark mode), or reaching for a preprocessor variable where a runtime custom property fits better."
---
# CSS Variables

## Purpose

This document defines how to use CSS custom properties (`--name` / `var()`): design
tokens, theming, scoping, fallbacks, and the runtime behavior that separates them from
preprocessor variables. It is written so an agent builds a maintainable, themeable
system instead of hardcoded values scattered across files.

Custom properties are *live* values resolved by the browser at runtime, inherited
through the cascade, and changeable with a single declaration or from JavaScript. That
is what makes theming, `prefers-color-scheme` switching, and component APIs possible.

## Why It Matters

Hardcoded values are the primary source of visual inconsistency and expensive redesigns:
change the brand color and you are hunting `#3b82f6` across hundreds of files, missing
some. Custom properties turn those values into a single source of truth. Unlike Sass
variables, which are compiled away, custom properties persist to runtime — so one
declaration under `[data-theme="dark"]` re-themes the entire app, and a component can
expose a `--gap` knob that consumers override without touching its internals. Used well,
they are the backbone of a design system; used carelessly, they become an untyped global
namespace that is just as hard to reason about as the magic numbers they replaced.

## Core Principles

- **Custom properties inherit and cascade; preprocessor variables do not.** A `--color`
  set on `:root` flows to every descendant and can be overridden locally. Sass `$color`
  is resolved at build time and knows nothing about the DOM.
- **Define global tokens on `:root`, scope component knobs locally.** Design tokens
  (color, spacing scale, radii) belong at the top; a component's tunable parameters
  belong on the component so they do not leak.
- **Always provide a fallback in `var()`.** `var(--gap, 1rem)` renders correctly even if
  the variable is undefined, preventing an entire property from being dropped.
- **Invalid values become `unset`, not ignored.** If `--x` holds garbage and you write
  `width: var(--x)`, the property becomes invalid-at-computed-value-time and inherits or
  falls to initial — a subtle failure mode; validate inputs.
- **Theme by redefinition, not duplication.** Switch themes by reassigning the same
  token names under a selector, not by writing a parallel set of rules.

## Best Practices

- Establish a token layer: primitive tokens (`--blue-500: #3b82f6`) referenced by
  semantic tokens (`--color-accent: var(--blue-500)`). Components use only semantic
  tokens, so a rebrand touches one line.
- Name tokens by role, not appearance: `--color-danger`, not `--color-red`. Roles
  survive redesigns; literal names lie after the first theme change.
- Implement dark mode by redefining semantic tokens under `@media (prefers-color-scheme:
  dark)` and/or a `[data-theme]` attribute — never a duplicate stylesheet.
- Expose component customization as documented custom properties (`--btn-padding`) with
  sensible fallbacks; this is a stable public API even when internals change.
- Prefer custom properties over Sass variables whenever the value might change at
  runtime (theme, breakpoint, JS interaction). Keep Sass for compile-time logic only.
- Register truly typed/animatable properties with `@property` when you need type safety
  or to transition a variable (e.g. animating a gradient angle).

## Examples

**Good Example** — layered tokens, role names, single-declaration theming

```css
:root {
  --blue-500: #3b82f6;            /* primitive: a raw value */
  --color-accent: var(--blue-500); /* semantic: role → primitive */
  --space-3: 1rem;
}

/* Dark mode re-themes everything by reassigning the SAME semantic tokens. */
@media (prefers-color-scheme: dark) {
  :root { --color-accent: #60a5fa; }
}

.button {
  --btn-padding: var(--space-3);        /* component knob, overridable */
  padding: var(--btn-padding, 0.75rem); /* fallback if unset */
  background: var(--color-accent);
}
```

**Bad Example** — hardcoded, appearance-named, duplicated theme

```css
.button { padding: 16px; background: #3b82f6; } /* magic numbers everywhere */

/* Dark mode duplicates the rule instead of re-theming a token → drifts out of sync. */
.dark .button { padding: 16px; background: #60a5fa; }

:root { --color-red: #dc2626; } /* appearance name lies once "danger" turns orange */
.alert { color: var(--color-red); } /* no fallback: undefined → whole prop dropped */
```

## Common Mistakes

- Treating custom properties like Sass variables and expecting compile-time behavior
  (they are runtime and inherited).
- Omitting the `var()` fallback, so an undefined variable silently drops the property.
- Naming tokens after their color (`--color-red`) instead of their role (`--color-danger`).
- Duplicating whole stylesheets for dark mode instead of reassigning semantic tokens.
- Defining every component's private variables on `:root`, polluting the global scope.
- Assuming an invalid custom property is ignored — it triggers invalid-at-computed-value,
  falling back to inherited or initial in ways that surprise you.

## Production Tips

- Read and write custom properties from JS with `getComputedStyle(el).getPropertyValue`
  and `el.style.setProperty('--x', v)` — this is the clean bridge for runtime theming.
- Use `@property` to give a variable a syntax, initial value, and inheritance flag; only
  registered properties can be smoothly animated.
- Audit your token graph: a semantic token that points at another semantic token instead
  of a primitive usually signals a naming-layer mistake.

## AI Review Checklist

- Are repeated literal values (colors, spacing, radii) hoisted into custom properties?
- Do global tokens live on `:root` and component knobs stay scoped to the component?
- Does every `var()` for a critical property include a fallback value?
- Are tokens named by role (`--color-accent`) rather than appearance (`--color-blue`)?
- Is theming done by redefining semantic tokens, not duplicating rule sets?
- Are runtime-changing values custom properties, with Sass reserved for compile-time?

## Related

- `knowledge/css/21-architecture.md`
- `knowledge/css/11-colors.md`
- `knowledge/css/18-media-queries.md`
- `knowledge/css/23-accessibility.md`
- `knowledge/css/29-css-methodologies.md`
