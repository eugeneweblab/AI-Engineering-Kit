---
id: django/07-testing
topic: django
slug: testing
title: "Django Testing"
type: doc
order: 7
status: ready
maturity: unverified
tags: [django, testing]
related: [django/01-version-support, django/05-querysets-and-transactions]
when_to_use: "Read when implementing or reviewing django testing in a Django project."
---
# Django Testing

## Purpose

Defines regression tests that exercise real framework boundaries.

## Rules

- Use TestCase for transactional isolation and TransactionTestCase only when commit or locking behavior is under test.
- Test permissions, validation errors, missing objects, and concurrent invariants, not only successful responses.
- Prefer persisted database assertions over mock call counts.
- Use the actual URL configuration, middleware, templates, and settings for integration behavior.
- Run migration checks and tests on every supported Django/Python combination.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Use TestCase for transactional isolation and TransactionTestCase only when commit or locking behavior is under test
- [ ] Test permissions, validation errors, missing objects, and concurrent invariants, not only successful responses
- [ ] Prefer persisted database assertions over mock call counts
- [ ] Use the actual URL configuration, middleware, templates, and settings for integration behavior
- [ ] Run migration checks and tests on every supported Django/Python combination

## Related

- `django/01-version-support`
- `django/05-querysets-and-transactions`
