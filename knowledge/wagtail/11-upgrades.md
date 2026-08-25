---
id: wagtail/11-upgrades
topic: wagtail
slug: upgrades
title: "Wagtail Upgrades"
type: doc
order: 11
status: ready
maturity: unverified
tags: [wagtail, upgrades]
related: [wagtail/01-version-compatibility, wagtail/10-testing]
when_to_use: "Read when implementing or reviewing wagtail upgrades in a Wagtail project."
---
# Wagtail Upgrades

## Purpose

Defines safe Wagtail upgrades and content migrations.

## Rules

- Read every intervening release note and execute documented upgrade checks.
- Upgrade Wagtail separately from Django and Python.
- Audit removed imports, renamed hooks, editor component APIs, search backends, and StreamField serialization changes.
- Back up the database and media and rehearse migration and rollback on production-scale data.
- Verify admin editing, preview, publishing, search, images, redirects, and APIs after upgrade.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Read every intervening release note and execute documented upgrade checks
- [ ] Upgrade Wagtail separately from Django and Python
- [ ] Audit removed imports, renamed hooks, editor component APIs, search backends, and StreamField serialization changes
- [ ] Back up the database and media and rehearse migration and rollback on production-scale data
- [ ] Verify admin editing, preview, publishing, search, images, redirects, and APIs after upgrade

## Related

- `wagtail/01-version-compatibility`
- `wagtail/10-testing`
