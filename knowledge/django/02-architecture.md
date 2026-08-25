---
id: django/02-architecture
topic: django
slug: architecture
title: "Django Architecture"
type: doc
order: 2
status: ready
maturity: unverified
tags: [django, architecture]
related: [django/04-models-and-migrations, django/05-querysets-and-transactions]
when_to_use: "Read when implementing or reviewing django architecture in a Django project."
---
# Django Architecture

## Purpose

Defines boundaries for Django applications and domain code.

## Rules

- Organize apps around cohesive business capabilities, not one app per database table.
- Keep views thin and place reusable policy in explicit services, model methods, managers, or selectors according to project convention.
- Avoid signal-based control flow for core business operations; make important writes explicit and testable.
- Do not introduce a repository layer unless it provides a real boundary beyond the ORM.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Organize apps around cohesive business capabilities, not one app per database table
- [ ] Keep views thin and place reusable policy in explicit services, model methods, managers, or selectors according to project convention
- [ ] Avoid signal-based control flow for core business operations
- [ ] Do not introduce a repository layer unless it provides a real boundary beyond the ORM

## Related

- `django/04-models-and-migrations`
- `django/05-querysets-and-transactions`
