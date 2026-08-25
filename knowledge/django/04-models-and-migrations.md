---
id: django/04-models-and-migrations
topic: django
slug: models-and-migrations
title: "Django Models and Migrations"
type: doc
order: 4
status: ready
maturity: unverified
tags: [django, models-and-migrations, ForeignKey, CheckConstraint, RunPython, SeparateDatabaseAndState]
related: [django/05-querysets-and-transactions, django/09-deployment]
when_to_use: "Read when changing models, constraints, or migration files."
---
# Django Models and Migrations

## Purpose

Defines safe schema and model evolution.

## Rules

- Represent invariants with database constraints (`CheckConstraint`, `UniqueConstraint`, `null=False`) when the database can enforce them.
- Review generated migrations; never edit an applied migration shared by other environments.
- Separate state and database operations with `SeparateDatabaseAndState` only with an explicit compatibility reason.
- Use staged expand-and-contract changes for large or zero-downtime deployments.
- Make `RunPython` data migrations deterministic, bounded, and reversible where practical.

## Good Example

```python
from django.db import models

class Order(models.Model):
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="order_quantity_positive",
            )
        ]
```

The database rejects invalid rows even when a caller bypasses the form.

## Bad Example

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(max_length=20),
        ),
    ]
```

Editing this file after it has already been applied on staging or production desynchronizes history. Create a new migration instead.

## Checklist

- [ ] Represent invariants with database constraints when the database can enforce them
- [ ] Review generated migrations; never edit an applied migration shared by other environments
- [ ] Separate state and database operations only with an explicit compatibility reason
- [ ] Use staged expand-and-contract changes for large or zero-downtime deployments
- [ ] Make data migrations deterministic, bounded, and reversible where practical

## Related

- `django/05-querysets-and-transactions`
- `django/09-deployment`
