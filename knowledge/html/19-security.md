---
id: html/19-security
topic: html
slug: security
title: "Security"
type: doc
order: 19
status: ready
tags: [html, security]
related: [html/04-links, html/08-forms, html/15-iframes, html/10-metadata, html/27-html-apis]
when_to_use: "Read before rendering user-supplied content, adding external links, embedding third-party frames, or setting document-level security policy."
---
# Security

## Purpose

This document defines how to write HTML that does not become an attack surface. It
covers the markup-level defenses against cross-site scripting (XSS), clickjacking,
tabnabbing, and untrusted embeds — the parts of security that live in the document
itself rather than in the server or transport layer.

HTML is where injected script executes and where trust boundaries between your page
and third parties are drawn. Getting the markup right is the last line of defense when
sanitization upstream fails.

## Why It Matters

The browser cannot distinguish markup you authored from markup an attacker injected
through a comment field — both are just characters in the DOM, and both run. A single
unescaped `<` in user content can turn into a `<script>` that steals every visitor's
session. A single `target="_blank"` without `rel="noopener"` hands the opened site a
handle to navigate your tab to a phishing page. These flaws execute in the victim's
browser with the victim's privileges, so the damage is done client-side where your
server logs never see it. Assume all rendered data is hostile until proven inert.

## Core Principles

- **Never build HTML by string concatenation from user input.** Use a templating
  engine that escapes by default, or set text with `textContent`, not `innerHTML`.
- **Escape by context, not globally.** The correct escaping for HTML body, an attribute,
  a URL, and a `<script>` block all differ. Attribute values and `javascript:` URLs are
  frequent bypasses.
- **Treat every external origin as untrusted.** Links, iframes, and scripts to other
  origins can navigate, frame, or read your page unless you constrain them.
- **Defense in depth.** A Content Security Policy is a backstop, not a substitute, for
  escaping — assume one layer will fail.
- **Deny by default.** Sandbox embeds and drop dangerous URL schemes unless a specific
  capability is explicitly required.

## Best Practices

- Escape user data for its context before it reaches the DOM. Prefer `textContent` /
  framework binding over `innerHTML`; if you must set HTML, sanitize with a vetted
  library (DOMPurify) — never a hand-rolled regex.
- Add `rel="noopener noreferrer"` to every `target="_blank"` link so the opened page
  cannot reach `window.opener` (reverse tabnabbing). Modern browsers imply `noopener`,
  but set it explicitly for older engines and clarity. See [links](04-links.md).
- Sandbox third-party iframes with `sandbox` and grant back only needed tokens
  (`allow-scripts`, `allow-forms`); never combine `allow-scripts allow-same-origin`
  for untrusted content — together they let the frame remove its own sandbox. See
  [iframes](15-iframes.md).
- Ship a Content Security Policy via response header (preferred) or `<meta http-equiv>`;
  avoid `unsafe-inline` and use nonces/hashes for any inline script.
- Reject `javascript:`, `data:`, and `vbscript:` URLs in user-provided `href`/`src`;
  allowlist `https:`, `mailto:`, and relative paths.
- Set `autocomplete="off"` and `type="password"` correctly on sensitive fields, and
  never reflect submitted values back into the page unescaped. See [forms](08-forms.md).

## Examples

**Good Example** — inert user content, safe external link, sandboxed embed

```html
<!-- Bind as text: the framework escapes < > & so markup cannot execute -->
<p>{{ comment.body }}</p>

<!-- noopener: opened tab cannot script window.opener; noreferrer hides the URL -->
<a href="https://partner.example" target="_blank" rel="noopener noreferrer">Partner</a>

<!-- Untrusted embed: scripts allowed but NOT same-origin, so it can't escape sandbox -->
<iframe src="https://widget.example" sandbox="allow-scripts" title="Widget"></iframe>
```

```js
// Setting untrusted data as text, never as markup
el.textContent = userInput; // <script> becomes visible text, not an executed node
```

**Bad Example** — injection, tabnabbing, escapable sandbox

```html
<!-- innerHTML with user input: a <script>/<img onerror> payload executes -->
<script>el.innerHTML = "Hi " + userInput;</script>

<!-- Missing rel: opened page can do window.opener.location = phishingUrl -->
<a href="https://partner.example" target="_blank">Partner</a>

<!-- allow-scripts + allow-same-origin on untrusted content defeats the sandbox -->
<iframe src="https://widget.example"
        sandbox="allow-scripts allow-same-origin"></iframe>
```

## Common Mistakes

- Interpolating user input into `innerHTML` or a template string, enabling XSS.
- Escaping for HTML body but forgetting attribute or URL context (e.g. `href`).
- `target="_blank"` without `rel="noopener"`, exposing the tab to reverse tabnabbing.
- Sandboxing an untrusted iframe with both `allow-scripts` and `allow-same-origin`.
- Relying on client-side escaping alone while trusting a `data:`/`javascript:` URL.
- Treating a CSP as a reason to skip output encoding — it is a backstop, not the fix.

## Production Tips

- Deploy CSP in `Content-Security-Policy-Report-Only` first, collect violation reports,
  then enforce — this catches inline scripts you did not know existed.
- Add security headers (`X-Content-Type-Options: nosniff`, `Referrer-Policy`) at the
  edge so every response is protected uniformly.
- Fuzz any endpoint that reflects input with XSS payloads in CI so a regression fails
  the build, not a pen test.

## AI Review Checklist

- Is all user-supplied content escaped for its context or set via `textContent`?
- Is dynamic HTML sanitized with a vetted library rather than string building?
- Does every `target="_blank"` link carry `rel="noopener noreferrer"`?
- Are untrusted iframes sandboxed without both `allow-scripts` and `allow-same-origin`?
- Are `javascript:`/`data:` URL schemes rejected in user-provided links?
- Is a Content Security Policy present, without `unsafe-inline`?

## Related

- `knowledge/html/04-links.md`
- `knowledge/html/08-forms.md`
- `knowledge/html/15-iframes.md`
- `knowledge/html/10-metadata.md`
- `knowledge/html/27-html-apis.md`
