---
id: django/15-authentication
topic: django
slug: authentication
title: "Django Authentication"
type: doc
order: 15
status: ready
maturity: unverified
tags: [django, authentication, AUTH_USER_MODEL, get_user_model, login_required, PermissionRequiredMixin]
related: [django/06-security, django/11-urls-and-views]
when_to_use: "Read when changing login, users, permissions, AUTH_USER_MODEL, or password hashing."
---
# Django Authentication

## Purpose

Defines how identities and permissions are stored and checked.

## Rules

- Set `AUTH_USER_MODEL` before the first user migration; reference the user with `get_user_model()` or `settings.AUTH_USER_MODEL`, not a hardcoded `auth.User` unless the project already uses it.
- Authenticate with Django's password hashers; do not store plaintext or home-rolled hashes.
- Use `login_required`, `PermissionRequiredMixin`, or `user_passes_test` on mutating and private views.
- Authorization is per object when the model is not global; `is_authenticated` is not ownership.
- Session cookies must be `Secure`, `HttpOnly`, and `SameSite` in production.

## Good Example

```python
from django.conf import settings
from django.db import models

class Invoice(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
```

Swapping the user model does not require rewriting every ForeignKey.

## Bad Example

```python
from django.contrib.auth.models import User

class Invoice(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
```

A later custom user model cannot be introduced without a painful table rewrite.

## Checklist

- [ ] User FKs use `AUTH_USER_MODEL` / `get_user_model()`
- [ ] Passwords go through Django hashers
- [ ] Private views require login and object-level authorization
- [ ] Production session cookies are `Secure` and `HttpOnly`

## Related

- `django/06-security`
- `django/11-urls-and-views`
