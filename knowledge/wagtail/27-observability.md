---
id: wagtail/27-observability
topic: wagtail
slug: observability
title: "Wagtail Observability"
type: doc
order: 27
status: ready
maturity: unverified
tags: [wagtail, observability, page_published, getLogger]
related: [django/22-logging-and-observability, wagtail/12-deployment]
when_to_use: "Read when logging publish events, tracing page serve, or adding CMS metrics."
---
# Wagtail Observability

## Purpose

Defines logs and metrics for editorial and serve paths.

## Rules

- Follow Django logging rules: `getLogger`, no secrets, no `print`.
- Log publish/unpublish with page id, user id, and site/locale — not the full StreamField body.
- Health checks must not `save_revision` or hit search backends at INFO on every ping.
- Trace `serve()` slowness with query counts; do not log every rendition at INFO.
- Error trackers should include the page id when `serve` fails.

## Good Example

```python
import logging
from wagtail.signals import page_published

logger = logging.getLogger(__name__)

def log_publish(sender, instance, **kwargs):
    logger.info(
        "page.published",
        extra={"page_id": instance.pk, "slug": instance.slug},
    )

page_published.connect(log_publish)
```

Publish is an event with identifiers, not a dump of page fields.

## Bad Example

```python
def serve(self, request, *args, **kwargs):
    print(self.body)
    return super().serve(request, *args, **kwargs)
```

Printing StreamField JSON on every view leaks editor content and bypasses log levels.

## Checklist

- [ ] Publish/unpublish logs are identifiers, not full bodies
- [ ] Django logging rules apply
- [ ] Health checks stay quiet

## Related

- `django/22-logging-and-observability`
- `wagtail/12-deployment`
