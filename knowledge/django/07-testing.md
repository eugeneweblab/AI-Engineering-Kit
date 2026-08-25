---
id: django/07-testing
topic: django
slug: testing
title: "Django Testing"
type: doc
order: 7
status: ready
maturity: unverified
tags: [django, testing, TestCase, TransactionTestCase, Client, RequestFactory]
related: [django/01-version-support, django/05-querysets-and-transactions]
when_to_use: "Read when adding Django tests, factories, or assertions against the database and HTTP stack."
---
# Django Testing

## Purpose

Defines regression tests that exercise real framework boundaries.

## Rules

- Use `TestCase` for transactional isolation and `TransactionTestCase` only when commit or locking behavior is under test.
- Test permissions, validation errors, missing objects, and concurrent invariants, not only successful responses.
- Prefer persisted database assertions over mock call counts.
- Use the actual URL configuration, middleware, templates, and settings for integration behavior (`Client`), and `RequestFactory` only for isolated view units.
- Run migration checks and tests on every supported Django/Python combination.

## Good Example

```python
from django.test import TestCase

class InvoiceViewTests(TestCase):
    def test_owner_can_get_invoice(self):
        user = User.objects.create_user("ada", password="x")
        invoice = Invoice.objects.create(owner=user)
        self.client.force_login(user)
        response = self.client.get(f"/invoices/{invoice.pk}/")
        self.assertEqual(response.status_code, 200)

    def test_stranger_is_forbidden(self):
        owner = User.objects.create_user("ada", password="x")
        stranger = User.objects.create_user("bob", password="x")
        invoice = Invoice.objects.create(owner=owner)
        self.client.force_login(stranger)
        response = self.client.get(f"/invoices/{invoice.pk}/")
        self.assertEqual(response.status_code, 403)
```

The failure path is a first-class test, not an afterthought.

## Bad Example

```python
from unittest.mock import patch

@patch("app.views.Invoice.objects")
def test_invoice_called(self, mock_objects):
    self.client.get("/invoices/1/")
    mock_objects.get.assert_called()
```

Asserting a mock call count does not prove authorization, status codes, or persisted state.

## Checklist

- [ ] Use `TestCase` for transactional isolation and `TransactionTestCase` only when commit or locking behavior is under test
- [ ] Test permissions, validation errors, missing objects, and concurrent invariants, not only successful responses
- [ ] Prefer persisted database assertions over mock call counts
- [ ] Use the actual URL configuration, middleware, templates, and settings for integration behavior
- [ ] Run migration checks and tests on every supported Django/Python combination

## Related

- `django/01-version-support`
- `django/05-querysets-and-transactions`
