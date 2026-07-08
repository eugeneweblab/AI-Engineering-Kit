---
id: javascript/13-fetch-api
topic: javascript
slug: fetch-api
title: "Fetch API"
type: doc
order: 13
status: ready
tags: [javascript, fetch-api]
related: [javascript/08-asynchronous-javascript, javascript/09-promises, javascript/14-error-handling, javascript/26-security, javascript/11-browser-api]
when_to_use: "Read before writing or reviewing any code that makes HTTP requests with fetch()."
---
# Fetch API

## Purpose

This document defines how to make HTTP requests with `fetch` — checking status, parsing
bodies, handling errors, setting timeouts, and cancelling — so an agent writes network
code that fails loudly and predictably instead of silently swallowing errors. `fetch` is
the standard Promise-based HTTP client in browsers and Node 18+; its ergonomics have one
sharp edge that causes most bugs, covered below.

## Why It Matters

`fetch` does **not reject on HTTP error status.** A `404`, `500`, or `403` resolves the
Promise successfully — `response.ok` is the only signal. Code that does
`const data = await (await fetch(url)).json()` will happily parse an error page's JSON or
throw a confusing parse error, then propagate garbage downstream. The failure surfaces
far from its cause, as a null render or a corrupt write, making it expensive to debug.
Network code also runs against the real world: it times out, gets cancelled, returns
partial data, and carries security implications (credentials, CORS, injected URLs).
Every one of these must be handled deliberately.

## Core Principles

- **A resolved Promise is not a successful request.** Always check `response.ok` (or
  `response.status`) before reading the body. Only network failures and aborts reject.
- **Match the parser to the response.** `.json()`, `.text()`, `.blob()` each consume the
  body once. Choose based on `Content-Type`, and never read the body twice.
- **Every request needs a timeout.** `fetch` has no default timeout; a hung server hangs
  your code forever. Use `AbortSignal.timeout(ms)`.
- **Make requests cancellable.** Tie in-flight requests to an `AbortController` so stale
  requests (unmounted component, superseded search) can be dropped.
- **Never build URLs or bodies by string concatenation of untrusted input.** Use
  `URL`/`URLSearchParams` and structured JSON to avoid injection and encoding bugs.

## Best Practices

- Centralize fetching in one wrapper that checks `res.ok`, throws a typed error with
  status and URL, applies a timeout, and parses the body. Call the wrapper everywhere.
- Set `Content-Type: application/json` and `JSON.stringify` the body for JSON APIs; read
  the response `Content-Type` before choosing a parser.
- Use `AbortSignal.timeout(ms)` for a hard deadline and pass a shared `signal` for
  caller-driven cancellation (combine with `AbortSignal.any([...])`).
- Control credentials explicitly: `credentials: "same-origin"` by default,
  `"include"` only for trusted cross-origin APIs that need cookies.
- Distinguish error classes for retry: retry idempotent requests on network errors and
  `5xx`/`429` with backoff; never blindly retry `4xx` or non-idempotent writes.
- Read `response.status` for control flow (`401` → re-auth, `429` → back off), not just a
  boolean.
- In Node, prefer the built-in `fetch` (Undici); avoid pulling in `node-fetch` unless you
  need a feature it lacks.

## Examples

**Good Example** — status check, timeout, typed error, cancellation

```js
class HttpError extends Error {
  constructor(res) {
    super(`HTTP ${res.status} for ${res.url}`);
    this.status = res.status; // callers can branch on 401/429/etc.
  }
}

async function getJson(url, { signal } = {}) {
  const res = await fetch(url, {
    headers: { Accept: "application/json" },
    // Hard 10s deadline AND caller cancellation, combined:
    signal: signal ? AbortSignal.any([signal, AbortSignal.timeout(10_000)])
                   : AbortSignal.timeout(10_000),
  });
  if (!res.ok) throw new HttpError(res); // resolved != success — must check
  return res.json();                     // body read exactly once
}

// URLSearchParams encodes untrusted input safely — no manual concatenation.
const url = new URL("/search", API);
url.searchParams.set("q", userQuery);
const data = await getJson(url);
```

**Bad Example** — no status check, no timeout, double-read, injection

```js
async function getJson(query) {
  // Untrusted query concatenated into the URL → breaks on `&`, `#`, spaces; injectable.
  const res = await fetch("https://api.example.com/search?q=" + query);
  // No res.ok check: a 500 HTML error page reaches .json() and throws a cryptic
  // "Unexpected token <" far from the real cause. No timeout: a hung server hangs forever.
  const data = await res.json();
  console.log(await res.text()); // body already consumed → throws "body already read"
  return data;
}
```

## Common Mistakes

- Treating a resolved Promise as success and skipping the `response.ok` check.
- No timeout, so a slow or dead endpoint leaves the request (and UI) hung indefinitely.
- Reading the body twice (`.json()` then `.text()`) — the stream is already consumed.
- Concatenating untrusted values into URLs instead of using `URL`/`URLSearchParams`.
- Retrying non-idempotent writes on timeout, causing duplicate side effects.
- Swallowing `AbortError` as a real failure — an intentional cancel is not an error to
  report to the user.
- Setting `credentials: "include"` broadly, leaking cookies to untrusted origins.

## Production Tips

- Log failed requests with method, URL, status, and duration — never the auth header or
  request body containing secrets.
- Add jittered exponential backoff for retries; honor the `Retry-After` header on `429`.
- Use `AbortController` per user action (search-as-you-type) so only the latest request's
  result is applied, preventing out-of-order responses overwriting newer data.

## AI Review Checklist

- Is `response.ok` (or `status`) checked before the body is read?
- Does every request have a timeout via `AbortSignal.timeout`?
- Is the body read exactly once with the parser matching `Content-Type`?
- Are URLs and query strings built with `URL`/`URLSearchParams`, not concatenation?
- Are only idempotent requests retried, with backoff, and `AbortError` handled distinctly?
- Is `credentials` set intentionally, not left permissive for cross-origin calls?

## Related

- `knowledge/javascript/08-asynchronous-javascript.md`
- `knowledge/javascript/09-promises.md`
- `knowledge/javascript/14-error-handling.md`
- `knowledge/javascript/26-security.md`
- `knowledge/javascript/11-browser-api.md`
