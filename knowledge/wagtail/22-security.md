---
id: wagtail/22-security
topic: wagtail
slug: security
title: "Wagtail Security"
type: doc
order: 22
status: ready
maturity: unverified
tags: [wagtail, security, PageViewRestriction, serve, mark_safe]
related: [django/06-security, wagtail/06-permissions]
when_to_use: "Read when changing private pages, document serving, or editor HTML rendering."
defers_to: django/06-security
---
# Wagtail Security

## Purpose

Defines CMS-specific security on top of Django's rules. Django security owns CSRF, XSS sinks, and auth cookies.

## Rules

- Honor `PageViewRestriction` / private pages in custom views and APIs; `live()` is not the same as `public()`.
- Serve documents through Wagtail's document serve view (or an equivalent authz check); do not expose `MEDIA_ROOT` as world-readable for private collections.
- Escape StreamField/RichText output; `|richtext` and `|safe` are sinks when the source is not the editor pipeline.
- Admin and preview URLs must require auth; do not cache them.
- Apply Django security rules to every custom view.

## Good Example

```python
from wagtail.models import Page

pages = Page.objects.live().public().descendant_of(site.root_page)
```

Private and draft pages are excluded before render.

## Bad Example

```python
return FileResponse(open(document.file.path, "rb"))
```

Streaming a private document by filesystem path skips collection permissions and range/content-type policy.

## Checklist

- [ ] Custom queries use `live().public()` (or an equivalent restriction check)
- [ ] Private documents are not served as static files
- [ ] Django CSRF/XSS/auth rules still apply
- [ ] Preview/admin are authenticated and uncached

## Related

- `django/06-security`
- `wagtail/06-permissions`
