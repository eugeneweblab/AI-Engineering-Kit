---
id: nextjs/15-authorization
topic: nextjs
slug: authorization
title: "Next.js Authorization"
type: doc
order: 15
status: ready
tags: [nextjs, authorization, requireUser, redirect, getSession, Layout, getInvoice, findFirst]
related: [nextjs/14-authentication, nextjs/24-security, nextjs/11-server-actions, nextjs/13-proxy, nextjs/06-server-components]
when_to_use: "Read before adding any access check, protected route, Server Action, or role gate in a Next.js app."
---
# Next.js Authorization

## Purpose

This document defines how to enforce *what a user is allowed to do* in a Next.js App Router
application. It assumes identity is already established (see [authentication](14-authentication.md))
and focuses on where and how to check permissions so that no unauthorized request reaches data.

Authorization answers "are you allowed to do this?" — checked on every request, next to the
resource, never once at the edge.

## Why It Matters

The most damaging Next.js vulnerabilities are broken authorization, not broken login. Because
Server Components, Server Actions, and Route Handlers are all independent server entry points,
a check placed in the wrong layer protects nothing. Middleware runs before routing and has been
bypassed by forged internal headers (the 2025 `x-middleware-subrequest` CVE); layouts do not
re-render on client navigation, so a check there is skipped on the very navigations that matter.
An authorization bug is invisible in the happy path and total in impact: one unguarded query
exposes every user's data.

## Core Principles

- **Check authorization closest to the data.** Enforce in the Data Access Layer (DAL) — the
  function that reads or writes the resource — so every caller inherits the check. Do not rely
  on UI or route position to gate access.
- **Never trust the client, the URL, or the proxy for enforcement.** They are optimizations
  (redirect early, hide a link). The real gate is the server function that touches data.
- **Treat every Server Action and Route Handler as a public endpoint.** They are POST-able by
  anyone. Re-verify session and permission inside each one, every time.
- **Fail closed and check ownership.** A missing session, an unknown role, or a resource the
  user does not own must deny. "Logged in" is not "authorized for *this* record."
- **Verify the session, do not just read a cookie.** Authorization decisions require a
  validated session (signature/expiry checked), not the presence of a token.

## Best Practices

- Centralize checks in a `server-only` auth module: `requireUser()`, `requireRole('admin')`,
  and `canAccess(user, resource)` — call them at the top of every protected operation.
- Scope every query by the current user (`where ownerId = session.userId`) instead of fetching
  by id and checking afterward; ownership becomes part of the query, not an afterthought.
- Use the proxy only for coarse, non-authoritative redirects (send anonymous users to
  `/login`). Duplicate the real check in the DAL.
- Return `notFound()` rather than `403` for resources the user may not even know exist, to
  avoid leaking their existence.
- Model permissions as data (roles/policies), not scattered `if` branches, so access rules are
  auditable in one place.

## Examples

**Good Example** — enforcement in the Data Access Layer

```ts
// src/server/auth.ts
import 'server-only';
import { cache } from 'react';
import { redirect } from 'next/navigation';
import { getSession } from './session';

export const requireUser = cache(async () => {
  const session = await getSession();          // verifies signature + expiry
  if (!session) redirect('/login');            // fail closed
  return session.user;
});

// src/features/invoices/queries.ts
import 'server-only';
import { requireUser } from '@/server/auth';

export async function getInvoice(id: string) {
  const user = await requireUser();
  // Ownership is part of the query: another user's id returns nothing.
  return db.invoice.findFirst({ where: { id, ownerId: user.id } });
}
```

```ts
// A Server Action re-checks — it is a public endpoint, not "internal".
'use server';
export async function deleteInvoice(id: string) {
  const user = await requireUser();            // never assume the caller is trusted
  await db.invoice.deleteMany({ where: { id, ownerId: user.id } });
}
```

**Bad Example** — check in the layout, trust the URL

```tsx
// app/dashboard/layout.tsx — layouts do NOT re-render on client navigation,
// so this check is skipped when the user navigates between dashboard pages.
export default async function Layout({ children }) {
  const user = await getUser();
  if (!user) redirect('/login');   // false sense of protection
  return <>{children}</>;
}

// app/api/invoices/[id]/route.ts — no ownership check at all
export async function GET(_req, { params }) {
  const invoice = await db.invoice.findUnique({ where: { id: params.id } });
  return Response.json(invoice); // any authenticated user reads any invoice → IDOR
}
```

## Common Mistakes

- Enforcing access only in the proxy or a layout and leaving the DAL/Route Handler open.
- Fetching a resource by id and then checking ownership, instead of scoping the query.
- Assuming a Server Action is safe because no UI calls it with bad input — it is publicly POST-able.
- Reading a role from a client-supplied cookie or request body instead of a verified session.
- Returning `403` (confirming the resource exists) where `notFound()` would leak less.
- Hiding a button client-side and treating that as authorization.

## Production Tips

- Log authorization *denials* (user id, resource, action) and alert on spikes — they signal
  probing or a broken UI gate.
- Add a test per protected operation for the negative path: wrong user, no session, foreign
  resource id. These are the paths attackers exercise.
- Keep proxy auth minimal and never the sole gate; assume it can be bypassed.

## AI Review Checklist

- Is every protected read/write gated in the DAL, not just in a layout or the proxy?
- Does each Server Action and Route Handler re-verify session and permission?
- Are queries scoped by owner rather than fetched-then-checked?
- Is the session validated (signature/expiry), not merely read from a cookie?
- Do unauthorized resource accesses return `notFound()` where existence should be hidden?
- Is there a negative-path test for each protected operation?

## Related

- `knowledge/nextjs/14-authentication.md`
- `knowledge/nextjs/24-security.md`
- `knowledge/nextjs/11-server-actions.md`
- `knowledge/nextjs/13-proxy.md`
- `knowledge/nextjs/06-server-components.md`
