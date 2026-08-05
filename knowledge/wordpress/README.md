---
id: wordpress/readme
topic: wordpress
slug: readme
title: "WordPress Engineering Standards"
type: index
order: -1
status: ready
tags: [wordpress]
related: []
when_to_use: "Read first when building, reviewing, or maintaining a WordPress project (themes, plugins, or custom builds)."
---
# WordPress Engineering Standards

## Purpose

This section defines the engineering standards, architectural principles, and best
practices for building and maintaining WordPress projects — custom themes, plugins,
and integrations.

The objective is a consistent approach to secure, performant, and maintainable
WordPress code that follows platform conventions instead of fighting them.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- WordPress architecture, project structure, and the hook system
- Content modelling: post types, taxonomies, metadata, and queries
- Themes, templates, block themes, and the block editor
- The REST API and direct database access
- Security, capabilities, performance, and caching
- Uploads, internationalization, multisite, and scheduled work
- Testing, debugging, deployment, and ongoing maintenance

For a map of which document answers which question, start with
[00. Overview](00-overview.md).

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. [Overview](00-overview.md)
- 01. [WordPress Architecture](01-wordpress-architecture.md)
- 02. [Project Structure](02-project-structure.md)
- 08. [Hooks — Actions and Filters](08-hooks.md)

## Writing Code

- 03. [Best Practices](03-best-practices.md)
- 04. [Code Style](04-code-style.md)
- 30. [Engineering Principles](30-engineering-principles.md)

## Content Modelling

- 09. [Custom Post Types](09-custom-post-types.md)
- 10. [Taxonomies](10-taxonomies.md)
- 11. [Metadata](11-metadata.md)
- 12. [Queries and The Loop](12-queries.md)
- 19. [Database and `$wpdb`](19-database.md)

## Building the Site

- 13. [Template Hierarchy](13-template-hierarchy.md)
- 14. [Theme Development](14-theme-development.md)
- 15. [Plugin Development](15-plugin-development.md)
- 16. [Block Editor](16-block-editor.md)
- 17. [Block Themes and theme.json](17-block-themes.md)
- 18. [REST API](18-rest-api.md)
- 21. [Media and Uploads](21-media-and-uploads.md)
- 24. [Internationalization](24-internationalization.md)

## Correctness and Speed

- 06. [Security](06-security.md)
- 20. [Users and Capabilities](20-users-and-capabilities.md)
- 05. [Performance](05-performance.md)
- 23. [Caching](23-caching.md)
- 07. [Testing](07-testing.md)
- 28. [Debugging](28-debugging.md)

## Operations

- 22. [Cron and Background Tasks](22-cron-and-background-tasks.md)
- 25. [Multisite](25-multisite.md)
- 26. [WP-CLI](26-wp-cli.md)
- 27. [Deployment](27-deployment.md)
- 29. [Maintenance](29-maintenance.md)

## Closing Checks

- 98. [Production Checklist](98-production-checklist.md)
- 99. [AI Review Checklist](99-ai-review-checklist.md)
- 100. [Common Antipatterns](100-common-antipatterns.md)

---

## Engineering Principles

Every WordPress feature should satisfy the following principles:

- Follow WordPress coding standards and naming conventions.
- Use hooks (actions and filters) instead of modifying core.
- Escape output, sanitize input, and validate all data.
- Never trust user input or third-party data.
- Enqueue scripts and styles properly; do not hardcode assets.
- Keep themes presentational and move logic into plugins.
- Prefer the WordPress APIs over reinventing existing functionality.
- Optimize database queries; avoid queries inside loops.
- Build for accessibility and internationalization.
- Measure performance before optimizing.

The reasoning behind each is in [30. Engineering Principles](30-engineering-principles.md).

---

## Related Topics

- [PHP](../php/00-overview.md) — the language underneath.
- [WooCommerce](../woocommerce/00-overview.md) and [Divi](../divi/00-overview.md) — platforms built on WordPress.
- [Workflow — Build a WordPress Feature](../workflows/09-build-wordpress-feature.md) — the process wrapper.
- [Workflow — Build a Gutenberg Block](../workflows/11-build-gutenberg-block.md) — editor-side components.

---

## Intended Audience

These standards are intended for:

- WordPress Developers
- Frontend and Fullstack Engineers
- Theme and Plugin Authors
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps WordPress projects secure, performant, and maintainable
while staying aligned with platform conventions and upgrade paths.
