---
id: wagtail/02-architecture
topic: wagtail
slug: architecture
title: "Wagtail Architecture"
type: doc
order: 2
status: ready
maturity: unverified
tags: [wagtail, architecture]
related: [wagtail/03-page-models, django/02-architecture]
when_to_use: "Read when implementing or reviewing wagtail architecture in a Wagtail project."
---
# Wagtail Architecture

## Purpose

Defines boundaries between CMS content, domain logic, and presentation.

## Rules

- Use Page models for routable editorial content and snippets for reusable non-page content.
- Keep business rules out of templates, hooks, and StreamField block rendering.
- Preserve the treebeard page tree through Wagtail APIs; do not manipulate path, depth, or numchild directly.
- Keep Django-domain services reusable outside the admin interface.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Use Page models for routable editorial content and snippets for reusable non-page content
- [ ] Keep business rules out of templates, hooks, and StreamField block rendering
- [ ] Preserve the treebeard page tree through Wagtail APIs
- [ ] Keep Django-domain services reusable outside the admin interface

## Related

- `wagtail/03-page-models`
- `django/02-architecture`
