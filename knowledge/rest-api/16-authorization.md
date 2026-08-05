---
id: rest-api/16-authorization
topic: rest-api
slug: authorization
title: "REST API Authorization"
type: doc
order: 16
status: ready
tags: [rest-api, authorization, NotFound, getOrder, Forbidden, includes, findOne, findById]
related: [rest-api/15-authentication, rest-api/24-security, rest-api/07-status-codes, rest-api/04-endpoints, rest-api/09-error-handling]
when_to_use: "Read before adding or reviewing any check that decides whether a caller may access a resource or action."
---
# REST API Authorization

## Purpose

This document defines how a REST API decides *what* an authenticated caller may do: enforcing
ownership, roles, and scopes on every endpoint, and preventing the object-level access flaws
that top every API vulnerability list. It is written so an agent can protect resources without
leaving a hole an attacker walks through by changing an ID in the URL.

Authorization answers "is this caller allowed to do this?"; it assumes
[authentication](15-authentication.md) has already answered "who is this caller?". Identity
first, permission second — never skip either.

## Why It Matters

Broken authorization is the single most common serious API flaw. The classic case — **Broken
Object Level Authorization (BOLA/IDOR)** — is trivial to exploit: a user authenticated as
themselves requests `GET /orders/1002` instead of their own `1001` and reads someone else's
data, because the endpoint checked *who they are* but never *whether this record is theirs*.
The request is perfectly valid HTTP with valid credentials, so nothing looks wrong in logs.
Every endpoint that takes a resource ID is a potential breach, which is why authorization must
be enforced per request, per object, without exception.

## Core Principles

- **Authorize every request at the object level.** Authenticating the caller is not enough;
  check that *this* caller may act on *this specific resource*. Ownership is per-record, not
  per-endpoint.
- **Deny by default.** Access is forbidden unless a rule explicitly grants it. A new endpoint
  with no rule must reject, not allow.
- **Enforce on the server, at the data boundary.** Never rely on the client hiding a button or
  omitting a field. Scope every query to the caller's permitted rows.
- **Least privilege.** Grant the narrowest role/scope that works. Tokens and API keys carry
  only the scopes they need.
- **Distinguish `401` from `403`.** `401` means "not authenticated"; `403` means
  "authenticated but not permitted." Do not swap them — see [status codes](07-status-codes.md).

## Best Practices

- Enforce ownership by **scoping the query**, not by fetching-then-checking after the fact:
  `WHERE id = $1 AND owner_id = $caller`. This makes "not yours" indistinguishable from "not
  found" and closes the IDOR class structurally.
- Centralize policy in one place (a policy/guard layer), not scattered `if role === "admin"`
  checks. Duplicated inline checks drift and one gets forgotten.
- Check authorization for **every** verb on a resource, including `GET`. Read access to
  another user's object is a breach, not a lesser one.
- Use **role- or attribute-based** access (RBAC/ABAC) with named permissions, not hardcoded
  user IDs or email checks.
- For token scopes, verify the required scope for the operation (`orders:write`) before acting,
  and reject with `403` if absent.
- Prefer returning `404` over `403` when even revealing a resource's existence leaks
  information (e.g. private records) — but be consistent about the policy.
- Never trust IDs, roles, or ownership sent in the request body; derive the caller's identity
  and permissions from the verified token only.

## Examples

**Good Example** — ownership enforced in the query, deny by default

```ts
async function getOrder(caller: Principal, orderId: string) {
  // Scope to the caller's own rows. If the order exists but isn't theirs,
  // the query returns nothing -> 404, leaking neither data nor existence.
  const order = await db.orders.findOne({ id: orderId, ownerId: caller.userId });
  if (!order) throw new NotFound();
  return order;
}

async function deleteOrder(caller: Principal, orderId: string) {
  if (!caller.scopes.includes("orders:write")) throw new Forbidden(); // 403, explicit grant
  const deleted = await db.orders.deleteOne({ id: orderId, ownerId: caller.userId });
  if (deleted === 0) throw new NotFound(); // never yours, never found
}
```

**Bad Example** — authenticated but no object-level check (IDOR)

```ts
async function getOrder(caller: Principal, orderId: string) {
  // Caller is authenticated, so this "feels" safe. But it fetches ANY order by id
  // with no ownership scope: GET /orders/1002 returns another user's order.
  const order = await db.orders.findById(orderId); // no owner filter -> BOLA/IDOR
  return order;
}
// Also trusts req.body.role to grant admin actions — client-supplied privilege.
```

## Common Mistakes

- Checking authentication but not object ownership, leaving IDOR/BOLA on every ID-taking route.
- Fetching a record first and checking ownership after, then leaking its existence via `403`
  vs `404` timing or messages.
- Enforcing access in the UI (hiding buttons) while the API endpoint stays open.
- Scattering inline role checks instead of a central policy, so one endpoint is forgotten.
- Trusting a role, `owner_id`, or scope sent in the request body rather than the verified token.
- Confusing `401` and `403`, or returning `200` with filtered-but-still-present forbidden data.
- Skipping authorization on `GET` because "it's only a read."

## Production Tips

- Add automated tests that call each endpoint as a *different* user and assert `404`/`403`;
  IDOR is invisible to single-user testing and only surfaces cross-user.
- Log authorization denials with caller id, resource, and action, and alert on spikes — a
  pattern of `403`s on sequential IDs is an active enumeration attack.
- Keep the permission model in code review's checklist: any new endpoint that takes a resource
  ID must show its ownership scope in the diff.

## AI Review Checklist

- Does every endpoint taking a resource ID scope the query to the caller's permitted rows?
- Is access denied by default, with each grant explicit (role/scope/ownership)?
- Is authorization enforced on the server for every verb, including `GET`?
- Are roles, scopes, and ownership derived from the verified token, never from the request body?
- Are `401` (unauthenticated) and `403` (forbidden) used correctly and distinctly?
- Are there cross-user tests proving one user cannot read or mutate another's resources?

## Related

- `knowledge/rest-api/15-authentication.md`
- `knowledge/rest-api/24-security.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/04-endpoints.md`
- `knowledge/rest-api/09-error-handling.md`
