---
id: wagtail/25-custom-users
topic: wagtail
slug: custom-users
title: "Wagtail Custom Users"
type: doc
order: 25
status: ready
maturity: unverified
tags: [wagtail, custom-users, AUTH_USER_MODEL, AbstractUser]
related: [django/15-authentication, wagtail/06-permissions]
when_to_use: "Read when customizing the user model on a Wagtail site."
---
# Wagtail Custom Users

## Purpose

Defines custom user models that still work with Wagtail admin.

## Rules

- Follow Django's `AUTH_USER_MODEL` rule: set it before the first migration.
- Keep the attributes Wagtail admin expects (`is_staff`, `is_active`, `is_superuser`, `get_username`, `get_full_name` or the project's `WAGTAIL_USER_*` settings).
- Do not replace Wagtail's permission tables with a parallel group model unless a documented adapter exists.
- Test login to `/admin/`, page create, and a non-superuser editor after the swap.
- Cross-check Django authentication rules.

## Good Example

```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    job_title = models.CharField(max_length=120, blank=True)
```

`AUTH_USER_MODEL = "accounts.User"` is set before `migrate`, and Wagtail still sees staff flags.

## Bad Example

```python
class User(models.Model):
    email = models.EmailField(unique=True)
```

A model that is not a Django user cannot log into Wagtail admin or own pages.

## Checklist

- [ ] `AUTH_USER_MODEL` was set before the first user table
- [ ] Staff/superuser flags and username accessors remain
- [ ] Admin login and editor flows were tested

## Related

- `django/15-authentication`
- `wagtail/06-permissions`
