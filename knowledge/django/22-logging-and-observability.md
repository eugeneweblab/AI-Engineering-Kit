---
id: django/22-logging-and-observability
topic: django
slug: logging-and-observability
title: "Django Logging and Observability"
type: doc
order: 22
status: ready
maturity: unverified
tags: [django, logging-and-observability, LOGGING, getLogger, request_id]
related: [django/03-settings, django/09-deployment]
when_to_use: "Read when changing LOGGING, adding loggers, request IDs, or error reporting."
---
# Django Logging and Observability

## Purpose

Defines how Django processes emit searchable logs without leaking secrets.

## Rules

- Configure logging in `LOGGING`; use `logging.getLogger(__name__)`, not `print()`.
- Include request identifiers where middleware sets them; keep log format structured enough to search.
- Never log `SECRET_KEY`, passwords, tokens, authorization headers, or full payment payloads.
- Send unhandled exceptions to the project's error tracker; do not swallow them in views.
- Health checks should not log at INFO on every hit.

## Good Example

```python
import logging

logger = logging.getLogger(__name__)

def invoice_detail(request, pk):
    logger.info("invoice.viewed", extra={"invoice_id": pk, "user_id": request.user.pk})
    return render(request, "invoices/detail.html")
```

The log line is an event name plus identifiers, not a interpolated secret.

## Bad Example

```python
def invoice_detail(request, pk):
    print(request.headers["Authorization"], request.POST)
    invoice = Invoice.objects.get(pk=pk)
    return render(request, "invoices/detail.html", {"invoice": invoice})
```

`print` bypasses log levels and dumps credentials and POST bodies.

## Checklist

- [ ] New log sites use `getLogger`, not `print`
- [ ] Secrets and raw request bodies are not logged
- [ ] Unhandled errors still reach the error tracker

## Related

- `django/03-settings`
- `django/09-deployment`
