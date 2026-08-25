---
id: django/10-upgrades
topic: django
slug: upgrades
title: "Django Upgrades"
type: doc
order: 10
status: ready
maturity: unverified
tags: [django, upgrades]
related: [django/01-version-support, django/07-testing]
when_to_use: "Read when implementing or reviewing django upgrades in a Django project."
---
# Django Upgrades

## Purpose

Defines safe movement between Django minor and major versions.

## Rules

- Upgrade one Django minor line at a time and read all intervening release notes.
- Resolve deprecation warnings on the current release before moving to the next major release.
- Upgrade Python and Django separately unless a compatibility constraint makes that impossible.
- Check database backend, middleware, template engine, and third-party app compatibility before changing the lock file.
- Keep rollback possible until migrations and production behavior are verified.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Upgrade one Django minor line at a time and read all intervening release notes
- [ ] Resolve deprecation warnings on the current release before moving to the next major release
- [ ] Upgrade Python and Django separately unless a compatibility constraint makes that impossible
- [ ] Check database backend, middleware, template engine, and third-party app compatibility before changing the lock file
- [ ] Keep rollback possible until migrations and production behavior are verified

## Related

- `django/01-version-support`
- `django/07-testing`
