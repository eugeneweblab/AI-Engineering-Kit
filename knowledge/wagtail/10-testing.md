---
id: wagtail/10-testing
topic: wagtail
slug: testing
title: "Wagtail Testing"
type: doc
order: 10
status: ready
maturity: unverified
tags: [wagtail, testing]
related: [wagtail/01-version-compatibility, django/07-testing]
when_to_use: "Read when implementing or reviewing wagtail testing in a Wagtail project."
---
# Wagtail Testing

## Purpose

Defines tests for content trees and editorial lifecycle.

## Rules

- Build pages through Wagtail APIs and factories that preserve tree invariants.
- Test draft, preview, publish, unpublish, scheduled, locale, alias, and permission paths as applicable.
- Assert public responses and persisted revision state, not only mocked hook calls.
- Test StreamField migrations against representative serialized values.
- Run the matrix selected by the Wagtail/Django/Python compatibility document.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Build pages through Wagtail APIs and factories that preserve tree invariants
- [ ] Test draft, preview, publish, unpublish, scheduled, locale, alias, and permission paths as applicable
- [ ] Assert public responses and persisted revision state, not only mocked hook calls
- [ ] Test StreamField migrations against representative serialized values
- [ ] Run the matrix selected by the Wagtail/Django/Python compatibility document

## Related

- `wagtail/01-version-compatibility`
- `django/07-testing`
