---
id: django/readme
topic: django
slug: readme
title: "Django Engineering Standards"
type: index
order: -1
status: ready
maturity: unverified
tags: [django, readme]
related: [django/00-overview]
when_to_use: "Read first when working in a Django repository."
---
# Django Engineering Standards

## Purpose

Version-aware engineering rules for production Django projects.

## Retrieval

Detect the installed framework and Python versions from lock files or package metadata before selecting rules. Detect Django from `manage.py` or a settings module. Read only documents marked `ready`; drafts reserve the standard layout and are not authoritative.

Resolve APIs from the diff (`select_related`, `transaction.atomic`, `ModelForm`, `path`) via `SIGNALS.symbols` and this topic's tags, not only the stack starter set.

## Ready Rules

- [Django Overview](00-overview.md)
- [Django Version Support](01-version-support.md)
- [Django Architecture](02-architecture.md)
- [Django Settings and Configuration](03-settings.md)
- [Django Models and Migrations](04-models-and-migrations.md)
- [Django QuerySets and Transactions](05-querysets-and-transactions.md)
- [Django Security](06-security.md)
- [Django Testing](07-testing.md)
- [Django Async and ASGI](08-async.md)
- [Django Deployment](09-deployment.md)
- [Django Upgrades](10-upgrades.md)
- [Django URLs and Views](11-urls-and-views.md)
- [Django Forms and Validation](12-forms-and-validation.md)
- [Django Templates](13-templates.md)
- [Django Static and Media Files](14-static-and-media.md)
- [Django Authentication](15-authentication.md)
- [Django Middleware](16-middleware.md)
- [Django Caching](17-caching.md)
- [Django Admin](18-admin.md)
- [Django Internationalization](19-internationalization.md)
- [Django Management Commands](20-management-commands.md)
- [Django Email](21-email.md)
- [Django Logging and Observability](22-logging-and-observability.md)
- [Django Error Handling](23-error-handling.md)
- [Django REST APIs](24-rest-apis.md)
- [Django Background Jobs](25-background-jobs.md)
- [Django Performance](26-performance.md)
- [Django Database Backends](27-database-backends.md)
- [Django Multi-Tenancy](28-multi-tenancy.md)
- [Django Maintenance](29-maintenance.md)
- [Django Engineering Principles](30-engineering-principles.md)

## Completion

Always finish with the production checklist, AI review checklist, and common antipatterns document.
