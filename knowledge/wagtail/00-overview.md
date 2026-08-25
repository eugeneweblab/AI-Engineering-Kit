---
id: wagtail/00-overview
topic: wagtail
slug: overview
title: "Wagtail Overview"
type: doc
order: 0
status: ready
maturity: unverified
tags: [wagtail, overview]
related: [wagtail/01-version-compatibility, django/00-overview]
when_to_use: "Read when implementing or reviewing wagtail overview in a Wagtail project."
---
# Wagtail Overview

## Purpose

Routes Wagtail CMS work to Django-aware rules.

## Rules

- Treat Wagtail as a Django application and apply both Wagtail and Django rules.
- Detect Wagtail, Django, and Python versions before selecting APIs.
- Preserve editorial workflows, revisions, permissions, locale, and tree invariants in every content change.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Treat Wagtail as a Django application and apply both Wagtail and Django rules
- [ ] Detect Wagtail, Django, and Python versions before selecting APIs
- [ ] Preserve editorial workflows, revisions, permissions, locale, and tree invariants in every content change

## Related

- `wagtail/01-version-compatibility`
- `django/00-overview`
