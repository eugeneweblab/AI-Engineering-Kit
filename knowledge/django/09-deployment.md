---
id: django/09-deployment
topic: django
slug: deployment
title: "Django Deployment"
type: doc
order: 9
status: ready
maturity: unverified
tags: [django, deployment]
related: [django/03-settings, django/04-models-and-migrations, django/98-production-checklist]
when_to_use: "Read when implementing or reviewing django deployment in a Django project."
---
# Django Deployment

## Purpose

Defines production release and runtime checks.

## Rules

- Deploy with a production WSGI or ASGI server, never runserver.
- Run check --deploy, collectstatic, migration planning, and smoke tests in the release pipeline.
- Apply compatible schema changes before code that requires them and define rollback limits.
- Configure health checks, structured logs, timeouts, trusted proxy handling, and static/media ownership.
- Back up and test restore procedures before risky migrations.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Deploy with a production WSGI or ASGI server, never runserver
- [ ] Run check --deploy, collectstatic, migration planning, and smoke tests in the release pipeline
- [ ] Apply compatible schema changes before code that requires them and define rollback limits
- [ ] Configure health checks, structured logs, timeouts, trusted proxy handling, and static/media ownership
- [ ] Back up and test restore procedures before risky migrations

## Related

- `django/03-settings`
- `django/04-models-and-migrations`
- `django/98-production-checklist`
