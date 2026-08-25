---
id: wagtail/14-admin-panels
topic: wagtail
slug: admin-panels
title: "Wagtail Admin Panels"
type: doc
order: 14
status: ready
maturity: unverified
tags: [wagtail, admin-panels, FieldPanel, MultiFieldPanel, TabbedInterface, content_panels]
related: [wagtail/03-page-models, wagtail/06-permissions]
when_to_use: "Read when changing content_panels, promote_panels, or custom edit handlers."
---
# Wagtail Admin Panels

## Purpose

Defines the editor UI for page and snippet fields.

## Rules

- Expose every editor-managed field on `content_panels` / `promote_panels` (or a `TabbedInterface`); a model field with no panel is invisible and still migrates.
- Group related fields with `FieldPanel`, `MultiFieldPanel`, and `InlinePanel`; do not dump 30 fields in one list without structure.
- Keep custom edit handlers cheap; do not run unbounded QuerySets in `on_bound` without a reason.
- Do not put secrets or internal IDs on panels staff should not see.
- Test that a non-superuser can still save the page after panel changes.

## Good Example

```python
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

class ArticlePage(Page):
    intro = models.CharField(max_length=250)
    body = StreamField([("story", StoryBlock())], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        MultiFieldPanel([FieldPanel("intro")], heading="Listing"),
    ]
```

Editors can reach every field; promote/SEO stays on `promote_panels`.

## Bad Example

```python
class ArticlePage(Page):
    body = StreamField([("story", StoryBlock())], use_json_field=True)
    content_panels = Page.content_panels
```

`body` exists in the database but never appears in the editor, so migrations look complete while authors cannot fill the field.

## Checklist

- [ ] Every editor-managed field has a panel
- [ ] Panels are grouped; secrets are not on the form
- [ ] A non-superuser save path was tested

## Related

- `wagtail/03-page-models`
- `wagtail/06-permissions`
