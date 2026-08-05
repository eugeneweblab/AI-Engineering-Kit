---
id: nextjs/24-security
topic: nextjs
slug: security
title: "Next.js Security"
type: doc
order: 24
status: ready
tags: [nextjs, security, NEXT_PUBLIC_, STRIPE_SECRET_KEY, dangerouslySetInnerHTML, createCharge, requireUser, positive]
related: [nextjs/15-authorization, nextjs/14-authentication, nextjs/11-server-actions, nextjs/21-environment-variables, nextjs/13-middleware]
when_to_use: "Read before shipping any Next.js feature that handles user input, secrets, headers, or external requests."
---
# Next.js Security

## Purpose

This document defines how to harden a Next.js App Router application: keeping secrets on the
server, protecting Server Actions and Route Handlers, setting security headers, and avoiding
the injection, SSRF, and data-leak classes specific to the Next.js runtime. It complements
[authentication](14-authentication.md) and [authorization](15-authorization.md), which cover
identity and access.

## Why It Matters

Next.js mixes server and client code in one tree, so the most common security failures are
*boundary* failures: a secret rendered into HTML, a server helper bundled into the browser, a
Server Action treated as private when it is a public POST endpoint. These leaks are silent —
the page renders fine while `DATABASE_URL` sits in the JavaScript payload. The framework gives
you the tools to draw the boundary correctly; the cost of drawing it wrong is total exposure.

## Core Principles

- **Secrets live on the server, only.** Any value read into a client component or prefixed
  `NEXT_PUBLIC_` is public — it ships in the bundle. Treat that prefix as "publish to the world."
- **Every server entry point is untrusted.** Server Actions and Route Handlers are POST-able by
  anyone; validate input and re-check auth inside each one (see [authorization](15-authorization.md)).
- **Validate at the boundary, before use.** Parse and validate all external input with a schema
  (e.g. Zod) at the first server function that receives it; never trust shapes from the client.
- **Escape by default, `dangerouslySetInnerHTML` never with untrusted input.** React escapes
  output; the only XSS you can introduce is by bypassing it or building raw HTML/URLs.
- **Deny outbound and inbound by default.** Set restrictive security headers and never let user
  input choose the host of a server-side fetch (SSRF) or a redirect target (open redirect).

## Best Practices

- Keep secrets out of client components; pass only the specific, non-sensitive fields the UI
  needs. Use `import 'server-only'` on secret-bearing modules so client imports fail at build.
- Set a strong Content-Security-Policy (prefer nonce-based), plus `X-Content-Type-Options:
  nosniff`, `Referrer-Policy`, and HSTS — via `headers()` in `next.config.ts` or middleware.
- Validate every Server Action and Route Handler input with a schema; reject on failure.
- Validate and allowlist any URL used in a server-side `fetch` or a `redirect()`; reject
  absolute external URLs you did not intend.
- Rely on Server Actions' built-in CSRF protection (Origin checks) and keep session cookies
  `HttpOnly`, `Secure`, `SameSite=Lax`; do not roll your own token in `localStorage`.
- Consider React's taint APIs (`experimental_taintObjectReference`, `taintUniqueValue`) to make
  passing a secret object to the client a runtime error.

## Examples

**Good Example** — validated action, secret stays server-side

```ts
'use server';
import { z } from 'zod';
import { requireUser } from '@/server/auth';

const Schema = z.object({ email: z.string().email(), amount: z.number().int().positive() });

export async function createCharge(input: unknown) {
  const user = await requireUser();               // re-check auth: public endpoint
  const data = Schema.parse(input);               // validate before use; throws on bad shape
  // STRIPE_SECRET_KEY is read server-side only — never returned to the client.
  return charge(process.env.STRIPE_SECRET_KEY!, data);
}
```

```ts
// next.config.ts — security headers applied to every response
const csp = "default-src 'self'; object-src 'none'; frame-ancestors 'none'";
export default {
  async headers() {
    return [{ source: '/:path*', headers: [
      { key: 'Content-Security-Policy', value: csp },
      { key: 'X-Content-Type-Options', value: 'nosniff' },
      { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
    ]}];
  },
};
```

**Bad Example** — leaked secret, unvalidated SSRF

```tsx
// A Server Component passing the whole config (with secrets) to a client child.
<Dashboard config={{ apiKey: process.env.STRIPE_SECRET_KEY }} />
// The apiKey is serialized into the HTML/RSC payload → visible in the browser.
```

```ts
// app/api/proxy/route.ts
export async function GET(req: Request) {
  const url = new URL(req.url).searchParams.get('url')!;
  return fetch(url); // user controls the host → SSRF into internal services / metadata
}
```

## Common Mistakes

- Prefixing a secret with `NEXT_PUBLIC_` "to make it work" — it is now shipped to every visitor.
- Passing a whole user or config object to a client component, serializing hidden secret fields.
- Trusting Server Action / Route Handler input because "only my form calls it."
- `dangerouslySetInnerHTML` with user content, or building `href`/redirect URLs from raw input.
- Committing `.env` files or exposing them; secrets belong in a secrets manager (see
  [environment variables](21-environment-variables.md)).
- Assuming middleware enforces security — it can be bypassed; enforce at the data layer.

## Production Tips

- Add `pnpm audit` / dependency scanning to CI and keep Next.js patched — several high-severity
  CVEs (middleware bypass, cache poisoning) have shipped fixes in point releases.
- Set CSP to report-only first, watch violations, then enforce, to avoid breaking third-party
  embeds silently.
- Redact secrets and tokens from logs and error reporting; never log request bodies verbatim.

## AI Review Checklist

- Are all secrets server-only, never `NEXT_PUBLIC_` and never passed into client components?
- Does every Server Action and Route Handler validate input with a schema and re-check auth?
- Are security headers (CSP, nosniff, Referrer-Policy, HSTS) configured?
- Is any URL used in server `fetch`/`redirect` validated against an allowlist?
- Is `dangerouslySetInnerHTML` free of untrusted input?
- Are secret-bearing modules marked `import 'server-only'`?

## Related

- `knowledge/nextjs/15-authorization.md`
- `knowledge/nextjs/14-authentication.md`
- `knowledge/nextjs/11-server-actions.md`
- `knowledge/nextjs/21-environment-variables.md`
- `knowledge/nextjs/13-middleware.md`
