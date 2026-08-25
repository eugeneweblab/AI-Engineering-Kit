---
id: django/03-settings
topic: django
slug: settings
title: "Django Settings and Configuration"
type: doc
order: 3
status: ready
maturity: unverified
tags: [django, settings]
related: [django/06-security, django/09-deployment]
when_to_use: "Read when implementing or reviewing django settings and configuration in a Django project."
---
# Django Settings and Configuration

## Purpose

Defines safe configuration across environments.

## Rules

- Split environment values from code and fail startup when required secrets are absent.
- Never enable DEBUG in production and configure ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, secure cookies, HTTPS redirect, and proxy headers deliberately.
- Keep secret values out of source control and logs.
- Run the deployment system check against production settings before release.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Split environment values from code and fail startup when required secrets are absent
- [ ] Never enable DEBUG in production and configure ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, secure cookies, HTTPS redirect, and proxy headers deliberately
- [ ] Keep secret values out of source control and logs
- [ ] Run the deployment system check against production settings before release

## Related

- `django/06-security`
- `django/09-deployment`
