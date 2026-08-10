---
id: javascript/12-dom
topic: javascript
slug: dom
title: "Dom"
type: doc
order: 12
status: ready
tags: [javascript, dom, innerHTML, getElementById, insertAdjacentHTML, querySelectorAll, textContent, AbortController, creates, nodes, mutates]
related: [javascript/11-browser-api, javascript/13-fetch-api, javascript/26-security, javascript/27-browser-performance, javascript/15-memory-management]
when_to_use: "Read before writing or reviewing any code that reads, creates, or mutates DOM nodes in the browser."
---
# Dom

## Purpose

This document defines how to work with the Document Object Model — selecting nodes,
mutating them, handling events, and inserting untrusted data — so an agent can build UI
code that is safe, correct, and fast. The DOM is a live tree of objects the browser
renders; every read and write here crosses from JavaScript into layout and paint, which
is where correctness bugs and performance cliffs both live.

## Why It Matters

The DOM is the single largest source of two problem classes: **XSS** (injecting HTML
from untrusted data) and **layout thrash** (forcing the browser to recompute geometry
in a loop). Both are invisible in a code review that only reads logic — the app works on
the developer's machine and fails in production under real data or real volume. A single
`innerHTML =` with a user-controlled string is a full account-takeover vector; a single
`offsetHeight` read inside a write loop turns a 10ms update into 2 seconds. Treat DOM
code as the boundary between your trusted logic and a hostile, expensive rendering
engine.

## Core Principles

- **Never inject untrusted data as HTML.** Use `textContent`, `setAttribute`, or DOM
  node creation. `innerHTML`, `outerHTML`, and `insertAdjacentHTML` parse markup and run
  scripts/handlers — they are XSS sinks.
- **Read then write, never interleave.** Batch all layout reads, then all writes.
  Interleaving forces synchronous reflow ("layout thrashing") on every iteration.
- **Query once, reuse the reference.** Repeated `querySelector` calls re-walk the tree.
  Cache the node in a variable.
- **Prefer declarative frameworks for complex UI.** Hand-written DOM mutation is
  error-prone; use it for widgets, glue, and hot paths, not entire applications.
- **Clean up what you create.** Every `addEventListener`, observer, or interval tied to a
  removed node must be removed too, or it leaks (see memory management).

## Best Practices

- Select with `querySelector`/`querySelectorAll` for flexibility, or `getElementById`
  for the fastest single lookup on a known id.
- Insert user data with `textContent` (escaped, plain text) or `node.append(string)`,
  never `innerHTML`. If you must render HTML, sanitize with a vetted library (DOMPurify)
  or the Sanitizer API first.
- Build subtrees off-DOM with `document.createElement` + a `DocumentFragment`, then
  insert once. One reflow instead of N.
- Use **event delegation**: attach one listener to a stable ancestor and read
  `event.target`, instead of N listeners on N children. Fewer listeners, works for
  dynamically added nodes.
- Batch visual work with `requestAnimationFrame`; observe visibility/size with
  `IntersectionObserver`/`ResizeObserver` instead of polling in `scroll`/`resize`.
- Use `classList.toggle`/`.add`/`.remove` and `dataset` rather than string-concatenating
  `className` or parsing attributes by hand.
- Prefer `element.closest(selector)` to manual parent-walking, and `AbortController` to
  remove groups of listeners at once.

## Examples

**Good Example** — safe text, off-DOM build, one insertion, delegated events

```js
const list = document.getElementById("results"); // cached once

function render(items) {
  const frag = document.createDocumentFragment(); // build off-DOM
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item.name;       // untrusted data as TEXT, never HTML → no XSS
    li.dataset.id = item.id;          // structured data via dataset, not innerHTML
    frag.append(li);
  }
  list.replaceChildren(frag);         // single reflow, not one per item
}

// One delegated listener handles every current AND future <li>.
list.addEventListener("click", (e) => {
  const li = e.target.closest("li");
  if (li) open(li.dataset.id);
});
```

**Bad Example** — HTML injection and layout thrash

```js
function render(items) {
  const list = document.getElementById("results");
  list.innerHTML = "";                       // re-queried each call is minor; the next line is fatal
  for (const item of items) {
    // item.name is user data parsed as HTML → <img onerror=...> runs. XSS.
    list.innerHTML += `<li>${item.name}</li>`; // also re-parses the whole list every iteration
    console.log(list.offsetHeight);            // read after write, inside loop → forced reflow each pass
  }
}
```

## Common Mistakes

- Assigning untrusted strings to `innerHTML`/`insertAdjacentHTML` — the top XSS sink.
- Reading layout properties (`offsetTop`, `getBoundingClientRect`, `scrollHeight`) inside
  a mutation loop, forcing a reflow per iteration.
- Adding a listener per element instead of delegating, then leaking them when nodes are
  removed without `removeEventListener`.
- Calling `querySelectorAll` repeatedly in a hot path instead of caching the result.
- Mutating the DOM directly inside a framework (React/Vue) it also controls, causing
  desync.
- Forgetting that `querySelectorAll` returns a static `NodeList` while `children` /
  `getElementsByClassName` are live — iterating a live collection while mutating it skips
  nodes.

## Production Tips

- Wrap third-party HTML in DOMPurify with an explicit allowlist; re-sanitize after any
  transform, not just on input.
- Debounce/throttle `scroll`, `resize`, `input`, and `mousemove` handlers, or move the
  work to `requestAnimationFrame`.
- Use `AbortController` to tear down all of a component's listeners on unmount in one
  call: `addEventListener(type, fn, { signal })`.

## AI Review Checklist

- Is any untrusted value assigned to `innerHTML`, `outerHTML`, or `insertAdjacentHTML`?
- Are user-supplied strings inserted as `textContent`, or sanitized before HTML render?
- Are layout reads separated from writes, not interleaved in a loop?
- Are repeated queries cached, and subtrees built off-DOM before insertion?
- Is event delegation used instead of per-element listeners for dynamic lists?
- Is every listener/observer removed when its node is removed (`AbortController`/cleanup)?

## Related

- `knowledge/javascript/11-browser-api.md`
- `knowledge/javascript/13-fetch-api.md`
- `knowledge/javascript/26-security.md`
- `knowledge/javascript/27-browser-performance.md`
- `knowledge/javascript/15-memory-management.md`
