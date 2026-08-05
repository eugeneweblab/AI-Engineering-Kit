---
id: tailwind/23-nextjs
topic: tailwind
slug: nextjs
title: "Next.js"
type: doc
order: 23
status: ready
tags: [tailwind, nextjs, postcss-import, autoprefixer, "@tailwindcss", RootLayout, className, Providers]
related: [tailwind/01-installation, tailwind/24-react, tailwind/12-dark-mode, tailwind/16-theme, tailwind/19-performance]
when_to_use: "Read before setting up or reviewing Tailwind in a Next.js App Router project."
---
# Next.js

## Purpose

This document defines how to integrate Tailwind CSS v4 with Next.js (App Router):
the PostCSS setup, where the global stylesheet is imported, how dark mode avoids a
flash under server rendering, and how `next/font` feeds font tokens into `@theme`.
It is written so an agent wires Tailwind into Next.js without the two classic
failures — CSS that never loads and a theme that flashes on every navigation.

Next.js compiles CSS through PostCSS, so v4 uses the `@tailwindcss/postcss` plugin
(not the Vite plugin). Everything else is standard v4: one `@import "tailwindcss"`
in a global stylesheet, imported once in the root layout.

## Why It Matters

Two integration mistakes dominate Next.js + Tailwind. First, importing the global
CSS in the wrong place (or a Client Component that is not always mounted) so styles
load inconsistently or not at all. Second, deciding dark mode in a React effect —
which, under server rendering, guarantees a flash of the wrong theme on first paint
*and* a hydration mismatch warning. Both are invisible on a fast local machine and
obvious to users. Getting the import location and the pre-hydration theme script
right eliminates both.

## Core Principles

- **Use the PostCSS plugin, not the Vite plugin.** Next.js runs PostCSS; install
  `@tailwindcss/postcss` and reference it in `postcss.config.mjs`.
- **Import the global stylesheet once, in the root layout.** `app/layout.tsx` is the
  single import site so every route gets the styles exactly once.
- **The theme must be decided before hydration.** Server HTML cannot read `localStorage`;
  set the class in a blocking inline script in `<head>` and add `suppressHydrationWarning`
  on `<html>` (see [12-dark-mode](12-dark-mode.md)).
- **Server Components can carry Tailwind classes.** Utilities are just `className`
  strings; only add `"use client"` when the component needs interactivity, not to style it.
- **Feed `next/font` into the theme.** Expose the font as a CSS variable and map it to a
  `--font-*` token so `font-sans` uses the optimized font.

## Best Practices

- Configure PostCSS with a single plugin: `{ plugins: { "@tailwindcss/postcss": {} } }`.
  Do not add `autoprefixer` or `postcss-import` — v4 handles both.
- Keep `app/globals.css` as `@import "tailwindcss";` plus your `@theme` and register it
  once with `import "./globals.css"` at the top of `app/layout.tsx`.
- Register the dark variant in CSS and set the class in a pre-hydration script; add
  `suppressHydrationWarning` to `<html>` because the script mutates it before React.
- Load fonts with `next/font` using `variable`, then map that variable in `@theme`:
  `--font-sans: var(--font-inter)`. This avoids layout shift and external font requests.
- Build a `cn()` helper (`clsx` + `tailwind-merge`) for conditional classes shared across
  Server and Client Components (see [24-react](24-react.md)).
- Let the Next.js production build minify and hash CSS; do not disable content detection.

## Examples

**Good Example** — root layout, PostCSS, no-flash theme, font token

```js
// postcss.config.mjs — the only plugin v4 needs under Next.js
export default { plugins: { "@tailwindcss/postcss": {} } };
```

```tsx
// app/layout.tsx
import "./globals.css"; // imported exactly once, at the root
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // suppressHydrationWarning: the inline script sets `.dark` before React hydrates.
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <head>
        <script
          // Blocking, pre-paint: decides theme with no flash of the wrong colors.
          dangerouslySetInnerHTML={{
            __html: `document.documentElement.classList.toggle('dark',
              localStorage.theme === 'dark' ||
              (!('theme' in localStorage) && matchMedia('(prefers-color-scheme: dark)').matches));`,
          }}
        />
      </head>
      <body className="bg-surface font-sans text-slate-900 dark:text-slate-100">
        {children}
      </body>
    </html>
  );
}
```

```css
/* app/globals.css */
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));
@theme {
  --font-sans: var(--font-inter); /* font-sans now uses the optimized next/font */
}
```

**Bad Example** — wrong plugin, effect-driven theme, per-page CSS import

```tsx
// BUG: theme decided in an effect → server renders light, client flips after
// hydration → flash on every load + hydration mismatch warning.
"use client";
export default function Providers() {
  useEffect(() => {
    if (localStorage.theme === "dark")
      document.documentElement.classList.add("dark");
  }, []);
  // BUG: importing globals.css here (a conditionally rendered client component)
  // means styles can load late or inconsistently across routes.
}
```

```js
// BUG: Vite plugin does nothing under Next.js (it runs PostCSS, not Vite) →
// utilities never compile, the whole app renders unstyled.
import tailwindcss from "@tailwindcss/vite";
```

## Common Mistakes

- Installing `@tailwindcss/vite` in a Next.js app; it is inert under PostCSS and no styles compile.
- Importing `globals.css` in a page or a conditional Client Component instead of once in `app/layout.tsx`.
- Deciding dark mode in `useEffect`, causing a theme flash and a hydration mismatch on every load.
- Omitting `suppressHydrationWarning` on `<html>` when a pre-hydration script mutates its class.
- Adding `"use client"` just to apply Tailwind classes; utilities work fine in Server Components.
- Adding `autoprefixer`/`postcss-import` to the PostCSS config, which v4 already handles.
- Loading fonts via `<link>` instead of `next/font`, adding a request and layout shift.

## Production Tips

- Verify the CSS loads on a hard refresh with JS disabled; the page should still be styled.
- Test theme with cache disabled and throttled CPU to confirm no flash before hydration.
- Confirm the emitted CSS is one hashed file per build and served compressed (see [19-performance](19-performance.md)).

## AI Review Checklist

- Is `@tailwindcss/postcss` used (not the Vite plugin) and is it the only PostCSS plugin?
- Is the global stylesheet imported exactly once, in `app/layout.tsx`?
- Is dark mode set by a pre-hydration inline script with `suppressHydrationWarning` on `<html>`?
- Are Server Components styled with `className` without an unnecessary `"use client"`?
- Is `next/font` used and mapped into a `--font-*` token in `@theme`?
- Are `autoprefixer` and `postcss-import` absent from the config?

## Related

- `knowledge/tailwind/01-installation.md`
- `knowledge/tailwind/24-react.md`
- `knowledge/tailwind/12-dark-mode.md`
- `knowledge/tailwind/16-theme.md`
- `knowledge/tailwind/19-performance.md`
