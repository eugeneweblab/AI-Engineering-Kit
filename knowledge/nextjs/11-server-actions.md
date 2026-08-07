---
id: nextjs/11-server-actions
topic: nextjs
slug: server-actions
title: "Next.js Server Actions"
type: doc
order: 11
status: ready
tags: [nextjs, server-actions, cancelOrder, FormData, createProduct, updateMany, updateTag, revalidateTag, useActionState]
applies_to: [app-router]
related: [nextjs/06-server-components, nextjs/24-security, nextjs/15-authorization, react/15-forms]
when_to_use: "Read before implementing form submissions or data mutations with Next.js Server Actions."
---
# Next.js Server Actions

## Purpose

This document defines the engineering standards for using Server Actions in Next.js applications.

The objective is to implement secure, maintainable, and efficient server-side mutations while minimizing client-side complexity.

Server Actions should be the preferred solution for handling user-initiated data mutations within the App Router architecture.

---

## Core Principle

Read on the server.

Write on the server.

The client initiates actions.

The server performs business logic.

---

## Responsibilities

Server Actions should be responsible for:

- creating data;
- updating data;
- deleting data;
- executing business workflows;
- validating permissions;
- interacting with databases;
- invalidating caches.

Avoid placing business logic inside Client Components.

---

## Typical Flow

```
Client Component

↓

User Interaction

↓

Server Action

↓

Validation

↓

Authorization

↓

Database

↓

Cache Invalidation

↓

Updated UI
```

Every mutation should follow this sequence.

---

## Creating a Server Action

A Server Action must begin with the `"use server"` directive.

Example:

```tsx
"use server";

export async function createProduct(
    input: CreateProductInput,
) {
    // Implementation
}
```

Keep Server Actions focused on a single responsibility.

---

## Validation

Validate all incoming data.

Validation should include:

- required fields;
- data types;
- string lengths;
- numeric limits;
- business constraints.

Never trust client-side validation alone.

---

## Authorization

Verify permissions before performing mutations.

Examples:

- authenticated user;
- ownership checks;
- role validation;
- organization membership.

Authorization belongs on the server.

---

## Authentication

Read authentication context directly from the server.

Examples:

- cookies;
- sessions;
- JWTs;
- authentication providers.

Avoid sending authentication information from the client when it is already available on the server.

---

## Database Operations

Server Actions may communicate directly with:

- Prisma;
- Drizzle;
- PostgreSQL;
- MySQL;
- MongoDB;
- Redis.

Avoid creating internal HTTP requests to your own backend.

---

## Error Handling

Every Server Action should define:

- validation failures;
- authorization failures;
- database failures;
- unexpected exceptions.

Return meaningful errors without exposing sensitive implementation details.

---

## Cache Invalidation

Mutations should invalidate affected cached content.

Examples:

- updated product;
- deleted article;
- modified profile;
- changed settings.

Invalidate the smallest practical scope.

---

## Redirects

Server Actions may redirect after successful completion.

Typical use cases:

- login;
- onboarding;
- resource creation;
- completed checkout.

Redirect only after the mutation has succeeded.

---

## Optimistic Updates

Use optimistic updates when:

- user feedback should be immediate;
- temporary inconsistency is acceptable;
- rollback can be handled safely.

Always define recovery behavior if the mutation fails.

---

## Forms

Server Actions integrate naturally with forms.

Typical workflow:

```
User Input

↓

Form Submission

↓

Server Action

↓

Validation

↓

Database

↓

Updated Response
```

Keep validation and persistence on the server.

---

## File Uploads

Handle uploads securely.

Verify:

- file size;
- MIME type;
- file extension;
- authorization.

Never trust metadata provided by the browser.

---

## Idempotency

Mutations should be safe from accidental duplication whenever appropriate.

Examples:

- payment processing;
- order creation;
- subscription changes.

Prevent duplicate execution when repeated requests are possible.

---

## Logging

Log important server-side events.

Examples:

- failed mutations;
- permission failures;
- unexpected exceptions;
- critical business events.

Logs should support debugging without exposing sensitive information.

---

## Performance

Server Actions should:

- minimize database queries;
- batch related operations;
- avoid unnecessary work;
- invalidate only affected caches.

Keep execution time as short as practical.

---

## Security

Never expose:

- secrets;
- database credentials;
- internal implementation;
- authorization logic.

All sensitive operations remain on the server.

---

## Accessibility

Forms using Server Actions should provide:

- loading indicators;
- accessible validation messages;
- keyboard support;
- focus management after submission.

Mutation workflows should remain accessible.

---

## AI Execution Checklist

## Investigation

☐ Identify mutation type.

☐ Review validation requirements.

☐ Review authorization rules.

☐ Review cache dependencies.

---

## Planning

☐ Validate input.

☐ Verify permissions.

☐ Perform mutation.

☐ Invalidate affected cache.

---

## Verification

☐ Business logic remains server-side.

☐ Validation implemented.

☐ Authorization verified.

☐ Errors handled gracefully.

☐ Cache updated correctly.

☐ Accessibility preserved.

---

## Examples

**Good Example** — an action authorises, validates, mutates, then revalidates

```ts
// app/orders/actions.ts
'use server';

import { z } from 'zod';
import { updateTag } from 'next/cache';

const CancelOrder = z.object({ orderId: z.string().uuid() });

export async function cancelOrder(_prev: ActionState, formData: FormData): Promise<ActionState> {
  // 1. A Server Action is a public HTTP endpoint. Authorise it like one — being
  //    reachable only from a protected page proves nothing.
  const session = await auth();
  if (!session) {
    return { ok: false, error: 'Not signed in' };
  }

  // 2. Validate: FormData values are strings from the network, never trusted types.
  const parsed = CancelOrder.safeParse({ orderId: formData.get('orderId') });
  if (!parsed.success) {
    return { ok: false, error: 'Invalid request' };
  }

  // 3. Scope the write to the caller, so ownership is enforced by the query.
  const { count } = await db.order.updateMany({
    where: { id: parsed.data.orderId, userId: session.userId, status: 'PENDING' },
    data: { status: 'CANCELLED' },
  });
  if (count === 0) {
    return { ok: false, error: 'This order can no longer be cancelled' };
  }

  // The user must see their own cancellation immediately, so expire and
  // refresh in the same request rather than marking it stale.
  updateTag(`order:${parsed.data.orderId}`);
  return { ok: true };
}
```

```tsx
// The form works before hydration, and reports progress after it.
'use client';

export function CancelForm({ orderId }: { orderId: string }) {
  const [state, action, pending] = useActionState(cancelOrder, { ok: false });
  return (
    <form action={action}>
      <input type="hidden" name="orderId" value={orderId} />
      <button disabled={pending}>{pending ? 'Cancelling…' : 'Cancel order'}</button>
      {state.error && <p role="alert">{state.error}</p>}
    </form>
  );
}
```

**Bad Example** — an unauthenticated mutation that trusts its arguments

```ts
'use server';

export async function cancelOrder(orderId: string) {
  // No session check. The action is a POST endpoint with a stable id, callable
  // by anyone who has ever loaded the page — including from curl.
  await db.order.update({ where: { id: orderId }, data: { status: 'CANCELLED' } });

  // No ownership scope: any order id cancels any customer's order.
  // No validation: `orderId` is whatever the caller sent.
  // No revalidation: the page keeps showing the order as pending.
}
```

Hiding the button behind a permission check in the UI does not protect the action — the
endpoint exists regardless of what the page renders.

---

## Common Mistakes

Avoid:

Moving business logic into Client Components.

Skipping authorization.

Trusting client-side validation.

Creating internal API calls.

Invalidating the entire cache unnecessarily.

Returning sensitive error information.

Making oversized Server Actions with multiple unrelated responsibilities.

---

## Completion Criteria

A Server Action implementation is complete when:

- input validation is implemented;
- authorization has been verified;
- the mutation executes successfully;
- affected caches are invalidated;
- errors are handled safely;
- sensitive information remains on the server.

---

## Summary

Server Actions are the preferred mechanism for handling data mutations in modern Next.js applications.

By centralizing validation, authorization, database access, and cache invalidation on the server, applications become simpler, more secure, easier to maintain, and better aligned with the server-first architecture of the App Router.

## Related

- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/24-security.md`
- `knowledge/nextjs/15-authorization.md`
- `knowledge/react/15-forms.md`
