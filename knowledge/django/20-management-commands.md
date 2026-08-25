---
id: django/20-management-commands
topic: django
slug: management-commands
title: "Django Management Commands"
type: doc
order: 20
status: ready
maturity: unverified
tags: [django, management-commands, BaseCommand, handle, call_command]
related: [django/05-querysets-and-transactions, django/07-testing]
when_to_use: "Read when adding django-admin commands, batch jobs invoked via manage.py, or call_command tests."
---
# Django Management Commands

## Purpose

Defines one-off and scheduled work that runs through `manage.py`.

## Rules

- Implement commands as `BaseCommand` subclasses with `handle()`; do not put production jobs in ad-hoc scripts that skip Django setup.
- Wrap multi-row writes in `transaction.atomic` and process QuerySets with `.iterator()` when the set is large.
- Accept options via `add_arguments`; do not parse `sys.argv` by hand.
- Make commands idempotent where practical and log progress on stderr via `self.stdout`.
- Test with `call_command` against the database, not by importing `handle` in isolation unless that is the unit under test.

## Good Example

```python
from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    help = "Close invoices older than the given days."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, required=True)

    def handle(self, *args, **options):
        with transaction.atomic():
            updated = Invoice.objects.filter(
                status="open", age_days__gte=options["days"]
            ).update(status="closed")
        self.stdout.write(f"closed {updated} invoices")
```

The command is option-driven, transactional, and testable with `call_command("close_invoices", days=30)`.

## Bad Example

```python
# scripts/close.py  (run with python scripts/close.py)
import django
django.setup()
Invoice.objects.all().update(status="closed")
```

The script skips argument parsing, transactions, and the project's command runner.

## Checklist

- [ ] New jobs are `BaseCommand` classes, not ad-hoc `django.setup()` scripts
- [ ] Bulk writes are transactional and bounded
- [ ] Commands are tested with `call_command`

## Related

- `django/05-querysets-and-transactions`
- `django/07-testing`
