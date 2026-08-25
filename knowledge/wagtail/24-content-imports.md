---
id: wagtail/24-content-imports
topic: wagtail
slug: content-imports
title: "Wagtail Content Imports"
type: doc
order: 24
status: ready
maturity: unverified
tags: [wagtail, content-imports, add_child, save_revision, bulk_create]
related: [wagtail/05-revisions-and-workflows, wagtail/10-testing]
when_to_use: "Read when importing CMS content from CSV, CMS dumps, or scripts that create pages."
---
# Wagtail Content Imports

## Purpose

Defines bulk page creation that keeps the tree and revisions valid.

## Rules

- Create pages with `add_child` / `add_sibling` (or the project's factory), not `bulk_create` into `wagtailcore_page`.
- Decide per import whether rows are drafts or published; call `save_revision().publish()` only when the source is already live.
- Map authors to Django users; do not attribute imports to a random superuser without a record.
- Idempotency: rerunning the importer must not duplicate tree nodes (stable slugs/source IDs).
- Rehearse on a copy of production-scale data; then `update_index`.

## Good Example

```python
home = HomePage.objects.get(slug="home")
page = ArticlePage(title=row["title"], slug=row["slug"])
home.add_child(instance=page)
page.save_revision().publish()
```

The page gets a valid path/depth and a revision.

## Bad Example

```python
Page.objects.bulk_create(
    [Page(title=row["title"], path="00010002", depth=2, numchild=0)]
)
```

`bulk_create` skips treebeard, revisions, and uniqueness of `path`.

## Checklist

- [ ] Imports use tree APIs, not `bulk_create` on `wagtailcore_page`
- [ ] Publish vs draft is explicit; reruns are idempotent
- [ ] Search is rebuilt after the import

## Related

- `wagtail/05-revisions-and-workflows`
- `wagtail/10-testing`
