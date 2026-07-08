---
id: backend/11-authorization
topic: backend
slug: authorization
title: "Authorization"
type: doc
order: 11
status: ready
tags: [backend, authorization]
related: [backend/10-authentication, backend/07-business-logic, backend/06-api-design, backend/21-security, backend/22-observability]
when_to_use: "Read before adding or reviewing any permission check, role, ownership rule, or access-control decision."
---
# Authorization

## Purpose

This document defines how a backend decides *what* an authenticated caller is allowed to
do: roles, permissions, resource ownership, and where those checks belong. It is written
so an agent can enforce access control consistently, on every path, without leaving a gap
an attacker can walk through.

Authorization answers "are you allowed to do this?". It runs *after*
[authentication](10-authentication.md) has established *who* you are. Never let a valid
identity imply permission — the two are separate decisions.

## Why It Matters

Broken access control is the single most common serious web vulnerability, because the
happy path hides it: the feature works for the intended user, so a missing check ships
unnoticed until someone changes an id in a URL and reads another tenant's data. Unlike a
crash, an authorization gap is silent and total — it exposes exactly the data the system
exists to protect. Every endpoint must be treated as reachable by a hostile,
authenticated user.

## Core Principles

- **Deny by default.** Access is forbidden unless a rule explicitly grants it. New
  endpoints must be locked until a check is added — the cost is friction, the payoff is
  that a forgotten check fails closed, not open.
- **Check on every request, at the server.** Never rely on a hidden UI button or a
  client-supplied role. The server re-derives permissions from trusted identity each time.
- **Enforce ownership, not just role.** "Is a user" is not "owns this resource". Every
  object access must confirm the caller is entitled to *that specific* object.
- **Authorize as close to the data as possible.** Put checks in the business/domain layer,
  not only in middleware, so every entry point (HTTP, jobs, admin tools) is covered. See
  [business logic](07-business-logic.md).
- **Least privilege.** Grant the narrowest permission that works, and scope tokens and
  service accounts the same way.

## Best Practices

- Centralize the policy in one place (a policy/guard module) and call it everywhere;
  scattered `if (user.role === "admin")` checks drift and get missed.
- Use a clear model: **RBAC** (roles) for coarse access, **ABAC/ReBAC** (attributes,
  relationships) when access depends on ownership or context. Pick one and apply it
  consistently.
- Perform object-level checks by loading the resource and verifying ownership/tenant
  *before* acting — the classic IDOR fix.
- Scope every query by tenant/owner at the data layer so a missing filter can't return
  another tenant's rows.
- Return `404` (not `403`) for resources the caller may not even know exist, to avoid
  leaking their existence; use `403` only when existence is already public.
- Validate the *action*, not just the route: a user may `GET` an order but not `DELETE`
  it. Authorize per operation.
- Re-check authorization for state-changing background jobs and webhooks; they bypass the
  HTTP middleware where checks often live.

## Examples

**Good Example** — deny by default, ownership enforced at the data layer

```ts
async function getInvoice(caller: User, invoiceId: string): Promise<Invoice> {
  // Scope the query by the caller's tenant: another tenant's id simply returns nothing.
  const invoice = await invoices.findOne({ id: invoiceId, tenantId: caller.tenantId });

  if (!invoice) throw new NotFound();          // 404 hides existence of others' data
  if (!policy.canRead(caller, invoice))        // explicit grant required (deny by default)
    throw new NotFound();                      // don't confirm it exists to an outsider
  return invoice;
}
```

**Bad Example** — trusts the id, checks role but not ownership

```ts
async function getInvoice(caller: User, invoiceId: string): Promise<Invoice> {
  // IDOR: fetches by id alone; any authenticated user reads any invoice by guessing ids.
  const invoice = await invoices.findById(invoiceId);
  if (caller.role !== "member")                // role check, but no OWNERSHIP check
    throw new Forbidden();                     // "is a member" != "owns this invoice"
  return invoice;                              // cross-tenant data leak
}
```

## Common Mistakes

- **IDOR**: acting on a client-supplied id without verifying the caller owns that object.
- Authorizing by role only, never checking resource ownership or tenant.
- Enforcing access in the UI or middleware alone, leaving jobs, webhooks, and admin paths
  unguarded.
- Trusting a role or permission claim sent by the client instead of deriving it server-side.
- Default-allow: new endpoints reachable until someone remembers to add a check.
- Leaking existence via `403` where a `404` was appropriate.
- Over-broad tokens/service accounts that grant far more than the task needs.

## Production Tips

- Add a default-deny guard at the framework level so an endpoint with no explicit policy
  is rejected, turning a forgotten check into a `403` instead of a breach.
- Log authorization *denials* with caller id, resource, and action, and alert on spikes —
  they often mark an attack in progress. See [observability](22-observability.md).
- Write tests that assert a user *cannot* access another user's/tenant's resource; test the
  negative, not just the happy path.
- Audit privileged actions (role changes, exports, deletes) to an append-only log.

## AI Review Checklist

- Is access denied by default, granted only by an explicit rule?
- Is every request authorized server-side, never trusting client-supplied roles?
- Are object-level accesses checked for ownership/tenant, not just role (no IDOR)?
- Are data queries scoped by tenant/owner at the data layer?
- Are checks enforced in the business layer so jobs and webhooks are also covered?
- Does the response avoid leaking a resource's existence to unauthorized callers?
- Are tokens and service accounts scoped to least privilege?

## Related

- `knowledge/backend/10-authentication.md`
- `knowledge/backend/07-business-logic.md`
- `knowledge/backend/06-api-design.md`
- `knowledge/backend/21-security.md`
- `knowledge/backend/22-observability.md`
