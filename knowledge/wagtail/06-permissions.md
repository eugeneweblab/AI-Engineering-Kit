---
id: wagtail/06-permissions
topic: wagtail
slug: permissions
title: "Wagtail Permissions"
type: doc
order: 6
status: ready
maturity: unverified
tags: [wagtail, permissions]
related: [django/06-security, wagtail/05-revisions-and-workflows]
when_to_use: "Read when implementing or reviewing wagtail permissions in a Wagtail project."
---
# Wagtail Permissions

## Purpose

Defines admin and content authorization.

## Rules

- Enforce permissions in server-side views, APIs, hooks, and actions; hiding admin UI is insufficient.
- Respect collection, page, locale, and workflow permissions when resolving objects.
- Use Wagtail permission policies and groups instead of duplicating authorization logic.
- Test users with no access, partial subtree access, and cross-site or cross-locale access.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Enforce permissions in server-side views, APIs, hooks, and actions
- [ ] Respect collection, page, locale, and workflow permissions when resolving objects
- [ ] Use Wagtail permission policies and groups instead of duplicating authorization logic
- [ ] Test users with no access, partial subtree access, and cross-site or cross-locale access

## Related

- `django/06-security`
- `wagtail/05-revisions-and-workflows`
