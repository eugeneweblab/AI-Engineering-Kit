---
id: wagtail/03-page-models
topic: wagtail
slug: page-models
title: "Wagtail Page Models"
type: doc
order: 3
status: ready
maturity: unverified
tags: [wagtail, page-models, Page, parent_page_types, subpage_types, specific, search_fields]
related: [wagtail/05-revisions-and-workflows, wagtail/07-search]
when_to_use: "Read when adding or changing Page subclasses, parent/child types, or specific() queries."
---
# Wagtail Page Models

## Purpose

Defines safe page type and content modeling.

## Rules

- Declare `parent_page_types` and `subpage_types` when the content model requires a constrained tree.
- Use `specific()` / `specific_deferred` intentionally when querying polymorphic pages and avoid per-row subtype queries.
- Treat live, revision, draft, and scheduled state as distinct.
- Add `search_fields` and editor panels alongside model fields, and create migrations for model changes.
- Use `route` or `serve` overrides only when ordinary page routing cannot express the requirement.

## Good Example

```python
from wagtail.models import Page
from wagtail.search import index

class ArticlePage(Page):
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    search_fields = Page.search_fields + [
        index.SearchField("title"),
    ]
```

Editors cannot hang an article under the wrong parent, and search knows the fields.

## Bad Example

```python
for page in Page.objects.all():
    print(page.specific.body)
```

Calling `specific` per row is N+1 against every page subclass table.

## Checklist

- [ ] `parent_page_types` / `subpage_types` match the editorial tree
- [ ] Polymorphic queries use `specific()` in bulk, not per row
- [ ] Live, draft, revision, and scheduled states are not conflated
- [ ] New fields have panels, `search_fields`, and a migration

## Related

- `wagtail/05-revisions-and-workflows`
- `wagtail/07-search`
