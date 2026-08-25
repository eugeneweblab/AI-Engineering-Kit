---
id: django/29-maintenance
topic: django
slug: maintenance
title: "Django Maintenance"
type: doc
order: 29
status: ready
maturity: unverified
tags: [django, maintenance, clearsessions, check, showmigrations]
related: [django/09-deployment, django/10-upgrades]
when_to_use: "Read when scheduling operational Django tasks, session cleanup, or health/maintenance windows."
---
# Django Maintenance

## Purpose

Defines recurring operations that keep a Django site healthy.

## Rules

- Run `clearsessions` (or the project's session backend cleanup) on a schedule when using database or cached sessions.
- Run `django-admin check` in CI; treat warnings from `--deploy` as release blockers.
- Review `showmigrations` before every production deploy; never fake a migration to hide drift without a written reason.
- Rotate `SECRET_KEY` only with a documented dual-key window if signed cookies or tokens exist.
- Keep dependency patches current; EOL Django lines are a maintenance incident, not a style choice.

## Good Example

```python
# cron / scheduled job
# django-admin clearsessions
# django-admin check --deploy --fail-level WARNING
```

Session rows and deploy checks run outside the request path.

## Bad Example

```python
# manage.py migrate --fake 0004_added_amount
```

Faking a migration to make CI green leaves production schema behind the code.

## Checklist

- [ ] Session cleanup is scheduled when the session engine needs it
- [ ] `check --deploy` runs in CI against production settings
- [ ] Migrations are applied, not faked, unless an incident doc says otherwise

## Related

- `django/09-deployment`
- `django/10-upgrades`
