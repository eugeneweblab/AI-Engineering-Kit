---
id: django/06-security
topic: django
slug: security
title: "Django Security"
type: doc
order: 6
status: ready
maturity: unverified
tags: [django, security]
related: [django/03-settings, django/09-deployment]
when_to_use: "Read when implementing or reviewing django security in a Django project."
---
# Django Security

## Purpose

Defines secure request, authentication, and deployment boundaries.

## Rules

- Enforce authorization server-side for every object and mutation; authentication alone is not authorization.
- Keep CSRF protection enabled for cookie-authenticated unsafe requests.
- Use ORM parameters and Django escaping; review raw SQL, mark_safe, SafeString, and user-controlled redirects as dangerous sinks.
- Validate uploaded file type, size, storage location, and access policy.
- Install security patches promptly and run check --deploy with production settings.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Enforce authorization server-side for every object and mutation
- [ ] Keep CSRF protection enabled for cookie-authenticated unsafe requests
- [ ] Use ORM parameters and Django escaping
- [ ] Validate uploaded file type, size, storage location, and access policy
- [ ] Install security patches promptly and run check --deploy with production settings

## Related

- `django/03-settings`
- `django/09-deployment`
