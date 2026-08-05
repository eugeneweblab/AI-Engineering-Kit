---
id: rest-api/15-authentication
topic: rest-api
slug: authentication
title: "REST API Authentication"
type: doc
order: 15
status: ready
tags: [rest-api, authentication]
related: [rest-api/16-authorization, rest-api/17-rate-limiting, rest-api/24-security, rest-api/07-status-codes, rest-api/09-error-handling]
when_to_use: "Read before adding, changing, or reviewing how a REST API identifies the caller of a request."
---
# REST API Authentication

## Purpose

This document defines how a REST API verifies *who* is calling: credential schemes, token
handling, and the stateless request-by-request nature of API authentication. It is written
so an agent can protect an endpoint without leaking credentials or trusting a forged token.

Authentication answers "who is this caller?"; it is distinct from
[authorization](16-authorization.md) ("is this caller allowed to do this?"). This doc covers
the API-transport side of the problem; for credential storage, hashing, and session
internals, see the security topic's authentication guide. Do not conflate the two questions
— check identity first, permission second.

## Why It Matters

Every REST request is independent and unauthenticated by default. There is no session the
server "remembers"; each call must prove identity on its own. Get this wrong and the failure
is total and silent: a forgeable token, a secret in a URL, or a missing signature check lets
an attacker impersonate any user while the API returns clean `200`s. Because REST APIs are
directly reachable over the network — no browser, no CSRF story, just HTTP — they are probed
constantly. Assume every request is hostile until identity is proven.

## Core Principles

- **Authenticate every request, statelessly.** REST is stateless; each request must carry
  its own proof of identity (a token or signature). Never trust IP, order, or prior calls.
- **Use standard schemes.** Bearer tokens (OAuth 2.1 / OIDC access tokens) or mTLS for
  service-to-service. Never invent a custom token format or signing scheme.
- **Credentials travel in headers, over TLS only.** Put tokens in `Authorization`, never in
  the URL or query string. Reject all non-HTTPS traffic.
- **Verify tokens fully before trust.** Signature, algorithm, issuer, audience, and expiry —
  all of them, every request. A token you did not fully verify is attacker-controlled input.
- **Fail closed and uniformly.** Missing or invalid credentials return `401`; a valid but
  insufficient identity is [authorization](16-authorization.md)'s `403`. Do not leak which.

## Best Practices

- Send credentials as `Authorization: Bearer <token>`. Return `401 Unauthorized` with a
  `WWW-Authenticate` header when they are missing or invalid.
- For JWT access tokens, verify the signature against the issuer's published keys (JWKS),
  pin the expected `alg`, and check `iss`, `aud`, and `exp` on every request. Reject `alg: none`.
- Keep access tokens **short-lived** (minutes) and use refresh tokens or re-authentication
  for longevity. Short lifetimes bound the damage of a leaked token.
- Support token **revocation**: a logout or key rotation must actually stop a token working.
  Pure stateless JWTs cannot be revoked mid-life — pair them with short expiry or a denylist.
- For machine-to-machine APIs, prefer OAuth client credentials or mTLS over static API keys.
  If you must use API keys, store only a hash, scope them, and make them rotatable.
- Never log the `Authorization` header, tokens, or API keys. Redact them at the logging boundary.
- Return `401` uniformly whether the token is absent, malformed, or expired — do not help an
  attacker distinguish cases.

## Examples

**Good Example** — full token verification, credentials in header

```ts
import { jwtVerify, createRemoteJWKSet } from "jose";

const JWKS = createRemoteJWKSet(new URL("https://auth.example.com/.well-known/jwks.json"));

async function authenticate(req: Request) {
  const header = req.headers.get("authorization") ?? "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : null;
  if (!token) throw new Unauthorized(); // 401, WWW-Authenticate set by handler

  // Verify signature via JWKS AND pin alg/iss/aud/exp. Any failure -> 401.
  const { payload } = await jwtVerify(token, JWKS, {
    issuer: "https://auth.example.com",
    audience: "orders-api",
    algorithms: ["RS256"], // reject alg:none and unexpected algorithms
  });
  return { userId: payload.sub, scopes: payload.scope };
}
```

**Bad Example** — token in URL, unverified signature

```ts
async function authenticate(req: Request) {
  const url = new URL(req.url);
  const token = url.searchParams.get("token"); // leaks into logs, history, referrers

  // decode() does NOT verify the signature: any attacker can forge this payload.
  const payload = jwtDecode(token!);
  if (payload.exp < Date.now() / 1000) throw new Error("expired"); // only expiry checked
  return { userId: payload.sub }; // trusts an unsigned, forgeable claim
}
```

## Common Mistakes

- Putting tokens or API keys in the URL/query string, where they leak to logs, proxies, and
  browser history.
- Decoding a JWT without verifying its signature, or not pinning `alg` (allowing `alg: none`).
- Skipping `iss`/`aud` checks, so a token minted for another service is accepted.
- Long-lived access tokens with no revocation path, so a leak is exploitable for months.
- Using `403` for "not logged in" (should be `401`) or `401` for "logged in but forbidden"
  (should be `403`) — see [status codes](07-status-codes.md).
- Logging the `Authorization` header, spilling live credentials into log storage.
- Static, unscoped, non-rotatable API keys treated as a permanent secret.

## Production Tips

- Cache JWKS keys with a short TTL and handle rotation gracefully; a hard-failing key fetch
  should not take down authentication.
- Emit auth events (success, `401`, token-expired, key-rotation) with caller id and IP, never
  the token itself, and alert on `401` spikes — a sign of credential stuffing.
- Rate-limit unauthenticated and failed-auth requests aggressively (see
  [rate limiting](17-rate-limiting.md)) to blunt brute-force and token-guessing.

## AI Review Checklist

- Does every protected endpoint require and verify a token on each request (stateless)?
- Are JWT signature, `alg`, `iss`, `aud`, and `exp` all verified, with `alg: none` rejected?
- Are credentials read from the `Authorization` header only, never the URL, over TLS only?
- Are access tokens short-lived with a working revocation or expiry strategy?
- Is missing/invalid auth answered with a uniform `401`, distinct from authorization's `403`?
- Are tokens and API keys kept out of all logs?

## Related

- `knowledge/rest-api/16-authorization.md`
- `knowledge/rest-api/17-rate-limiting.md`
- `knowledge/rest-api/24-security.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/09-error-handling.md`
