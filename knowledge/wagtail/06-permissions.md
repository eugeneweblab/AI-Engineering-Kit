---
id: wagtail/06-permissions
topic: wagtail
slug: permissions
title: "Wagtail Permissions"
type: doc
order: 6
status: ready
maturity: unverified
tags: [wagtail, permissions, page_permissions, Collection, ModelPermissionPolicy]
related: [django/06-security, wagtail/05-revisions-and-workflows]
when_to_use: "Read when changing Wagtail groups, page permissions, collections, or admin actions."
---
# Wagtail Permissions

## Purpose

Defines admin and content authorization.

## Rules

- Enforce permissions in server-side views, APIs, hooks, and actions; hiding admin UI is insufficient.
- Respect collection, page, locale, and workflow permissions when resolving objects.
- Use Wagtail permission policies and groups instead of duplicating authorization logic.
- Test users with no access, partial subtree access, and cross-site or cross-locale access.

## Good Example

```python
from django.http import JsonResponse
from wagtail.models import Page

def article_api(request, pk):
    page = (
        Page.objects.live()
        .public()
        .specific()
        .get(pk=pk)
    )
    return JsonResponse({"title": page.title})
```

`live().public()` excludes drafts and private pages before any field is serialized.

## Bad Example

```
{% if request.user.is_staff %}
  <a href="{{ page.url }}">{{ page.title }}</a>
{% endif %}
```

Hiding a link in the template does not stop a crafted GET to the draft or private URL.

## Checklist

- [ ] Permissions are enforced in views, APIs, hooks, and actions
- [ ] Collection, page, locale, and workflow permissions are respected
- [ ] Wagtail permission policies are reused
- [ ] Tests cover no access, partial subtree, and cross-site/locale users

## Related

- `django/06-security`
- `wagtail/05-revisions-and-workflows`
