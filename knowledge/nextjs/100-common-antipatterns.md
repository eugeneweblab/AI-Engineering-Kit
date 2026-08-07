---
id: nextjs/100-common-antipatterns
topic: nextjs
slug: common-antipatterns
title: "Common Anti-Patterns"
type: antipatterns
order: 100
status: ready
tags: [nextjs, common-antipatterns, cookies, UserCard, Stripe, revalidatePath, NEXT_PUBLIC_, ProductsPage]
applies_to: [app-router]
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

```tsx
// Bad — "use client" on the page turns the whole subtree into a client bundle
"use client";
export default function Page() {
  return <Dashboard />; // no server data access anywhere below this line
}
```

```tsx
// Good — the page stays a Server Component; only the leaf opts into the client
// app/dashboard/page.tsx  (no directive = Server Component)
import { LikeButton } from "./like-button";

export default async function Page() {
  const stats = await getStats(); // runs on the server, never shipped
  return (
    <section>
      <h1>{stats.title}</h1>
      <LikeButton postId={stats.id} /> {/* "use client" lives in this file */}
    </section>
  );
}
```

### 2. Importing server-only code into Client Components

- **Why it is wrong:** Anything a Client Component imports is bundled to the browser. A db
  client, API key, or private query becomes readable by any user — total exposure, not a bug.
- **The fix:** Keep data access and secrets in server-only modules (mark with
  `import "server-only"`). Client Components receive data as serializable props, never by importing the source.

```tsx
// Bad — a Client Component imports the db client; its connection string is
// now inlined into the browser bundle for every visitor to read
"use client";
import { db } from "@/lib/db";

export function UserCard({ id }: { id: string }) {
  const user = db.users.find(id); // secret + query shipped to the client
  return <span>{user.name}</span>;
}
```

```tsx
// Good — mark the module server-only; the Client Component gets a plain prop
// lib/db.ts
import "server-only"; // build error if a Client Component ever imports this
export const db = createClient(process.env.DATABASE_URL!);

// user-card.tsx
"use client";
export function UserCard({ name }: { name: string }) {
  return <span>{name}</span>; // receives serializable data, imports nothing server-side
}
```

### 3. Fetching on the client what the server could render

- **Why it is wrong:** A `useEffect`+`fetch` adds a round trip, a loading spinner, and a
  waterfall for content the Server Component could have rendered directly — hurting LCP and SEO.
- **The fix:** Fetch in an async Server Component and pass the result down. Reserve client
  fetching for data that is genuinely user-specific and post-interaction.

```tsx
// Bad — client waterfall: a round trip and a spinner for content the server had
"use client";
import { useEffect, useState } from "react";

export function Products() {
  const [items, setItems] = useState<Product[] | null>(null);
  useEffect(() => {
    fetch("/api/products").then((r) => r.json()).then(setItems);
  }, []);
  if (!items) return <Spinner />; // blank until the second round trip resolves
  return <List items={items} />;
}
```

```tsx
// Good — fetch in an async Server Component and render directly (better LCP/SEO)
export default async function ProductsPage() {
  const items: Product[] = await getProducts();
  return <List items={items} />;
}
```

### 4. Assuming `fetch` is cached by default

- **Why it is wrong:** In Next.js 15+, `fetch` is uncached by default. Code written for the
  old default silently refetches on every request (or, if you assume the reverse, serves stale data).
- **The fix:** Make caching explicit: `cache: "force-cache"` or `next: { revalidate: N }`
  for cacheable data, `cache: "no-store"` for per-request data. State the intent in code.

```tsx
// Bad — relies on a default that no longer exists; caching intent is unstated.
// In Next 15+ this refetches on every request, which may or may not be intended.
const res = await fetch("https://api.example.com/products");
```

```tsx
// Good — the caching decision is explicit at every call site
// Cacheable data: cache it and revalidate at most once an hour
const products = await fetch("https://api.example.com/products", {
  next: { revalidate: 3600 },
});
// Per-request data: opt out of the Data Cache on purpose
const me = await fetch("https://api.example.com/me", { cache: "no-store" });
```

### 5. Calling request APIs synchronously

- **Why it is wrong:** `cookies()`, `headers()`, `draftMode()`, `params`, and `searchParams`
  are async. Next.js 15 made them async and kept a temporary synchronous shim; Next.js 16
  removed it, so synchronous access no longer warns — it simply fails. Older examples that
  showed it working were written during that compatibility window.
- **The fix:** `await` them: `const store = await cookies();`. Await `params`/`searchParams`
  props before reading their fields.

```tsx
// Bad — request APIs and route props are async in Next 15+; this throws at runtime
import { cookies } from "next/headers";

export default function Page({ params }: { params: { id: string } }) {
  const token = cookies().get("token"); // TypeError: cookies() is a Promise
  return <Item id={params.id} />;
}
```

```tsx
// Good — await cookies()/headers() and the params/searchParams props
import { cookies } from "next/headers";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>; // props are Promises in Next 15+
}) {
  const { id } = await params;
  const token = (await cookies()).get("token");
  return <Item id={id} token={token?.value} />;
}
```

### 6. Server Actions without input validation or authorization

- **Why it is wrong:** A Server Action is a public POST endpoint. The client is
  attacker-controlled, so unvalidated input and missing auth checks let anyone mutate any data.
- **The fix:** Validate every argument with a schema (e.g. Zod) and re-check authentication
  and authorization at the top of the action — never rely on the UI having hidden the control.

```tsx
// Bad — a public POST endpoint with no auth check and no validation
"use server";
export async function deletePost(id: string) {
  await db.post.delete({ where: { id } }); // anyone can delete any post
}
```

```tsx
// Good — authenticate, authorize, then validate every argument
"use server";
import { z } from "zod";
import { revalidatePath } from "next/cache";
import { auth } from "@/lib/auth";

const Input = z.object({ id: z.string().uuid() });

export async function deletePost(raw: unknown) {
  const session = await auth();
  if (!session) throw new Error("Unauthorized");

  const { id } = Input.parse(raw); // never trust the client-supplied shape
  const post = await db.post.findUnique({ where: { id } });
  if (post?.authorId !== session.userId) throw new Error("Forbidden");

  await db.post.delete({ where: { id } });
  revalidatePath("/posts");
}
```

### 7. Leaking secrets through `NEXT_PUBLIC_`

- **Why it is wrong:** Every `NEXT_PUBLIC_`-prefixed variable is inlined into the client
  bundle. Prefixing a secret (API key, token) publishes it to every visitor.
- **The fix:** Only expose truly public values via `NEXT_PUBLIC_`. Read secrets from
  unprefixed env vars in server code exclusively.

```tsx
// Bad — the NEXT_PUBLIC_ prefix inlines this secret into the client bundle
const stripe = new Stripe(process.env.NEXT_PUBLIC_STRIPE_SECRET_KEY!);
```

```tsx
// Good — secrets stay in unprefixed vars, read only from server-only code
// lib/stripe.ts
import "server-only";
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

// Reserve NEXT_PUBLIC_ for values that are safe to publish, e.g.:
//   process.env.NEXT_PUBLIC_SITE_URL
```

### 8. Using `<a>` instead of `<Link>` for internal navigation

- **Why it is wrong:** A raw `<a>` triggers a full-page reload, discarding client state,
  refetching everything, and skipping prefetch — a visibly slower transition.
- **The fix:** Use `next/link` `<Link>` for internal routes so navigation is client-side and prefetched.

```tsx
// Bad — full-page reload: discards client state, refetches everything, no prefetch
<a href="/dashboard">Dashboard</a>

// Good — client-side, automatically prefetched navigation
import Link from "next/link";
<Link href="/dashboard">Dashboard</Link>
```

### 9. Missing `error.tsx` and `loading.tsx` boundaries

- **Why it is wrong:** Without an error boundary, one failing segment can crash a larger part
  of the UI; without a loading boundary, streaming and Suspense fall back to a blank or blocked page.
- **The fix:** Add `error.tsx` to segments that can fail and `loading.tsx` (or `<Suspense>`)
  around async work so failures and pending states are contained and streamed.

```tsx
// app/dashboard/loading.tsx — instant fallback while the segment streams
export default function Loading() {
  return <Skeleton />;
}
```

```tsx
// app/dashboard/error.tsx — MUST be a Client Component to receive reset()
"use client";
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div role="alert">
      <p>Something went wrong.</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### 10. `<img>` and external font links instead of framework primitives

- **Why it is wrong:** Plain `<img>` skips optimization, lazy loading, and dimensions,
  causing layout shift and oversized payloads; external font `<link>`s block rendering and shift text.
- **The fix:** Use `next/image` (with `width`/`height` or `fill`) and `next/font` so assets
  are optimized, self-hosted, and shift-free.

```tsx
// Bad — unoptimized image (layout shift, oversized payload) + render-blocking font
<img src="/hero.png" />
<link href="https://fonts.googleapis.com/css2?family=Inter" rel="stylesheet" />
```

```tsx
// Good — next/image reserves space; next/font self-hosts with no extra request
import Image from "next/image";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export default function Hero() {
  return (
    <div className={inter.className}>
      <Image src="/hero.png" alt="Product hero" width={1200} height={630} priority />
    </div>
  );
}
```

### 11. Mutating without revalidating the cache

- **Why it is wrong:** After a successful mutation, cached pages and data still show the old
  value, so users see stale UI until an unrelated refresh.
- **The fix:** Call `revalidatePath(...)` or `revalidateTag(...)` (or `router.refresh()` on
  the client) after the mutation so affected caches update.

```tsx
// Bad — the write succeeds but cached views keep serving the old value
"use server";
export async function renameProject(id: string, name: string) {
  await db.project.update({ where: { id }, data: { name } });
  // stale UI until some unrelated navigation refreshes the cache
}
```

```tsx
// Good — revalidate the affected cache scope right after the write
"use server";
import { revalidatePath, updateTag } from "next/cache";

export async function renameProject(id: string, name: string) {
  await db.project.update({ where: { id }, data: { name } });
  revalidatePath(`/projects/${id}`); // or updateTag("projects") for tag-based data
}
```

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
