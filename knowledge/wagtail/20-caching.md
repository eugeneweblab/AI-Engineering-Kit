---
id: wagtail/20-caching
topic: wagtail
slug: caching
title: "Wagtail Caching"
type: doc
order: 20
status: ready
maturity: unverified
tags: [wagtail, caching, page_published, cache.delete, purge]
related: [django/17-caching, wagtail/05-revisions-and-workflows]
when_to_use: "Read when caching page responses or purging CDN/cache on publish."
---
# Wagtail Caching

## Purpose

Defines cache keys and purge events for CMS pages.

## Rules

- Cache only live, public, anonymous responses; never cache preview, draft, or personalized pages under a shared key.
- Purge or version keys on `page_published`, unpublish, move, redirect, and locale changes.
- Include site and locale in the cache key.
- Follow Django caching rules for the backend (Redis, not locmem in multi-process).
- Document who purges the CDN; a Django cache delete does not clear Cloudflare by magic.

## Good Example

```python
from django.core.cache import cache
from wagtail.signals import page_published

def invalidate_article(sender, instance, **kwargs):
    cache.delete(f"article:{instance.pk}:{instance.locale_id}")

page_published.connect(invalidate_article, sender=ArticlePage)
```

Publish drops the public key; preview never used that key.

## Bad Example

```python
from django.views.decorators.cache import cache_page

@cache_page(3600)
def preview(request, page_id):
    return Page.objects.get(pk=page_id).serve(request)
```

Caching preview (or an unscoped `Page.objects.get`) serves drafts to whoever hits the cache first.

## Checklist

- [ ] Only anonymous live/public responses are cached
- [ ] Keys include site/locale; publish/unpublish/move purge them
- [ ] CDN purge is explicit if a CDN is in front

## Related

- `django/17-caching`
- `wagtail/05-revisions-and-workflows`
