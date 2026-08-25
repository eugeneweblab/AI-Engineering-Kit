---
id: wagtail/12-deployment
topic: wagtail
slug: deployment
title: "Wagtail Deployment"
type: doc
order: 12
status: ready
maturity: unverified
tags: [wagtail, deployment, update_index, collectstatic, fixtree]
related: [django/09-deployment, wagtail/11-upgrades, wagtail/98-production-checklist]
when_to_use: "Read when releasing a Wagtail site, rebuilding search, or placing media."
---
# Wagtail Deployment

## Purpose

Defines production release checks for CMS sites.

## Rules

- Apply all Django deployment rules plus Wagtail system and upgrade checks.
- Coordinate schema, search index (`wagtail update_index`), static assets, and application rollout.
- Preserve media independently from ephemeral application filesystems.
- Smoke-test admin login, edit, preview, publish, image renditions, search, and public routing.
- Define cache purge behavior for publish, unpublish, move, redirect, and locale changes.

## Good Example

```python
# release pipeline
# django-admin migrate
# django-admin collectstatic --noinput
# django-admin wagtail update_index
# django-admin check --deploy
```

Search is rebuilt after schema changes, and media lives on a volume the app container does not delete.

## Bad Example

```python
# docker image with MEDIA_ROOT inside the container and no update_index
```

Renditions and uploads vanish on redeploy, and search serves a stale index.

## Checklist

- [ ] Django deploy rules plus Wagtail checks run in the pipeline
- [ ] Schema, `update_index`, static, and app roll out in a defined order
- [ ] Media is on durable storage
- [ ] Smoke tests cover admin, preview, publish, images, search, and routing
- [ ] Cache purge is defined for publish/unpublish/move/redirect/locale

## Related

- `django/09-deployment`
- `wagtail/11-upgrades`
- `wagtail/98-production-checklist`
