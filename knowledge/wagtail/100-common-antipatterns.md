---
id: wagtail/100-common-antipatterns
topic: wagtail
slug: common-antipatterns
title: "Common Wagtail Antipatterns"
type: antipatterns
order: 100
status: ready
maturity: unverified
tags: [wagtail, common-antipatterns, path, save_revision, specific]
related: [wagtail/99-ai-review-checklist]
when_to_use: "Read when reviewing Wagtail changes for known failure modes."
---
# Common Wagtail Antipatterns

## Purpose

Use this as a mandatory, evidence-based gate against known Wagtail mistakes.

## Rules

**Rules:** [02-architecture](02-architecture.md) · [05-revisions-and-workflows](05-revisions-and-workflows.md) · [04-streamfield-and-blocks](04-streamfield-and-blocks.md)

- [ ] Do not guess versions from memory or pair Django 6.1 with Wagtail 7.4.
- [ ] Do not write `path`, `depth`, or `numchild`, or `bulk_create` into `wagtailcore_page`.
- [ ] Do not update live page rows with `QuerySet.update` or skip `save_revision`.
- [ ] Do not call `page.specific` inside a loop or rename StreamField blocks without a data migration.
- [ ] Do not hide authorization only in the admin UI or cache preview/draft responses.
- [ ] Do not deploy without `update_index` after indexed-field or search-backend changes.
