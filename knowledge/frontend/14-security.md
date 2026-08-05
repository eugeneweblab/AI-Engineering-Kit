---
id: frontend/14-security
topic: frontend
slug: security
title: "Frontend Security"
type: doc
order: 14
status: ready
tags: [frontend, security, Comment, HttpOnly, "data:", localStorage, "javascript:", login]
related: [frontend/12-forms, frontend/13-error-handling, frontend/06-data-fetching, frontend/07-rendering, frontend/19-build-tools]
when_to_use: "Read before rendering user-controlled content, storing tokens, handling auth in the browser, or configuring headers."
---
# Frontend Security

## Purpose

This document defines the security responsibilities that live in the browser: preventing
XSS, storing credentials safely, defending against CSRF and clickjacking, and shipping the
right response headers. It is scoped to what frontend code and its build/serve config
control, so an agent can build a UI that does not open holes the backend cannot close.

Frontend security is about the trust boundary between untrusted content (user input, URLs,
third-party scripts) and the powerful capabilities the browser grants your origin.
Everything the client does is visible and modifiable by the user; the frontend's job is to
avoid *executing* attacker-controlled content, never to *hide* secrets.

## Why It Matters

The browser runs your code on the user's machine with access to their cookies, session,
and DOM. A single injected `<script>` — from a comment field, a URL param, a compromised
dependency — runs with full authority of the logged-in user: it can read tokens, submit
forms, and exfiltrate data, all silently. Unlike a server bug behind a firewall, a
frontend vulnerability executes directly in every victim's session. And because the entire
bundle ships to the client, any secret embedded in it is already public. These failures are
invisible in normal testing and total in impact, so untrusted content must be treated as
hostile by default.

## Core Principles

- **Never inject unsanitized HTML.** Rendering user content as HTML (`innerHTML`,
  `dangerouslySetInnerHTML`) is the primary XSS vector. Prefer text; if you must render
  HTML, sanitize with a vetted library first.
- **The client holds no secrets.** API keys, signing secrets, and admin flags in bundle
  code are public. Anything that must stay secret lives on the server.
- **Auth in the browser means `HttpOnly` cookies, not `localStorage`.** Tokens in
  `localStorage` are readable by any XSS. Let the browser hold session cookies your JS
  cannot touch.
- **Validate that the server enforces, don't rely on the UI.** Hiding a button is not
  access control. Every guarded action must be re-checked server-side.
- **Lock down the origin's capabilities.** A strict Content-Security-Policy turns a
  successful injection into a no-op by refusing to run inline or foreign scripts.

## Best Practices

- Render user content as **text by default**. Only use `dangerouslySetInnerHTML` /
  `innerHTML` on output run through a sanitizer like DOMPurify, and treat every such call
  as a reviewable exception.
- Validate and constrain URLs before using them in `href`/`src`. Reject `javascript:`,
  `data:`, and `vbscript:` schemes; allowlist `https:` (and `mailto:`/`tel:` where needed).
- Add `rel="noopener noreferrer"` to every `target="_blank"` link to prevent reverse-tabnabbing.
- Ship a **Content-Security-Policy** that forbids inline scripts and unknown origins;
  prefer nonces/hashes over `unsafe-inline`. Add `X-Content-Type-Options: nosniff` and
  `X-Frame-Options: DENY` (or CSP `frame-ancestors 'none'`) to block MIME-sniffing and
  clickjacking.
- Store session tokens in `Secure`, `HttpOnly`, `SameSite` cookies. Pair with a CSRF token
  (or `SameSite=Strict`/`Lax`) for state-changing requests.
- Pin and audit dependencies; a supply-chain compromise runs with your origin's full
  authority. Enable `npm audit`/lockfile checks in CI and use Subresource Integrity for any
  third-party script you cannot self-host.
- Keep secrets out of the client build entirely — never read a private key from
  `NEXT_PUBLIC_*`/`VITE_*` env vars; those are inlined into the public bundle.

## Examples

**Good Example** — text by default, sanitized HTML, safe links

```tsx
import DOMPurify from "dompurify";

// Plain user text: React escapes it automatically — no HTML is executed.
function Comment({ body }: { body: string }) {
  return <p>{body}</p>;
}

// Rich content that MUST be HTML: sanitize before injecting.
function RichComment({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html); // strips <script>, event handlers, etc.
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}

function ExternalLink({ href, children }: { href: string; children: React.ReactNode }) {
  const safe = /^https?:\/\//i.test(href) ? href : "#"; // reject javascript:/data:
  return (
    <a href={safe} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  );
}
```

**Bad Example** — raw injection, token in localStorage, unchecked scheme

```tsx
function Comment({ body }) {
  // body is user-controlled: <img src=x onerror=steal()> now runs. XSS.
  return <div dangerouslySetInnerHTML={{ __html: body }} />;
}

async function login(creds) {
  const { token } = await api.login(creds);
  localStorage.setItem("token", token); // any XSS on the page can read this
}

function Link({ url, text }) {
  // url could be "javascript:fetch('/evil?c='+document.cookie)"
  return <a href={url}>{text}</a>;
}
```

## Common Mistakes

- Passing user or URL-derived content into `dangerouslySetInnerHTML`/`innerHTML` unsanitized.
- Storing JWTs or session tokens in `localStorage`/`sessionStorage`, exposing them to XSS.
- Putting API keys or secrets in `NEXT_PUBLIC_`/`VITE_` env vars, which ship in the bundle.
- Treating a hidden UI element as authorization instead of enforcing it on the server.
- `target="_blank"` links without `rel="noopener"`, enabling reverse-tabnabbing.
- No Content-Security-Policy, so any injected script executes freely.
- Rendering unvalidated `href`/`src` values, allowing `javascript:` and `data:` URIs.

## Production Tips

- Start CSP in `Content-Security-Policy-Report-Only` mode, collect violation reports, then
  enforce once the policy is clean — this avoids breaking the app on rollout.
- Add automated dependency and secret scanning to CI (lockfile audit, secret detection) so
  a leaked key or malicious package is caught before deploy.
- Prefer the backend-for-frontend / auth-code-with-PKCE pattern so the SPA never handles
  raw refresh tokens; the server sets an `HttpOnly` cookie instead.

## AI Review Checklist

- Is all user-controlled content rendered as text, or sanitized before being injected as HTML?
- Are session tokens kept in `HttpOnly` cookies rather than `localStorage`/`sessionStorage`?
- Are there any secrets or API keys embedded in client-side/bundle code or public env vars?
- Are `href`/`src` values validated to reject `javascript:`/`data:` schemes?
- Does every `target="_blank"` carry `rel="noopener noreferrer"`?
- Is a strict CSP plus `nosniff` and anti-clickjacking header configured?
- Is every UI-gated action also enforced server-side?

## Related

- `knowledge/frontend/12-forms.md`
- `knowledge/frontend/13-error-handling.md`
- `knowledge/frontend/06-data-fetching.md`
- `knowledge/frontend/07-rendering.md`
- `knowledge/frontend/19-build-tools.md`
