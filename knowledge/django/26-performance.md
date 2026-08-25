---
id: django/26-performance
topic: django
slug: performance
title: "Django Performance"
type: doc
order: 26
status: ready
maturity: unverified
tags: [django, performance, select_related, prefetch_related, iterator, only, Count]
related: [django/05-querysets-and-transactions, django/17-caching]
when_to_use: "Read when fixing N+1 queries, slow views, or large QuerySet iteration."
---
# Django Performance

## Purpose

Defines how to keep request query counts and memory bounded.

## Rules

- Measure with `assertNumQueries` or the project's profiler before adding `select_related`, `prefetch_related`, `only`, or `defer`.
- Iterate large QuerySets with `.iterator()` so rows are not all cached in memory.
- Aggregate in the database (`Count`, `Sum`, `annotate`) instead of looping in Python.
- Paginate lists; never ship `Model.objects.all()` to a template or JSON encoder.
- Cache only after the query shape is correct; cache does not fix N+1.

## Good Example

```python
from django.db.models import Count

invoices = (
    Invoice.objects.filter(owner=request.user)
    .select_related("owner")
    .annotate(item_count=Count("items"))
    .order_by("-id")[:50]
)
```

The page is sliced, relations are joined, and the count is one query.

## Bad Example

```python
total = 0
for invoice in Invoice.objects.all():
    total += invoice.items.count()
```

This is N+1 plus an unbounded table scan.

## Checklist

- [ ] Related access is prefetched after measuring query count
- [ ] Large scans use `.iterator()` and database aggregation
- [ ] Lists are paginated or sliced

## Related

- `django/05-querysets-and-transactions`
- `django/17-caching`
