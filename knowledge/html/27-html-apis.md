---
id: html/27-html-apis
topic: html
slug: html-apis
title: "HTML APIs"
type: doc
order: 27
status: ready
tags: [html, html-apis, IntersectionObserver, localStorage, showModal, querySelectorAll, getElementById, addEventListener]
related: [html/25-web-components, html/09-media, html/17-canvas, html/18-performance, html/19-security]
when_to_use: "Read before using a browser HTML/DOM API (drag-and-drop, storage, observers, dialog, etc.)."
---
# HTML APIs

## Purpose

This document covers the JavaScript APIs the HTML standard exposes for interacting with
the document and the browser: the `<dialog>` element, `<details>`, Drag-and-Drop, Web
Storage, the observer family (Intersection/Mutation/Resize), History, Clipboard, and the
constraint-validation API on forms. These turn static markup into behavior. The goal is
to use the native platform capability instead of reimplementing it, and to use each API
with its correct lifecycle and permission model.

## Why It Matters

The platform already ships accessible, performant implementations of things teams
routinely rebuild badly: modal dialogs with focus trapping (`<dialog>`), lazy loading
(`IntersectionObserver`), and form validation (constraint validation). A hand-rolled
modal usually leaks focus to the background; a scroll handler that a single
`IntersectionObserver` would replace can jank the main thread. Choosing the native API
buys correctness, accessibility, and performance for free — and misusing one (unbounded
`localStorage`, observers never disconnected) introduces leaks and security holes just as
easily.

## Core Principles

- **Prefer the native element over the scripted clone.** `<dialog>`, `<details>`, and
  the constraint-validation API give you accessibility and keyboard behavior that a
  `<div>` rebuild will miss.
- **Observers are cheaper than event loops.** `IntersectionObserver`/`ResizeObserver`
  batch off the main thread; replace `scroll`/`resize` polling with them.
- **Every observer and listener has an owner responsible for disconnecting it.** Leaks
  come from observers and listeners that outlive their target node.
- **Storage is a cache, never a source of truth for secrets.** `localStorage` is
  synchronous, unencrypted, and readable by any script — never store tokens or PII there.
- **Respect the permission and gesture requirements.** Clipboard, fullscreen, and
  notifications require a user gesture and/or granted permission; don't fight the model.

## Best Practices

- Open modals with `dialog.showModal()` — it traps focus, renders the `::backdrop`, and
  closes on `Esc`; add a form with `method="dialog"` so buttons return a value.
- Use `IntersectionObserver` for lazy-loading, infinite scroll, and reveal-on-scroll;
  set `rootMargin`/`threshold` deliberately and `disconnect()` when done.
- Use `MutationObserver` for reacting to DOM changes, but scope it tightly (`childList`,
  `subtree` only as needed) — broad observers fire constantly.
- Drive form UX with constraint validation: `input.validity`, `setCustomValidity()`, and
  `form.checkValidity()` instead of ad-hoc regex-in-onclick.
- Use `history.pushState`/`replaceState` for client routing and always handle
  `popstate`; keep URLs shareable and the back button working.
- Read/write the clipboard via the async `navigator.clipboard` API inside a click
  handler; feature-detect and provide a fallback.
- Prefer `structuredClone()` over `JSON.parse(JSON.stringify())` for deep copies.

## Examples

**Good Example** — native dialog + a lazy-load observer that cleans up

```html
<dialog id="confirm">
  <!-- method="dialog" makes the button close the dialog and set returnValue -->
  <form method="dialog">
    <p>Delete this item?</p>
    <button value="cancel">Cancel</button>
    <button value="ok">Delete</button>
  </form>
</dialog>

<script>
// showModal() traps focus, renders a backdrop, and wires Esc — for free
document.getElementById("open").addEventListener("click", () =>
  document.getElementById("confirm").showModal());

// one observer replaces a scroll handler; it batches work off the main thread
const io = new IntersectionObserver((entries, obs) => {
  for (const e of entries) {
    if (!e.isIntersecting) continue;
    e.target.src = e.target.dataset.src;
    obs.unobserve(e.target);           // stop watching images already loaded
  }
}, { rootMargin: "200px" });
document.querySelectorAll("img[data-src]").forEach(img => io.observe(img));
</script>
```

**Bad Example** — hand-rolled modal and a leaking scroll loop

```html
<!-- a div modal: no focus trap, no Esc, invisible to screen readers as a dialog -->
<div class="modal" style="position:fixed; inset:0;">Delete this item?</div>

<script>
// runs on every scroll frame, on the main thread → jank; never removed → leak
window.addEventListener("scroll", () => {
  document.querySelectorAll("img[data-src]").forEach(img => {
    if (img.getBoundingClientRect().top < innerHeight) img.src = img.dataset.src;
  });
});
// auth token in localStorage: synchronous, unencrypted, stealable by any XSS
localStorage.setItem("token", authToken);
</script>
```

## Common Mistakes

- Rebuilding a modal from a `<div>` instead of `<dialog>`, losing focus trapping and
  keyboard/`Esc` handling.
- Polling `scroll`/`resize` where a single `IntersectionObserver`/`ResizeObserver` would
  batch the work off-thread.
- Creating observers or listeners and never calling `disconnect()`/`removeEventListener`,
  leaking memory when nodes are removed.
- Storing tokens, sessions, or PII in `localStorage`/`sessionStorage`.
- Calling clipboard, fullscreen, or notification APIs outside a user gesture and getting
  a silent rejection.
- Reimplementing form validation instead of using the constraint-validation API.

## Production Tips

- Feature-detect newer APIs (`if ("showModal" in dialog)`) and provide graceful
  fallbacks; not every embedded webview is current.
- Disconnect observers in component teardown (`disconnectedCallback`, effect cleanup) to
  avoid leaks in long-lived SPAs.
- Wrap storage access in a small module that JSON-serializes, guards quota errors, and
  namespaces keys — raw `localStorage` calls scattered everywhere rot fast.
- Keep client-routing URLs meaningful so deep links and the back/forward buttons work.

## AI Review Checklist

- Are modals built on `<dialog>`/`showModal()` rather than a scripted `<div>`?
- Are scroll/resize behaviors implemented with observers, not per-frame event handlers?
- Is every observer and listener disconnected/removed when its target is gone?
- Is `localStorage`/`sessionStorage` free of tokens, credentials, and PII?
- Do clipboard/fullscreen/notification calls happen inside a user gesture?
- Is form validation using the constraint-validation API where possible?
- Are new APIs feature-detected with a fallback path?

## Related

- `knowledge/html/25-web-components.md`
- `knowledge/html/09-media.md`
- `knowledge/html/17-canvas.md`
- `knowledge/html/18-performance.md`
- `knowledge/html/19-security.md`
