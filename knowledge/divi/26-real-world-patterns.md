---
id: divi/26-real-world-patterns
topic: divi
slug: real-world-patterns
title: "Real World Patterns"
type: doc
order: 26
status: ready
tags: [divi, real-world-patterns]
related: [divi/02-theme-builder, divi/07-dynamic-content, divi/14-woocommerce, divi/15-custom-fields, divi/09-custom-css]
when_to_use: "Read when implementing a common Divi feature (dynamic archive, mega menu, pricing table, gated content) to use the proven approach instead of improvising."
---
# Real World Patterns

## Purpose

This document catalogs recurring build patterns that appear on almost every real Divi
project and the correct way to implement each. These are the situations where an agent is
most tempted to improvise with raw HTML or a plugin, and where doing so produces the most
maintenance pain. Each pattern names the right Divi primitive to reach for and why.

Where [best-practices](24-best-practices.md) gives general rules, this doc gives concrete
recipes for specific, repeated jobs.

## Why It Matters

The same handful of requirements — a dynamic blog archive, a mega menu, a repeatable card
grid, gated content, a global CTA — come up on nearly every client site. Solved with the
right Divi feature, they are one change to update and survive theme updates. Solved with
pasted HTML or a redundant plugin, they multiply weight and break the moment a client edits
them. Knowing the canonical pattern is what keeps a build consistent and fast.

## Core Principles

- **Reach for the Divi primitive first.** Theme Builder templates, dynamic content, presets,
  and global modules solve most patterns without custom code or plugins.
- **Bind to data, don't hard-code it.** Post titles, prices, and fields should come from
  [dynamic-content](07-dynamic-content.md) and [custom-fields](15-custom-fields.md), so one
  source of truth drives every display.
- **Template the repeatable, not the page.** If a design repeats across posts/products, it
  belongs in a Theme Builder template, not copied per page.
- **Keep custom code minimal and enqueued.** When Divi genuinely can't do it, add a small
  child-theme snippet — not a Code module full of markup.

## Best Practices

- **Dynamic post/archive layouts:** build them in the [Theme Builder](02-theme-builder.md)
  with a Blog or Post module bound to [dynamic content](07-dynamic-content.md) — never one
  static page per post.
- **Mega menus / complex navigation:** use Divi's built-in menu module or a Theme Builder
  header template; avoid pasting nav HTML that bypasses WordPress menus and breaks a11y.
- **Repeatable card grids (team, services, testimonials):** style one module as a preset,
  place it in a row, and duplicate the row — a preset change restyles all cards at once.
- **Custom fields / ACF data:** map fields via dynamic content into modules so editors update
  data in the field, not the layout. See [custom-fields](15-custom-fields.md).
- **WooCommerce product/shop templates:** build them in the Theme Builder with Woo modules
  bound to product data, not hand-built product pages. See [woocommerce](14-woocommerce.md).
- **Global CTA / banner:** save it as a global module or Theme Builder block so one edit
  updates every placement.
- **Conditional/gated content:** use Theme Builder display conditions or a membership plugin's
  logic — not client-side JS that hides content already sent to the browser.

## Examples

**Good Example** — a card grid driven by one preset and dynamic data

```
Theme Builder "Services" template:
  Section
    Row (3 columns)
      Blurb module ← styled by preset "Service Card"
        Title  = Dynamic Content: Post Title
        Body   = Dynamic Content: Excerpt
        Image  = Dynamic Content: Featured Image

// WHY: the Blurb pulls each service from its post via dynamic content, and every
// card shares the "Service Card" preset. Add a service = add a post. Restyle every
// card = edit one preset. Nothing is hard-coded or duplicated.
```

**Bad Example** — hand-built, hard-coded card grid

```html
<!-- Pasted into a Code module, repeated per service. -->
<div class="service-card">
  <img src="/wp-content/uploads/design.jpg">   <!-- hard-coded URL -->
  <h3>Design</h3><p>We design things.</p>       <!-- content trapped in markup -->
</div>
<!-- WHY it's wrong: editors can't update it in the builder, it dodges responsive
     and a11y handling, and restyling means editing every copy by hand. -->
```

## Common Mistakes

- Building one static page per blog post instead of a dynamic Theme Builder template.
- Pasting navigation or card HTML into Code modules, bypassing menus, responsiveness, and a11y.
- Hard-coding data (prices, titles, images) that should come from dynamic content/custom fields.
- Duplicating a CTA across pages instead of using a global module.
- Hiding "gated" content with CSS/JS while still shipping it in the HTML source.
- Installing a plugin for a grid/slider/tabs pattern Divi already provides.

## Production Tips

- Document which Theme Builder template drives which URL pattern; it is the first place to
  look when "a page changed and I can't find where".
- When a pattern needs a snippet, keep it in a clearly named child-theme file, not inline,
  so it survives updates and is reviewable.

## AI Review Checklist

- Is repeated/dynamic content driven by a Theme Builder template, not per-page copies?
- Do titles, prices, images, and fields come from dynamic content/custom fields?
- Are repeated designs styled via a shared preset or global module?
- Is navigation built from WordPress menus, not pasted HTML?
- Is gated content enforced server-side, not merely hidden client-side?

## Related

- `knowledge/divi/02-theme-builder.md`
- `knowledge/divi/07-dynamic-content.md`
- `knowledge/divi/09-custom-css.md`
- `knowledge/divi/14-woocommerce.md`
- `knowledge/divi/15-custom-fields.md`
