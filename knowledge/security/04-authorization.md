---
id: security/04-authorization
topic: security
slug: authorization
title: "Authorization"
type: doc
order: 4
status: ready
tags: [security, authorization]
related: [security/03-authentication, security/01-security-fundamentals, security/06-session-management, security/29-security-review, security/28-owasp-top10]
when_to_use: "Read before building or reviewing any code that decides what an authenticated user is allowed to do."
---
# Authorization

## Purpose

This document defines how to decide *what* an authenticated user may do: permission
models, ownership checks, and enforcing access on every protected resource.
Authorization answers "are you allowed to do this?" — it runs *after*
[authentication](03-authentication.md) has answered "who are you?". A system that
authenticates perfectly but authorizes carelessly is wide open.

## Why It Matters

Broken access control is the single most common serious web vulnerability (OWASP #1).
The failure is quiet and total: an attacker changes an ID in a URL and reads another
customer's invoices, or flips a hidden field and grants themselves admin. The code
works, the tests pass, and every user's data is exposed. Unlike authentication, which
is one front door, authorization must be enforced at *every* door — miss one and the
whole floor is open. That breadth is why it is so easily botched.

## Core Principles

- **Deny by default.** Access starts at "no". A resource is reachable only when an
  explicit rule grants it. A missing rule must mean denied, never allowed.
- **Enforce on the server, on every request.** The client's UI hiding a button is not
  a control. Re-check permission on the server for each action; never trust a
  client-supplied role, ID ownership, or "isAdmin" flag.
- **Check ownership, not just role.** "Is a logged-in user" is not "may edit *this*
  record". Bind the resource to the actor: does *this* user own or have rights to
  *this* object? Skipping this is IDOR (Insecure Direct Object Reference).
- **Centralize the decision, enforce at the boundary.** Put authorization logic in one
  place (a policy layer), not scattered across handlers where one will be forgotten.
- **Least privilege.** Grant the narrowest permission that works, for the shortest
  time. Prefer scoped, revocable grants over broad standing roles.
- **Fail closed.** If the policy cannot be evaluated — an error, a missing role — deny.

## Best Practices

- Choose a model that fits: **RBAC** (roles → permissions) for coarse org structures,
  **ABAC/ReBAC** (attributes/relationships) when access depends on ownership,
  tenancy, or context. Most apps need ownership checks regardless of role.
- Scope every data query by the actor: `WHERE owner_id = :currentUser`, so the database
  cannot return another tenant's rows even if a check is missed above it.
- Return **404, not 403**, for resources the user may not even know exist — a 403
  confirms the record is real and leaks its existence.
- Check authorization as close to the data as possible (service/repository layer), so
  every caller inherits it, rather than in each controller.
- Re-authorize on privilege-sensitive actions even within a session; do not cache
  "allowed" past a role or ownership change.
- Enforce multi-tenant isolation at the query layer and test it explicitly — cross-tenant
  reads are a top cause of data leaks.

## Examples

**Good Example** — deny by default, ownership-scoped, fails closed

```ts
async function updateInvoice(user: User, invoiceId: string, patch: InvoicePatch) {
  // Scope the read to the actor: another tenant's row cannot even be loaded.
  const invoice = await invoices.findOne({ id: invoiceId, tenantId: user.tenantId });
  if (!invoice) throw new NotFoundError();          // 404, not 403 — no existence leak

  // Explicit, resource-bound permission check; absence of a grant = denied.
  if (!policy.can(user, "invoice:update", invoice)) {
    throw new ForbiddenError();
  }
  return invoices.update(invoice.id, patch);
}
```

**Bad Example** — trusts the client, checks role but not ownership (IDOR)

```ts
async function updateInvoice(req: Request) {
  // Trusting a client-set role, and checking only "is admin-ish", not ownership.
  if (req.body.role !== "user") { /* ... */ }

  // Loads by ID with no tenant/owner scope — any id works for any user (IDOR).
  const invoice = await invoices.findById(req.body.invoiceId);
  return invoices.update(invoice.id, req.body.patch); // no permission check at all
}
```

## Common Mistakes

- **IDOR:** loading a resource by ID without checking the caller owns it.
- Enforcing access only in the UI, then trusting the client on the server.
- Trusting a role, tenant, or `isAdmin` value sent by the client.
- Checking role but not ownership ("any manager can edit any record").
- Returning 403 for hidden resources, confirming their existence.
- Scattering checks across controllers so one endpoint silently lacks them.
- Caching an authorization result past the point the underlying grant can change.

## Production Tips

- Log authorization denials with actor, action, and resource; a spike often signals an
  enumeration or privilege-escalation attempt.
- Write negative tests: user A must get 404/403 for user B's resources, per endpoint.
- Add a default-deny middleware so a new route without an explicit policy fails safe
  instead of being open.
- Review new endpoints specifically for the ownership check — the most-forgotten control.

## AI Review Checklist

- Is access denied by default, granted only by an explicit rule?
- Is every protected action authorized on the server, on each request?
- Is ownership/tenancy checked, not just role (no IDOR)?
- Are data queries scoped by the current actor at the query layer?
- Do hidden resources return 404 rather than 403?
- Does the policy fail closed when it cannot be evaluated?
- Is authorization clearly separated from [authentication](03-authentication.md)?

## Related


- `knowledge/security/03-authentication.md`
- `knowledge/security/01-security-fundamentals.md`
- `knowledge/security/06-session-management.md`
- `knowledge/security/29-security-review.md`
- `knowledge/security/28-owasp-top10.md`
