---
id: django/05-querysets-and-transactions
topic: django
slug: querysets-and-transactions
title: "Django QuerySets and Transactions"
type: doc
order: 5
status: ready
maturity: unverified
tags: [django, querysets-and-transactions]
related: [django/04-models-and-migrations, django/07-testing]
when_to_use: "Read when implementing or reviewing django querysets and transactions in a Django project."
---
# Django QuerySets and Transactions

## Purpose

Defines correct data access and concurrency behavior.

## Rules

- Evaluate QuerySets intentionally and prevent N+1 access with select_related or prefetch_related after measuring query shape.
- Wrap only the atomic unit of work in transaction.atomic; do not hold transactions across network calls.
- Use select_for_update or database constraints when correctness depends on concurrent writers.
- Do not catch database exceptions inside the atomic block whose rollback they require.
- Use F expressions for race-safe in-database updates when appropriate.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Evaluate QuerySets intentionally and prevent N+1 access with select_related or prefetch_related after measuring query shape
- [ ] Wrap only the atomic unit of work in transaction.atomic
- [ ] Use select_for_update or database constraints when correctness depends on concurrent writers
- [ ] Do not catch database exceptions inside the atomic block whose rollback they require
- [ ] Use F expressions for race-safe in-database updates when appropriate

## Related

- `django/04-models-and-migrations`
- `django/07-testing`
