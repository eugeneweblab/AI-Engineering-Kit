---
id: nextjs/17-fonts
topic: nextjs
slug: fonts
title: "Next.js Fonts"
type: doc
order: 17
status: ready
tags: [nextjs, fonts, Inter, RootLayout, ReactNode, size-adjust, Header, "@theme"]
related: [nextjs/20-performance, performance/12-fonts, nextjs/16-images]
when_to_use: "Read before loading or optimizing web fonts in a Next.js app."
---
# Next.js Fonts

## Purpose

This document defines the engineering standards for working with fonts in Next.js applications.

The objective is to deliver fast-loading, accessible, and visually consistent typography while minimizing layout shifts and improving Core Web Vitals.

Fonts should be considered a critical part of application performance rather than a purely visual asset.

---

## Core Principle

Load only the fonts that users need.

Optimize typography without sacrificing performance.

---

## Typography Goals

Every application should strive for:

- fast font loading;
- minimal layout shifts;
- readable typography;
- consistent rendering;
- accessible text;
- efficient caching.

---

## Font Loading

Prefer the built-in `next/font` optimization.

Benefits include:

- automatic self-hosting (fonts are downloaded at build time and served from your own origin);
- no runtime request to Google or any third party;
- automatic `size-adjust` fallback metrics to reduce layout shift;
- `preload` and `font-display: swap` applied by default.

Avoid loading fonts directly from external CDNs unless required.

`next/font` is not a runtime `fetch` — it runs at build time and self-hosts the
files, so the uncached-`fetch` default does not apply here. The font
assets are emitted as static, content-hashed files and served with immutable
caching automatically.

> A `next/font` loader (`Inter(...)`, `localFont(...)`) must be called at
> **module scope** with **literal** arguments. It cannot be called inside a
> component, a hook, or with values computed at runtime — the loader is
> evaluated at build time.

---

## Local Fonts

Use local fonts when:

- branding requires custom typography;
- commercial licenses prohibit redistribution;
- offline availability is required.

Store font files inside the app (co-located with the loader), not in `public/`.
`next/font/local` reads the file at build time and emits a hashed, self-hosted
asset — you do not reference the raw path at runtime.

Load them with `next/font/local`. A variable font is a single file; static
fonts list one entry per weight/style:

```ts
// app/fonts.ts
import localFont from "next/font/local";

// Single variable font file — preferred.
export const brand = localFont({
  src: "./fonts/BrandVariable.woff2",
  display: "swap",
  variable: "--font-brand",
});

// Static family — one src entry per weight/style.
export const brandStatic = localFont({
  src: [
    { path: "./fonts/Brand-Regular.woff2", weight: "400", style: "normal" },
    { path: "./fonts/Brand-Bold.woff2", weight: "700", style: "normal" },
    { path: "./fonts/Brand-Italic.woff2", weight: "400", style: "italic" },
  ],
  display: "swap",
  variable: "--font-brand",
});
```

---

## Google Fonts

Use `next/font/google` — it self-hosts Google Fonts at build time, so no
request ever reaches Google's servers in production.

Call the loader once at module scope, then apply it in the **root layout** so
the font covers the whole tree. Expose it as a CSS variable so any component
(server or client) can reference it without importing the loader:

```ts
// app/fonts.ts
import { Inter } from "next/font/google";

// Variable font: omit `weight` to load the full axis in one file.
export const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});
```

```tsx
// app/layout.tsx  (Server Component — no "use client")
import { inter } from "./fonts";
import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
```

```css
/* app/globals.css */
body {
  font-family: var(--font-inter), system-ui, sans-serif;
}
```

Avoid importing fonts using CSS `@import` or a `<link>` to `fonts.googleapis.com`
— that reintroduces the third-party request, render-blocking, and layout shift
that `next/font` exists to remove.

---

## Font Variants

Load only the required:

- font weights;
- font styles;
- subsets.

Avoid downloading unused font variants.

For **non-variable** Google fonts you must pass an explicit `weight`. For
variable fonts, omit `weight` to get the full axis in a single file.

```ts
// Good — variable font, one file, the whole weight axis available.
import { Inter } from "next/font/google";
export const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

// Good — non-variable font: request only the weights you actually render.
import { Roboto } from "next/font/google";
export const roboto = Roboto({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-roboto",
});
```

```ts
// Bad — pulling nine weights when the design uses two.
import { Roboto } from "next/font/google";
export const roboto = Roboto({
  subsets: ["latin"],
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"],
});
```

---

## Font Subsets

Configure only the language subsets required by the application.

Examples:

- latin;
- latin-ext;
- cyrillic;
- greek;
- vietnamese.

Smaller subsets improve loading performance.

```ts
// Only the subsets you actually preload — each one adds a preloaded file.
import { Noto_Sans } from "next/font/google";
export const notoSans = Noto_Sans({
  subsets: ["latin", "cyrillic"],
  variable: "--font-noto",
});
```

The `subsets` you declare are the ones `next/font` preloads. Omitting `subsets`
entirely disables preloading and logs a warning, so always declare at least the
primary subset.

---

## Font Display

Use an appropriate font display strategy.

Prefer behavior that minimizes invisible text while reducing layout shifts.

Typography should remain readable during loading.

`next/font` defaults `display` to `swap`, which renders a fallback immediately
and swaps in the web font when ready — no flash of invisible text (FOIT). Set it
explicitly to document intent:

```ts
import { Inter } from "next/font/google";
export const inter = Inter({
  subsets: ["latin"],
  display: "swap", // "auto" | "block" | "swap" | "fallback" | "optional"
  variable: "--font-inter",
});
```

Use `display: "optional"` for non-critical fonts where you would rather show the
fallback than risk any layout shift on slow connections.

---

## Font Preloading

Preload critical fonts used above the fold.

Avoid preloading fonts that are only used on specific pages.

`next/font` preloads automatically whenever a `subsets` value is provided. For a
font used only on one route, load it in that route's file (not the root layout)
and set `preload: false` so it is not fetched eagerly on every page:

```ts
// app/(marketing)/pricing/fonts.ts — used only on the pricing page.
import { Playfair_Display } from "next/font/google";
export const playfair = Playfair_Display({
  subsets: ["latin"],
  preload: false,
  variable: "--font-playfair",
});
```

---

## Font Fallbacks

Always define appropriate fallback fonts.

`next/font` already generates a metric-adjusted fallback (using `size-adjust`,
`ascent-override`, etc.) so the fallback occupies almost the same space as the
web font — this is what keeps CLS near zero during the swap. You can steer which
system font it adjusts against and add explicit fallbacks with `fallback` and
`adjustFontFallback`:

```ts
import { Inter } from "next/font/google";
export const inter = Inter({
  subsets: ["latin"],
  fallback: ["system-ui", "arial"],
  adjustFontFallback: true, // default; set false to opt out of the metric fallback
  variable: "--font-inter",
});
```

Fallback fonts should closely match the primary font's metrics to reduce layout
shifts.

---

## Layout Stability

Typography should not introduce unexpected layout movement.

Verify:

- line height;
- font metrics;
- fallback compatibility;
- responsive scaling.

Minimize Cumulative Layout Shift (CLS).

---

## Responsive Typography

Typography should adapt to different screen sizes.

Review:

- font size;
- line height;
- spacing;
- readability.

Avoid fixed typography that performs poorly on mobile devices.

---

## Accessibility

Ensure typography supports:

- sufficient contrast;
- readable font sizes;
- scalable text;
- predictable spacing.

Users should be able to zoom content without losing readability.

---

## Variable Fonts

Prefer variable fonts when they replace multiple static font files.

Benefits include:

- fewer network requests;
- smaller total payload;
- greater design flexibility.

Avoid using variable fonts if browser compatibility requirements prohibit them.

Exposing the font as a CSS variable (`variable: "--font-inter"`) is the cleanest
way to wire it into a design system. With Tailwind, map the variable in your
theme so utilities like `font-sans` resolve to it. In Tailwind v4 this is done in
CSS:

```css
/* app/globals.css */
@import "tailwindcss";

@theme inline {
  --font-sans: var(--font-inter), system-ui, sans-serif;
}
```

The `--font-inter` variable becomes available anywhere under the element that
carries `inter.variable` (the `<html>` tag in the root layout example above).

---

## Caching

Fonts should be cached aggressively.

Version font assets to support long cache lifetimes without serving outdated files.

---

## Performance

Review:

- font file size;
- number of variants;
- preload usage;
- caching strategy;
- layout stability.

Typography should contribute positively to Core Web Vitals.

---

## Organization

Keep font configuration centralized: call each loader once in a single module
and import the result where needed.

```ts
// Good — app/fonts.ts: one loader call, reused everywhere.
import { Inter } from "next/font/google";
export const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
```

```tsx
// Good — every consumer imports the shared instance.
import { inter } from "@/app/fonts";
// ...className={inter.variable}
```

```tsx
// Bad — calling the loader again in a component. Each call produces a new
// hashed instance and a separate preload, and next/font also rejects loader
// calls outside module scope at build time.
export default function Header() {
  const inter = Inter({ subsets: ["latin"] }); // ✗ build error
  return <h1 className={inter.className}>...</h1>;
}
```

Avoid scattering font configuration throughout the application.

---

## Security

Load fonts only from trusted sources.

Avoid introducing unnecessary third-party font providers.

---

## AI Execution Checklist

## Investigation

☐ Review typography requirements.

☐ Identify required font families.

☐ Review language support.

☐ Review performance goals.

---

## Planning

☐ Optimize font loading.

☐ Minimize variants.

☐ Configure fallbacks.

☐ Enable caching.

---

## Verification

☐ Fonts load efficiently.

☐ Layout shifts minimized.

☐ Typography accessible.

☐ Responsive behavior verified.

☐ Caching configured.

☐ Performance reviewed.

---

## Examples

**Good Example** — self-hosted at build time, one weight axis, exposed as a variable

```ts
// app/fonts.ts
import { Inter, JetBrains_Mono } from 'next/font/google';

// next/font downloads the files at BUILD time and serves them from your origin:
// no request to Google at runtime, no third-party connection, no layout shift.
export const sans = Inter({
  subsets: ['latin'],
  display: 'swap',              // text is visible immediately in the fallback
  variable: '--font-sans',
  // A variable font covers every weight in one file — smaller than three statics.
  axes: [],
});

export const mono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono',
  weight: ['400'],              // only the weight actually used
});
```

```tsx
// app/layout.tsx
import { sans, mono } from './fonts';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
```

```css
/* The fallback is metric-adjusted automatically, so the swap does not move text. */
:root {
  --font-fallback: var(--font-sans), ui-sans-serif, system-ui, sans-serif;
}
```

**Bad Example** — a stylesheet link, every weight, and a blocking swap

```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {/* A render-blocking request to a third-party origin: an extra DNS lookup,
            TLS handshake, and round trip before any text can paint. */}
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=block"
          rel="stylesheet"
        />
      </head>
      {/* display=block hides the text entirely until the font arrives (FOIT),
          and nine weights are downloaded to use two. */}
      <body style={{ fontFamily: 'Inter' }}>{children}</body>
    </html>
  );
}
```

---

## Common Mistakes

Avoid:

Loading unnecessary font weights.

Using CSS `@import` for fonts.

Missing fallback fonts.

Loading fonts from multiple providers.

Ignoring layout shifts.

Preloading every font.

Using decorative fonts for body text.

Duplicating font configuration.

---

## Completion Criteria

Font implementation is complete when:

- fonts load efficiently;
- only required variants are included;
- layout shifts are minimized;
- typography remains accessible;
- caching is configured appropriately;
- performance objectives are satisfied.

---

## Summary

Typography directly affects usability, accessibility, and performance.

By using Next.js font optimization, minimizing downloaded variants, configuring appropriate fallbacks, and preventing layout shifts, applications provide a faster and more consistent user experience across all devices.

## Related

- `knowledge/nextjs/20-performance.md`
- `knowledge/performance/12-fonts.md`
- `knowledge/nextjs/16-images.md`
