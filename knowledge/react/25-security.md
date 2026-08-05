---
id: react/25-security
topic: react
slug: security
title: "React Security"
type: doc
order: 25
status: ready
tags: [react, security, dangerouslySetInnerHTML, localStorage, href, Comment, HttpOnly, VITE_]
related: [react/16-data-fetching, react/15-forms, react/19-error-handling, react/28-production, react/26-best-practices]
when_to_use: "Read before rendering user-supplied content, handling tokens, or shipping a React app to production."
---
# React Security

## Purpose

This document defines how to write React code that does not expose users to
cross-site scripting (XSS), token theft, or data leakage. It covers the parts of
security that live in the client: rendering untrusted content, handling URLs,
storing tokens, and keeping secrets out of the bundle. Server-side auth and
authorization live in the `security` topic — this doc is the browser half.

React escapes text by default, which prevents the most common XSS. Every serious
React vulnerability comes from stepping *outside* that default — `dangerouslySetInnerHTML`,
raw `href`, injected `<script>`, or trusting the client with a secret.

## Why It Matters

A React bundle runs on the user's machine, fully readable and modifiable. Anything
you ship — API keys, feature flags, business logic — is public. Anything you render
from untrusted data can execute as script in the victim's session. A single XSS lets
an attacker read the DOM, exfiltrate tokens, and act as the user. Because React feels
safe by default, developers assume it *is* safe and reach for `dangerouslySetInnerHTML`
without a second thought. That assumption is where the breach happens.

## Core Principles

- **Trust React's escaping; never defeat it casually.** `{userInput}` is safe.
  `dangerouslySetInnerHTML` is not — the name is a warning, treat it as one.
- **Sanitize on the way in, escape on the way out.** If you must render HTML, run it
  through a vetted sanitizer (DOMPurify) — never a regex or a hand-rolled allowlist.
- **The client keeps no secrets.** Any value in the bundle or in `import.meta.env`
  reaching the browser is public. Secrets stay server-side, behind an API.
- **URLs are code.** `javascript:` and `data:` URLs in `href` or `src` execute.
  Validate protocol before rendering user-controlled links.
- **Store tokens where XSS cannot reach them.** Prefer `HttpOnly` cookies over
  `localStorage`; a single XSS drains `localStorage` instantly.

## Best Practices

- Render untrusted text as `{value}` — JSX escapes it. Do not build HTML strings.
- If HTML is unavoidable (rich text, CMS content), sanitize with **DOMPurify** and
  render the *sanitized* string, with an allowlist of tags and attributes.
- Validate link protocols: allow only `http:`, `https:`, `mailto:`, `tel:`. Reject
  anything else before it reaches an `href`.
- Keep access tokens in `HttpOnly`, `Secure`, `SameSite` cookies. If you must use
  `localStorage`, accept that XSS defeats it and minimize token lifetime.
- Prefix client-exposed env vars deliberately (`VITE_`, `NEXT_PUBLIC_`) and audit
  every one — the prefix means "safe to ship to the browser."
- Set a Content-Security-Policy header that blocks inline script and restricts
  origins; it turns many XSS payloads into no-ops.
- Pin and audit dependencies (`npm audit`, Dependabot). Most React supply-chain
  risk enters through transitive packages, not your own code.

## Examples

**Good Example** — sanitize untrusted HTML, validate the URL protocol

```tsx
import DOMPurify from "dompurify";

function SAFE_HREF(url: string) {
  // Only allow protocols that cannot execute script.
  return /^(https?:|mailto:|tel:)/i.test(url) ? url : "#";
}

function Comment({ html, authorUrl }: { html: string; authorUrl: string }) {
  // Sanitizer strips <script>, onerror=, javascript: before it ever hits the DOM.
  const clean = DOMPurify.sanitize(html, { ALLOWED_TAGS: ["b", "i", "a", "p"] });
  return (
    <article>
      <a href={SAFE_HREF(authorUrl)}>author</a>
      <div dangerouslySetInnerHTML={{ __html: clean }} />
    </article>
  );
}
```

**Bad Example** — raw HTML and unchecked URL

```tsx
function Comment({ html, authorUrl }: { html: string; authorUrl: string }) {
  return (
    <article>
      {/* authorUrl = "javascript:fetch('/api/steal',{...})" runs on click */}
      <a href={authorUrl}>author</a>
      {/* html = "<img src=x onerror=stealCookies()> executes immediately */}
      <div dangerouslySetInnerHTML={{ __html: html }} />
    </article>
  );
}
```

## Common Mistakes

- Passing user content to `dangerouslySetInnerHTML` without sanitizing it.
- "Sanitizing" HTML with a regex — attackers have decades of bypasses; use DOMPurify.
- Putting an API key or secret in a `VITE_`/`NEXT_PUBLIC_` var and assuming it's hidden.
- Storing JWTs in `localStorage`, then treating them as safe from theft.
- Rendering `href={user.website}` without protocol validation.
- Disabling CSP because it "breaks something," instead of fixing the violation.

## Production Tips

- Enforce CSP in report-only mode first, review violations, then enforce.
- Add `npm audit --production` (or a scanner) as a blocking CI step.
- Keep DOMPurify and framework versions current — sanitizer bypasses get patched.

## AI Review Checklist

- Is every `dangerouslySetInnerHTML` fed sanitized output from DOMPurify?
- Are user-controlled `href`/`src` values protocol-validated?
- Are tokens in `HttpOnly` cookies rather than `localStorage`?
- Does any client-exposed env var contain a real secret?
- Is a restrictive CSP configured and enforced?
- Are dependencies audited in CI?

## Related

- `knowledge/react/16-data-fetching.md`
- `knowledge/react/15-forms.md`
- `knowledge/react/19-error-handling.md`
- `knowledge/react/28-production.md`
- `knowledge/react/26-best-practices.md`
