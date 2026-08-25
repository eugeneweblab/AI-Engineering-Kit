---
id: django/04-models-and-migrations
topic: django
slug: models-and-migrations
title: "Django Models and Migrations"
type: doc
order: 4
status: ready
maturity: unverified
tags: [django, models-and-migrations]
related: [django/05-querysets-and-transactions, django/09-deployment]
when_to_use: "Read when implementing or reviewing django models and migrations in a Django project."
---
# Django Models and Migrations

## Purpose

Defines safe schema and model evolution.

## Rules

- Represent invariants with database constraints when the database can enforce them.
- Review generated migrations; never edit an applied migration shared by other environments.
- Separate state and database operations only with an explicit compatibility reason.
- Use staged expand-and-contract changes for large or zero-downtime deployments.
- Make data migrations deterministic, bounded, and reversible where practical.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Represent invariants with database constraints when the database can enforce them
- [ ] Review generated migrations
- [ ] Separate state and database operations only with an explicit compatibility reason
- [ ] Use staged expand-and-contract changes for large or zero-downtime deployments
- [ ] Make data migrations deterministic, bounded, and reversible where practical

## Related

- `django/05-querysets-and-transactions`
- `django/09-deployment`
