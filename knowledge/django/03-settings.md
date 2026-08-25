---
id: django/03-settings
topic: django
slug: settings
title: "Django Settings and Configuration"
type: doc
order: 3
status: ready
maturity: unverified
tags: [django, settings, DEBUG, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, SECRET_KEY]
related: [django/06-security, django/09-deployment]
when_to_use: "Read when changing settings, environment variables, or per-environment configuration."
---
# Django Settings and Configuration

## Purpose

Defines safe configuration across environments.

## Rules

- Split environment values from code and fail startup when required secrets are absent.
- Never enable `DEBUG` in production and configure `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, secure cookies, HTTPS redirect, and proxy headers deliberately.
- Keep `SECRET_KEY` and other secret values out of source control and logs.
- Run `django-admin check --deploy` against production settings before release.

## Good Example

```python
import os

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = os.environ["DJANGO_ALLOWED_HOSTS"].split(",")
CSRF_TRUSTED_ORIGINS = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
```

Missing secrets fail at import time instead of shipping with a committed fallback.

## Bad Example

```python
DEBUG = True
SECRET_KEY = "not-secret"
ALLOWED_HOSTS = ["*"]
```

A committed debug configuration with a wildcard host list exposes traces and accepts any Host header.

## Checklist

- [ ] Split environment values from code and fail startup when required secrets are absent
- [ ] Never enable `DEBUG` in production and configure `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, secure cookies, HTTPS redirect, and proxy headers deliberately
- [ ] Keep secret values out of source control and logs
- [ ] Run `check --deploy` against production settings before release

## Related

- `django/06-security`
- `django/09-deployment`
