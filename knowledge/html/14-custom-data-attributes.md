---
id: html/14-custom-data-attributes
topic: html
slug: custom-data-attributes
title: "Custom Data Attributes"
type: doc
order: 14
status: ready
tags: [html, custom-data-attributes, dataset, aria-expanded, textContent, innerHTML, data-testid, getAttribute]
related: [html/02-semantic-html, html/11-accessibility, html/19-security, html/27-html-apis]
when_to_use: "Read before stashing state or hooks on DOM elements with data-* attributes."
---
# Custom Data Attributes

## Purpose

This document defines how to use `data-*` attributes to attach custom, page-specific
data to HTML elements — and, just as important, when *not* to. It covers the naming
rules, the `dataset` DOM API, type handling, and the security and semantic boundaries
that keep `data-*` from becoming a dumping ground.

A `data-*` attribute is the standards-blessed way to store private application data on
an element without inventing non-standard attributes. It is a tool for wiring
JavaScript and CSS to markup — not a substitute for [semantic HTML](02-semantic-html.md)
or accessible [ARIA](11-accessibility.md) attributes.

## Why It Matters

`data-*` is convenient, so it gets abused. Teams reach for it to encode state that
belongs in ARIA (breaking accessibility), to smuggle secrets to the client (leaking
them), or to serialize whole objects into a string (creating a parsing minefield).
Every `data-*` value ships to the browser in plain text and is fully editable by the
user, so treating it as trusted or private is a bug. Getting the boundaries right keeps
markup honest, accessible, and safe.

## Core Principles

- **`data-*` is for custom data with no standard attribute.** If a native or ARIA
  attribute expresses the meaning (`hidden`, `aria-expanded`, `value`), use that first.
- **The value is always a string, and always untrusted.** It is client-visible and
  client-editable. Never store secrets; never trust it without validation.
- **Name in lowercase kebab-case.** `data-user-id` maps to `dataset.userId`. Uppercase
  in the attribute name is invalid and mangles the `dataset` key.
- **Keep values small and flat.** `data-*` holds identifiers and flags, not serialized
  objects. Large JSON blobs belong in a `<script type="application/json">` payload.
- **Data, not behavior or presentation state.** Toggle real state through ARIA and
  classes; use `data-*` as a stable hook or to carry a value, not as the source of truth
  for accessibility.

## Best Practices

- Read and write via the `dataset` API (`el.dataset.userId`), not
  `getAttribute("data-user-id")` — it is the intended interface and handles the
  kebab-to-camel mapping for you.
- Parse types explicitly on read: `Number(el.dataset.count)`, `el.dataset.active ===
  "true"`. The DOM gives you strings; convert deliberately.
- Prefix hooks used only by JavaScript so intent is obvious, e.g. `data-testid` for
  tests or `data-js-toggle` for behavior wiring — and never style off them if they may
  change.
- For larger structured payloads, embed JSON in `<script type="application/json">` and
  `JSON.parse` its `textContent`, rather than stuffing JSON into an attribute.
- Treat any `data-*` value that will be inserted into the DOM as untrusted input:
  set it with `textContent`, never `innerHTML`, to avoid XSS.
- Use `[data-state="open"]` style attribute selectors in CSS for variant styling when a
  class would proliferate — but drive real widget state through ARIA in parallel.

## Examples

**Good Example** — small values, typed reads, safe rendering

```html
<button class="row" data-user-id="42" data-role="admin">Jane</button>

<script>
  const btn = document.querySelector(".row");
  const id = Number(btn.dataset.userId);      // string → number, explicit
  const isAdmin = btn.dataset.role === "admin";
  // Render via textContent so the value can't inject markup:
  status.textContent = `User ${id}${isAdmin ? " (admin)" : ""}`;
</script>
```

**Bad Example** — secrets, big blobs, ARIA replaced by data

```html
<!-- Secret shipped to the client in plain text; anyone can read/edit it -->
<div data-api-key="sk_live_9f3..."
     data-user='{"id":42,"perms":["read","write","delete"]}'  <!-- JSON in an attr -->
     data-expanded="true">                                     <!-- should be ARIA -->
  ...
</div>

<script>
  // Fragile hand-parse; no validation; screen readers never learn it's expanded
  const perms = JSON.parse(div.getAttribute("data-user")).perms;
  panel.innerHTML = div.dataset.expanded;   // innerHTML with untrusted value → XSS risk
</script>
```

The fix: drop the API key entirely (keep secrets server-side), replace `data-expanded`
with `aria-expanded`, and move the JSON into a `<script type="application/json">` block.

## Common Mistakes

- Storing secrets, tokens, or internal IDs you assumed were hidden — nothing in HTML is.
- Using `data-*` where an ARIA state (`aria-expanded`, `aria-selected`) is required,
  so assistive tech never learns the state changed.
- Cramming serialized JSON into an attribute and hand-parsing it fragilely.
- Forgetting values are strings, so `if (el.dataset.count)` treats `"0"` as truthy.
- Rendering a `data-*` value with `innerHTML`, opening an XSS hole.
- Uppercase or camelCase in the attribute name (`data-userId`), which does not round-
  trip through `dataset`.

## Production Tips

- Adopt a convention: reserve `data-testid` for test hooks and keep it out of styling
  and logic, so refactors do not break tests or vice versa.
- Lint for `data-*` attributes containing anything key- or token-shaped in your build to
  catch accidental secret exposure.
- When migrating from framework-specific attributes, prefer standard `data-*` so the
  markup stays portable across tooling.

## AI Review Checklist

- Is `data-*` used only where no standard/ARIA attribute fits?
- Are all values small identifiers or flags, not secrets or serialized objects?
- Are values read via `dataset` and type-converted explicitly on use?
- Is real widget/accessibility state expressed with ARIA, not `data-*`?
- Are `data-*` values rendered with `textContent`, never `innerHTML`?
- Are attribute names lowercase kebab-case so they map cleanly to `dataset`?

## Related

- `knowledge/html/02-semantic-html.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/19-security.md`
- `knowledge/html/27-html-apis.md`
