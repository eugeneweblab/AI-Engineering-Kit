---
id: tailwind/19-performance
topic: tailwind
slug: performance
title: "Tailwind CSS Performance"
type: doc
order: 19
status: ready
tags: [tailwind, performance]
related: [tailwind/20-optimization, tailwind/27-production, tailwind/03-utility-first, tailwind/23-nextjs, tailwind/17-components]
when_to_use: "Read before diagnosing slow builds, large CSS output, or render jank in a Tailwind app."
---
# Tailwind CSS Performance

## Purpose

This document defines how to keep a Tailwind CSS v4 project fast in two dimensions:
**build performance** (how quickly the engine compiles your CSS) and **runtime
performance** (how small and cheap the shipped stylesheet is to parse and paint).
It is written so an agent can spot the patterns that inflate build time or CSS size
and fix them at the source.

Tailwind's core performance promise is that you ship only the utilities you use. The
Oxide engine (v4) makes builds fast by default; the ways to lose that speed are almost
always self-inflicted — dynamic class names the scanner cannot see, or safelists that
reinflate the bundle Tailwind exists to shrink.

## Why It Matters

CSS is render-blocking: the browser cannot paint until it downloads and parses the
stylesheet. A bloated Tailwind build — caused by a broad safelist or by disabling
content detection — turns a 10 KB file into hundreds of KB, delaying first paint on
every page. On the build side, patterns that defeat the scanner force full rebuilds
and slow the dev feedback loop. Both failures are invisible in local testing on fast
hardware and only show up as poor field metrics (LCP, CLS) for real users.

## Core Principles

- **The scanner only keeps classes it can see as complete strings.** Tailwind extracts
  utilities by matching literal substrings in source. A class assembled at runtime
  (`` `bg-${color}-500` ``) is never emitted — style it with complete class names.
- **Ship what you use, nothing more.** Do not safelist broadly or disable content
  detection to "be safe." That defeats tree-shaking and reinflates the bundle.
- **Fast builds come from letting the engine auto-detect.** v4 scans source
  automatically; hand-maintaining wide globs or scanning `node_modules` slows builds.
- **CSS size, not class-string length, is what ships.** Repeating `p-4` on 500 elements
  emits `.p-4{}` once. Long class lists in markup are cheap; unique arbitrary values are
  what grow the file.

## Best Practices

- Use complete, static class names so the scanner keeps them. Map data to a lookup of
  full classes rather than interpolating fragments (see the Good example).
- Prefer design-scale utilities over arbitrary values: `p-4` reuses one rule; `p-[17px]`,
  `p-[18px]`, `p-[19px]` each emit a distinct rule and grow the file.
- Never scan dependencies: keep `node_modules` out of detected sources unless a specific
  package ships Tailwind classes you actually use, then add it narrowly with `@source`.
- Let the framework minify and hash the CSS in production; do not disable minification.
- Use `content-visibility: auto` (via a `content-auto` utility) on long, offscreen lists
  to cut layout/paint cost — a runtime win independent of CSS size.
- Reuse via components/loops (see [17-components](17-components.md)) so one class recipe
  serves many elements instead of copy-pasting divergent arbitrary values.

## Examples

**Good Example** — static classes the scanner can see; scoped source detection

```tsx
// Full class strings → all three are emitted and safe to tree-shake.
const TONE = {
  info: "bg-blue-100 text-blue-800",
  warn: "bg-amber-100 text-amber-800",
  error: "bg-red-100 text-red-800",
} as const;

export function Badge({ tone }: { tone: keyof typeof TONE }) {
  return <span className={`rounded px-2 py-1 ${TONE[tone]}`}>{tone}</span>;
}
```

```css
/* app.css — auto-detection is on; add outside sources narrowly, never node_modules broadly */
@import "tailwindcss";
@source "../packages/ui/src"; /* only the sibling package that uses Tailwind */
```

**Bad Example** — runtime-built classes and a bundle-inflating safelist

```tsx
// BUG: `bg-${tone}-100` is never a literal string in source → class never emitted,
// so the badge renders with no background. "Fixing" it by safelisting makes it worse.
export function Badge({ tone }: { tone: string }) {
  return <span className={`bg-${tone}-100 text-${tone}-800`}>{tone}</span>;
}
```

```css
/* BUG: safelisting every color × shade emits thousands of unused rules → huge CSS,
   slower parse, worse LCP. This reinflates exactly what Tailwind tree-shakes away. */
@source inline("{bg,text}-{red,blue,green,amber}-{100,200,300,400,500,600,700,800}");
```

## Common Mistakes

- Building class names by string interpolation and wondering why styles vanish in the
  production build (they were tree-shaken because they were never seen).
- Adding a wide safelist as a blanket fix, trading a correctness bug for a bloat bug.
- Adding `node_modules` to detected sources, ballooning both scan time and output.
- Chasing "class-string is too long" as a performance problem — it is not; unique CSS
  rules are the cost.
- Preloading fonts and images but leaving the render-blocking Tailwind CSS unminified.
- Rendering thousands of rows without `content-visibility`, paying full paint cost for
  offscreen DOM.

## Production Tips

- Measure the emitted CSS size in CI and alert if it jumps; a sudden increase usually
  means a new safelist or an arbitrary-value explosion.
- Profile dev rebuild times; if they regress, check for newly scanned directories.
- Inline critical CSS or let the framework do it, and load the rest without blocking.

## AI Review Checklist

- Are all utility classes complete literal strings (no runtime interpolation)?
- Is content auto-detection used, with `@source` added narrowly and never for `node_modules`?
- Is the safelist empty or minimal, rather than a broad `@source inline(...)` net?
- Are design-scale utilities preferred over many unique arbitrary values?
- Is the production CSS minified and cache-hashed?
- Are long offscreen lists using `content-visibility` to reduce paint cost?

## Related

- `knowledge/tailwind/20-optimization.md`
- `knowledge/tailwind/27-production.md`
- `knowledge/tailwind/03-utility-first.md`
- `knowledge/tailwind/23-nextjs.md`
- `knowledge/tailwind/17-components.md`
