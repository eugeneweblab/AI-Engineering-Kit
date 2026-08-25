---
id: django/05-querysets-and-transactions
topic: django
slug: querysets-and-transactions
title: "Django QuerySets and Transactions"
type: doc
order: 5
status: ready
maturity: unverified
tags: [django, querysets-and-transactions, select_related, prefetch_related, transaction.atomic, select_for_update, F]
related: [django/04-models-and-migrations, django/07-testing]
when_to_use: "Read when writing QuerySets, preventing N+1 queries, or wrapping writes in transactions."
---
# Django QuerySets and Transactions

## Purpose

Defines correct data access and concurrency behavior.

## Rules

- Evaluate QuerySets intentionally and prevent N+1 access with `select_related` or `prefetch_related` after measuring query shape.
- Wrap only the atomic unit of work in `transaction.atomic`; do not hold transactions across network calls.
- Use `select_for_update` or database constraints when correctness depends on concurrent writers.
- Do not catch database exceptions inside the atomic block whose rollback they require.
- Use `F` expressions for race-safe in-database updates when appropriate.

## Good Example

```python
from django.db import transaction
from django.db.models import F

orders = (
    Order.objects.select_related("user")
    .prefetch_related("items__product")
    .filter(status="open")
)
with transaction.atomic():
    Order.objects.filter(pk=order_id).select_for_update().update(
        quantity=F("quantity") + 1
    )
```

Related rows load in bounded queries; the increment happens in the database under a row lock.

## Bad Example

```python
for order in Order.objects.all():
    print(order.user.email)
    order.quantity += 1
    order.save()
```

Each iteration hits the user table (N+1) and the increment races under concurrent writers.

## Checklist

- [ ] Evaluate QuerySets intentionally and prevent N+1 access with `select_related` or `prefetch_related` after measuring query shape
- [ ] Wrap only the atomic unit of work in `transaction.atomic`
- [ ] Use `select_for_update` or database constraints when correctness depends on concurrent writers
- [ ] Do not catch database exceptions inside the atomic block whose rollback they require
- [ ] Use `F` expressions for race-safe in-database updates when appropriate

## Related

- `django/04-models-and-migrations`
- `django/07-testing`
