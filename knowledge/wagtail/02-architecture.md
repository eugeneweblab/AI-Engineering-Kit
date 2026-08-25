---
id: wagtail/02-architecture
topic: wagtail
slug: architecture
title: "Wagtail Architecture"
type: doc
order: 2
status: ready
maturity: unverified
tags: [wagtail, architecture, Page, snippet, path, depth, numchild]
related: [wagtail/03-page-models, django/02-architecture]
when_to_use: "Read when deciding Page vs snippet vs Django model, or touching the page tree."
---
# Wagtail Architecture

## Purpose

Defines boundaries between CMS content, domain logic, and presentation.

## Rules

- Use `Page` models for routable editorial content and snippets for reusable non-page content.
- Keep business rules out of templates, hooks, and StreamField block rendering.
- Preserve the treebeard page tree through Wagtail APIs; do not manipulate `path`, `depth`, or `numchild` directly.
- Keep Django-domain services reusable outside the admin interface.

## Good Example

```python
from wagtail.models import Page

class ArticlePage(Page):
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["related"] = ArticlePage.objects.live().sibling_of(self)[:3]
        return context
```

Tree queries go through `Page` QuerySets; pricing or checkout stays in a Django service the view can call.

## Bad Example

```python
page.path = page.path[:-4]
page.depth -= 1
page.save()
```

Rewriting `path` / `depth` corrupts the tree and bypasses `move()` / `add_child()`.

## Checklist

- [ ] Routable content is a `Page`; reusable non-routable content is a snippet
- [ ] Business rules are not in templates, hooks, or block rendering
- [ ] Tree mutations use Wagtail APIs, not `path` / `depth` / `numchild`
- [ ] Django-domain services remain usable outside admin

## Related

- `wagtail/03-page-models`
- `django/02-architecture`
