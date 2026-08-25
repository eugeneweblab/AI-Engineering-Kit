---
id: django/10-upgrades
topic: django
slug: upgrades
title: "Django Upgrades"
type: doc
order: 10
status: ready
maturity: unverified
tags: [django, upgrades, django-admin, RemovedInDjango]
related: [django/01-version-support, django/07-testing]
when_to_use: "Read when upgrading Django or Python, or resolving deprecation warnings."
---
# Django Upgrades

## Purpose

Defines safe movement between Django minor and major versions.

## Rules

- Upgrade one Django minor line at a time and read all intervening release notes.
- Resolve deprecation warnings on the current release before moving to the next major release.
- Upgrade Python and Django separately unless a compatibility constraint makes that impossible.
- Check database backend, middleware, template engine, and third-party app compatibility before changing the lock file.
- Keep rollback possible until migrations and production behavior are verified.

## Good Example

```python
# Current: Django 5.2.17. Next step: Django 6.0.x, not 6.1.
import django

assert django.VERSION[:2] == (5, 2)
```

The project clears 5.2 deprecations, then moves to 6.0, then to 6.1. Each step has its own test run.

## Bad Example

```python
# pip install 'Django==6.1'  # jumped from 4.2 in one commit
from django.conf import settings
```

Skipping minor lines hides removed APIs and unapplied release notes until production import errors.

## Checklist

- [ ] Upgrade one Django minor line at a time and read all intervening release notes
- [ ] Resolve deprecation warnings on the current release before moving to the next major release
- [ ] Upgrade Python and Django separately unless a compatibility constraint makes that impossible
- [ ] Check database backend, middleware, template engine, and third-party app compatibility before changing the lock file
- [ ] Keep rollback possible until migrations and production behavior are verified

## Related

- `django/01-version-support`
- `django/07-testing`
