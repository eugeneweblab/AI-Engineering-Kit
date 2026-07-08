---
id: nextjs/100-common-antipatterns
topic: nextjs
slug: common-antipatterns
title: "Common Anti-Patterns"
type: doc
order: 100
status: ready
tags: [nextjs, common-antipatterns]
related: [nextjs/06-server-components, nextjs/07-client-components, nextjs/10-caching, nextjs/11-server-actions, nextjs/99-ai-review-checklist]
when_to_use: "Read when writing or reviewing App Router code to recognize and avoid the recurring mistakes that ship silently."
---
# Common Anti-Patterns

## Purpose

This document catalogs the recurring mistakes made in Next.js App Router codebases. Each
entry names the anti-pattern, explains *why it is wrong* (the concrete failure it causes),
and gives *the fix*. An agent uses this as a lookup: if the code resembles the "wrong"
shape, apply the fix. These are the patterns most likely to compile, pass a quick test, and
still fail in production.

## Why It Matters

The App Router's power — one file that can run on server or client, implicit caching, colocated
mutations — is also its foot-gun. The same misunderstanding produces the same bug across
teams: a secret in the bundle, a spinner where a static page belonged, a mutation that
trusts the client. Naming these patterns makes them recognizable on sight so they get fixed
in review instead of in an incident.

## Anti-Patterns

### 1. `"use client"` at the top of a page or layout

- **Why it is wrong:** It turns the entire subtree into Client Components, shipping data
  logic and dependencies to the browser, losing server-side data access, and inflating the bundle.
- **The fix:** Keep pages and layouts as Server Components. Push `"use client"` down to the
  smallest interactive leaf (the button, the input) and pass server-rendered content in as `children`.

### 2. Importing server-only code into Client Components

- **Why it is wrong:** Anything a Client Component imports is bundled to the browser. A db
  client, API key, or private query becomes readable by any user — total exposure, not a bug.
- **The fix:** Keep data access and secrets in server-only modules (mark with
  `import "server-only"`). Client Components receive data as serializable props, never by importing the source.

### 3. Fetching on the client what the server could render

- **Why it is wrong:** A `useEffect`+`fetch` adds a round trip, a loading spinner, and a
  waterfall for content the Server Component could have rendered directly — hurting LCP and SEO.
- **The fix:** Fetch in an async Server Component and pass the result down. Reserve client
  fetching for data that is genuinely user-specific and post-interaction.

### 4. Assuming `fetch` is cached by default

- **Why it is wrong:** In Next.js 15+, `fetch` is uncached by default. Code written for the
  old default silently refetches on every request (or, if you assume the reverse, serves stale data).
- **The fix:** Make caching explicit: `cache: "force-cache"` or `next: { revalidate: N }`
  for cacheable data, `cache: "no-store"` for per-request data. State the intent in code.

### 5. Calling request APIs synchronously

- **Why it is wrong:** `cookies()`, `headers()`, `params`, and `searchParams` are async in
  Next.js 15+. Using them synchronously throws at runtime even though older examples showed it working.
- **The fix:** `await` them: `const store = await cookies();`. Await `params`/`searchParams`
  props before reading their fields.

### 6. Server Actions without input validation or authorization

- **Why it is wrong:** A Server Action is a public POST endpoint. The client is
  attacker-controlled, so unvalidated input and missing auth checks let anyone mutate any data.
- **The fix:** Validate every argument with a schema (e.g. Zod) and re-check authentication
  and authorization at the top of the action — never rely on the UI having hidden the control.

### 7. Leaking secrets through `NEXT_PUBLIC_`

- **Why it is wrong:** Every `NEXT_PUBLIC_`-prefixed variable is inlined into the client
  bundle. Prefixing a secret (API key, token) publishes it to every visitor.
- **The fix:** Only expose truly public values via `NEXT_PUBLIC_`. Read secrets from
  unprefixed env vars in server code exclusively.

### 8. Using `<a>` instead of `<Link>` for internal navigation

- **Why it is wrong:** A raw `<a>` triggers a full-page reload, discarding client state,
  refetching everything, and skipping prefetch — a visibly slower transition.
- **The fix:** Use `next/link` `<Link>` for internal routes so navigation is client-side and prefetched.

### 9. Missing `error.tsx` and `loading.tsx` boundaries

- **Why it is wrong:** Without an error boundary, one failing segment can crash a larger part
  of the UI; without a loading boundary, streaming and Suspense fall back to a blank or blocked page.
- **The fix:** Add `error.tsx` to segments that can fail and `loading.tsx` (or `<Suspense>`)
  around async work so failures and pending states are contained and streamed.

### 10. `<img>` and external font links instead of framework primitives

- **Why it is wrong:** Plain `<img>` skips optimization, lazy loading, and dimensions,
  causing layout shift and oversized payloads; external font `<link>`s block rendering and shift text.
- **The fix:** Use `next/image` (with `width`/`height` or `fill`) and `next/font` so assets
  are optimized, self-hosted, and shift-free.

### 11. Mutating without revalidating the cache

- **Why it is wrong:** After a successful mutation, cached pages and data still show the old
  value, so users see stale UI until an unrelated refresh.
- **The fix:** Call `revalidatePath(...)` or `revalidateTag(...)` (or `router.refresh()` on
  the client) after the mutation so affected caches update.

## Common Mistakes

- Treating these anti-patterns as style nits rather than correctness/security defects.
- Fixing the symptom (adding a spinner) instead of the cause (fetch on the client).
- Adding `"use client"` to silence an error instead of understanding which code needs the browser.

## AI Review Checklist

- Does any file place `"use client"` on a page/layout rather than an interactive leaf?
- Can any secret or server-only module be reached from the client import graph?
- Is any content fetched client-side that a Server Component could render?
- Is `fetch` caching explicit, and are request APIs awaited (Next.js 15+)?
- Does every Server Action validate input and re-check authorization?
- Are `<Link>`, `next/image`, `next/font`, and error/loading boundaries used where required?
- Is the cache revalidated after every mutation?

## Related

- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/07-client-components.md`
- `knowledge/nextjs/10-caching.md`
- `knowledge/nextjs/11-server-actions.md`
- `knowledge/nextjs/99-ai-review-checklist.md`
