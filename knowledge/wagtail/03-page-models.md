---
id: wagtail/03-page-models
topic: wagtail
slug: page-models
title: "Wagtail Page Models"
type: doc
order: 3
status: ready
maturity: unverified
tags: [wagtail, page-models]
related: [wagtail/05-revisions-and-workflows, wagtail/07-search]
when_to_use: "Read when implementing or reviewing wagtail page models in a Wagtail project."
---
# Wagtail Page Models

## Purpose

Defines safe page type and content modeling.

## Rules

- Declare allowed parent and child types when the content model requires a constrained tree.
- Use specific() intentionally when querying polymorphic pages and avoid per-row subtype queries.
- Treat live, revision, draft, and scheduled state as distinct.
- Add searchable fields and editor panels alongside model fields, and create migrations for model changes.
- Use route or serve overrides only when ordinary page routing cannot express the requirement.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Declare allowed parent and child types when the content model requires a constrained tree
- [ ] Use specific() intentionally when querying polymorphic pages and avoid per-row subtype queries
- [ ] Treat live, revision, draft, and scheduled state as distinct
- [ ] Add searchable fields and editor panels alongside model fields, and create migrations for model changes
- [ ] Use route or serve overrides only when ordinary page routing cannot express the requirement

## Related

- `wagtail/05-revisions-and-workflows`
- `wagtail/07-search`
