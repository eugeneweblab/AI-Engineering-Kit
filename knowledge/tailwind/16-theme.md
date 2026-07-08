---
id: tailwind/16-theme
topic: tailwind
slug: theme
title: "Theme"
type: doc
order: 16
status: ready
tags: [tailwind, theme]
related: [tailwind/15-customization, tailwind/10-colors, tailwind/21-design-system, tailwind/12-dark-mode, tailwind/02-core-concepts]
when_to_use: "Read before defining design tokens — colors, spacing, fonts, breakpoints — with the v4 @theme block."
---
# Theme

## Purpose

This document defines how to author the design token system in Tailwind CSS v4
using the `@theme` block: what a theme variable is, the namespaces that generate
utilities, how tokens become CSS custom properties, and how to reference them.
The theme is the single source of truth for the design system —
[15-customization](15-customization.md) covers the surrounding tools; this doc is
about the tokens themselves.

In v4, a theme variable is just a CSS custom property with a known prefix,
declared inside `@theme`. `--color-brand-500: …` simultaneously (a) generates the
utilities `bg-brand-500`, `text-brand-500`, etc., and (b) exposes
`var(--color-brand-500)` for use anywhere in CSS. One declaration, two outputs.

## Why It Matters

The theme is where consistency is enforced or lost. Because theme variables emit
real CSS custom properties, they cascade — which means dark mode, per-section
theming, and runtime theming become trivial (swap a variable) *if* you define
semantic tokens, and painful if you hardcoded raw colors everywhere. The most
common failure is the wrong namespace or prefix: `--brand-color` (no known
namespace) generates *no* utilities and silently does nothing, while a v3-shaped
JS theme object is ignored entirely on v4. Getting the namespace and the semantic
layer right makes the whole system flex from one place.

## Core Principles

- **Theme variables follow namespace conventions.** The prefix determines which
  utilities are generated: `--color-*` → color utilities, `--spacing-*` →
  spacing, `--font-*` → font-family, `--text-*` → font-size, `--breakpoint-*` →
  responsive variants, `--radius-*`, `--shadow-*`, and so on. The wrong prefix
  produces no utilities.
- **Tokens are CSS variables — use that.** Reference them as
  `var(--color-brand-500)` in custom CSS and reap live cascade behavior for
  theming.
- **Define a semantic layer, not just a palette.** Map raw scale tokens to
  intent: `--color-surface`, `--color-text`, `--color-border`. Markup references
  intent; a theme swap redefines the intent tokens once.
- **Extend by default; override deliberately.** Adding keys extends the defaults.
  To start from a blank palette, `--color-*: initial;` first — but know you are
  discarding Tailwind's built-ins.
- **Keep the theme central and small.** One `@theme` block per project is the
  source of truth. Resist duplicating tokens across files.

## Best Practices

- Declare tokens in `@theme` in your main CSS after `@import "tailwindcss";`.
  Group by namespace and comment intent.
- Prefer `oklch()` for colors so lightness/chroma scale predictably and dark
  variants stay perceptually even; see [10-colors](10-colors.md).
- Build the semantic layer with variables that *reference* palette tokens, then
  redefine them under a theme selector for dark mode:
  `.dark { --color-surface: var(--color-slate-900); }`.
- Use `@theme inline { … }` when a token's value references another variable that
  should be resolved at definition rather than emitted as a `var()` — needed for
  tokens consumed by third-party CSS.
- Fill gaps in the numeric scales (`--spacing-18`, `--text-2xs`) rather than
  reaching for arbitrary values in markup.
- Reset a namespace to empty with `--namespace-*: initial;` only when you truly
  want to replace, not extend.

## Examples

**Good Example** — namespaced tokens, semantic layer, theme swap

```css
@import "tailwindcss";

@theme {
  /* Palette — generates bg-brand-500, text-brand-500, ... */
  --color-brand-500: oklch(0.62 0.19 255);
  --color-slate-50:  oklch(0.98 0 0);
  --color-slate-900: oklch(0.21 0.03 264);

  /* Scale gap — now usable as p-18, gap-18, m-18 */
  --spacing-18: 4.5rem;

  /* Custom breakpoint → generates the `3xl:` variant */
  --breakpoint-3xl: 120rem;
}

/* Semantic layer: intent tokens reference palette tokens */
@theme {
  --color-surface: var(--color-slate-50);
  --color-text:    var(--color-slate-900);
}

/* Dark mode = redefine the SAME intent tokens once, no markup churn */
.dark {
  --color-surface: var(--color-slate-900);
  --color-text:    var(--color-slate-50);
}
```

```html
<!-- Markup references intent; the theme decides the actual color -->
<div class="bg-surface text-text p-18">Adapts automatically.</div>
```

**Bad Example** — wrong prefix, JS-shaped config, no semantic layer

```css
@theme {
  /* BUG: not a known namespace → generates NO utilities, silently useless */
  --brand-color: #3b82f6;
}
```

```js
// BUG: v4 ignores this for theming; tokens must live in @theme (CSS)
export default { theme: { extend: { colors: { brand: "#3b82f6" } } } };
```

```html
<!-- BUG: hardcoded palette everywhere → dark mode means editing every call site -->
<div class="bg-slate-50 text-slate-900">…</div>
```

## Common Mistakes

- Using a prefix outside the known namespaces (`--brand-color` instead of
  `--color-brand`), so no utilities are generated.
- Defining theme tokens in a JS config object on a v4 project, which is ignored.
- Skipping the semantic layer and hardcoding palette classes, making dark mode
  and rethemes a codebase-wide edit.
- Overriding a namespace when you meant to extend it, deleting Tailwind defaults.
- Duplicating tokens across multiple CSS files instead of one source of truth.
- Reaching for arbitrary values in markup instead of adding the missing scale
  token to the theme.

## Production Tips

- Document each token's intent inline; reviewers should understand a color from
  its name, not by resolving the hex.
- For runtime theming (user-picked accent), write the intent tokens as variables
  you can set from JS on `:root`; utilities update live with no rebuild.
- Verify generated utilities after adding tokens (inspect the compiled CSS or the
  IntelliSense list) to catch namespace typos early.

## AI Review Checklist

- Are theme tokens defined in an `@theme` block in CSS, not a JS config?
- Do token prefixes match a real namespace (`--color-*`, `--spacing-*`, etc.) so
  utilities are actually generated?
- Is there a semantic layer (`--color-surface`, `--color-text`) driving markup,
  rather than hardcoded palette classes?
- Does dark mode redefine intent tokens rather than restyling every element?
- Do additions extend the defaults unless replacement is intentional?
- Are scale gaps filled with tokens instead of arbitrary values in markup?

## Related

- `knowledge/tailwind/15-customization.md`
- `knowledge/tailwind/10-colors.md`
- `knowledge/tailwind/21-design-system.md`
- `knowledge/tailwind/12-dark-mode.md`
- `knowledge/tailwind/02-core-concepts.md`
