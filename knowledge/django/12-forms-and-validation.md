---
id: django/12-forms-and-validation
topic: django
slug: forms-and-validation
title: "Django Forms and Validation"
type: doc
order: 12
status: ready
maturity: unverified
tags: [django, forms-and-validation, ModelForm, ValidationError, clean, is_valid]
related: [django/06-security, django/11-urls-and-views, django/13-templates]
when_to_use: "Read when adding ModelForm, Form, clean_* methods, or processing POST bodies."
---
# Django Forms and Validation

## Purpose

Defines how user input is validated before it reaches the database.

## Rules

- Accept mutating input through `Form` or `ModelForm`; do not write `request.POST` straight onto a model.
- Put cross-field rules in `clean()` and per-field rules in `clean_<field>()`; raise `ValidationError`.
- Re-render the bound form on `is_valid()` failure so field errors reach the template.
- Keep CSRF on cookie-authenticated POST forms; include `{% csrf_token %}` in the template.
- Bound-file validation must check type and size, not only the filename extension.

## Good Example

```python
from django import forms
from django.core.exceptions import ValidationError

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ("amount", "currency")

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise ValidationError("Amount must be positive.")
        return amount
```

Invalid amounts never reach `Invoice.objects.create`.

## Bad Example

```python
def create_invoice(request):
    Invoice.objects.create(
        owner=request.user,
        amount=request.POST["amount"],
        currency=request.POST["currency"],
    )
```

Missing keys, negative amounts, and CSRF-unsafe clients all hit the database.

## Checklist

- [ ] Mutating views use a `Form` or `ModelForm`, not raw `request.POST`
- [ ] `clean()` / `clean_<field>()` raise `ValidationError` for domain rules
- [ ] Invalid POSTs re-render the bound form
- [ ] CSRF token is present on cookie-authenticated forms

## Related

- `django/06-security`
- `django/11-urls-and-views`
- `django/13-templates`
