---
id: wagtail/23-migrations
topic: wagtail
slug: migrations
title: "Wagtail Migrations"
type: doc
order: 23
status: ready
maturity: unverified
tags: [wagtail, migrations, StreamField, RunPython, parent_page_types]
related: [django/04-models-and-migrations, wagtail/04-streamfield-and-blocks]
when_to_use: "Read when migrating Page fields, StreamField JSON, or parent_page_types changes."
---
# Wagtail Migrations

## Purpose

Defines schema and content migrations that keep revisions readable.

## Rules

- Follow Django migration rules: never edit applied migrations; expand-and-contract for large tables.
- StreamField block renames, moves, and type changes need `RunPython` that rewrites stored JSON and is tested against real revision payloads.
- Changing `parent_page_types` / `subpage_types` does not move existing pages; write an explicit tree move if the tree must change.
- Do not `QuerySet.update` live page rows to "fix" content; use revisions when editors must see history.
- Rebuild search after fields that are indexed change.

## Good Example

```python
from django.db import migrations

def rename_story_block(apps, schema_editor):
    ArticlePage = apps.get_model("home", "ArticlePage")
    for page in ArticlePage.objects.all().iterator():
        body = page.body
        for block in body:
            if block["type"] == "old_story":
                block["type"] = "story"
        page.body = body
        page.save(update_fields=["body"])
```

The stored type name is rewritten in a data migration before the block definition is removed.

## Bad Example

```python
# Deleted CharBlock "heading" from StreamField in models.py only
```

Existing revisions still contain `"type": "heading"` and will fail to render.

## Checklist

- [ ] Applied migrations were not edited
- [ ] StreamField shape changes have a tested `RunPython`
- [ ] Tree-rule changes include an explicit move if pages would become invalid
- [ ] Search is rebuilt when indexed fields change

## Related

- `django/04-models-and-migrations`
- `wagtail/04-streamfield-and-blocks`
