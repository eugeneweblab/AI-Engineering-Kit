---
id: django/09-deployment
topic: django
slug: deployment
title: "Django Deployment"
type: doc
order: 9
status: ready
maturity: unverified
tags: [django, deployment, gunicorn, uvicorn, collectstatic, check --deploy]
related: [django/03-settings, django/04-models-and-migrations, django/98-production-checklist]
when_to_use: "Read when changing process model, release steps, collectstatic, or production servers."
---
# Django Deployment

## Purpose

Defines production release and runtime checks.

## Rules

- Deploy with a production WSGI or ASGI server (`gunicorn`, `uvicorn`), never `runserver`.
- Run `check --deploy`, `collectstatic`, migration planning, and smoke tests in the release pipeline.
- Apply compatible schema changes before code that requires them and define rollback limits.
- Configure health checks, structured logs, timeouts, trusted proxy handling, and static/media ownership.
- Back up and test restore procedures before risky migrations.

## Good Example

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
timeout = 30
```

The app is served by a production WSGI server with an explicit timeout; `runserver` is not the process model.

## Bad Example

```python
# Dockerfile CMD
# python manage.py runserver 0.0.0.0:8000
```

`runserver` is a development server: no production worker model, weak static handling, and no deploy checks.

## Checklist

- [ ] Deploy with a production WSGI or ASGI server, never `runserver`
- [ ] Run `check --deploy`, `collectstatic`, migration planning, and smoke tests in the release pipeline
- [ ] Apply compatible schema changes before code that requires them and define rollback limits
- [ ] Configure health checks, structured logs, timeouts, trusted proxy handling, and static/media ownership
- [ ] Back up and test restore procedures before risky migrations

## Related

- `django/03-settings`
- `django/04-models-and-migrations`
- `django/98-production-checklist`
