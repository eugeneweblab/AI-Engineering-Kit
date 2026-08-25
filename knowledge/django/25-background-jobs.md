---
id: django/25-background-jobs
topic: django
slug: background-jobs
title: "Django Background Jobs"
type: doc
order: 25
status: ready
maturity: unverified
tags: [django, background-jobs, delay, apply_async, on_commit, Celery]
related: [django/05-querysets-and-transactions, django/20-management-commands]
when_to_use: "Read when enqueueing Celery/RQ/Huey tasks or moving work off the request thread."
---
# Django Background Jobs

## Purpose

Defines asynchronous work that must not run inside the request/response cycle.

## Rules

- Use the project's existing worker (Celery, RQ, Huey, Cloud Tasks). Do not start threads or `subprocess` from a view to "do it later".
- Enqueue after a successful commit (`transaction.on_commit`) so workers do not see uncommitted rows.
- Tasks must be idempotent: retries will happen.
- Pass IDs, not ORM instances, into the queue.
- Do not `sleep()` or call slow HTTP APIs in a request thread when a job queue exists.

## Good Example

```python
from django.db import transaction

def create_invoice(user, payload):
    invoice = Invoice.objects.create(owner=user, **payload)

    def enqueue():
        send_invoice_email.delay(invoice.pk)

    transaction.on_commit(enqueue)
    return invoice
```

The worker loads the row by primary key after commit.

## Bad Example

```python
import threading

def create_invoice(user, payload):
    invoice = Invoice.objects.create(owner=user, **payload)
    threading.Thread(target=invoice.send_email).start()
    return invoice
```

A request-scoped thread has no retry, no observability, and can exit with the worker process.

## Checklist

- [ ] Slow work goes to the existing queue, not a request thread
- [ ] Enqueue runs on `transaction.on_commit`
- [ ] Tasks receive IDs and are safe to retry

## Related

- `django/05-querysets-and-transactions`
- `django/20-management-commands`
