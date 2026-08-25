---
id: django/00-overview
topic: django
slug: overview
title: "Django Overview"
type: doc
order: 0
status: ready
maturity: unverified
tags: [django, overview]
related: [django/01-version-support, django/98-production-checklist]
when_to_use: "Read when implementing or reviewing django overview in a Django project."
---
# Django Overview

## Purpose

Routes Django work to the applicable, version-aware rules.

## Rules

- Identify Django and Python versions from resolved dependencies, not from task prose.
- Prefer framework APIs and existing project patterns over parallel abstractions.
- Treat migrations, authorization, transactions, and deployment settings as correctness boundaries.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Identify Django and Python versions from resolved dependencies, not from task prose
- [ ] Prefer framework APIs and existing project patterns over parallel abstractions
- [ ] Treat migrations, authorization, transactions, and deployment settings as correctness boundaries

## Related

- `django/01-version-support`
- `django/98-production-checklist`
