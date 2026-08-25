---
id: django/08-async
topic: django
slug: async
title: "Django Async and ASGI"
type: doc
order: 8
status: ready
maturity: unverified
tags: [django, async, ASGI, sync_to_async, async_to_sync, aclose]
related: [django/01-version-support, django/09-deployment]
when_to_use: "Read when adding async views, ASGI, Channels, or mixing sync ORM code with async."
---
# Django Async and ASGI

## Purpose

Defines safe use of async Django code.

## Rules

- Use async only across an end-to-end async call path; avoid sync-to-async bouncing.
- Do not call async-unsafe ORM or middleware code from an async context without `sync_to_async`.
- Keep blocking CPU or network work off the event loop.
- Test under the production ASGI server when deploying ASGI behavior.

## Good Example

```python
from asgiref.sync import sync_to_async

async def order_status(request, pk):
    order = await Order.objects.aget(pk=pk)
    return JsonResponse({"status": order.status})


@sync_to_async
def write_audit(order_id, message):
    Audit.objects.create(order_id=order_id, message=message)
```

ORM reads use async QuerySet APIs; unavoidable sync writes are wrapped once at the boundary.

## Bad Example

```python
async def order_status(request, pk):
    order = Order.objects.get(pk=pk)
    requests.get("https://billing.example/charge")
    return JsonResponse({"status": order.status})
```

Calling the sync ORM and a blocking HTTP client from an async view stalls the event loop and is async-unsafe.

## Checklist

- [ ] Use async only across an end-to-end async call path
- [ ] Do not call async-unsafe ORM or middleware code from an async context without `sync_to_async`
- [ ] Keep blocking CPU or network work off the event loop
- [ ] Test under the production ASGI server when deploying ASGI behavior

## Related

- `django/01-version-support`
- `django/09-deployment`
