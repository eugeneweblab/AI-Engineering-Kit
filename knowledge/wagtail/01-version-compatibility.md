---
id: wagtail/01-version-compatibility
topic: wagtail
slug: version-compatibility
title: "Wagtail and Django Version Compatibility"
type: doc
order: 1
status: ready
maturity: unverified
tags: [wagtail, version-compatibility]
related: [django/01-version-support, wagtail/11-upgrades]
when_to_use: "Read before choosing framework APIs or changing dependencies."
verified_against: "Wagtail 6.3 LTS through 7.4 LTS; Django 4.2 through 6.0"
source_urls: ["https://docs.wagtail.org/en/stable/releases/upgrading.html", "https://docs.wagtail.org/en/stable/releases/index.html"]
last_reviewed: "2026-08-25"
review_after: "2026-11-25"
---
# Wagtail and Django Version Compatibility

## Purpose

Defines the supported Wagtail, Django, and Python matrix.

## Rules

- Use the official compatibility matrix; never assume the newest Django works with an older Wagtail.
- Compatibility is not security support: reject Django 4.2, 5.0, and 5.1 for new deployments even when an older Wagtail release can import them.
- Wagtail 6.3 LTS supports Django 4.2, 5.0, 5.1, and 5.2 with the documented patch caveat; Wagtail 7.0 LTS supports Django 4.2, 5.1, and 5.2.
- Wagtail 7.2 supports Django 4.2, 5.1, 5.2, and 6.0; Wagtail 7.4 LTS supports Django 5.2 and 6.0.
- Wagtail 7.4 LTS does not list Django 6.1 as compatible; do not upgrade a Wagtail project to Django 6.1 until its installed Wagtail line adds support.
- Upgrade Wagtail, Django, and Python as separate tested steps.
- Read every intervening Wagtail upgrade note and use the upgrade-check command when available.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Use the official compatibility matrix
- [ ] Every selected Django version is both Wagtail-compatible and still security-supported
- [ ] Wagtail 6.3 LTS supports Django 4.2, 5.0, 5.1, and 5.2 with the documented patch caveat
- [ ] Wagtail 7.2 supports Django 4.2, 5.1, 5.2, and 6.0
- [ ] Django 6.1 is not selected with Wagtail 7.4 LTS
- [ ] Upgrade Wagtail, Django, and Python as separate tested steps
- [ ] Read every intervening Wagtail upgrade note and use the upgrade-check command when available

## Related

- `django/01-version-support`
- `wagtail/11-upgrades`
