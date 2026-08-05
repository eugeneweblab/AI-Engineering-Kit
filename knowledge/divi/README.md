---
id: divi/readme
topic: divi
slug: readme
title: "Divi Engineering Standards"
type: index
order: -1
status: ready
tags: [divi]
related: []
when_to_use: "Read first when starting work on a Divi site, to see how this section's docs fit together and where builder constraints apply."
---
# Divi Engineering Standards

## Purpose

This section defines the engineering standards for building and maintaining sites on the Divi
builder: how the builder fits into WordPress, where custom code belongs, and how to keep a
builder-driven site fast, accessible, and maintainable by the people who edit it.

Divi changes the ownership model of a WordPress site. Page structure lives in shortcode
content edited through a visual interface, not in templates under version control. That has
practical consequences for every engineering discipline — deployment, code review, testing,
and performance — and this section is largely about working with that reality rather than
against it.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Divi architecture and the Theme Builder
- Modules: built-in, custom, and global elements
- Layouts, templates, and dynamic content
- Custom CSS, responsive design, and accessibility
- Integration: WordPress hooks, custom fields, REST API, WooCommerce, headless
- Performance, security, debugging, and testing
- Deployment, maintenance, and client-project practice
- AI-assisted workflow and review

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. [Overview](00-overview.md)
- 01. [Architecture](01-architecture.md)
- 02. [Theme Builder](02-theme-builder.md)
- 30. [Engineering Principles](30-engineering-principles.md)

## Building Pages

- 03. [Modules](03-modules.md)
- 05. [Layouts](05-layouts.md)
- 06. [Global Elements](06-global-elements.md)
- 08. [Templates](08-templates.md)
- 07. [Dynamic Content](07-dynamic-content.md)
- 15. [Custom Fields](15-custom-fields.md)

## Extending Divi

- 04. [Custom Modules](04-custom-modules.md)
- 16. [WordPress Hooks](16-wordpress-hooks.md)
- 17. [REST API](17-rest-api.md)
- 18. [Headless](18-headless.md)
- 14. [WooCommerce](14-woocommerce.md)

## Presentation Quality

- 09. [Custom CSS](09-custom-css.md)
- 11. [Responsive Design](11-responsive-design.md)
- 12. [Accessibility](12-accessibility.md)
- 13. [SEO](13-seo.md)

## Correctness and Speed

- 10. [Performance](10-performance.md)
- 19. [Security](19-security.md)
- 20. [Debugging](20-debugging.md)
- 21. [Testing](21-testing.md)

## Operations

- 22. [Deployment](22-deployment.md)
- 23. [Maintenance](23-maintenance.md)
- 25. [Production](25-production.md)
- 27. [Client Projects](27-client-projects.md)

## Applied Guidance

- 24. [Best Practices](24-best-practices.md)
- 26. [Real-World Patterns](26-real-world-patterns.md)
- 28. [AI Workflow](28-ai-workflow.md)
- 29. [Review](29-review.md)

## Verification

- 98. [Production Checklist](98-production-checklist.md)
- 99. [AI Review Checklist](99-ai-review-checklist.md)
- 100. [Common Antipatterns](100-common-antipatterns.md)

---

## Engineering Principles

Every Divi change should satisfy the following principles:

- Never edit the Divi theme. Use a child theme, hooks, and custom modules — updates overwrite
  everything else.
- Prefer configuration to code: a global element, preset, or Theme Builder template often
  removes the need for a custom module entirely.
- A custom module's field set is a content contract; renaming or removing a field breaks every
  page already saved with it.
- Escape every builder value at output — module settings are user-authored content.
- Design for the editor who will maintain the page, not only for the launch state.
- Keep design values in tokens and the child theme, not scattered across per-module custom CSS.
- Content lives in the database, so deployment and code review cover only part of the site —
  plan migrations and backups accordingly.
- Verify every change in both the Visual Builder and the front end; they render differently.
- Builder markup is verbose: performance and accessibility need explicit attention rather than
  assumption.
- Test after Divi and WordPress updates; builder output changes between versions.

---

## Intended Audience

These standards are intended for:

- WordPress and Divi Developers
- Frontend Engineers on client projects
- Agency Tech Leads
- Site Maintainers
- AI Coding Assistants
- Code Reviewers

---

## Summary

Work with the builder rather than around it: extend through child themes, hooks, and custom
modules; treat module fields and saved content as contracts; escape everything the editor can
set; and remember that on a Divi site much of what ships lives in the database rather than the
repository.
