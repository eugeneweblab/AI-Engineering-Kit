---
id: wagtail/21-performance
topic: wagtail
slug: performance
title: "Wagtail Performance"
type: doc
order: 21
status: ready
maturity: unverified
tags: [wagtail, performance, specific, prefetch_related, get_rendition]
related: [django/26-performance, wagtail/03-page-models]
when_to_use: "Read when page listings are slow, specific() N+1 appears, or renditions stampede."
---
# Wagtail Performance

## Purpose

Defines query and rendition costs on CMS pages.

## Rules

- Use `specific()` in bulk (`Page.objects.specific()`) rather than `page.specific` inside a loop.
- `prefetch_related` images, authors, and snippet FKs the template will walk.
- Generate renditions with fixed specs; pre-generate or cache them rather than creating unique specs per request.
- Limit listings with `live().public()` plus slice/pagination; do not walk the whole tree per request.
- Apply Django performance rules to remaining ORM.

## Good Example

```python
pages = (
    ArticlePage.objects.live()
    .public()
    .specific()
    .select_related("locale")
    .prefetch_related("hero")[:20]
)
```

Twenty specific articles, locale joined, hero fetched, no per-row subtype query.

## Bad Example

```python
for page in Page.objects.all():
    print(page.specific.hero.get_rendition(request.GET["spec"]).url)
```

This is N+1 `specific`, unbounded tree scan, and user-controlled renditions.

## Checklist

- [ ] `specific()` is bulk, not per row
- [ ] Template relations are prefetched
- [ ] Rendition specs are fixed; listings are sliced

## Related

- `django/26-performance`
- `wagtail/03-page-models`
