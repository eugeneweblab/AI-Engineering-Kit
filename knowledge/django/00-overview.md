---
id: django/00-overview
topic: django
slug: overview
title: "Django Overview"
type: doc
order: 0
status: ready
maturity: unverified
tags: [django, overview, manage.py, DJANGO_SETTINGS_MODULE]
related: [django/01-version-support, django/02-architecture, django/98-production-checklist]
when_to_use: "Read first when working in a Django repository, before choosing APIs or files to change."
---
# Django Overview

## Purpose

Routes Django work to the applicable, version-aware rules.

## Rules

- Identify Django and Python versions from resolved dependencies (`requirements.txt`, `poetry.lock`, `uv.lock`, `pyproject.toml`), not from task prose.
- Prefer framework APIs and existing project patterns over parallel abstractions.
- Treat migrations, authorization, transactions, and deployment settings as correctness boundaries.
- After detecting `manage.py`, keep reading topic documents that match the change (`path`, `ModelForm`, `select_related`), not only the stack starter set.

## Good Example

```python
import django

print(django.get_version())
```

Record that version in the change notes, then apply the matching topic rules and add a regression test for the failure path.

## Bad Example

```python
from django.conf import settings

settings.DEBUG = False
```

Mutating `settings` at runtime hides the real environment and does not prove the installed Django line is supported.

## Checklist

- [ ] Identify Django and Python versions from resolved dependencies, not from task prose
- [ ] Prefer framework APIs and existing project patterns over parallel abstractions
- [ ] Treat migrations, authorization, transactions, and deployment settings as correctness boundaries
- [ ] Read the topic document that governs the API being changed

## Related

- `django/01-version-support`
- `django/02-architecture`
- `django/98-production-checklist`
