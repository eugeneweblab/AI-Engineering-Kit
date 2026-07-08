---
id: security/18-https
topic: security
slug: https
title: "HTTPS"
type: doc
order: 18
status: ready
tags: [security, https]
related: [security/17-encryption, security/16-secrets-management, security/22-security-headers, security/19-cors]
when_to_use: "Read before configuring TLS, serving traffic, setting cookies, or reviewing any transport-layer security."
---
# HTTPS

## Purpose

This document defines how to serve traffic over HTTPS so that data in transit is
confidential, tamper-evident, and delivered only to the genuine server. HTTPS is
HTTP carried over TLS. Getting it right means more than "installing a certificate":
it means enforcing TLS everywhere, refusing weak protocols, and configuring the
browser to never fall back to plaintext.

HTTPS is the transport-layer application of [encryption](17-encryption.md) and the
prerequisite for safely sending [secrets](16-secrets-management.md), cookies, and
tokens. It works alongside [security headers](22-security-headers.md).

## Why It Matters

Without TLS, every byte — passwords, session cookies, API tokens — travels in
plaintext readable and modifiable by anyone on the network path: coffee-shop
Wi-Fi, ISPs, compromised routers. An active attacker can inject scripts, strip
security controls, or steal sessions. Even one plaintext request (an HTTP redirect,
a mixed-content asset) can leak a cookie or be hijacked. Because the exposure
happens on the wire, the application never sees it — which is why enforcement must
be absolute, not best-effort.

## Core Principles

- **HTTPS everywhere, no exceptions.** Every endpoint, asset, and internal service
  hop should use TLS. Partial coverage leaves an exploitable gap.
- **Redirect and enforce, don't merely offer.** Redirect all HTTP to HTTPS and use
  HSTS so browsers refuse plaintext for your domain thereafter.
- **Modern protocols only.** Serve TLS 1.3 (and 1.2); disable SSLv3, TLS 1.0/1.1,
  and weak ciphers. Old versions have known, exploitable breaks.
- **A certificate proves identity, not just secrecy.** Use certificates from a
  trusted CA, keep them valid, and automate renewal so they never expire.
- **Bind sensitive state to the secure channel.** Mark cookies `Secure` so they are
  never sent over HTTP, and eliminate mixed content.

## Best Practices

- Terminate TLS with a current configuration: **TLS 1.3 preferred, TLS 1.2
  minimum**, strong cipher suites, forward secrecy. Follow Mozilla's "modern"
  (or "intermediate") profile rather than hand-picking ciphers.
- Redirect all HTTP (port 80) to HTTPS with a `301`, then send
  `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` so
  browsers upgrade automatically and refuse HTTP for your domain.
- Obtain certificates from a trusted CA (e.g. Let's Encrypt) and **automate
  renewal** (ACME); monitor expiry so a lapsed cert never causes an outage.
- Set the `Secure` (plus `HttpOnly`, `SameSite`) attribute on all cookies so they
  are never transmitted over plaintext.
- Eliminate mixed content: load every script, style, image, and API call over
  HTTPS. A single HTTP asset on an HTTPS page is a hijack point.
- Use HTTPS for internal service-to-service traffic too (mTLS where possible); the
  internal network is not a trust boundary.
- Keep the TLS terminator (proxy/load balancer/library) patched; protocol and
  implementation flaws are fixed there.

## Examples

**Good Example** — enforce HTTPS and pin browsers with HSTS

```nginx
server {
    listen 80;
    server_name app.example.com;
    return 301 https://$host$request_uri;   # every HTTP request upgraded, no plaintext served
}

server {
    listen 443 ssl;
    server_name app.example.com;
    ssl_protocols TLSv1.3 TLSv1.2;          # modern only; TLS 1.0/1.1 and SSL disabled
    ssl_certificate     /etc/letsencrypt/live/app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app/privkey.pem;
    # Browsers refuse HTTP for this domain for 2 years, including subdomains.
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
}
```

**Bad Example** — plaintext allowed, weak protocol, insecure cookie

```nginx
server {
    listen 80;                              # serves the app over plaintext HTTP
    server_name app.example.com;
    ssl_protocols TLSv1 TLSv1.1;            # obsolete, broken protocols enabled
    # Session cookie set without Secure → sent over HTTP and sniffable on the wire.
    # No HTTPS redirect and no HSTS → attacker keeps the victim on plaintext.
}
```

## Common Mistakes

- Serving the app on HTTP with HTTPS merely "also available" — no redirect, no HSTS.
- Leaving TLS 1.0/1.1 or weak ciphers enabled for "compatibility."
- Setting session cookies without the `Secure` flag, so they leak over any HTTP hop.
- Mixed content: an HTTPS page pulling scripts or APIs over HTTP.
- Letting certificates expire because renewal is manual; automate and monitor it.
- Assuming the internal network is safe and running service-to-service calls in
  plaintext.
- Enabling HSTS `preload` before you are certain the whole domain and all subdomains
  are HTTPS-only — preload is hard to undo quickly.

## Production Tips

- Automate certificate issuance and renewal with ACME, and alert well before expiry.
- Test configuration against an external scanner (e.g. SSL Labs) and aim for an A/A+;
  re-test after any proxy or cipher change.
- Roll out HSTS with a short `max-age` first, confirm no HTTP dependencies break,
  then raise it and consider `preload`.

## AI Review Checklist

- Is all HTTP redirected to HTTPS, with HSTS set (`includeSubDomains`)?
- Is TLS restricted to 1.3/1.2 with SSL and TLS 1.0/1.1 disabled?
- Are certificates from a trusted CA with automated renewal and expiry monitoring?
- Do all cookies carrying session/auth state have the `Secure` attribute?
- Is the page free of mixed content (all assets and APIs over HTTPS)?
- Is internal service-to-service traffic also encrypted?

## Related

- `knowledge/security/17-encryption.md`
- `knowledge/security/16-secrets-management.md`
- `knowledge/security/22-security-headers.md`
- `knowledge/security/19-cors.md`
