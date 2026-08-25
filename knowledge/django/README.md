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

Detect the installed framework and Python versions from lock files or package metadata before selecting rules. Read only documents marked `ready`; drafts reserve the standard layout and are not authoritative.

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

## Completion

Always finish with the production checklist, AI review checklist, and common antipatterns document.
