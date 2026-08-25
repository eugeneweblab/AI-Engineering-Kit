---
id: wagtail/28-maintenance
topic: wagtail
slug: maintenance
title: "Wagtail Maintenance"
type: doc
order: 28
status: ready
maturity: unverified
tags: [wagtail, maintenance, fixtree, update_index, purgerevisions]
related: [django/29-maintenance, wagtail/12-deployment]
when_to_use: "Read when repairing the page tree, rebuilding search, or purging old revisions."
---
# Wagtail Maintenance

## Purpose

Defines operational jobs unique to Wagtail.

## Rules

- Run `fixtree` only after diagnosing tree corruption; it is not a deploy step.
- Schedule `wagtail update_index` after large imports or search-backend changes.
- Purge old revisions with the project's documented command (`purge_revisions` or equivalent) and a retention policy.
- Apply Django maintenance (`clearsessions`, `check --deploy`) as well.
- Never `flush` a production CMS to "clear drafts".

## Good Example

```python
# after a large import on a replica
# django-admin wagtail update_index
# django-admin check --deploy
```

Search catches up; the tree is not rewritten.

## Bad Example

```python
# django-admin fixtree && django-admin flush
```

`flush` deletes pages; `fixtree` on a healthy tree is cargo-cult and can hide real path bugs.

## Checklist

- [ ] `update_index` runs after imports or search-backend changes
- [ ] `fixtree` is incident-only
- [ ] Revision retention is explicit
- [ ] Django maintenance jobs still run

## Related

- `django/29-maintenance`
- `wagtail/12-deployment`
