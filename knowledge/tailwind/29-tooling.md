---
id: tailwind/29-tooling
topic: tailwind
slug: tooling
title: "Tooling"
type: doc
order: 29
status: ready
tags: [tailwind, tooling]
related: [tailwind/01-installation, tailwind/25-debugging, tailwind/27-production, tailwind/26-best-practices, tailwind/19-performance]
when_to_use: "Read when setting up or reviewing the Tailwind toolchain: editor, linting, class sorting, and build plugins."
---
# Tooling

## Purpose

This document defines the toolchain that makes a Tailwind codebase fast to write
and safe to maintain: the editor extension, the Prettier class sorter, the ESLint
rules, the build plugins, and the small runtime helpers (`clsx`, `tailwind-merge`,
`class-variance-authority`). It is written so an agent can set up or review a
Tailwind project's tooling and know why each piece is there.

Tailwind's ergonomics depend heavily on tooling. Without IntelliSense and the
sorter, utility-first is error-prone; with them, it is faster and more consistent
than hand-written CSS.

## Why It Matters

Tailwind moves styling into long class strings, which are easy to typo, easy to
disorder, and easy to duplicate. The tooling turns those weaknesses into
non-issues: IntelliSense catches typos as you type, the Prettier plugin ends all
ordering debates, the ESLint plugin flags conflicts and invalid classes in CI, and
the build plugin does the purging that keeps production small. Skipping the tooling
does not just cost convenience — it lets exactly the class of silent bugs
(purged classes, merge conflicts) reach production that the rest of these docs
work to prevent.

## Core Principles

- **Editor feedback beats runtime discovery.** IntelliSense turns invalid-class and
  wrong-token mistakes into red squiggles, not visual bugs.
- **Automate class order.** The Prettier plugin makes order deterministic so it is
  never reviewed, discussed, or diffed.
- **Lint conflicts mechanically.** An ESLint rule catches contradictory utilities
  and typos that humans miss in a 15-class string.
- **Use the framework's build plugin.** It runs content detection and minification;
  the CDN is a prototype tool only.
- **Keep the runtime helpers tiny and standard.** `clsx` + `tailwind-merge` (often
  via `cva`) is the whole runtime footprint you need.

## Best Practices

- Install the official Tailwind CSS IntelliSense editor extension and point it at
  your CSS entry so it resolves your custom `@theme` tokens, not just defaults.
- Add `prettier-plugin-tailwindcss` so classes sort in a canonical order on save;
  configure `tailwindFunctions`/`tailwindAttributes` so it also sorts inside
  `cn()`, `cva()`, and custom props.
- Add `eslint-plugin-tailwindcss` (or `eslint-plugin-better-tailwindcss`) with
  rules for conflicting classes and unknown classes; run it in CI as a gate.
- Wire the build with `@tailwindcss/vite` or `@tailwindcss/postcss`; use
  `@tailwindcss/cli` only for standalone/non-bundler builds.
- Standardize on one `cn()` helper built from `clsx` + `tailwind-merge`; use
  `class-variance-authority` for variant components.
- Pin the tooling versions and keep the editor plugin, Prettier plugin, and core
  engine on the same major version so token resolution stays consistent.
- Configure the sorter and IntelliSense in the repo (committed config), not per
  developer, so behavior is identical for everyone and CI.

## Examples

**Good Example** — sorter aware of helpers, correct build plugin

```js
// prettier.config.js — sort classes everywhere they actually appear
export default {
  plugins: ["prettier-plugin-tailwindcss"],
  // Sort inside cn(...) and cva(...) too, not just className="".
  tailwindFunctions: ["cn", "cva", "clsx"],
};
```

```ts
// lib/cn.ts — the one canonical class combiner for the whole app
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));
```

**Bad Example** — no tooling, CDN build, ad-hoc merging

```html
<!-- CDN "build": no purge, no minify, recompiles in the browser. -->
<script src="https://cdn.tailwindcss.com"></script>
```

```tsx
// No IntelliSense to catch "flexx"/"justfy"; no sorter, so order churns in every
// diff; hand concat means conflicting py-* both ship and order picks the winner.
const cls = "flexx items-center justfy-between py-2 " + (tight ? "py-1" : "");
```

## Common Mistakes

- Working without the IntelliSense extension, so class typos become runtime visual
  bugs instead of editor errors.
- Not configuring `tailwindFunctions`, so classes inside `cn()`/`cva()` go unsorted
  and inconsistent.
- Skipping the ESLint plugin, letting conflicting utilities and unknown classes
  reach production.
- Using the Play CDN as the build instead of the Vite/PostCSS plugin, losing purge
  and minification.
- Reinventing class merging per file instead of one shared `cn()`.
- Version-skewing the editor plugin against the engine, so custom tokens do not
  autocomplete or resolve.

## Production Tips

- Run the Prettier sort and the Tailwind ESLint rules in CI so unsorted or
  conflicting classes fail the pipeline, not just a local pre-commit hook.
- Keep the toolchain versions in the lockfile and bump them together; a mismatched
  Prettier plugin can reorder classes in a way that changes cascade outcomes.
- Add the IntelliSense and Prettier config to the repo's recommended-extensions and
  editor settings so onboarding is zero-config.

## AI Review Checklist

- Is the Tailwind IntelliSense extension configured against the project's CSS
  entry/tokens?
- Is `prettier-plugin-tailwindcss` enabled and aware of `cn()`/`cva()` via
  `tailwindFunctions`?
- Is `eslint-plugin-tailwindcss` (or equivalent) running in CI to catch conflicts
  and unknown classes?
- Is the build using the Vite/PostCSS plugin rather than the Play CDN?
- Is there a single shared `cn()` (clsx + tailwind-merge) helper?
- Are the editor plugin, Prettier plugin, and engine on compatible versions?

## Related

- `knowledge/tailwind/01-installation.md`
- `knowledge/tailwind/25-debugging.md`
- `knowledge/tailwind/27-production.md`
- `knowledge/tailwind/26-best-practices.md`
- `knowledge/tailwind/19-performance.md`
