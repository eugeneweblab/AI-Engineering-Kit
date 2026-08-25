---
id: wagtail/05-revisions-and-workflows
topic: wagtail
slug: revisions-and-workflows
title: "Wagtail Revisions, Publishing, and Workflows"
type: doc
order: 5
status: ready
maturity: unverified
tags: [wagtail, revisions-and-workflows, save_revision, publish, unpublish, go_live_at]
related: [wagtail/03-page-models, wagtail/06-permissions]
when_to_use: "Read when publishing, unpublishing, scheduling, or writing page content from code."
---
# Wagtail Revisions, Publishing, and Workflows

## Purpose

Defines editorial-state correctness.

## Rules

- Write editable `Page` content through `save_revision()` and publish APIs rather than direct live-table updates.
- Preserve moderation workflows, scheduled publication (`go_live_at` / `expire_at`), and audit history.
- Test draft preview separately from live serving.
- Make bulk content operations explicit about whether they create revisions, publish, or leave drafts.
- Do not infer public visibility from row existence; apply live, locale, site, and privacy constraints.

## Good Example

```python
page.title = "Updated title"
revision = page.save_revision(user=editor)
revision.publish()
```

The live page changes only after an explicit publish; a revision row records who edited.

## Bad Example

```python
Page.objects.filter(pk=page.pk).update(title="Updated title", live=True)
```

`QuerySet.update` skips revisions, workflows, and `page_published` signal consumers.

## Checklist

- [ ] Programmatic edits use `save_revision` / publish APIs
- [ ] Workflows and scheduled publish windows are preserved
- [ ] Preview is tested separately from live serving
- [ ] Bulk jobs state whether they publish or leave drafts
- [ ] Public queries filter `live`, site, locale, and privacy

## Related

- `wagtail/03-page-models`
- `wagtail/06-permissions`
