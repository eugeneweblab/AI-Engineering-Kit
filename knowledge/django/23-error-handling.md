---
id: django/23-error-handling
topic: django
slug: error-handling
title: "Django Error Handling"
type: doc
order: 23
status: ready
maturity: unverified
tags: [django, error-handling, Http404, PermissionDenied, ValidationError, SuspiciousOperation]
related: [django/06-security, django/11-urls-and-views, django/12-forms-and-validation]
when_to_use: "Read when mapping exceptions to HTTP status, writing handlers, or catching ORM errors."
---
# Django Error Handling

## Purpose

Defines which exceptions become which HTTP responses.

## Rules

- Raise `Http404` for missing objects, `PermissionDenied` for forbidden ones, and `ValidationError` inside forms. Do not convert all failures to 500.
- Let `SuspiciousOperation` and CSRF failures stay 400/403; do not catch and ignore them.
- Do not catch `IntegrityError` inside `transaction.atomic` if you still need the rollback of that block; handle it outside or use a nested atomic savepoint.
- Custom `handler404` / `handler500` must not leak `DEBUG` traces in production.
- Tests must cover 403, 404, and validation failures, not only 200.

## Good Example

```python
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if invoice.owner_id != request.user.id:
        raise PermissionDenied
    return render(request, "invoices/detail.html", {"invoice": invoice})
```

Missing rows are 404; other people's rows are 403.

## Bad Example

```python
def invoice_detail(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Exception:
        return JsonResponse({"error": "nope"}, status=200)
    return render(request, "invoices/detail.html", {"invoice": invoice})
```

A bare `except` turns missing rows, permission bugs, and programming errors into a 200.

## Checklist

- [ ] Missing vs forbidden vs invalid are distinct status codes
- [ ] CSRF and `SuspiciousOperation` are not swallowed
- [ ] Failure paths have tests

## Related

- `django/06-security`
- `django/11-urls-and-views`
- `django/12-forms-and-validation`
