---
id: html/25-web-components
topic: html
slug: web-components
title: "Web Components"
type: doc
order: 25
status: ready
tags: [html, web-components]
related: [html/02-semantic-html, html/27-html-apis, html/11-accessibility, html/23-progressive-enhancement, html/14-custom-data-attributes]
when_to_use: "Read before authoring or reviewing a Custom Element, Shadow DOM, or <template>-based component."
---
# Web Components

## Purpose

This document defines how to build reusable, framework-agnostic UI using the native Web
Components platform: Custom Elements, Shadow DOM, `<template>`, and slots. These are
browser standards, not a library — a well-built component works unchanged in React, Vue,
plain HTML, or no framework at all. The goal is components that encapsulate their markup
and styles without leaking into or breaking the surrounding page.

## Why It Matters

Component code outlives the framework it was born in. A Custom Element written against
the platform survives framework churn, ships without a runtime, and cannot have its
styles clobbered by a global stylesheet because Shadow DOM scopes them. But the same
encapsulation that protects you also hides content from the accessibility tree and the
page's forms if you use it carelessly. Web Components reward correct use with durability
and punish careless use with invisible, inaccessible widgets.

## Core Principles

- **Name custom elements with a hyphen.** The spec requires `<my-widget>`, never
  `<widget>`; the hyphen is how the parser distinguishes custom from built-in elements.
- **Upgrade, don't assume.** An element may be parsed before its class is defined. Read
  attributes in `connectedCallback`, and reflect state via `observedAttributes` +
  `attributeChangedCallback`, so the element works however it is created.
- **Encapsulate with Shadow DOM, but keep the boundary permeable where it must be.**
  Shadow styles don't leak out or in; use `<slot>` for user content and CSS custom
  properties + `::part()` for intentional theming hooks.
- **Degrade without JavaScript.** Render meaningful light-DOM content so the component is
  usable before (or if) its script runs — progressive enhancement, not replacement.
- **Preserve accessibility across the shadow boundary.** Put ARIA roles and focus
  management inside the component; the boundary is invisible to assistive tech only if
  you wire it correctly.

## Best Practices

- Define elements with `customElements.define("my-widget", MyWidget)` and guard against
  double registration if the script can load twice.
- Attach shadow roots as `{ mode: "open" }` unless you have a concrete reason to hide the
  internals; `open` keeps the component debuggable and testable.
- Clone from a `<template>` instead of setting `innerHTML` per instance — the template is
  parsed once and cloning is cheaper and safer.
- Use lifecycle callbacks for their intended job: `connectedCallback` for setup and
  listeners, `disconnectedCallback` to remove listeners and prevent leaks.
- Expose theming via CSS custom properties and `::part()`, not by asking consumers to
  reach into shadow internals.
- For form controls, use `ElementInternals` (`formAssociated = true`) so the element
  participates in form submission and validation like a native input.
- Never `innerHTML` untrusted input inside a component; sanitize or use text nodes.

## Examples

**Good Example** — hyphenated name, template clone, cleanup, theming hook

```html
<template id="counter-tpl">
  <style>
    /* :host styles the element itself; --accent lets consumers theme it */
    button { color: var(--accent, #06c); }
  </style>
  <button part="btn"><slot>Count</slot>: <span id="n">0</span></button>
</template>

<script>
class CounterButton extends HTMLElement {
  connectedCallback() {
    if (!this.shadowRoot) {                       // upgrade-safe: only build once
      const tpl = document.getElementById("counter-tpl");
      this.attachShadow({ mode: "open" })         // open: inspectable in devtools
          .append(tpl.content.cloneNode(true));   // clone template, don't re-parse HTML
    }
    this._onClick = () => this._bump();
    this.shadowRoot.querySelector("button").addEventListener("click", this._onClick);
  }
  disconnectedCallback() {                        // remove listener to avoid a leak
    this.shadowRoot.querySelector("button").removeEventListener("click", this._onClick);
  }
  _bump() { this.shadowRoot.getElementById("n").textContent = ++this._c || (this._c = 1); }
}
customElements.define("counter-button", CounterButton); // hyphen is required
</script>
```

**Bad Example** — invalid name, no encapsulation, leaks and unstyleable

```html
<script>
// no hyphen: browser rejects this as a custom element name
class Counter extends HTMLElement {
  connectedCallback() {
    // innerHTML on the host wipes any slotted content and re-parses every insert
    this.innerHTML = `<button>Count: <span>0</span></button>`;
    // listener is never removed → memory leak when the node is detached
    this.querySelector("button").addEventListener("click", () => {});
  }
}
customElements.define("counter", Counter); // throws: "counter" has no hyphen
</script>
```

## Common Mistakes

- Naming a custom element without a hyphen, so `customElements.define` throws.
- Reading attributes in the constructor before the element is connected/upgraded.
- Setting `innerHTML` per instance instead of cloning a parsed `<template>`.
- Adding event listeners in `connectedCallback` but never removing them, leaking memory.
- Trapping content and controls inside Shadow DOM without ARIA/focus wiring, breaking
  screen readers and forms.
- Rendering nothing without JS, so the component is a blank box on slow or failed loads.

## Production Tips

- Ship a light-DOM fallback and enhance; SSR/hydration frameworks can pre-render the
  slotted content so first paint is not empty.
- Prefer `ElementInternals` over hidden `<input>` hacks for form-associated controls.
- Keep component CSS inside the shadow root; expose only a documented set of custom
  properties and parts so theming stays a stable contract.
- Test in isolation with the shadow root in `open` mode so tests can query internals.

## AI Review Checklist

- Does every custom element name contain a hyphen?
- Are attributes read in `connectedCallback`/`attributeChangedCallback`, not the constructor?
- Is markup cloned from a `<template>` rather than assigned via `innerHTML` per instance?
- Are listeners added in `connectedCallback` removed in `disconnectedCallback`?
- Is theming exposed through CSS custom properties / `::part()`, not internal reach-in?
- Do slotted content and focus/ARIA survive the shadow boundary for assistive tech?
- Is untrusted content sanitized before it enters the component?

## Related

- `knowledge/html/02-semantic-html.md`
- `knowledge/html/27-html-apis.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/23-progressive-enhancement.md`
- `knowledge/html/14-custom-data-attributes.md`
