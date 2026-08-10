---
id: security/19-cors
topic: security
slug: cors
title: "CORS"
type: doc
order: 19
status: ready
tags: [security, cors, setHeader, Origin, SameSite, browser, error, access]
related: [security/22-security-headers, security/12-csrf, security/03-authentication, security/20-csp]
when_to_use: "Read before configuring cross-origin API access or debugging a browser CORS error."
---
# CORS

## Purpose

This document defines how to configure Cross-Origin Resource Sharing (CORS) safely:
which origins a browser is allowed to read responses from, and how to expose an API to
first-party front-ends without opening it to the whole web. It is written so an agent can
set CORS headers without accidentally granting hostile sites read access to authenticated
responses.

CORS is a *relaxation* of the browser's Same-Origin Policy, not a security control on the
server. It decides what other-origin JavaScript may *read*; it never decides what your
server will *do*. Enforce access in the server ([authorization](04-authorization.md)),
and use CORS only to widen the browser's default deny.

## Why It Matters

Developers reach for CORS the moment a front-end on one origin calls an API on another,
and the fastest way to make the error disappear is `Access-Control-Allow-Origin: *` — or,
worse, reflecting the request's `Origin` back with credentials enabled. That "fix" turns
every user's browser into a proxy: any malicious page the victim visits can call your API
with the victim's cookies and read the response. The app looks fine in testing because the
attack only happens from an origin you never test from. A wrong CORS line is a silent,
account-wide data leak.

## Core Principles

- **CORS controls read access, not authorization.** A permissive CORS policy does not
  authenticate or authorize anyone; a restrictive one does not protect an unauthenticated
  endpoint. Get server-side access control right regardless of CORS.
- **Allowlist exact origins.** Compare the request `Origin` against a fixed set of known
  origins and echo back the single matching value. Never trust a substring or suffix match.
- **Never combine `*` with credentials.** The browser forbids `Allow-Origin: *` together
  with `Allow-Credentials: true`. If you find yourself reflecting `Origin` to work around
  that rule, you have recreated the vulnerability the rule exists to prevent.
- **Default to no CORS.** If a resource is only used same-origin, send no CORS headers at
  all. Widen only the specific endpoints that genuinely need cross-origin reads.
- **CORS is not CSRF protection.** A cross-origin `POST` can still reach your server even
  when the browser hides the *response*. Defend state-changing requests with
  [CSRF](12-csrf.md) tokens or `SameSite` cookies.

## Best Practices

- Maintain an explicit allowlist of origins (from config, not hard-coded per request).
  Reflect the request `Origin` only after confirming it is in the list; otherwise omit the
  header entirely so the browser blocks the read.
- Add `Vary: Origin` whenever the `Allow-Origin` value depends on the request, so caches
  and CDNs never serve one origin's allowed response to another origin.
- Set `Access-Control-Allow-Credentials: true` only when the API genuinely uses cookies or
  HTTP auth, and only alongside a specific origin — never `*`.
- Restrict `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers` to what the
  API actually accepts, instead of echoing whatever the preflight asks for.
- Keep `Access-Control-Max-Age` modest (e.g. 600 seconds) to cache preflights without
  freezing a policy you may need to change.
- Handle the `OPTIONS` preflight explicitly and return `204` with the CORS headers; do not
  let it fall through to application logic or authentication.

## Examples

**Good Example** — strict allowlist, credentials bound to an exact origin

```ts
const ALLOWED = new Set([
  "https://app.example.com",
  "https://admin.example.com",
]);

function applyCors(req: Request, res: Response) {
  const origin = req.headers.origin;
  // Echo the origin ONLY when it is an exact, known match. Unknown origins get
  // no header, so the browser blocks the cross-origin read.
  if (origin && ALLOWED.has(origin)) {
    res.setHeader("Access-Control-Allow-Origin", origin);
    res.setHeader("Access-Control-Allow-Credentials", "true"); // safe: origin is specific
    res.setHeader("Vary", "Origin"); // prevent a shared cache from leaking across origins
  }
  if (req.method === "OPTIONS") {
    res.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type,Authorization");
    res.statusCode = 204; // answer the preflight and stop
    res.end();
  }
}
```

**Bad Example** — reflects any origin with credentials

```ts
function applyCors(req: Request, res: Response) {
  // Reflecting whatever Origin arrives means EVERY site is allowed. Combined with
  // credentials, any page the victim visits can read their authenticated data.
  res.setHeader("Access-Control-Allow-Origin", req.headers.origin ?? "*");
  res.setHeader("Access-Control-Allow-Credentials", "true"); // total account-wide leak
  // No Vary: Origin, so a CDN may cache one user's response and serve it cross-origin.
}
```

## Common Mistakes

- Using `Access-Control-Allow-Origin: *` on endpoints that return user-specific data.
- Reflecting the request `Origin` unconditionally — an allowlist that allows everything.
- Matching origins by `endsWith("example.com")`, which also matches `evil-example.com`.
- Enabling `Allow-Credentials` with a wildcard or reflected origin.
- Forgetting `Vary: Origin`, so a shared cache serves the wrong origin's response.
- Assuming CORS stops the request — it only hides the *response* from cross-origin script.
- Treating a passing CORS setup as CSRF protection.

## Production Tips

- Drive the allowlist from environment config so staging, preview, and production differ
  without code changes; fail startup if the list is empty in production.
- Log requests whose `Origin` was rejected — a spike often means a misconfigured client or
  an attacker probing the policy.
- Test CORS in CI with requests from an allowed origin, a disallowed origin, and a preflight
  `OPTIONS`, asserting the exact headers returned.

## AI Review Checklist

- Is `Allow-Origin` set from an exact allowlist, never a reflected or wildcard value on
  credentialed responses?
- Is `Allow-Credentials: true` paired only with a specific origin, never `*`?
- Is `Vary: Origin` sent whenever `Allow-Origin` varies per request?
- Are origin matches exact (no `endsWith`/substring checks)?
- Are `Allow-Methods` and `Allow-Headers` restricted to what the API supports?
- Is server-side [authorization](04-authorization.md) enforced independently of CORS?
- Are state-changing routes protected by [CSRF](12-csrf.md) defenses, not CORS alone?

## Related

- `knowledge/security/22-security-headers.md`
- `knowledge/security/12-csrf.md`
- `knowledge/security/03-authentication.md`
- `knowledge/security/20-csp.md`
