---
id: django/08-async
topic: django
slug: async
title: "Django Async and ASGI"
type: doc
order: 8
status: ready
maturity: unverified
tags: [django, async]
related: [django/01-version-support, django/09-deployment]
when_to_use: "Read when implementing or reviewing django async and asgi in a Django project."
---
# Django Async and ASGI

## Purpose

Defines safe use of async Django code.

## Rules

- Use async only across an end-to-end async call path; avoid sync-to-async bouncing.
- Do not call async-unsafe ORM or middleware code from an async context without the supported adapter.
- Keep blocking CPU or network work off the event loop.
- Test under the production ASGI server when deploying ASGI behavior.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Use async only across an end-to-end async call path
- [ ] Do not call async-unsafe ORM or middleware code from an async context without the supported adapter
- [ ] Keep blocking CPU or network work off the event loop
- [ ] Test under the production ASGI server when deploying ASGI behavior

## Related

- `django/01-version-support`
- `django/09-deployment`
