---
id: wagtail/07-search
topic: wagtail
slug: search
title: "Wagtail Search"
type: doc
order: 7
status: ready
maturity: unverified
tags: [wagtail, search, search_fields, update_index, autocomplete]
related: [wagtail/03-page-models, wagtail/12-deployment]
when_to_use: "Read when changing search_fields, backends, or rebuild-index jobs."
---
# Wagtail Search

## Purpose

Defines predictable indexing and querying.

## Rules

- Declare `search_fields` deliberately and rebuild indexes after incompatible schema changes (`wagtail update_index`).
- Use the configured backend's supported operators; database and Elasticsearch/OpenSearch behavior can differ.
- Apply live, site, locale, and permission filters before returning results.
- Measure query counts and index freshness, and define behavior while indexing is delayed.

## Good Example

```python
from wagtail.search.models import Query

results = (
    ArticlePage.objects.live()
    .public()
    .filter(locale=request.locale)
    .search(query_string)
)
```

Search runs on an already-filtered live/public/locale queryset.

## Bad Example

```python
results = Page.objects.search(query_string)
```

Unfiltered `Page.objects.search` can return drafts, other sites, and pages the user cannot view.

## Checklist

- [ ] `search_fields` match the fields editors expect to find
- [ ] Indexes are rebuilt after incompatible schema changes
- [ ] Results are filtered by live, site, locale, and permission
- [ ] Backend-specific operators are not assumed portable

## Related

- `wagtail/03-page-models`
- `wagtail/12-deployment`
