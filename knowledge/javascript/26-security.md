---
id: javascript/26-security
topic: javascript
slug: security
title: "Security"
type: doc
order: 26
status: ready
tags: [javascript, security]
related: [javascript/13-fetch-api, javascript/12-dom, javascript/14-error-handling, javascript/29-tooling, javascript/28-best-practices]
when_to_use: "Read before writing JavaScript that handles untrusted input, renders HTML, builds queries, or pulls in dependencies."
---
# Security

## Purpose

This document defines how to write JavaScript that does not become an attack vector:
avoiding injection (XSS, prototype pollution, `eval`), handling untrusted input, using
crypto correctly, and managing the risk that dependencies introduce. It covers the
language- and application-level concerns of both Node and browser JavaScript. It is
written so an agent ships code that treats every external input as hostile.

## Why It Matters

JavaScript runs at the two most exposed layers of a system: the browser, where it handles
whatever a user types or a server returns, and Node, where it faces the open internet.
A single unsanitized string reaching `innerHTML` hands an attacker a script running as
your user. One `eval` on untrusted input is remote code execution. And most modern apps
ship more third-party code than first-party — a compromised dependency runs with your
full privileges. These failures are silent until they are catastrophic.

## Core Principles

- **Never trust input.** Anything from the network, the URL, `localStorage`, or another
  origin is attacker-controlled. Validate and encode at the boundary, every time.
- **Encode for the destination, don't sanitize by guessing.** HTML, URL, and JS contexts
  each need different escaping. Use the right encoder for where the data lands.
- **Never build code from data.** No `eval`, no `new Function`, no `setTimeout("...")`
  with a string. If you construct code from input, you have handed over execution.
- **Least privilege for dependencies.** Every package is code you run. Pin, audit, and
  minimize the tree; a transitive dependency is still your attack surface.
- **Fail closed and don't leak.** On error, deny; never surface stack traces, secrets, or
  internal paths to the client.

## Best Practices

- Render untrusted data as **text**, not HTML: `textContent`/`.setAttribute`, or a
  framework's default escaping. If you must render HTML, sanitize with a vetted library
  (**DOMPurify**) — never a hand-rolled regex.
- Set a strict **Content-Security-Policy** so injected scripts cannot execute even if
  markup slips through. CSP is defense in depth, not a substitute for encoding.
- Use **parameterized queries** / prepared statements for any datastore; never
  string-concatenate SQL or build shell commands from input.
- Guard against **prototype pollution**: reject `__proto__`/`constructor`/`prototype`
  keys when merging untrusted objects; prefer `Map` or `Object.create(null)` for
  user-keyed data.
- Use the platform crypto (**Web Crypto** / Node `crypto`) for hashing, random, and
  signatures. Use `crypto.randomUUID()` and `crypto.getRandomValues()` — never `Math.random()`
  for anything security-relevant.
- Keep secrets out of client bundles and out of source; load from environment/secret stores.
- Run `npm audit` / a supply-chain scanner in CI; pin versions with a lockfile and enable
  automated dependency updates with review.

## Examples

**Good Example** — text rendering, sanitized HTML, safe randomness

```js
// Untrusted comment rendered as text: the browser never interprets it as markup.
node.textContent = comment.body; // <img onerror=...> shows up as literal characters

// When HTML is genuinely required, sanitize with a maintained library.
import DOMPurify from "dompurify";
node.innerHTML = DOMPurify.sanitize(userHtml, { ALLOWED_TAGS: ["b", "i", "a"] });

// Security tokens use a CSPRNG, not Math.random (which is predictable).
const token = crypto.randomUUID();
```

**Bad Example** — injection, code-from-data, weak randomness

```js
node.innerHTML = comment.body;               // XSS: <script> / onerror runs immediately
const filter = eval("(" + req.query.f + ")"); // remote code execution from a URL param
const sessionId = Math.random().toString(36); // predictable → guessable session tokens
const merged = Object.assign({}, defaults, JSON.parse(body)); // __proto__ key pollutes prototype
```

## Common Mistakes

- Assigning untrusted strings to `innerHTML`/`outerHTML`/`insertAdjacentHTML`.
- Using `eval`, `new Function`, or string `setTimeout` on any external data.
- `Math.random()` for tokens, IDs, salts, or nonces.
- Concatenating user input into SQL, shell commands, or file paths.
- Merging untrusted JSON into objects without blocking `__proto__`/`constructor`.
- Shipping API keys or secrets inside the client bundle.
- Trusting a dependency tree with no lockfile, no audit, and no update process.
- Returning raw stack traces or internal error details to the client.

## Production Tips

- Enforce CSP in report-only mode first, review violations, then flip to enforcing.
- Add a secret scanner (e.g. gitleaks) to CI so credentials never reach the repo.
- Set security headers (`Strict-Transport-Security`, `X-Content-Type-Options`,
  `Referrer-Policy`) — a helper like `helmet` covers the defaults.
- Regenerate and rotate any secret that has ever touched a log or a client bundle.

## AI Review Checklist

- Is all untrusted data rendered as text, or sanitized with DOMPurify before `innerHTML`?
- Is there any `eval`/`new Function`/string `setTimeout` on external input?
- Are queries and commands parameterized rather than string-built from input?
- Is security-relevant randomness from Web Crypto / Node `crypto`, not `Math.random()`?
- Is untrusted object merging protected against prototype pollution?
- Are secrets kept out of the client bundle and out of source control?
- Are dependencies pinned with a lockfile and audited in CI?

## Related

- `knowledge/javascript/13-fetch-api.md`
- `knowledge/javascript/12-dom.md`
- `knowledge/javascript/14-error-handling.md`
- `knowledge/javascript/29-tooling.md`
- `knowledge/javascript/28-best-practices.md`
