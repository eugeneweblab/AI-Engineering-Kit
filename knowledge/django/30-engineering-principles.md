---
id: django/30-engineering-principles
topic: django
slug: engineering-principles
title: "Django Engineering Principles"
type: doc
order: 30
status: ready
maturity: unverified
tags: [django, engineering-principles]
related: [django/00-overview, django/02-architecture, django/06-security]
when_to_use: "Read when a Django change spans several topics and you need the default decision order."
---
# Django Engineering Principles

## Purpose

States the decision order for Django work when several documents could apply.

## Rules

- Detect installed Django and Python versions first; APIs from another line are out of scope.
- Prefer the framework feature that already exists in the project (`ModelForm`, `select_related`, `transaction.atomic`) over a new library.
- Keep HTTP handlers thin, policy explicit, and authorization on the server.
- Schema, queues, and cache invalidation are part of the change, not follow-up tickets.
- Finish with the production checklist, the AI review checklist, and the antipatterns list.

## Good Example

```python
def create_invoice(request):
    form = InvoiceForm(request.POST)
    if not form.is_valid():
        return render(request, "invoices/form.html", {"form": form})
    invoice = form.save(commit=False)
    invoice.owner = request.user
    invoice.save()
    return redirect("invoice-detail", pk=invoice.pk)
```

Validation, ownership, and a named redirect are all in the same change.

## Bad Example

```python
def create_invoice(request):
    Invoice.objects.create(**request.POST.dict())
    return HttpResponse("ok")
```

The handler skips validation, ownership, CSRF-safe form rendering, and a stable URL.

## Checklist

- [ ] Versions were read from the lock file
- [ ] Existing framework APIs were reused
- [ ] Authorization, schema, and tests shipped with the change
- [ ] Checklists 98, 99, and 100 were run

## Related

- `django/00-overview`
- `django/02-architecture`
- `django/06-security`
