---
id: nextjs/13-middleware
topic: nextjs
slug: middleware
title: "Next.js Middleware"
type: doc
order: 13
status: ready
tags: [nextjs, middleware]
related: [nextjs/14-authentication, nextjs/15-authorization, nextjs/04-routing]
when_to_use: "Read before adding middleware for redirects, rewrites, or request processing in Next.js."
---
# Next.js Middleware

## Purpose

This document defines the engineering standards for implementing Middleware in Next.js applications.

The objective is to execute lightweight request processing before routing, enabling authentication, authorization, localization, redirects, rewrites, and request normalization while keeping Middleware fast and predictable.

Middleware should solve request-level concerns—not business logic.

---

## Core Principle

Middleware intercepts requests.

It should make routing decisions, not application decisions.

Keep Middleware lightweight.

---

## Request Lifecycle

Middleware executes before a route is rendered.

```
Incoming Request

↓

Middleware

↓

Redirect / Rewrite / Continue

↓

Route Handler

↓

Page or API Response
```

Middleware should make decisions quickly and avoid unnecessary work.

---

## File Location and Signature

Middleware lives in a single `middleware.ts` file at the project root (or inside
`src/` if you use that layout). There is exactly one Middleware file per app; it
runs for every request that matches its `config.matcher`.

By default Middleware runs on the **Edge runtime**, so only Edge-compatible APIs
are available (no `fs`, no native Node modules, no long-lived DB drivers). Use
Web-standard APIs (`fetch`, `URL`, `crypto.subtle`) and Edge-safe libraries such
as `jose` for JWT verification.

```ts
// middleware.ts
import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Read request state.
  const { pathname } = request.nextUrl;

  // Make a routing decision: continue, redirect, or rewrite.
  if (pathname === "/old-home") {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Continue to the matched route unchanged.
  return NextResponse.next();
}

// Only run Middleware where it is actually needed.
export const config = {
  matcher: ["/dashboard/:path*", "/admin/:path*"],
};
```

`middleware` may be `async`, but keep any awaited work fast and non-blocking —
every matched request pays for it.

> Node.js runtime for Middleware is available as an opt-in
> (`export const config = { runtime: "nodejs" }`) on recent Next.js versions when
> you need Node-only APIs. Prefer the Edge default unless you have a concrete
> reason; it keeps Middleware fast and portable.

---

## Appropriate Use Cases

Middleware is well suited for:

- authentication checks;
- authorization gates;
- locale detection;
- URL normalization;
- redirects;
- rewrites;
- A/B testing;
- security headers;
- bot detection;
- request logging.

If logic requires database queries or complex business rules, it likely belongs elsewhere.

---

## Avoid Business Logic

Do not perform:

- database mutations;
- payment processing;
- complex validation;
- heavy computations;
- report generation.

Middleware should not replace Server Actions or Route Handlers.

---

## Authentication

Middleware may determine whether a request is authenticated.

Typical workflow:

```
Read Cookie

↓

Validate Session

↓

Continue

or

Redirect to Login
```

Keep authentication checks efficient. In Middleware, do an **optimistic** check —
verify that a signed session token is present and cryptographically valid — and
leave full database session validation to the page, layout, or Data Access Layer
that actually reads user data. This keeps Middleware fast and avoids a database
round-trip on every request.

Good — verify a signed JWT at the edge with a Web-standard crypto library, then
redirect on failure:

```ts
// middleware.ts
import { NextResponse, type NextRequest } from "next/server";
import { jwtVerify } from "jose";

const secret = new TextEncoder().encode(process.env.SESSION_SECRET);

export async function middleware(request: NextRequest) {
  const token = request.cookies.get("session")?.value;

  if (!token) {
    return redirectToLogin(request);
  }

  try {
    await jwtVerify(token, secret); // Edge-compatible signature check.
    return NextResponse.next();
  } catch {
    return redirectToLogin(request);
  }
}

function redirectToLogin(request: NextRequest) {
  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("from", request.nextUrl.pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/dashboard/:path*", "/settings/:path*"],
};
```

Bad — hitting the database on every matched request. This adds latency to all
traffic, will not run on the Edge runtime, and duplicates authorization that
belongs in the Data Access Layer:

```ts
// middleware.ts — anti-pattern
export async function middleware(request: NextRequest) {
  const token = request.cookies.get("session")?.value;
  // ❌ DB lookup per request, not Edge-safe, blocks routing.
  const session = await db.session.findUnique({ where: { token } });
  if (!session || session.role !== "admin") {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}
```

---

## Authorization

Only lightweight authorization should occur in Middleware.

Examples:

- protected route access;
- role presence;
- subscription existence.

Detailed permission checks should remain inside the application.

---

## Redirects

Middleware is an excellent place for redirects.

Examples:

- login redirects;
- legacy URLs;
- canonical URLs;
- locale redirects;
- trailing slash normalization.

Always build the target with `new URL(path, request.url)` so the redirect
resolves to an absolute URL. `NextResponse.redirect` issues a 307 by default;
pass a status for permanent moves.

```ts
// Permanent redirect for a retired URL.
return NextResponse.redirect(new URL("/pricing", request.url), 308);
```

Prefer server-side redirects over client-side redirects.

---

## Rewrites

Use rewrites when changing the destination without changing the visible URL.

Examples:

- multi-tenant routing;
- feature rollout;
- localization;
- proxy behavior.

A rewrite changes what renders while the browser URL stays the same. Example —
route each tenant subdomain to a shared `/[tenant]` segment:

```ts
export function middleware(request: NextRequest) {
  const host = request.headers.get("host") ?? "";
  const subdomain = host.split(".")[0];

  if (subdomain && subdomain !== "www" && subdomain !== "app") {
    const url = request.nextUrl.clone();
    url.pathname = `/${subdomain}${url.pathname}`;
    return NextResponse.rewrite(url); // URL bar still shows the subdomain.
  }

  return NextResponse.next();
}
```

Keep rewrite rules easy to understand.

---

## Internationalization

Middleware may detect:

- language;
- country;
- locale.

Typical workflow:

```
Request

↓

Detect Locale

↓

Rewrite

↓

Localized Route
```

Detect the locale once, then redirect requests that lack a locale prefix:

```ts
const LOCALES = ["en", "de", "fr"] as const;
const DEFAULT_LOCALE = "en";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip paths that already carry a locale prefix.
  const hasLocale = LOCALES.some(
    (l) => pathname === `/${l}` || pathname.startsWith(`/${l}/`),
  );
  if (hasLocale) return NextResponse.next();

  const accept = request.headers.get("accept-language") ?? "";
  const preferred = accept.split(",")[0]?.split("-")[0];
  const locale = LOCALES.includes(preferred as (typeof LOCALES)[number])
    ? preferred
    : DEFAULT_LOCALE;

  return NextResponse.redirect(
    new URL(`/${locale}${pathname}`, request.url),
  );
}

export const config = {
  // Exclude API routes and static assets from locale handling.
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

Do not duplicate locale detection throughout the application.

---

## Security Headers

Middleware may attach security headers.

Examples:

- Content Security Policy;
- X-Frame-Options;
- Referrer-Policy;
- Permissions-Policy.

Attach headers to the response returned from Middleware:

```ts
export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set(
    "Permissions-Policy",
    "camera=(), microphone=(), geolocation=()",
  );

  return response;
}
```

For a strict Content Security Policy that supports inline scripts, generate a
per-request nonce here and forward it to the app via a request header, so Server
Components can read it and stamp it onto their `<script>` tags:

```ts
export function middleware(request: NextRequest) {
  const nonce = crypto.randomUUID();
  const csp = `script-src 'self' 'nonce-${nonce}' 'strict-dynamic';`;

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("Content-Security-Policy", csp);
  return response;
}
```

Security policies should remain centralized.

---

## Cookies

Middleware may:

- read cookies;
- set cookies;
- remove cookies.

Read from `request.cookies`; write to the response you return. Cookies set on
`NextResponse.next()` are sent back to the browser:

```ts
export function middleware(request: NextRequest) {
  const consent = request.cookies.get("consent")?.value;
  const response = NextResponse.next();

  if (!consent) {
    response.cookies.set("consent", "pending", {
      httpOnly: true,
      secure: true,
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 365,
    });
  }

  return response;
}
```

Avoid storing sensitive business state inside cookies.

---

## Request Headers

Middleware may modify request headers when required.

Typical examples:

- tracing identifiers;
- localization;
- feature flags.

To pass data forward to the route, clone the incoming headers, mutate the copy,
and hand it to `NextResponse.next` via the `request.headers` option — you cannot
mutate `request.headers` directly:

```ts
export function middleware(request: NextRequest) {
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-request-id", crypto.randomUUID());

  return NextResponse.next({ request: { headers: requestHeaders } });
}
```

The route (a Server Component or Route Handler) then reads it with
`headers()` from `next/headers`.

Avoid unnecessary header manipulation.

---

## Response Headers

Middleware may append response headers.

Examples:

- caching directives;
- security headers;
- diagnostics.

Headers should remain consistent across the application.

---

## Matchers

Use matchers to limit Middleware execution. The `config.matcher` is read
statically at build time — it must be a literal array, not a computed value.

Path patterns support named parameters and wildcards:

```ts
export const config = {
  matcher: ["/dashboard/:path*", "/admin/:path*"],
};
```

A negative lookahead is the idiomatic way to run Middleware everywhere except
framework internals and static assets:

```ts
export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\.\\w+$).*)"],
};
```

The object form adds conditional matching with `has` / `missing`, letting you
skip prefetch requests or gate on a header, cookie, or query value:

```ts
export const config = {
  matcher: [
    {
      source: "/((?!api|_next/static|_next/image|favicon.ico).*)",
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },
  ],
};
```

Avoid executing Middleware for routes that do not require it.

---

## Performance

Middleware should:

- execute quickly;
- minimize allocations;
- avoid unnecessary parsing;
- avoid blocking operations.

Every request passes through Middleware.

Small inefficiencies become expensive at scale.

---

## Logging

Log only meaningful request events.

Examples:

- denied access;
- unexpected failures;
- security events.

Avoid excessive logging on every request.

---

## Error Handling

Middleware should fail safely.

If recovery is impossible:

- redirect appropriately;
- return an appropriate response;
- avoid exposing internal implementation details.

---

## Testing

Verify:

- protected routes;
- redirects;
- rewrites;
- locale detection;
- security headers;
- matcher behavior.

Middleware should be covered by integration tests whenever practical.

---

## Security

Never expose:

- secrets;
- internal infrastructure;
- permission rules;
- sensitive diagnostics.

Treat every request as untrusted.

---

## Accessibility

Middleware should preserve accessible navigation.

Redirects and rewrites must not create confusing navigation flows or inaccessible user journeys.

---

## AI Execution Checklist

## Investigation

☐ Identify request-level concerns.

☐ Review authentication flow.

☐ Review redirect requirements.

☐ Review localization.

---

## Planning

☐ Keep Middleware lightweight.

☐ Restrict execution with matchers.

☐ Centralize request handling.

☐ Avoid business logic.

---

## Verification

☐ Middleware executes efficiently.

☐ Redirects function correctly.

☐ Security headers applied.

☐ Authentication verified.

☐ Error handling implemented.

☐ Performance reviewed.

---

## Examples

**Good Example** — cheap checks only, with a matcher that excludes assets

```ts
// middleware.ts — runs on the edge, before every matched request.
import { NextRequest, NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('session')?.value;

  // Presence check only: enough to redirect an anonymous visitor away from a
  // protected area, and cheap enough to run on every request.
  if (!token) {
    const signIn = new URL('/sign-in', request.url);
    signIn.searchParams.set('next', request.nextUrl.pathname);
    return NextResponse.redirect(signIn);
  }

  // Pass request-scoped context downstream instead of re-reading it later.
  const response = NextResponse.next();
  response.headers.set('x-request-id', crypto.randomUUID());
  return response;
}

export const config = {
  // Never run on static assets, images, or the favicon — that is pure overhead.
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|webp)$).*)'],
};
```

The real authorisation decision happens in the page, the Server Action, or the Route Handler,
where the user record and the resource are both available.

**Bad Example** — authorisation and database access in middleware

```ts
export async function middleware(request: NextRequest) {
  const token = request.cookies.get('session')?.value;

  // A database query on the edge runtime, on every request including assets:
  // Node APIs are unavailable, the connection cannot be pooled, and latency is
  // added to every navigation.
  const user = await db.user.findUnique({ where: { sessionToken: token } });

  // The full authorisation policy expressed as path prefixes, which drift from
  // the routes the moment one is renamed or a new one is added.
  if (request.nextUrl.pathname.startsWith('/admin') && user?.role !== 'admin') {
    return NextResponse.redirect(new URL('/', request.url));
  }
  if (request.nextUrl.pathname.startsWith('/orders/') && !user) {
    return new NextResponse('forbidden', { status: 403 });
  }

  return NextResponse.next();
}

// No matcher: this runs for every image, font, and JS chunk the page loads.
```

---

## Common Mistakes

Avoid:

Performing database queries inside Middleware.

Executing heavy computations.

Running Middleware for every route unnecessarily.

Duplicating authorization logic.

Creating redirect loops.

Ignoring matcher configuration.

Placing business workflows inside request interception.

---

## Completion Criteria

A Middleware implementation is complete when:

- request-level concerns are centralized;
- authentication and routing decisions are efficient;
- matchers limit unnecessary execution;
- security headers are applied where required;
- redirects and rewrites behave predictably;
- performance impact remains minimal.

---

## Summary

Middleware provides a centralized mechanism for handling request-level concerns before the application is rendered.

By limiting Middleware to lightweight routing, security, and request processing responsibilities, applications remain fast, scalable, secure, and easier to reason about.

## Related

- `knowledge/nextjs/14-authentication.md`
- `knowledge/nextjs/15-authorization.md`
- `knowledge/nextjs/04-routing.md`
