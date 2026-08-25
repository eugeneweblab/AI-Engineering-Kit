---
id: django/27-database-backends
topic: django
slug: database-backends
title: "Django Database Backends"
type: doc
order: 27
status: ready
maturity: unverified
tags: [django, database-backends, ENGINE, CONN_MAX_AGE, ATOMIC_REQUESTS, PostgreSQL]
related: [django/03-settings, django/04-models-and-migrations]
when_to_use: "Read when changing DATABASES, CONN_MAX_AGE, engine-specific features, or ATOMIC_REQUESTS."
---
# Django Database Backends

## Purpose

Defines engine-specific settings without baking one vendor into portable apps.

## Rules

- Set `DATABASES["default"]["ENGINE"]` and credentials from the environment; never commit production passwords.
- Enable `CONN_MAX_AGE` only with a pooler or a process model that can hold connections; serverless needs a pooler (pgbouncer, RDS proxy).
- Leave `ATOMIC_REQUESTS` off unless the project already relies on it; prefer explicit `transaction.atomic`.
- Use engine features (`JSONB`, `ArrayField`, `JSONField`) only when the deployed backend supports them.
- Do not write raw SQL that only one backend understands unless the project is single-engine and documented as such.

## Good Example

```python
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "CONN_MAX_AGE": 60,
    }
}
```

Credentials come from the environment; the engine matches production.

## Bad Example

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "prod.db",
    }
}
```

SQLite as a silent production default loses concurrency and type features the code may assume.

## Checklist

- [ ] Engine and secrets come from the environment
- [ ] `CONN_MAX_AGE` matches the process and pooler model
- [ ] Vendor-specific fields are allowed by the deployed backend

## Related

- `django/03-settings`
- `django/04-models-and-migrations`
