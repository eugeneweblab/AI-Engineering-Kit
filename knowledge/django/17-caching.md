---
id: django/17-caching
topic: django
slug: caching
title: "Django Caching"
type: doc
order: 17
status: ready
maturity: unverified
tags: [django, caching, cache_page, cache.get, cache.set, locmem, Redis]
related: [django/03-settings, django/09-deployment]
when_to_use: "Read when adding cache_page, low-level cache.get/set, or a cache backend."
---
# Django Caching

## Purpose

Defines when Django may reuse a response or computed value.

## Rules

- Choose the backend explicitly (`Redis`, Memcached); do not use locmem in multi-process production.
- Never cache personalized responses under a key shared across users. Vary on cookies/auth or skip the cache.
- Give every cached value a TTL and an invalidation path (`cache.delete`, versioned keys, or signal on write).
- `cache_page` is for public, idempotent GET views only.
- Do not store secrets, raw `request.POST`, or unbounded querysets in the cache.

## Good Example

```python
from django.core.cache import cache

def published_home():
    key = "home:published:v1"
    payload = cache.get(key)
    if payload is None:
        payload = list(Invoice.objects.filter(status="open").values("id", "amount"))
        cache.set(key, payload, timeout=60)
    return payload
```

The key is versioned, public, and expires; a publish handler can `cache.delete("home:published:v1")`.

## Bad Example

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 60)
def dashboard(request):
    return render(request, "dashboard.html", {"user": request.user})
```

A shared page cache of a per-user dashboard leaks one user's data to the next.

## Checklist

- [ ] Production uses a shared cache backend, not locmem
- [ ] Personalized responses are not stored under a global key
- [ ] Every cache entry has a TTL and a delete/version path
- [ ] `cache_page` is limited to public GET views

## Related

- `django/03-settings`
- `django/09-deployment`
