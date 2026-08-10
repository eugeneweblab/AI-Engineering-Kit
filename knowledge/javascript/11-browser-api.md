---
id: javascript/11-browser-api
topic: javascript
slug: browser-api
title: "Browser API"
type: doc
order: 11
status: ready
tags: [javascript, browser-api, IntersectionObserver, sessionStorage, localStorage, setInterval, setItem, URL, observers, global, timers]
related: [javascript/12-dom, javascript/13-fetch-api, javascript/26-security, javascript/27-browser-performance]
when_to_use: "Read before using Web Storage, timers, observers, Web Workers, or any global browser API."
---
# Browser API

## Purpose

This document defines how to use the platform APIs the browser exposes to JavaScript
— `localStorage`/`sessionStorage`, timers, `URL`, observers (`Intersection`,
`Resize`, `Mutation`), Web Workers, and geolocation/notifications — safely and
without leaking resources. It complements [DOM](12-dom.md) and [fetch](13-fetch-api.md),
and is written so an agent can call browser globals without breaking security, memory,
or feature-detection expectations.

Browser APIs run in an untrusted, user-controlled environment across dozens of engine
versions. Assume any given API may be missing, denied, quota-limited, or observed by
hostile scripts.

## Why It Matters

Browser APIs touch the user's device, data, and privacy, so misuse has consequences
beyond a wrong value. Storing a token in `localStorage` exposes it to every XSS on the
page. An observer or interval you never disconnect leaks memory and keeps firing after
the component is gone. Assuming an API exists crashes the whole script on browsers or
contexts where it does not (private mode, older engines, non-secure origins). Because
the environment is the user's, not yours, defensive use is mandatory, not optional.

## Core Principles

- **Feature-detect, never assume.** Check `"IntersectionObserver" in window` or
  `navigator.geolocation` before use. The environment is not yours to control.
- **Web Storage is synchronous, string-only, and origin-scoped.** It blocks the main
  thread and holds no secrets — never store tokens or PII there.
- **Every subscription must be cleaned up.** Timers, observers, and event listeners
  you create must be cleared/disconnected, or they leak and keep firing.
- **Powerful APIs require permission and a secure context.** Geolocation,
  notifications, clipboard, and more need HTTPS and explicit user grant, and can be denied.
- **Heavy work belongs off the main thread.** Use Web Workers so the UI stays
  responsive (see [event-loop](10-event-loop.md)).

## Best Practices

- Prefer `sessionStorage` over `localStorage` for transient data, and store only
  non-sensitive, serializable values. Wrap access in `try/catch` — quota errors and
  disabled storage (private mode) throw.
- Always keep the handle returned by `setTimeout`/`setInterval` and call
  `clearTimeout`/`clearInterval` on teardown. Uncleared intervals are a classic leak.
- Use `IntersectionObserver` for visibility/lazy-loading and `ResizeObserver` for
  size changes instead of scroll/resize listeners with manual math — they are cheaper
  and fire off the main thread. `disconnect()` them when done.
- Use the `URL` and `URLSearchParams` constructors to build and parse URLs; never
  concatenate query strings by hand (encoding bugs, injection).
- Request permissions lazily, in response to a user gesture, and handle denial as a
  normal path — not an error. Check `navigator.permissions.query` where supported.
- Offload CPU-heavy parsing/crypto to a Web Worker; pass data with structured clone or
  transferables, not by blocking the UI thread.

## Examples

**Good Example** — feature detection, guarded storage, cleanup

```js
// Guarded storage: private mode and quota limits throw — do not crash the app.
function saveDraft(key, value) {
  try {
    sessionStorage.setItem(key, JSON.stringify(value)); // transient, non-sensitive only
  } catch {
    /* storage full or disabled — degrade gracefully, do not throw */
  }
}

// Lazy-load images with IntersectionObserver, and disconnect when finished.
function lazyLoad(images) {
  if (!("IntersectionObserver" in window)) {            // feature-detect
    images.forEach((img) => (img.src = img.dataset.src)); // fallback: load all
    return;
  }
  const io = new IntersectionObserver((entries, obs) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.src = entry.target.dataset.src;
      obs.unobserve(entry.target);                       // stop watching loaded images
    }
  });
  images.forEach((img) => io.observe(img));
  return () => io.disconnect();                          // caller cleans up on teardown
}
```

**Bad Example** — token in localStorage, leaked interval, no detection

```js
// XSS-readable secret storage: any injected script can steal this token.
localStorage.setItem("authToken", token);

// Interval is never cleared: it keeps polling forever, even after the view is gone,
// leaking memory and hammering the server.
setInterval(() => {
  navigator.geolocation.getCurrentPosition(sendLocation); // assumes it exists + is granted
}, 5000);
// no feature detection, no permission handling, no clearInterval
```

## Common Mistakes

- Storing tokens, secrets, or PII in `localStorage`/`sessionStorage` (readable by XSS).
- Never clearing `setInterval`/`setTimeout` or disconnecting observers, leaking memory.
- Assuming an API exists instead of feature-detecting, crashing on unsupported contexts.
- Treating permission denial (geolocation, notifications) as an error instead of a path.
- Building URLs by string concatenation, causing encoding and injection bugs.
- Doing heavy CPU work on the main thread instead of a Web Worker.
- Ignoring that Web Storage is synchronous and blocks the thread on large writes.

## Production Tips

- Store auth tokens in `HttpOnly` cookies, not Web Storage — see the security docs.
- Prefer observer APIs over `scroll`/`resize` listeners; if you must listen, throttle
  and use `{ passive: true }` for scroll to avoid blocking the compositor.
- Wrap all Web Storage access behind a small typed helper with `try/catch`, so quota
  and private-mode failures are handled in one place.

## AI Review Checklist

- Is any sensitive data stored in `localStorage`/`sessionStorage`? (It must not be.)
- Are all timers cleared and all observers/listeners disconnected on teardown?
- Is every non-baseline API feature-detected before use?
- Are permissioned APIs requested on a user gesture, with denial handled gracefully?
- Are URLs built with `URL`/`URLSearchParams` rather than string concatenation?
- Is CPU-heavy work moved to a Web Worker to keep the main thread responsive?
- Is Web Storage access wrapped in `try/catch` for quota and private-mode failures?

## Related

- `knowledge/javascript/12-dom.md`
- `knowledge/javascript/13-fetch-api.md`
- `knowledge/javascript/26-security.md`
- `knowledge/javascript/27-browser-performance.md`
