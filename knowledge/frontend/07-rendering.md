---
id: frontend/07-rendering
topic: frontend
slug: rendering
title: "Rendering"
type: doc
order: 7
status: ready
tags: [frontend, rendering]
related: [frontend/06-data-fetching, frontend/08-performance, frontend/11-seo, frontend/21-code-splitting, frontend/09-accessibility]
when_to_use: "Read before choosing where a page renders (server, client, static) or debugging hydration mismatches."
---
# Rendering

## Purpose

This document defines *where and when* the UI turns into HTML: server rendering (SSR),
static generation (SSG), client rendering (CSR), streaming, and hydration. It is written
so an agent can pick a rendering strategy per route and avoid the classic failures —
hydration mismatches, layout shift, and shipping a blank page that only fills in after JS.

Rendering strategy is a routing-level decision, not a global one. Different routes have
different needs; a marketing page and a logged-in dashboard should not render the same way.

## Why It Matters

Rendering determines what the user sees during the seconds before your JavaScript loads
and runs — the single biggest lever on perceived speed and on [SEO](11-seo.md). Client-only
rendering ships a blank shell, then downloads, parses, and executes a bundle before
anything appears; on a slow phone that is a multi-second white screen and an empty page for
crawlers. Server rendering paints meaningful HTML immediately. The trade-offs are real and
route-specific, so this is a decision an agent must make deliberately, not by default.

## Core Principles

- **Render on the server by default; opt into the client for interactivity.** Server HTML
  is faster to first paint, indexable, and ships less JS. The cost is server compute and
  no direct access to browser APIs.
- **Static when it can be, dynamic when it must be.** Content that is the same for everyone
  should be generated at build (SSG/ISR) and served from a CDN. Per-user or per-request
  content is dynamic (SSR).
- **Hydration must match the server output exactly.** The client's first render has to
  produce identical markup; any divergence (random values, `Date.now()`, `window` reads)
  corrupts the DOM and throws hydration errors.
- **Stream to shorten time-to-first-byte-of-content.** Send the shell immediately and flush
  slower sections as they resolve, instead of blocking the whole page on the slowest query.
- **JavaScript is a progressive enhancement, not a prerequisite.** Core content and
  navigation should be present in the HTML; interactivity layers on top.

## Best Practices

- Choose per route: **SSG/ISR** for content pages, **SSR** for personalized or real-time
  pages, **CSR** only for highly interactive app shells behind auth where SEO is irrelevant.
- Keep values that differ between server and client out of the initial render. Read
  `window`, `localStorage`, and time-based values inside effects that run only on the client.
- Reserve space for async and media content with explicit dimensions or skeletons to prevent
  **Cumulative Layout Shift** — content that jumps as it loads is a poor experience.
- Use **streaming SSR** with `Suspense` boundaries so a slow data section does not delay the
  rest of the page. Put boundaries around the slow parts, not the whole tree.
- Minimize the JavaScript that hydrates: server components / islands render most of the tree
  as static HTML and hydrate only the interactive leaves. Less hydration = faster interaction.
- Set a stable, meaningful HTML `lang`, title, and meta on the server so the first byte is
  correct for crawlers and screen readers, not patched in later by JS.
- Cache and revalidate static output with clear invalidation (tags, on-demand revalidation)
  so stale generated pages do not linger after content changes.

## Examples

**Good Example** — client-only value read after hydration, no mismatch

```tsx
// Server and client both render the same placeholder first, so hydration matches.
function LastVisited() {
  const [when, setWhen] = useState<string | null>(null);

  // localStorage only exists in the browser; reading it in render would differ
  // from the server output and break hydration. Read it after mount instead.
  useEffect(() => {
    setWhen(localStorage.getItem("lastVisit"));
  }, []);

  return <span>{when ? `Last visit: ${when}` : "Welcome"}</span>;
}
```

**Bad Example** — reads browser/time state during render → hydration mismatch + CLS

```tsx
function LastVisited() {
  // `localStorage` is undefined on the server (crash) or differs from the client,
  // so the server HTML and first client render disagree → hydration error.
  const when = localStorage.getItem("lastVisit");

  // `Date.now()` differs by the round-trip time between server and client renders,
  // guaranteeing a mismatch on every load.
  return <span>{when ?? `Now: ${Date.now()}`}</span>;
  // Image below has no dimensions → it pushes text down when it loads (layout shift).
}
```

## Common Mistakes

- Defaulting the whole app to client-side rendering, shipping a blank page to users and crawlers.
- Reading `window`, `localStorage`, or `Date.now()` during render, causing hydration mismatches.
- Wrapping the entire page in one `Suspense` boundary, so the slowest query blocks everything.
- Omitting image/embed dimensions, causing layout shift as content loads.
- Marking a route dynamic (SSR) when its content is identical for every user and could be static.
- Patching title and meta tags client-side, after crawlers have already read the empty HTML.

## Production Tips

- Watch **Core Web Vitals** — LCP, CLS, INP — in real-user monitoring; they directly reflect
  rendering choices (see [performance](08-performance.md)).
- Set cache headers and CDN rules per rendering mode; static pages should be immutable and
  long-lived, dynamic pages private and short-lived.
- Test with JavaScript disabled: the core content and links should still be there.

## AI Review Checklist

- Is each route's rendering mode chosen deliberately (SSG/ISR, SSR, or CSR) for its needs?
- Does the initial client render match the server output — no `window`/`Date` reads in render?
- Are `Suspense`/streaming boundaries around slow sections, not the whole page?
- Do images, embeds, and async slots reserve space to avoid layout shift?
- Are title, `lang`, and meta rendered on the server, not patched in later?
- Is hydration limited to interactive components rather than the entire tree?

## Related

- `knowledge/frontend/06-data-fetching.md`
- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/11-seo.md`
- `knowledge/frontend/21-code-splitting.md`
- `knowledge/frontend/09-accessibility.md`
