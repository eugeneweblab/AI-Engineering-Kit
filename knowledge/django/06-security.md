---
id: django/06-security
topic: django
slug: security
title: "Django Security"
type: doc
order: 6
status: ready
maturity: unverified
tags: [django, security, csrf_exempt, mark_safe, extra, raw, PermissionDenied]
related: [django/03-settings, django/09-deployment, django/15-authentication]
when_to_use: "Read when changing authentication, authorization, CSRF, uploads, raw SQL, or HTML escaping."
---
# Django Security

## Purpose

Defines secure request, authentication, and deployment boundaries.

## Rules

- Enforce authorization server-side for every object and mutation; authentication alone is not authorization. Raise `PermissionDenied` or return 404, do not hide buttons only.
- Keep CSRF protection enabled for cookie-authenticated unsafe requests; do not add `csrf_exempt` without a documented non-cookie auth scheme.
- Use ORM parameters and Django escaping; review `extra`, `RawSQL`, `raw()`, `mark_safe`, `SafeString`, and user-controlled redirects as dangerous sinks.
- Validate uploaded file type, size, storage location, and access policy.
- Install security patches promptly and run `check --deploy` with production settings.

## Good Example

```python
from django.core.exceptions import PermissionDenied

def invoice_detail(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    if invoice.owner_id != request.user.id and not request.user.is_staff:
        raise PermissionDenied
    return render(request, "invoices/detail.html", {"invoice": invoice})
```

Object ownership is checked in the view before any data is rendered.

## Bad Example

```python
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def comment(request):
    html = mark_safe(request.POST["body"])
    return HttpResponse(html)
```

Disabling CSRF and marking request data safe turns user input into an HTML and state-changing sink.

## Checklist

- [ ] Enforce authorization server-side for every object and mutation
- [ ] Keep CSRF protection enabled for cookie-authenticated unsafe requests
- [ ] Use ORM parameters and Django escaping
- [ ] Validate uploaded file type, size, storage location, and access policy
- [ ] Install security patches promptly and run `check --deploy` with production settings

## Related

- `django/03-settings`
- `django/09-deployment`
- `django/15-authentication`
