---
id: wagtail/04-streamfield-and-blocks
topic: wagtail
slug: streamfield-and-blocks
title: "Wagtail StreamField and Blocks"
type: doc
order: 4
status: ready
maturity: unverified
tags: [wagtail, streamfield-and-blocks, StreamField, StructBlock, ListBlock, StreamBlock]
related: [wagtail/03-page-models, wagtail/10-testing, wagtail/23-migrations]
when_to_use: "Read when adding StreamField, renaming blocks, or migrating stored block JSON."
---
# Wagtail StreamField and Blocks

## Purpose

Defines stable structured-content schemas.

## Rules

- Give every block a stable name and preserve stored block shape across refactors.
- Use `StructBlock`, `ListBlock`, and `StreamBlock` to express structure instead of parsing free-form rich text.
- Write and test data migrations before renaming, moving, or changing block types.
- Validate external choices and references without making historical revisions unreadable.
- Keep rendering logic small and escape or sanitize editor-provided HTML at the correct boundary.

## Good Example

```python
from wagtail import blocks
from wagtail.fields import StreamField

class StoryBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    body = blocks.RichTextBlock()

class ArticlePage(Page):
    body = StreamField(
        [("story", StoryBlock())],
        use_json_field=True,
    )
```

The stored type name `story` stays stable; a rename would ship a tested data migration first.

## Bad Example

```python
body = StreamField([
    ("heading", blocks.CharBlock()),
    ("heading_v2", blocks.CharBlock()),
])
```

Introducing `heading_v2` without migrating existing `heading` values splits the schema and breaks templates.

## Checklist

- [ ] Every block has a stable name; stored JSON shape is unchanged or migrated
- [ ] Structure uses `StructBlock` / `ListBlock` / `StreamBlock`, not ad-hoc HTML parsing
- [ ] Block type changes have a tested data migration
- [ ] Historical revisions remain readable

## Related

- `wagtail/03-page-models`
- `wagtail/10-testing`
- `wagtail/23-migrations`
