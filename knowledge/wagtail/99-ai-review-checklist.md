---
id: wagtail/99-ai-review-checklist
topic: wagtail
slug: ai-review-checklist
title: "Wagtail AI Review Checklist"
type: checklist
order: 99
status: ready
maturity: unverified
tags: [wagtail, ai-review-checklist]
related: [wagtail/98-production-checklist, wagtail/100-common-antipatterns]
when_to_use: "Read when reviewing a Wagtail diff for correctness before merge."
---
# Wagtail AI Review Checklist

## Purpose

Use this as a mandatory review of the diff, not a second copy of the release gate.

## Version and architecture

**Rules:** [01-version-compatibility](01-version-compatibility.md) · [02-architecture](02-architecture.md)

- [ ] APIs in the diff exist on the installed Wagtail/Django line.
- [ ] New CMS types are `Page` vs snippet correctly; Django services do not live in page `models.py` without cause.
- [ ] No hook is the only place a publish, charge, or tree move happens.

## Correctness and security

**Rules:** [03-page-models](03-page-models.md) · [04-streamfield-and-blocks](04-streamfield-and-blocks.md) · [05-revisions-and-workflows](05-revisions-and-workflows.md)

- [ ] `specific()` is not called per row; `parent_page_types` / `subpage_types` match the tree.
- [ ] StreamField block names were not renamed without a data migration.
- [ ] The diff does not `QuerySet.update` live pages or insert `path` / `depth` by hand.

## Release

**Rules:** [10-testing](10-testing.md) · [12-deployment](12-deployment.md)

- [ ] Tests use `add_child` / `WagtailPageTests` and cover publish or permission as applicable.
- [ ] Search index and media implications of the change are named.
