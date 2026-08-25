---
id: wagtail/readme
topic: wagtail
slug: readme
title: "Wagtail Engineering Standards"
type: index
order: -1
status: ready
maturity: unverified
tags: [wagtail, readme]
related: [wagtail/00-overview]
when_to_use: "Read first when working in a Wagtail repository."
---
# Wagtail Engineering Standards

## Purpose

Version-aware engineering rules for production Wagtail projects.

## Retrieval

Detect Wagtail from `wagtail` imports, `Page` subclasses, `StreamField`, `wagtail_hooks.py`, or `home/templates/home/home_page.html`. Detect Django from `manage.py`. Intersect Wagtail, Django, and Python versions from the lock file before selecting APIs.

Read only documents marked `ready`. Apply Django rules as well as Wagtail rules.

Resolve APIs from the diff (`save_revision`, `specific`, `StreamField`, `add_child`) via `SIGNALS.symbols` and this topic's tags.

## Ready Rules

- [Wagtail Overview](00-overview.md)
- [Wagtail and Django Version Compatibility](01-version-compatibility.md)
- [Wagtail Architecture](02-architecture.md)
- [Wagtail Page Models](03-page-models.md)
- [Wagtail StreamField and Blocks](04-streamfield-and-blocks.md)
- [Wagtail Revisions, Publishing, and Workflows](05-revisions-and-workflows.md)
- [Wagtail Permissions](06-permissions.md)
- [Wagtail Search](07-search.md)
- [Wagtail Images and Documents](08-images-and-documents.md)
- [Wagtail Headless API](09-headless-api.md)
- [Wagtail Testing](10-testing.md)
- [Wagtail Upgrades](11-upgrades.md)
- [Wagtail Deployment](12-deployment.md)
- [Wagtail Snippets](13-snippets.md)
- [Wagtail Admin Panels](14-admin-panels.md)
- [Wagtail Hooks](15-hooks.md)
- [Wagtail Multisite](16-multisite.md)
- [Wagtail Localization](17-localization.md)
- [Wagtail Forms](18-forms.md)
- [Wagtail Redirects](19-redirects.md)
- [Wagtail Caching](20-caching.md)
- [Wagtail Performance](21-performance.md)
- [Wagtail Security](22-security.md)
- [Wagtail Migrations](23-migrations.md)
- [Wagtail Content Imports](24-content-imports.md)
- [Wagtail Custom Users](25-custom-users.md)
- [Wagtail Frontend Assets](26-frontend-assets.md)
- [Wagtail Observability](27-observability.md)
- [Wagtail Maintenance](28-maintenance.md)
- [Wagtail Project Structure](29-project-structure.md)
- [Wagtail Engineering Principles](30-engineering-principles.md)

## Completion

Always finish with the production checklist, AI review checklist, and common antipatterns document.
