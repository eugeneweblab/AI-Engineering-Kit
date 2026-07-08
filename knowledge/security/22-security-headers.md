---
id: security/22-security-headers
topic: security
slug: security-headers
title: "Security Headers"
type: doc
order: 22
status: ready
tags: [security, security-headers]
related: [security/20-csp, security/18-https, security/19-cors, security/11-xss]
when_to_use: "Read before configuring HTTP response headers for a web app or API gateway."
---
# Security Headers

## Purpose

This document defines the set of HTTP response headers that harden a web application in the
browser, and the exact values to send. It is written so an agent can configure a header
middleware once, correctly, rather than copying a stale snippet that includes deprecated or
counterproductive headers.

These headers are cheap, defense-in-depth controls: they instruct the browser to enforce
transport security, framing rules, and content-type discipline. They complement — never
replace — server-side validation, [output encoding](10-output-encoding.md), and
[CSP](20-csp.md).

## Why It Matters

Browsers default to permissive, backward-compatible behavior: they will downgrade to HTTP,
sniff content types, allow framing, and leak referrer URLs unless told otherwise. Each of
those defaults is an exploitable gap — protocol downgrade, MIME-confusion XSS, clickjacking,
credential leakage in `Referer`. Setting a handful of headers closes all of them in one
place, for every response. Because they apply globally, a single misconfiguration (or a
missing header) silently affects the entire app, so the values must be deliberate and
reviewed, not cargo-culted.

## Core Principles

- **Set headers globally, in one middleware.** Per-route header logic drifts; centralize so
  every response is covered and the policy is reviewable as a unit.
- **Prefer the modern header when two overlap.** `CSP: frame-ancestors` supersedes
  `X-Frame-Options`; the modern `Referrer-Policy` supersedes ad-hoc referrer tricks. Do not
  ship deprecated headers as if they add protection.
- **Only send headers that do something.** `X-XSS-Protection` is deprecated and can *create*
  vulnerabilities; omit it. Sending noise obscures the real policy.
- **HSTS is a commitment.** Once you send `Strict-Transport-Security` with a long `max-age`,
  browsers refuse HTTP to your domain for that duration. Get HTTPS right first
  ([HTTPS](18-https.md)) before enabling it, especially with `preload`.
- **Headers are the floor, not the ceiling.** They reduce impact; the underlying code must
  still be correct.

## Best Practices

- Send [CSP](20-csp.md) as the centerpiece — it does the heavy lifting against XSS and
  clickjacking (`frame-ancestors`).
- `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` — two years,
  all subdomains, once you are certain every subdomain serves HTTPS.
- `X-Content-Type-Options: nosniff` — stop MIME sniffing that turns an uploaded file into
  executable script.
- `Referrer-Policy: strict-origin-when-cross-origin` (or `no-referrer`) — avoid leaking full
  URLs (which may contain tokens) to third-party sites.
- `X-Frame-Options: DENY` only for legacy-browser support; rely on CSP `frame-ancestors`
  for the real control.
- `Permissions-Policy` — disable powerful features the app does not use, e.g.
  `geolocation=(), camera=(), microphone=()`.
- For APIs, add `Cache-Control: no-store` on responses containing sensitive data so
  browsers and proxies do not retain them.

## Examples

**Good Example** — one middleware, modern values, no deprecated headers

```ts
function securityHeaders(_req: Request, res: Response, next: Next) {
  res.setHeader("Strict-Transport-Security",
    "max-age=63072000; includeSubDomains; preload");   // force HTTPS, all subdomains
  res.setHeader("Content-Security-Policy",
    "default-src 'self'; object-src 'none'; frame-ancestors 'none'"); // XSS + clickjacking
  res.setHeader("X-Content-Type-Options", "nosniff");  // block MIME-sniffing attacks
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin"); // no URL/token leak
  res.setHeader("Permissions-Policy", "geolocation=(), camera=(), microphone=()");
  // Note: no X-XSS-Protection — it is deprecated and can introduce bugs.
  next();
}
```

**Bad Example** — deprecated and dangerous values

```ts
function securityHeaders(_req: Request, res: Response, next: Next) {
  res.setHeader("X-XSS-Protection", "1; mode=block"); // deprecated; can enable XSS in old browsers
  res.setHeader("Strict-Transport-Security", "max-age=60"); // 1 minute ≈ no protection
  // No CSP, no nosniff, no Referrer-Policy → sniffing, clickjacking, and token leakage all open.
  res.setHeader("X-Frame-Options", "ALLOWALL"); // not a valid value; effectively no framing control
  next();
}
```

## Common Mistakes

- Shipping `X-XSS-Protection` — deprecated, and enabling it can introduce vulnerabilities.
- Setting `HSTS` with a tiny `max-age` (no real protection) or enabling `preload` before all
  subdomains serve HTTPS (locks users out).
- Relying on `X-Frame-Options` alone instead of CSP `frame-ancestors`.
- Omitting `X-Content-Type-Options: nosniff` on endpoints that serve user uploads.
- A permissive `Referrer-Policy` leaking URLs that carry session tokens or reset codes.
- Setting headers per-route, so some responses are unprotected.

## Production Tips

- Scan the deployed site with a headers checker (e.g. an automated Mozilla Observatory run)
  in CI and fail the build on regressions.
- Keep header values in config where they can be tightened without redeploying application
  logic, and diff them in code review.
- When enabling HSTS `preload`, submit the domain to the preload list only after a burn-in
  period at a long `max-age` without `preload`.

## AI Review Checklist

- Are headers applied globally in one place, covering every response?
- Is [CSP](20-csp.md) present and carrying `frame-ancestors`?
- Is `Strict-Transport-Security` set with a long `max-age` and `includeSubDomains` (and only
  `preload` once HTTPS is universal)?
- Is `X-Content-Type-Options: nosniff` set?
- Is `Referrer-Policy` restrictive enough to avoid leaking token-bearing URLs?
- Is the deprecated `X-XSS-Protection` header absent?
- Does `Permissions-Policy` disable unused powerful features?

## Related

- `knowledge/security/20-csp.md`
- `knowledge/security/18-https.md`
- `knowledge/security/19-cors.md`
- `knowledge/security/11-xss.md`
