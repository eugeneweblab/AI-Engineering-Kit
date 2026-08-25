---
id: django/18-admin
topic: django
slug: admin
title: "Django Admin"
type: doc
order: 18
status: ready
maturity: unverified
tags: [django, admin, ModelAdmin, list_display, get_queryset, has_change_permission]
related: [django/06-security, django/15-authentication]
when_to_use: "Read when registering ModelAdmin, changing list filters, or exposing models in /admin/."
---
# Django Admin

## Purpose

Defines a safe operator UI, not a public application.

## Rules

- Register only models operators must edit. Do not treat admin as the product API.
- Scope `get_queryset`, `has_view_permission`, `has_change_permission`, and `has_delete_permission` for non-superusers.
- Keep `list_display` and search fields cheap; avoid unbounded joins on the changelist.
- Never display secrets, hashes, or tokens in `list_display` or `fields`.
- Protect `/admin/` with staff auth, HTTPS, and rate limiting at the edge.

## Good Example

```python
from django.contrib import admin

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "amount", "status")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)
```

Non-superusers only see their rows.

## Bad Example

```python
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "secret_token", "raw_payload")
```

The changelist dumps secrets and unbounded JSON to any staff user.

## Checklist

- [ ] Admin is scoped with `get_queryset` and permission hooks
- [ ] `list_display` has no secrets and no unbounded relations
- [ ] `/admin/` is not used as the public write API

## Related

- `django/06-security`
- `django/15-authentication`
