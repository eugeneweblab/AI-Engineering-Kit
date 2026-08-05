---
id: divi/08-templates
topic: divi
slug: templates
title: "Divi Templates"
type: doc
order: 8
status: ready
tags: [divi, templates, template, Footer]
related: [divi/02-theme-builder, divi/07-dynamic-content, divi/05-layouts, divi/06-global-elements, divi/11-responsive-design]
when_to_use: "Read before creating or scoping a Theme Builder template for a post type, archive, or 404."
---
# Divi Templates

## Purpose

This document defines how to build and **scope** Theme Builder templates in Divi: the
page-level structures (Header, Body, Footer areas) that Divi wraps around content based on
conditions like post type, category, archive, or specific page. It is written so an agent
assigns a template to exactly the right set of URLs — no more, no less.

A *template* here means a Theme Builder assignment, distinct from a saved *layout* (reusable
page content — see [layouts](05-layouts.md)) and from a *global element* (a single shared
module — see [global-elements](06-global-elements.md)). Templates consume
[dynamic-content](07-dynamic-content.md) tokens to render per-post data.

## Why It Matters

Template *scope* is where Divi sites break in confusing ways. A template assigned too broadly
("All Posts" when you meant one category) silently overrides pages you never intended to touch,
and the client reports "the blog looks wrong" with no obvious cause. Assigned too narrowly, posts
fall through to the default and look unstyled. Because Divi resolves overlapping templates by a
specificity order, two templates that both match a URL can fight, and which one wins is not
obvious from either editing screen. Getting scope right the first time avoids a whole class of
"why does this page look like that" debugging.

## Core Principles

- **Scope is the design.** A template is defined as much by *which URLs it matches* as by its
  layout. Decide the condition set before building the content.
- **Specific beats general.** When multiple templates match a URL, Divi applies the most specific
  one (a single-page assignment beats a post-type assignment beats the site-wide default). Design
  the hierarchy deliberately; do not rely on accident.
- **One default, then exceptions.** Establish a broad default template (e.g. "All Posts"), then
  add narrow templates only for genuine exceptions (a category, a specific page). Fewer templates
  are easier to reason about.
- **Body area is where content renders.** In a template, the post's builder content appears inside
  the Body area's Post Content module. Omit it and the post's own content vanishes — a common,
  baffling bug.
- **Templates are per-site, not per-page ownership.** Editing a template changes every URL it
  matches at once. Confirm the match set before every edit.

## Best Practices

- Write down the condition set (post type, taxonomy, specific items, archives, 404, search) before
  building. Assign the narrowest condition that covers the intended pages.
- Always include a **Post Content** module in the Body area of any template used for singular
  content, or the page body will not render.
- Keep a single site-wide default Header and Footer, and override only where a section genuinely
  differs (e.g. a landing page with no header).
- Use dynamic content for everything per-post inside the template (title, image, meta); a template
  with static text is not a template. See [dynamic-content](07-dynamic-content.md).
- Test overlap explicitly: after adding a narrow template, load a URL that matches *both* it and a
  broader one and confirm the intended template wins.
- Verify responsiveness of the template itself, not just sample content — header/footer areas are
  common breakpoints. See [responsive-design](11-responsive-design.md).

## Examples

**Good Example** — a clear default plus one deliberate, specific exception

```text
Theme Builder
├── Default template            → Header + Footer (site-wide)
├── "All Posts" template        → assigned: All Posts
│     Body: [Post Title dynamic][Featured Image dynamic][Post Content module]
└── "Case Study" template       → assigned: Post Type "Case Study" ONLY
      Body: custom layout + [Post Content module]

Result: a normal blog post → "All Posts" template.
        a case-study post   → "Case Study" template (more specific wins), predictably.
```

Why: scope is explicit and non-overlapping in intent, the Body area includes a Post Content
module so bodies render, and the specificity order is designed, not accidental.

**Bad Example** — over-broad scope with a missing content module

```text
Theme Builder
└── "Landing" template → assigned: ALL Pages     // meant only the homepage
      Body: hero + CTA         // NO Post Content module

Result: every page (About, Contact, Privacy) is forced into the landing layout,
        and none of their actual content renders — the Body has no Post Content module.
```

Why this is wrong: the condition is far broader than intended, so unrelated pages are hijacked,
and the missing Post Content module means even the pages' real content disappears.

## Common Mistakes

- Assigning "All Posts"/"All Pages" when a single item or one taxonomy was meant, silently
  overriding unrelated URLs.
- Forgetting the Post Content module in the Body area, so post/page bodies render blank.
- Two overlapping templates whose winner is left to chance instead of designed via specificity.
- Building the template with static text and expecting it to vary per post.
- Not creating a 404 or archive template, so those pages fall back to an unstyled default.
- Editing a template without checking how many URLs it currently matches.

## Production Tips

- Maintain a short table of template → conditions in project docs; it is the fastest way to debug
  "wrong layout on page X".
- After launch, spot-check one URL from each template's match set, plus a 404 and a search result.
- When cloning a template for a new post type, re-check its condition set — clones inherit the
  original's assignment and will double-match until you narrow them.

## AI Review Checklist

- Is each template assigned the narrowest condition that covers its intended URLs?
- Does every singular-content template include a Post Content module in the Body area?
- When templates overlap, is the winning (most specific) one the intended one?
- Are per-post values inside templates dynamic, not static?
- Do 404, search, and archive have deliberate templates rather than falling back unstyled?

## Related

- `knowledge/divi/02-theme-builder.md`
- `knowledge/divi/07-dynamic-content.md`
- `knowledge/divi/05-layouts.md`
- `knowledge/divi/06-global-elements.md`
- `knowledge/divi/11-responsive-design.md`
