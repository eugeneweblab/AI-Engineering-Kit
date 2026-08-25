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

Detect the installed framework and Python versions from lock files or package metadata before selecting rules. Read only documents marked `ready`; drafts reserve the standard layout and are not authoritative.

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

## Completion

Always finish with the production checklist, AI review checklist, and common antipatterns document.
