---
id: nextjs/14-authentication
topic: nextjs
slug: authentication
title: "Next.js Authentication"
type: doc
order: 14
status: ready
tags: [nextjs, authentication]
related: [nextjs/15-authorization, nextjs/13-middleware, nextjs/11-server-actions, nextjs/06-server-components, nextjs/21-environment-variables, nextjs/24-security]
when_to_use: "Read before implementing authentication or authorization in a Next.js app."
---
# Next.js Authentication

## Purpose

This document defines the engineering standards for authentication and authorization in Next.js applications.

The objective is to build secure, scalable, and maintainable authentication systems that fully leverage the server-first architecture of the App Router.

Authentication verifies identity.

Authorization determines permissions.

These concerns must remain primarily on the server.

---

## Core Principle

Authenticate on the server.

Authorize on the server.

Never trust the client.

---

## Authentication Flow

Every authentication workflow should follow this sequence.

```
User

↓

Login Request

↓

Identity Provider

↓

Session Creation

↓

Session Validation

↓

Authorization

↓

Protected Resource
```

Every protected request should verify authentication before accessing business logic.

---

## Authentication Methods

Supported authentication mechanisms include:

- Auth.js (NextAuth.js);
- Clerk;
- OAuth 2.0;
- OpenID Connect (OIDC);
- JWT;
- Session Cookies;
- Enterprise SSO.

Choose the simplest solution that satisfies the project requirements.

---

## Sessions

Prefer secure server-side sessions whenever practical.

A session should contain only the minimum information required to identify the authenticated user.

Avoid storing business data inside sessions.

Centralize session logic in one `server-only` module so cookie handling never leaks into the
client bundle. In Next.js 15+, `cookies()`, `headers()`, and `draftMode()` are **async** — you
must `await` them. Cookies can only be *written* inside a Server Action or a Route Handler;
attempting `cookies().set()` during a Server Component render throws.

```ts
// src/server/session.ts
import 'server-only';
import { cookies } from 'next/headers';
import { SignJWT, jwtVerify, type JWTPayload } from 'jose';

// Server-only secret — NO NEXT_PUBLIC_ prefix, or it ships to the browser.
const key = new TextEncoder().encode(process.env.SESSION_SECRET);
const COOKIE = 'session';
const MAX_AGE = 60 * 60 * 24 * 7; // 7 days, in seconds

export async function createSession(userId: string) {
  const token = await new SignJWT({ sub: userId })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(key);

  const cookieStore = await cookies(); // async in Next 15+
  cookieStore.set(COOKIE, token, {
    httpOnly: true,                              // invisible to document.cookie
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',                             // survives top-level OAuth redirects
    path: '/',
    maxAge: MAX_AGE,
  });
}

// Returns a verified payload or null. Never trust the raw cookie value.
export async function getSession(): Promise<JWTPayload | null> {
  const token = (await cookies()).get(COOKIE)?.value;
  if (!token) return null;
  try {
    const { payload } = await jwtVerify(token, key, { algorithms: ['HS256'] });
    return payload; // signature + expiry checked by jwtVerify
  } catch {
    return null; // tampered, expired, or wrong algorithm
  }
}

export async function deleteSession() {
  (await cookies()).delete(COOKIE);
}
```

Session identity is per-request and must never be shared across users. Do **not** put it behind
the Data Cache (`fetch` is uncached by default in Next 15, so this is safe unless you opt in).
To deduplicate the session read within a single request, wrap it in React's `cache()`, not a
cross-request cache.

---

## Cookies

Authentication cookies should be:

- HttpOnly;
- Secure;
- SameSite protected;
- encrypted or signed where appropriate.

Never expose authentication cookies to client-side JavaScript.

**Good Example** — signed, HttpOnly, scoped, transport-secure:

```ts
(await cookies()).set('session', token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',
  path: '/',
  maxAge: 60 * 60 * 24 * 7,
});
```

**Bad Example** — readable by any script, unsigned, sent over plain HTTP:

```ts
// XSS steals it via document.cookie; the raw userId is client-forgeable.
(await cookies()).set('session', userId, { httpOnly: false });
```

---

## JWT

JWTs should be used when stateless authentication is required.

Verify:

- signature;
- expiration;
- issuer;
- audience.

Never trust an unsigned or expired token.

Pin the algorithm on verification (`algorithms: ['HS256']`) to defeat `alg: none` and
algorithm-confusion attacks. `jwtVerify` from `jose` runs in the Edge and Node runtimes, so the
same `getSession()` helper works in Server Components, Route Handlers, and (sparingly) Middleware:

```ts
const { payload } = await jwtVerify(token, key, {
  algorithms: ['HS256'],        // reject anything else — do not read alg from the token
  issuer: 'https://auth.example.com',
  audience: 'example-app',
});
```

---

## OAuth

OAuth providers may include:

- Google;
- Microsoft;
- GitHub;
- Apple;
- Facebook.

Delegate identity verification to trusted providers whenever appropriate.

---

## User Identity

Every authenticated request should establish a trusted user identity before accessing protected resources.

Typical information includes:

- user ID;
- organization ID;
- roles;
- permissions.

Avoid repeatedly querying identity information during the same request.

---

## Authorization

Authentication answers:

```
Who are you?
```

Authorization answers:

```
What are you allowed to do?
```

Never confuse these responsibilities.

---

## Role-Based Access Control (RBAC)

Use roles to define broad access levels.

Examples:

- Admin;
- Manager;
- Editor;
- Customer;
- Guest.

Roles should remain stable and easy to understand.

---

## Permission-Based Access

Permissions provide fine-grained authorization.

Examples:

- create product;
- update order;
- delete user;
- publish article.

Permissions should remain independent of presentation logic.

---

## Resource Ownership

Verify ownership before allowing access.

Example:

```
User

↓

Order

↓

Owner?

↓

Allow / Deny
```

Ownership checks belong on the server.

---

## Protected Routes

Protect routes before rendering.

Examples:

- dashboard;
- profile;
- administration;
- billing.

Avoid rendering protected pages before authentication has been verified.

---

## Middleware

Middleware may perform lightweight authentication checks.

Typical responsibilities:

- verify session existence;
- redirect anonymous users;
- normalize authentication flow.

Complex authorization belongs inside Server Components, Route Handlers, or Server Actions.

Treat middleware as an **optimistic** gate: it redirects obviously-anonymous traffic early, but
it is not the authoritative check. Middleware runs before routing and has been bypassed by forged
internal headers (the 2025 `x-middleware-subrequest` CVE), so the real verification must live next
to the data. Use a `matcher` so it never runs on static assets or the login route itself.

**Good Example** — presence check + redirect, real verification deferred to the Data Access Layer:

```ts
// middleware.ts
import { NextResponse, type NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  const hasSession = req.cookies.has('session'); // presence only — cheap, non-authoritative
  if (!hasSession) {
    const url = new URL('/login', req.url);
    url.searchParams.set('next', req.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  // Run only on protected sections; skip _next, static files, and public routes.
  matcher: ['/dashboard/:path*', '/billing/:path*', '/settings/:path*'],
};
```

**Bad Example** — treating the middleware redirect as the whole defense:

```ts
// If a Route Handler or Server Component under /dashboard reads data WITHOUT re-checking
// the session, a request that skips middleware (matcher gap, forged header) reaches the data.
// Middleware guards navigation, not data. Always re-verify in the DAL.
```

---

## Server Components

Server Components should:

- read authentication context;
- fetch authenticated data;
- perform authorization checks;
- render protected content.

Keep sensitive operations on the server.

Verify the session at the top of the protected component (or in the DAL it calls) — not once in a
layout, since layouts do not re-render on client-side navigation. Wrap the resolved user in
React's `cache()` so multiple components in the same render tree share one verification, not one
per call:

```tsx
// src/server/current-user.ts
import 'server-only';
import { cache } from 'react';
import { redirect } from 'next/navigation';
import { getSession } from './session';
import { getUserById } from './users';

export const requireUser = cache(async () => {
  const session = await getSession();          // verified signature + expiry
  if (!session?.sub) redirect('/login');       // fail closed
  return getUserById(session.sub);
});

// app/dashboard/page.tsx  (Server Component — no "use client")
export default async function DashboardPage() {
  const user = await requireUser();            // enforced on every render
  return <h1>Welcome, {user.name}</h1>;
}
```

---

## Client Components

Client Components should only:

- display authenticated UI;
- collect user input;
- initiate authenticated actions.

They should not make authorization decisions.

---

## Server Actions

Every Server Action should verify:

- authentication;
- authorization;
- resource ownership.

Never assume that the client has already validated permissions.

A Server Action is a public POST endpoint — anyone can invoke it, with any payload. Sign-in and
sign-out are themselves Server Actions that set or clear the session cookie (which is why cookie
mutation is allowed here but not during render):

```ts
// app/(auth)/actions.ts
'use server';
import { redirect } from 'next/navigation';
import { createSession, deleteSession } from '@/server/session';
import { verifyCredentials } from '@/server/users';

// Shape works with useActionState on the client form.
export async function login(_prev: unknown, formData: FormData) {
  const email = String(formData.get('email') ?? '');
  const password = String(formData.get('password') ?? '');

  const user = await verifyCredentials(email, password); // constant-time hash compare
  if (!user) return { error: 'Invalid email or password' }; // do not reveal which field

  await createSession(user.id);
  redirect('/dashboard');
}

export async function logout() {
  await deleteSession();
  redirect('/login');
}
```

The form is a thin Client Component that only collects input and calls the action — it makes no
authorization decision:

```tsx
'use client';
import { useActionState } from 'react';
import { login } from './actions';

export function LoginForm() {
  const [state, action, pending] = useActionState(login, null);
  return (
    <form action={action}>
      <input name="email" type="email" autoComplete="email" required />
      <input name="password" type="password" autoComplete="current-password" required />
      {state?.error && <p role="alert">{state.error}</p>}
      <button disabled={pending}>Sign in</button>
    </form>
  );
}
```

---

## API Routes

Every protected API endpoint should:

- authenticate the request;
- authorize the action;
- validate the input.

Security should never depend on the client application.

A Route Handler (`app/**/route.ts`) is a bare HTTP entry point with no implicit auth — verify the
session before doing anything, and return `401` when it is missing. OAuth callbacks are also Route
Handlers: they validate the `state` parameter, exchange the code, then create the session cookie:

```ts
// app/api/me/route.ts
import { NextResponse } from 'next/server';
import { getSession } from '@/server/session';

export async function GET() {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  return NextResponse.json({ userId: session.sub });
}
```

Do not rely on `fetch` caching for authenticated responses. In Next 15 `fetch` is uncached by
default, but if you opt a request into the Data Cache (`cache: "force-cache"` or
`next: { revalidate }`), never do so for per-user data — a cached response can be served to the
wrong user.

---

## Logout

Logout should:

- invalidate the session;
- clear authentication cookies;
- invalidate cached authenticated content.

Users should immediately lose access to protected resources.

The `logout` Server Action above deletes the cookie and redirects. If any authenticated content was
opted into the cache, evict it on sign-out so a stale render cannot leak the previous user's data:

```ts
'use server';
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { deleteSession } from '@/server/session';

export async function logout() {
  await deleteSession();
  revalidatePath('/', 'layout'); // drop cached authenticated segments
  redirect('/login');
}
```

For truly stateless JWTs there is no server record to revoke before expiry; keep sessions
short-lived and maintain a server-side revocation list (or rotate the signing key) if immediate
invalidation is required.

---

## Password Security

If passwords are stored:

- hash them using a modern algorithm;
- never store plaintext passwords;
- never log passwords;
- enforce strong password policies.

Credential handling must follow industry best practices.

Use a memory-hard algorithm (Argon2id preferred, bcrypt acceptable) with a per-password salt,
which the library embeds in the hash string. Hashing runs in the Node.js runtime, so keep it out
of Middleware. The verify step must compare against the stored hash, never a fetched plaintext:

```ts
// src/server/users.ts
import 'server-only';
import { hash, verify } from '@node-rs/argon2';

export async function hashPassword(plain: string) {
  return hash(plain); // salt generated and embedded automatically
}

export async function verifyCredentials(email: string, password: string) {
  const user = await db.user.findUnique({ where: { email } });
  if (!user) {
    await hash(password); // dummy work: keep timing uniform for unknown emails
    return null;
  }
  const ok = await verify(user.passwordHash, password);
  return ok ? user : null;
}
```

---

## Multi-Factor Authentication (MFA)

Support MFA when appropriate.

Examples:

- TOTP;
- hardware security keys;
- passkeys;
- email verification.

Higher-risk operations should require stronger authentication.

---

## Rate Limiting

Protect authentication endpoints against abuse.

Examples:

- login attempts;
- password reset;
- verification requests.

Limit repeated failed attempts.

---

## Audit Logging

Log security-sensitive events.

Examples:

- successful login;
- failed login;
- permission denial;
- password change;
- role change.

Logs should never expose sensitive credentials.

---

## Security

Always verify:

- authentication;
- authorization;
- ownership;
- input validation.

Security should never rely on hidden client-side behavior.

---

## Accessibility

Authentication workflows should support:

- keyboard navigation;
- screen readers;
- accessible validation messages;
- clear recovery flows.

Security must remain accessible.

---

## AI Execution Checklist

## Investigation

☐ Identify authentication provider.

☐ Review authorization model.

☐ Review protected routes.

☐ Review session strategy.

---

## Planning

☐ Authenticate on the server.

☐ Authorize every protected action.

☐ Protect sensitive resources.

☐ Minimize session data.

---

## Verification

☐ Authentication verified.

☐ Authorization enforced.

☐ Cookies secured.

☐ Sessions protected.

☐ Audit logging implemented.

☐ Accessibility preserved.

---

## Common Mistakes

Avoid:

Trusting client-side authentication.

Skipping authorization.

Storing sensitive data inside JWTs.

Making authorization decisions in Client Components.

Using insecure cookies.

Exposing authentication tokens.

Failing to verify resource ownership.

Ignoring rate limiting.

---

## Completion Criteria

An authentication implementation is complete when:

- users are securely authenticated;
- authorization is enforced for every protected resource;
- sessions and cookies are protected;
- security best practices are followed;
- audit logging exists;
- accessibility has been verified.

---

## Summary

Authentication and authorization form the security foundation of every Next.js application.

By keeping identity verification, permission checks, and protected business logic on the server while minimizing trust in the client, applications remain secure, scalable, maintainable, and aligned with modern App Router best practices.

## Related

- `knowledge/nextjs/15-authorization.md`
- `knowledge/nextjs/13-middleware.md`
- `knowledge/security/03-authentication.md`
- `knowledge/security/07-jwt.md`
