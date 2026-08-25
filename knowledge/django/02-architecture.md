---
id: django/02-architecture
topic: django
slug: architecture
title: "Django Architecture"
type: doc
order: 2
status: ready
maturity: unverified
tags: [django, architecture, apps, AppConfig]
related: [django/04-models-and-migrations, django/05-querysets-and-transactions, django/11-urls-and-views]
when_to_use: "Read when adding apps, placing business rules, or introducing services, managers, or signals."
---
# Django Architecture

## Purpose

Defines boundaries for Django applications and domain code.

## Rules

- Organize apps around cohesive business capabilities, not one app per database table.
- Keep views thin and place reusable policy in explicit services, model methods, managers, or selectors according to project convention.
- Avoid `pre_save` / `post_save` signal-based control flow for core business operations; make important writes explicit and testable.
- Do not introduce a repository layer unless it provides a real boundary beyond the ORM.

## Good Example

```python
def place_order(user, payload):
    order = Order.objects.create_for_user(user, payload)
    order.charge()
    return order
```

The write path is a named function the view calls; tests can invoke it without going through signals.

## Bad Example

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Order)
def charge_on_save(sender, instance, created, **kwargs):
    if created:
        instance.charge()
```

Hiding checkout inside `post_save` makes retries, bulk creates, and tests implicit and easy to skip.

## Checklist

- [ ] Organize apps around cohesive business capabilities, not one app per database table
- [ ] Keep views thin and place reusable policy in explicit services, model methods, managers, or selectors according to project convention
- [ ] Avoid signal-based control flow for core business operations
- [ ] Do not introduce a repository layer unless it provides a real boundary beyond the ORM

## Related

- `django/04-models-and-migrations`
- `django/05-querysets-and-transactions`
- `django/11-urls-and-views`
