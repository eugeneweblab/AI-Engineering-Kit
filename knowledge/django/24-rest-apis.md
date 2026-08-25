---
id: django/24-rest-apis
topic: django
slug: rest-apis
title: "Django REST APIs"
type: doc
order: 24
status: ready
maturity: unverified
tags: [django, rest-apis, JsonResponse, serializer, permission_classes, authentication_classes]
related: [django/06-security, django/11-urls-and-views, rest-api/03-resource-design]
when_to_use: "Read when adding JSON endpoints, serializers, or token/session API authentication."
---
# Django REST APIs

## Purpose

Defines JSON HTTP APIs built on Django, including Django REST framework when the project uses it.

## Rules

- Follow the project's existing API library (Django REST framework, Django Ninja, plain views). Do not add a second framework.
- Whitelist serializer/output fields; never dump `model.__dict__` or an unsliced queryset.
- Put authentication and permissions on the view (`authentication_classes`, `permission_classes`, or equivalent). Session-cookie APIs keep CSRF.
- Return explicit status codes (201 create, 204 delete, 400 validation, 403/404 as in the error-handling doc).
- Paginate list endpoints; test unauthorized and invalid bodies.

## Good Example

```python
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def invoice_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)
    invoices = Invoice.objects.filter(owner=request.user).values("id", "amount", "status")
    return JsonResponse({"results": list(invoices)})
```

The payload is a whitelist and scoped to the owner.

## Bad Example

```python
def invoice_list(request):
    data = [invoice.__dict__ for invoice in Invoice.objects.all()]
    return JsonResponse(data, safe=False)
```

Every column, including secrets, is published with no auth and no pagination.

## Checklist

- [ ] Output fields are explicit and scoped to the caller
- [ ] Auth and CSRF match the chosen credential type
- [ ] List endpoints are paginated; 401/403/400 are tested

## Related

- `django/06-security`
- `django/11-urls-and-views`
- `rest-api/03-resource-design`
