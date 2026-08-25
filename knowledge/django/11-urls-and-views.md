---
id: django/11-urls-and-views
topic: django
slug: urls-and-views
title: "Django URLs and Views"
type: doc
order: 11
status: ready
maturity: unverified
tags: [django, urls-and-views, path, include, reverse, get_object_or_404, LoginRequiredMixin]
related: [django/02-architecture, django/06-security, django/15-authentication]
when_to_use: "Read when adding or changing URL routes, views, mixins, or reverse() names."
---
# Django URLs and Views

## Purpose

Defines how HTTP routes reach thin, authorized views.

## Rules

- Declare routes with `path()` / `re_path()` and `include()`; give every route a stable `name` for `reverse()`.
- Keep views as HTTP adapters: parse input, call domain code, return a response. Do not embed QuerySets and policy in the view beyond a few lines.
- Load objects with `get_object_or_404` (or an equivalent scoped queryset) so missing rows are 404, not uncaught `DoesNotExist`.
- Apply authentication and authorization in the view or mixin (`LoginRequiredMixin`, `PermissionRequiredMixin`, `user_passes_test`), not only in the template.
- Prefer class-based views only when the project already uses them; do not mix styles in one app without cause.

## Good Example

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import path

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice.objects.filter(owner=request.user), pk=pk)
    return render(request, "invoices/detail.html", {"invoice": invoice})

urlpatterns = [
    path("invoices/<int:pk>/", invoice_detail, name="invoice-detail"),
]
```

The queryset is already scoped to the owner; `reverse("invoice-detail", args=[pk])` stays stable.

## Bad Example

```python
def invoice_detail(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    return render(request, "invoices/detail.html", {"invoice": invoice})
```

An unauthenticated user can fetch any invoice, and a missing pk raises 500 instead of 404.

## Checklist

- [ ] Every new route has a stable `name` and is included from the root URLconf
- [ ] Views stay thin and delegate writes to explicit domain functions
- [ ] Object lookup is scoped and uses `get_object_or_404` or equivalent
- [ ] Authentication and authorization run in the view, not only in the template

## Related

- `django/02-architecture`
- `django/06-security`
- `django/15-authentication`
