---
id: wagtail/09-headless-api
topic: wagtail
slug: headless-api
title: "Wagtail Headless API"
type: doc
order: 9
status: ready
maturity: unverified
tags: [wagtail, headless-api, WagtailAPIRouter, pages, DRAFT]
related: [rest-api/03-resource-design, wagtail/05-revisions-and-workflows]
when_to_use: "Read when exposing Pages over the v2 API, GraphQL, or a custom headless serializer."
---
# Wagtail Headless API

## Purpose

Defines safe API exposure of CMS content.

## Rules

- Whitelist exposed fields and serializers; do not publish model internals by default.
- Filter by live state, site, locale, and permissions before serialization.
- Design preview authentication separately from the public API.
- Version response contracts and test cache invalidation after publish and unpublish events.

## Good Example

```python
from wagtail.api.v2.views import PagesAPIViewSet

class ArticleAPIViewSet(PagesAPIViewSet):
    model = ArticlePage
    body_fields = ["title", "body", "hero"]
```

Only listed fields leave the CMS; drafts stay off the public endpoint.

## Bad Example

```python
def pages_api(request):
    return JsonResponse(
        {"pages": list(Page.objects.values())},
        safe=False,
    )
```

`values()` on all pages leaks drafts, internal path/depth, and unpublished titles.

## Checklist

- [ ] Exposed fields are an explicit whitelist
- [ ] Live, site, locale, and permission filters run before serialize
- [ ] Preview auth is separate from the public API
- [ ] Publish/unpublish cache invalidation is tested

## Related

- `rest-api/03-resource-design`
- `wagtail/05-revisions-and-workflows`
