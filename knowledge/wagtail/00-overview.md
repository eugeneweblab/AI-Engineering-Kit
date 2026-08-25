---
id: wagtail/00-overview
topic: wagtail
slug: overview
title: "Wagtail Overview"
type: doc
order: 0
status: ready
maturity: unverified
tags: [wagtail, overview, Page, StreamField]
related: [wagtail/01-version-compatibility, django/00-overview]
when_to_use: "Read first when working in a Wagtail repository, including when wagtail_hooks.py is absent."
---
# Wagtail Overview

## Purpose

Routes Wagtail CMS work to Django-aware rules.

## Rules

- Treat Wagtail as a Django application and apply both Wagtail and Django rules.
- Detect Wagtail from `wagtail` imports, `Page` subclasses, `StreamField`, or `wagtail_hooks.py` — not only from one filename.
- Detect Wagtail, Django, and Python versions from the lock file before selecting APIs.
- Preserve editorial workflows, revisions, permissions, locale, and tree invariants in every content change.

## Good Example

```python
from wagtail.models import Page

class HomePage(Page):
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["home.StandardPage"]
```

The change is a `Page` subclass with an explicit tree contract, then Django rules still apply to its migrations.

## Bad Example

```python
from django.db import connection

connection.cursor().execute(
    "UPDATE wagtailcore_page SET live = TRUE WHERE id = %s",
    [page_id],
)
```

Updating `wagtailcore_page` directly skips revisions, permissions, and tree integrity.

## Checklist

- [ ] Wagtail was detected from imports or `Page` / `StreamField`, not guessed from the ticket
- [ ] Django rules were applied as well as Wagtail rules
- [ ] Versions were read from the lock file
- [ ] Editorial workflow, revisions, permissions, locale, and tree invariants were preserved

## Related

- `wagtail/01-version-compatibility`
- `django/00-overview`
