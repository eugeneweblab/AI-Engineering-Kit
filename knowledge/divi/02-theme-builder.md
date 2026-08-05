---
id: divi/02-theme-builder
topic: divi
slug: theme-builder
title: "Theme Builder"
type: doc
order: 2
status: ready
tags: [divi, theme-builder, Footer, Header]
related: [divi/01-architecture, divi/05-layouts, divi/07-dynamic-content, divi/08-templates, divi/00-overview]
when_to_use: "Read before building or changing site-wide headers, footers, or templated pages like blog posts and archives."
---
# Theme Builder

## Purpose

This document covers the **Divi Theme Builder** — the system for defining site-wide
templates: global headers and footers, and body templates for posts, pages, archives, 404s,
and other WordPress query contexts. It is how you stop rebuilding the same header on every
page and instead design it once.

## Why It Matters

Without the Theme Builder, teams recreate headers, footers, and post layouts on every page,
so a single branding change means editing dozens of pages by hand — and one gets missed.
The Theme Builder centralizes these into templates driven by WordPress's template hierarchy
and [dynamic content](07-dynamic-content.md). Getting the assignment rules and dynamic
bindings right is the difference between a site that maintains itself and one that drifts
out of sync.

## Core Principles

- **Templates are assigned by condition, not by page.** A template applies to "all posts",
  "a specific category", "all archives", etc. Assignment follows WordPress's template
  hierarchy, so specific rules override general ones.
- **The Default Website Template is the fallback.** Its header and footer apply everywhere
  unless a more specific template overrides them. Design the global header/footer here.
- **Body areas are dynamic.** A post-body template uses dynamic content (title, featured
  image, post content, meta) so one template renders every post correctly.
- **Header, Body, and Footer are independent slots.** You can override just the footer for a
  section of the site while inheriting the global header.
- **Specificity resolves conflicts.** When multiple templates could match, Divi picks the
  most specific, mirroring WordPress core behavior.

## Best Practices

- Build the global header and footer once in the Default Website Template; override only where
  a section genuinely differs.
- Use [dynamic content](07-dynamic-content.md) for every field that varies per post — title,
  author, date, featured image — never hard-code sample text into a body template.
- Include the **Post Content** module in body templates, or the actual page content will not
  render inside your template frame.
- Verify assignment rules against the WordPress template hierarchy; test a specific category
  template does not accidentally shadow a broader one.
- Export Theme Builder templates as part of your deployment artifact so staging and production
  stay identical. See [deployment](22-deployment.md).

## Examples

**Good Example** — one dynamic post template for all posts

```text
Template: "All Posts"  (assigned to: All Posts)
  Header  → Global Header (inherited from Default Website Template)
  Body    → Title:        Dynamic Content → Post/Archive Title
            Featured img:  Dynamic Content → Featured Image
            Content:       Post Content module   // renders the actual post body
            Meta:          Dynamic Content → Author, Date, Categories
  Footer  → Global Footer (inherited)
// One template renders every post; editing it updates the whole blog.
```

**Bad Example** — hard-coded body rebuilt per post

```text
Template: "Blog Post – How To Bake Bread"  (assigned to: one specific post)
  Body → Text module: "How To Bake Bread"      // hard-coded title
         Image module: bread.jpg               // hard-coded image
         Text module: pasted article body...   // content not from Post Content
// A new post needs a whole new template; the post editor no longer drives the page.
```

## Common Mistakes

- Omitting the **Post Content** module, so the template shows the frame but not the article.
- Hard-coding titles, images, or dates instead of binding dynamic content, defeating the
  template's purpose.
- Overlapping assignment rules that unexpectedly override each other; not testing which
  template wins on a given URL.
- Building the header inside individual pages instead of the Theme Builder, reintroducing the
  duplication the tool exists to remove.
- Forgetting to export/import Theme Builder templates during deploys, so environments diverge.

## Production Tips

- After changing assignment rules, spot-check one URL per context (single post, category
  archive, 404) to confirm the intended template renders.
- Keep template count small; a sprawl of near-identical templates is a maintenance liability.
  Prefer conditional dynamic content over cloning templates.
- Version Theme Builder exports in your repo alongside child-theme code.

## AI Review Checklist

- Are global header and footer defined once in the Default Website Template?
- Does every body template use dynamic content for per-post fields?
- Is a Post Content module present so the actual content renders?
- Are assignment rules tested against the WordPress template hierarchy for conflicts?
- Are Theme Builder templates exported and versioned for deployment parity?

## Related

- `knowledge/divi/01-architecture.md`
- `knowledge/divi/05-layouts.md`
- `knowledge/divi/07-dynamic-content.md`
- `knowledge/divi/08-templates.md`
- `knowledge/divi/00-overview.md`
