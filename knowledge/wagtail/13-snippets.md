---
id: wagtail/13-snippets
topic: wagtail
slug: snippets
title: "Wagtail Snippets"
type: doc
order: 13
status: ready
maturity: unverified
tags: [wagtail, snippets, register_snippet, ClusterableModel, ParentalKey]
related: [wagtail/02-architecture, wagtail/03-page-models]
when_to_use: "Read when adding snippets, snippet choosers, or non-page reusable CMS models."
---
# Wagtail Snippets

## Purpose

Defines reusable non-page CMS records.

## Rules

- Register snippets with `@register_snippet` (or the project's snippet viewset) for content that is not routable.
- Do not subclass `Page` for things that should not live in the tree (authors, calls-to-action, settings rows).
- Use `ClusterableModel` / `ParentalKey` when the snippet has ordered child relations that must save with the parent.
- Permission snippets like pages: server-side, not only by hiding the admin menu.
- Point pages at snippets by chooser/FK, not by copying snippet HTML into StreamField on every page unless editors need a one-off override.

## Good Example

```python
from wagtail.snippets.models import register_snippet
from django.db import models

@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name
```

Authors are choosable from many pages without becoming tree nodes.

## Bad Example

```python
class AuthorPage(Page):
    """One author, but it still occupies a URL and a tree slot."""
```

A directory of 200 authors as pages creates URLs, search noise, and parent-type constraints the product does not need.

## Checklist

- [ ] Non-routable CMS data is a snippet, not a `Page`
- [ ] Child relations use `ClusterableModel` / `ParentalKey` when they must save atomically
- [ ] Snippet permissions are enforced server-side

## Related

- `wagtail/02-architecture`
- `wagtail/03-page-models`
