---
id: tailwind/01-installation
topic: tailwind
slug: installation
title: "Tailwind CSS Installation"
type: doc
order: 1
status: ready
tags: [tailwind, installation, content, tailwindcss, postcss-import, autoprefixer, tailwind.config.js, "@tailwindcss"]
related: [tailwind/00-overview, tailwind/02-core-concepts, tailwind/15-customization, tailwind/16-theme, tailwind/23-nextjs]
when_to_use: "Read before setting up Tailwind in a new project or upgrading an existing build."
---
# Tailwind CSS Installation

## Purpose

This document defines how to install and wire up **Tailwind CSS v4** so that utility
classes actually compile into CSS. It covers the three supported entry points — the Vite
plugin, the PostCSS plugin, and the standalone CLI — and the single line of CSS that
replaces v3's directives. Get this wrong and the whole framework silently produces no
styles.

## Why It Matters

Installation is where v3 knowledge does the most damage. v4 removed `npx tailwindcss init`,
the required `tailwind.config.js`, the `content` array, and the `@tailwind base/components/utilities`
directives. An agent that reproduces the v3 setup on a v4 project gets a build that runs
without error but emits an empty or broken stylesheet — a failure that looks like "Tailwind
isn't working" and burns hours. The correct v4 setup is shorter, so the fix is to unlearn,
not to add.

## Core Principles

- **Pick the integration that matches the toolchain.** Vite project → `@tailwindcss/vite`.
  Framework on PostCSS → `@tailwindcss/postcss`. No bundler → `@tailwindcss/cli`.
- **One import replaces three directives.** `@import "tailwindcss";` is the whole entry
  point in v4. There is no `@tailwind base`.
- **Content is auto-detected.** v4 scans your source automatically; you do not maintain a
  `content` glob. Only override detection when files live outside the project root.
- **Configuration is optional and lives in CSS.** Customize via `@theme` in your CSS
  (see [16-theme](16-theme.md)); a JS config is legacy and loaded explicitly with `@config`.

## Best Practices

- Prefer the **Vite plugin** for Vite-based apps (React, Vue, SvelteKit): it is faster
  than PostCSS and needs no `postcss.config.js`.
- Pin the major version in `package.json` (`"tailwindcss": "^4"`) and commit the lockfile
  so CI builds the same CSS you built locally.
- Keep the Tailwind import as the first line of your global stylesheet so your own layers
  can override or extend it predictably.
- Verify browser targets: v4 requires Safari 16.4+, Chrome 111+, and Firefox 128+. If you
  must support older browsers, stay on v3 — do not ship v4 output that silently degrades.

## Examples

**Good Example** — Vite plugin, v4 idioms

```ts
// vite.config.ts
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite"; // official first-party plugin

export default defineConfig({
  plugins: [tailwindcss()], // no postcss.config.js, no content array needed
});
```

```css
/* src/styles.css — the entire Tailwind entry point in v4 */
@import "tailwindcss";

/* Customize by extending the theme in CSS, not in a JS config file. */
@theme {
  --color-brand: oklch(0.62 0.19 259); /* becomes bg-brand, text-brand, ... */
}
```

**Bad Example** — v3 setup on a v4 project

```js
// tailwind.config.js — v4 does NOT require or auto-load this file
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"], // v4 auto-detects content; this is ignored
  theme: { extend: {} },
};
```

```css
/* v4 removed these directives — they no-op and emit no base styles */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Common Mistakes

- Running `npx tailwindcss init` (removed in v4) and building the setup around the
  generated config.
- Keeping `@tailwind base/components/utilities` after upgrading — utilities never load.
- Hand-maintaining a `content` array and assuming missing classes mean a glob is wrong,
  when v4 has already auto-detected them.
- Installing bare `tailwindcss` and importing it as a PostCSS plugin directly; in v4 the
  PostCSS plugin is the separate `@tailwindcss/postcss` package.
- Adding `autoprefixer` and `postcss-import` manually — v4 handles both internally.

## Production Tips

- Let the build tool tree-shake unused utilities; do not disable content detection to
  "include everything." That reinflates the bundle Tailwind exists to keep small.
- In monorepos, if source lives outside the CSS file's directory, add explicit sources
  with `@source "../other-package/src";` rather than loosening detection globally.

## AI Review Checklist

- Is the installed major version confirmed (`^4`) before choosing a setup?
- Does the CSS use `@import "tailwindcss";` and not `@tailwind` directives?
- Is the correct integration package used (`@tailwindcss/vite` / `-postcss` / `-cli`)?
- Is there no stray `tailwind.config.js` with a `content` array being relied upon?
- Are `autoprefixer` and `postcss-import` absent (handled by v4 internally)?
- Are the project's browser targets compatible with v4's baseline?

## Related

- `knowledge/tailwind/00-overview.md`
- `knowledge/tailwind/02-core-concepts.md`
- `knowledge/tailwind/15-customization.md`
- `knowledge/tailwind/16-theme.md`
- `knowledge/tailwind/23-nextjs.md`
