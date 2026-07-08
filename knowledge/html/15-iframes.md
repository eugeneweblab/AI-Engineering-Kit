---
id: html/15-iframes
topic: html
slug: iframes
title: "Iframes"
type: doc
order: 15
status: ready
tags: [html, iframes]
related: [html/19-security, html/09-media, html/18-performance, html/11-accessibility]
when_to_use: "Read before embedding third-party content or untrusted HTML with an <iframe>."
---
# Iframes

## Purpose

This document defines how to embed one browsing context inside another with `<iframe>`
safely and performantly. It covers sandboxing, the `allow` permissions policy,
`referrerpolicy`, lazy loading, sizing, and accessibility. The overriding concern is
security: an iframe is a doorway to another origin's code running inside your page.

An `<iframe>` embeds an independent document — a video, a map, a payment widget, a
partner's app. Because that document can be code you do not control, the default posture
is *least privilege*: grant nothing, then add back exactly what the embed needs. This
connects directly to [HTML security](19-security.md).

## Why It Matters

An unsandboxed iframe pointed at untrusted content can run scripts, submit forms,
navigate your top window to a phishing page, trigger downloads, and read the referrer
URL you sent it. Conversely, letting *your* page be framed by anyone enables clickjacking
— your UI rendered invisibly over an attacker's. Both are default behaviors you must
actively restrict. The failures are not visible in normal use; they surface only when
someone abuses them. Least-privilege embedding is the difference between a widget and a
breach.

## Core Principles

- **Least privilege by default.** Add `sandbox` and grant only the specific tokens the
  embed provably needs. An empty `sandbox=""` blocks scripts, forms, popups, and same-
  origin access entirely.
- **Never combine `allow-scripts` and `allow-same-origin` for untrusted content.**
  Together they let the framed page remove its own sandbox and access your origin.
- **Control who may frame *you*.** Set `Content-Security-Policy: frame-ancestors`
  (and/or `X-Frame-Options`) so your pages cannot be silently clickjacked.
- **Minimize what you hand across the boundary.** Use `referrerpolicy` to avoid leaking
  full URLs, and `allow` to deny camera, microphone, geolocation, and payment by default.
- **An iframe is a performance and a11y cost.** It loads a whole document; treat it as
  heavyweight and give it an accessible name.

## Best Practices

- Add `sandbox` to any iframe hosting untrusted or third-party HTML; start from empty
  and add only needed tokens (`allow-scripts`, `allow-forms`, `allow-popups`, …).
- Scope the Permissions Policy with `allow`: grant `allow="fullscreen"` for a video,
  and explicitly withhold the rest — do not leave the default open.
- Set `referrerpolicy="no-referrer"` (or `strict-origin-when-cross-origin`) so you do
  not leak the embedding page's full URL to the third party.
- Lazy-load below-the-fold embeds with `loading="lazy"` to defer their (often large)
  network and CPU cost until needed.
- Give every iframe a `title` attribute describing its content — screen readers
  announce it, and a missing title is a WCAG failure.
- Prefer a specific `src` over `srcdoc` for external content; use `srcdoc` only for
  small, controlled inline documents (still sandboxed).
- Protect your own pages: send `Content-Security-Policy: frame-ancestors 'self'` (or an
  allowlist) so only you can frame them.
- Set explicit `width`/`height` or an aspect-ratio wrapper to avoid layout shift.

## Examples

**Good Example** — sandboxed, scoped, titled, lazy

```html
<iframe
  src="https://widgets.partner.com/rating"
  title="Product rating widget"          <!-- accessible name for screen readers -->
  sandbox="allow-scripts"                 <!-- scripts only; NO allow-same-origin -->
  allow="clipboard-write"                 <!-- grant just this; camera/mic denied -->
  referrerpolicy="no-referrer"            <!-- don't leak our URL to the partner -->
  loading="lazy"                          <!-- defer offscreen load -->
  width="320" height="120">               <!-- fixed box: no layout shift -->
</iframe>
```

**Bad Example** — full trust, leaky, unlabeled

```html
<iframe
  src="https://random-embed.example/app"
  sandbox="allow-scripts allow-same-origin">  <!-- combo lets it escape the sandbox -->
  <!-- no title → screen readers announce "iframe", WCAG fail -->
  <!-- no allow policy → camera, mic, geolocation, payment all permitted by default -->
  <!-- no referrerpolicy → full embedding URL sent to the third party -->
  <!-- no loading="lazy", no dimensions → eager load + layout shift -->
</iframe>
```

## Common Mistakes

- Setting both `allow-scripts` and `allow-same-origin` on untrusted content, which
  neutralizes the sandbox.
- Omitting `sandbox` entirely for third-party embeds, granting them full capability.
- No `title`, leaving the embed unlabeled for assistive technology.
- Leaving the Permissions Policy at default, silently exposing camera/mic/geolocation.
- Forgetting `frame-ancestors`/`X-Frame-Options` on your own app, enabling clickjacking.
- Leaking full URLs via the default referrer policy to a third-party origin.
- Eager-loading heavy embeds, tanking Core Web Vitals with an offscreen iframe.

## Production Tips

- Audit third-party embeds periodically — the `src` you trusted can change what it
  loads. Pin to a specific widget URL and review the `allow`/`sandbox` grant.
- Prefer a lightweight facade (a static thumbnail that loads the iframe on click) for
  heavy embeds like video, so the third-party document loads only on interaction.
- Combine a strict page-level [CSP](19-security.md) with per-iframe `sandbox`; the two
  layers cover different attack surfaces.

## AI Review Checklist

- Does every iframe with untrusted content have a `sandbox` with minimal tokens?
- Is the `allow-scripts` + `allow-same-origin` combination avoided for untrusted embeds?
- Does each iframe have a descriptive `title`?
- Is the Permissions Policy scoped with `allow`, denying unused capabilities?
- Is `referrerpolicy` set to avoid leaking the embedding URL?
- Are below-the-fold iframes `loading="lazy"` with explicit dimensions?
- Do your own pages restrict `frame-ancestors` to prevent clickjacking?

## Related

- `knowledge/html/19-security.md`
- `knowledge/html/09-media.md`
- `knowledge/html/18-performance.md`
- `knowledge/html/11-accessibility.md`
