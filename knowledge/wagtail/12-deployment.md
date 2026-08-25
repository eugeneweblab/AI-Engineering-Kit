---
id: wagtail/12-deployment
topic: wagtail
slug: deployment
title: "Wagtail Deployment"
type: doc
order: 12
status: ready
maturity: unverified
tags: [wagtail, deployment]
related: [django/09-deployment, wagtail/11-upgrades, wagtail/98-production-checklist]
when_to_use: "Read when implementing or reviewing wagtail deployment in a Wagtail project."
---
# Wagtail Deployment

## Purpose

Defines production release checks for CMS sites.

## Rules

- Apply all Django deployment rules plus Wagtail system and upgrade checks.
- Coordinate schema, search index, static assets, and application rollout.
- Preserve media independently from ephemeral application filesystems.
- Smoke-test admin login, edit, preview, publish, image renditions, search, and public routing.
- Define cache purge behavior for publish, unpublish, move, redirect, and locale changes.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Apply all Django deployment rules plus Wagtail system and upgrade checks
- [ ] Coordinate schema, search index, static assets, and application rollout
- [ ] Preserve media independently from ephemeral application filesystems
- [ ] Smoke-test admin login, edit, preview, publish, image renditions, search, and public routing
- [ ] Define cache purge behavior for publish, unpublish, move, redirect, and locale changes

## Related

- `django/09-deployment`
- `wagtail/11-upgrades`
- `wagtail/98-production-checklist`
