---
id: wordpress/00-overview
topic: wordpress
slug: overview
title: "WordPress Overview"
type: doc
order: 0
status: ready
tags: [wordpress, overview]
related: [wordpress/01-wordpress-architecture, wordpress/02-project-structure, wordpress/08-hooks, wordpress/06-security, wordpress/30-engineering-principles, wordpress/03-best-practices]
when_to_use: "Read first when starting work on a WordPress project, to understand what this topic covers and which document answers your question."
---
# WordPress Overview

## Purpose

This document is the entry point to the WordPress topic. It states what WordPress is as an
engineering platform, what makes building on it different from building a standalone
application, and which document in this section answers which question.

WordPress powers a large share of the web, and most of the code written for it is written
against conventions rather than against an API contract. Those conventions are what this
topic documents.

---

## What WordPress Is, Architecturally

WordPress is a PHP application with three properties that shape every decision made on top
of it:

- **It is extended by events, not by inheritance.** Actions and filters are the primary
  extension mechanism. Almost nothing is overridden; almost everything is hooked. See
  [Hooks](08-hooks.md).
- **It is a shared runtime.** The theme, every plugin, and core all execute in one PHP
  process with one global namespace and one database connection. A slow query or a fatal
  error in any of them affects all of them.
- **Its data model is generic.** Posts, meta, terms, users, and options carry almost all
  content, regardless of what that content represents. Modelling a domain in WordPress means
  mapping it onto that fixed schema — see [Custom Post Types](09-custom-post-types.md) and
  [Metadata](11-metadata.md).

The consequence: WordPress rewards code that follows platform conventions and punishes code
that works around them. Working around the platform usually survives until the next core or
plugin update.

---

## What This Topic Covers

**Foundations** — how the platform is put together and where your code belongs.

- [01. WordPress Architecture](01-wordpress-architecture.md) — request lifecycle, load order, responsibilities.
- [02. Project Structure](02-project-structure.md) — themes, plugins, mu-plugins, and what goes where.
- [08. Hooks](08-hooks.md) — actions, filters, priorities, and the extension model.

**Content modelling** — mapping a domain onto the WordPress schema.

- [09. Custom Post Types](09-custom-post-types.md) · [10. Taxonomies](10-taxonomies.md) · [11. Metadata](11-metadata.md)
- [12. Queries](12-queries.md) — `WP_Query`, the main query, and the cost of getting it wrong.
- [19. Database](19-database.md) — `$wpdb`, custom tables, and when they are justified.

**Building the site** — themes, plugins, and the editor.

- [13. Template Hierarchy](13-template-hierarchy.md) · [14. Theme Development](14-theme-development.md) · [15. Plugin Development](15-plugin-development.md)
- [16. Block Editor](16-block-editor.md) · [17. Block Themes](17-block-themes.md)
- [18. REST API](18-rest-api.md) — the interface for headless front ends and the editor itself.
- [21. Media and Uploads](21-media-and-uploads.md) · [24. Internationalization](24-internationalization.md)

**Correctness and quality.**

- [03. Best Practices](03-best-practices.md) · [04. Code Style](04-code-style.md)
- [06. Security](06-security.md) · [20. Users and Capabilities](20-users-and-capabilities.md)
- [05. Performance](05-performance.md) · [23. Caching](23-caching.md)
- [07. Testing](07-testing.md) · [28. Debugging](28-debugging.md)

**Operations.**

- [22. Cron and Background Tasks](22-cron-and-background-tasks.md) · [25. Multisite](25-multisite.md) · [26. WP-CLI](26-wp-cli.md)
- [27. Deployment](27-deployment.md) · [29. Maintenance](29-maintenance.md)

**Closing checks** — run these before calling work done.

- [98. Production Checklist](98-production-checklist.md) · [99. AI Review Checklist](99-ai-review-checklist.md) · [100. Common Antipatterns](100-common-antipatterns.md)

---

## The Five Rules That Prevent Most Defects

Nearly every WordPress defect found in review traces back to one of these:

1. **Escape at output, sanitize at input.** Not the reverse, and not once at the boundary
   and never again. `esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses_post()`.
2. **Check the capability, then verify the nonce.** A nonce proves intent, not permission —
   both are required for a state-changing request.
3. **Never edit core, a parent theme, or a third-party plugin.** Use hooks, a child theme, or
   a template override. Edits are erased by the next update.
4. **Never query inside a loop.** Use `WP_Query` with the right arguments, or prime the cache
   for the objects you are about to touch.
5. **Prefix everything global.** Functions, classes, options, meta keys, and post types share
   one namespace with every other plugin on the site.

---

## Where This Topic Fits

WordPress sits below the platform-specific topics and above the language:

- [PHP](../php/00-overview.md) — the language underneath; error handling, namespaces, and modern syntax.
- [WooCommerce](../woocommerce/00-overview.md) and [Divi](../divi/00-overview.md) — platforms built on top of WordPress; their conventions extend, not replace, these.
- [Security](../security/00-overview.md), [Performance](../performance/00-overview.md), [Accessibility](../accessibility/00-overview.md), [SEO](../seo/00-overview.md) — cross-cutting concerns; the WordPress documents here describe how those concerns are expressed on this platform.
- [Workflow — Build a WordPress Feature](../workflows/09-build-wordpress-feature.md) — the process wrapper around all of it.

---

## How to Use This Topic

For a specific task, read the document that matches the integration point you are working on
rather than reading in order. For onboarding to WordPress as a platform, follow the reading
order in [README](README.md).

Before marking WordPress work complete, run it through
[98](98-production-checklist.md) / [99](99-ai-review-checklist.md) /
[100](100-common-antipatterns.md).

---

## Summary

WordPress is a convention-driven, hook-extended, shared-runtime platform with a deliberately
generic data model. Code that respects those four facts survives updates and stays
maintainable; code that fights them does not.

## Related

- `knowledge/wordpress/01-wordpress-architecture.md`
- `knowledge/wordpress/02-project-structure.md`
- `knowledge/wordpress/08-hooks.md`
- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/30-engineering-principles.md`
- `knowledge/wordpress/03-best-practices.md`
