---
id: django/01-version-support
topic: django
slug: version-support
title: "Django Version Support"
type: doc
order: 1
status: ready
maturity: unverified
tags: [django, version-support, LTS, get_version]
related: [django/10-upgrades, wagtail/01-version-compatibility]
when_to_use: "Read before choosing framework APIs or changing Django or Python dependencies."
verified_against: "Django 5.2 LTS, 6.0, and 6.1; legacy 4.2 LTS"
source_urls: ["https://www.djangoproject.com/download/", "https://docs.djangoproject.com/en/6.1/faq/install/", "https://docs.djangoproject.com/en/6.1/releases/"]
last_reviewed: "2026-08-25"
review_after: "2026-11-25"
---
# Django Version Support

## Purpose

Defines version selection and upgrade policy for maintained Django lines.

## Rules

- Pin a supported Django minor line and latest patched release; never use an unsupported line for new work.
- As of 2026-08-25, supported lines are Django 5.2 LTS, 6.0, and 6.1; Django 4.2 LTS is legacy and no longer receives fixes.
- Django 5.2 supports Python 3.10 through 3.14, while Django 6.0 and 6.1 require Python 3.12 or newer.
- Gate APIs by the installed minor version and read every intervening release note during upgrades.
- Test reusable apps against the oldest and newest supported Django/Python combinations.
- For Wagtail projects, intersect Django compatibility with the installed Wagtail release before changing either dependency.

## Good Example

```python
# pyproject.toml: django>=5.2.17,<5.3
import django

assert django.VERSION[:2] >= (5, 2)
```

The lock file pins a supported line; code that needs 6.x APIs is gated on `django.VERSION`, not on memory of the latest release.

## Bad Example

```python
from django.db.models import GeneratedField
```

Importing a field class from a newer line than the lock file allows produces code that may import in development and fail in production.

## Checklist

- [ ] Pin a supported Django minor line and latest patched release
- [ ] The selected line is Django 5.2 LTS, 6.0, or 6.1 unless maintaining an explicitly accepted legacy system
- [ ] The selected Python version is supported by that Django line
- [ ] Gate APIs by the installed minor version and read every intervening release note during upgrades
- [ ] Test reusable apps against the oldest and newest supported Django/Python combinations
- [ ] For Wagtail projects, intersect Django compatibility with the installed Wagtail release before changing either dependency

## Related

- `django/10-upgrades`
- `wagtail/01-version-compatibility`
