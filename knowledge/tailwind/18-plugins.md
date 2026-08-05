---
id: tailwind/18-plugins
topic: tailwind
slug: plugins
title: "Plugins"
type: doc
order: 18
status: ready
tags: [tailwind, plugins, "@tailwindcss", prose, "@utility", "@custom-variant", "@container", "@import"]
related: [tailwind/15-customization, tailwind/16-theme, tailwind/17-components, tailwind/09-typography, tailwind/24-react]
when_to_use: "Read before adding a Tailwind plugin or writing a custom utility/variant in v4."
---
# Plugins

## Purpose

This document defines how to extend Tailwind CSS v4 with plugins and custom
utilities: loading first-party plugins with the CSS-first `@plugin` directive,
adding project utilities with `@utility`, and registering new variants with
`@custom-variant`. It is written so an agent adds capability the idiomatic v4 way
instead of resurrecting the v3 JavaScript plugin config.

A "plugin" in Tailwind is a package that registers new utilities, variants, or
base styles (`@tailwindcss/typography`, `@tailwindcss/forms`). In v4 you rarely
need a full plugin for project-local additions — `@utility` and `@theme` cover
most cases in CSS.

## Why It Matters

v4 moved plugin registration out of `tailwind.config.js` and into CSS. An agent
that emits a `plugins: [require("@tailwindcss/typography")]` array on a v4 project
produces a config that is never loaded, so the `prose` classes silently do not
exist and the markup renders unstyled. The failure looks like "the plugin isn't
working" and wastes review cycles. Knowing that `@plugin` replaces the array — and
that most custom utilities no longer need a plugin at all — keeps extensions small
and actually loaded.

## Core Principles

- **Load plugins in CSS with `@plugin`, not a JS array.** `@plugin "@tailwindcss/typography";`
  is the v4 mechanism. The `plugins: []` config key is legacy and only read through
  an explicit `@config`.
- **Prefer `@utility` over a plugin for project-local utilities.** A one-off utility
  belongs in your CSS via `@utility`, which participates in variants and sorting.
  Reach for a real plugin only when you must generate many utilities programmatically.
- **Prefer built-ins before adding a dependency.** Container queries, `@starting-style`,
  and many v3 plugins are now first-class in v4. Check core before installing.
- **Custom variants use `@custom-variant`.** New stateful prefixes (`theme-*`, a data
  attribute) are registered in CSS, not in a plugin's `addVariant`.

## Best Practices

- Load first-party plugins by package name after the Tailwind import:
  `@import "tailwindcss"; @plugin "@tailwindcss/forms";`.
- Pass plugin options with a nested block: `@plugin "@tailwindcss/forms" { strategy: base; }`.
- Define custom utilities with `@utility`; they automatically support `hover:`, `md:`,
  and `dark:` because they flow through the engine like core utilities.
- Keep plugin-registered tokens in `@theme` so they show up in autocomplete and the
  generated CSS variables (see [16-theme](16-theme.md)).
- Do not reinstall v3 plugins that v4 absorbed: `@tailwindcss/container-queries` is
  now core (`@container`, `@md:`), so installing it is redundant and can conflict.
- Audit every plugin for output size — a plugin that emits hundreds of utilities you
  never use still costs scan time and, if safelisted, bytes.

## Examples

**Good Example** — v4 CSS-first plugin load and a custom utility

```css
/* app.css */
@import "tailwindcss";

/* Load first-party plugins in CSS; options go in a nested block. */
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms" {
  strategy: base; /* base = style all inputs; class = opt-in via form-* classes */
}

/* Project-local utility: no plugin needed. Supports hover:/md:/dark: for free. */
@utility content-auto {
  content-visibility: auto; /* becomes content-auto, md:content-auto, ... */
}

/* A new variant, registered in CSS rather than a plugin's addVariant(). */
@custom-variant pointer-coarse (@media (pointer: coarse));
```

```html
<!-- The plugin's utilities now exist and compile. -->
<article class="prose dark:prose-invert pointer-coarse:text-lg">…</article>
```

**Bad Example** — v3 JS plugin config on a v4 project

```js
// tailwind.config.js — v4 does NOT auto-load this; the plugins never register.
module.exports = {
  // The `prose` classes silently do not exist → article renders unstyled.
  plugins: [require("@tailwindcss/typography"), require("@tailwindcss/forms")],
};
```

```js
// Reinstalling a plugin v4 already ships as core → redundant, can conflict.
plugins: [require("@tailwindcss/container-queries")]; // @container is built in
```

## Common Mistakes

- Registering plugins in a `plugins: []` array on v4 and assuming they load — they
  do not without an explicit `@config` pointing at the JS file.
- Writing a full plugin (`addUtilities`) for something a two-line `@utility` handles.
- Installing `@tailwindcss/container-queries` on v4, where it is already core.
- Forgetting `dark:prose-invert`, leaving `prose` content unreadable in dark mode.
- Applying `@tailwindcss/forms` with the `base` strategy and then fighting its resets
  instead of choosing the `class` strategy for opt-in control.
- Defining plugin tokens outside `@theme`, so they miss autocomplete and variable output.

## Production Tips

- Pin plugin versions to the same major as Tailwind; a v3 plugin on v4 may register
  utilities against removed internals.
- Review the plugin's generated CSS in the build output at least once; confirm it only
  emits what you use.
- Prefer official `@tailwindcss/*` plugins over community forks for long-term support.

## AI Review Checklist

- Are plugins loaded with `@plugin` in CSS (v4), not a `plugins: []` JS array?
- Is a full plugin avoided where `@utility` or `@theme` would do?
- Are v4-core features (container queries) used instead of the old standalone plugins?
- Does typography content include `dark:prose-invert` where dark mode is supported?
- Are plugin options passed via the nested `@plugin { … }` block, not JS arguments?
- Are custom variants registered with `@custom-variant` rather than a plugin?

## Related

- `knowledge/tailwind/15-customization.md`
- `knowledge/tailwind/16-theme.md`
- `knowledge/tailwind/17-components.md`
- `knowledge/tailwind/09-typography.md`
- `knowledge/tailwind/24-react.md`
