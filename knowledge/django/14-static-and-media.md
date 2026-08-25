---
id: django/14-static-and-media
topic: django
slug: static-and-media
title: "Django Static and Media Files"
type: doc
order: 14
status: ready
maturity: unverified
tags: [django, static-and-media, STATIC_ROOT, MEDIA_ROOT, collectstatic, FileField]
related: [django/03-settings, django/06-security, django/09-deployment]
when_to_use: "Read when changing static assets, FileField uploads, MEDIA_ROOT, or collectstatic."
---
# Django Static and Media Files

## Purpose

Defines how hashed static assets and user uploads are stored and served.

## Rules

- Keep `STATIC_ROOT` (collected assets) separate from `MEDIA_ROOT` (user uploads).
- Run `collectstatic` in the release pipeline; do not commit collected files unless the project already does so by convention.
- Do not serve media with `django.views.static.serve` in production; use the platform's object store or web server with an access policy.
- Validate `FileField` / `ImageField` uploads for size and type; do not trust the filename extension.
- Never put secrets or source maps with private keys in `STATIC_ROOT`.

## Good Example

```python
import os
from django.core.files.storage import FileSystemStorage

STATIC_URL = "/static/"
STATIC_ROOT = os.environ["DJANGO_STATIC_ROOT"]
MEDIA_URL = "/media/"
MEDIA_ROOT = os.environ["DJANGO_MEDIA_ROOT"]
```

Collected assets and uploads resolve to different directories provided by the environment.

## Bad Example

```python
STATIC_ROOT = "/var/www/app"
MEDIA_ROOT = "/var/www/app"
MEDIA_URL = STATIC_URL
```

Mixing uploads with collected static files lets a user-uploaded HTML file be served as a static asset.

## Checklist

- [ ] `STATIC_ROOT` and `MEDIA_ROOT` are distinct directories
- [ ] `collectstatic` runs in the release pipeline
- [ ] Production does not use Django's debug static/media views
- [ ] Uploads are validated for size and type

## Related

- `django/03-settings`
- `django/06-security`
- `django/09-deployment`
