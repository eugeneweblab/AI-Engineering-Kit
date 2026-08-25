---
id: wagtail/08-images-and-documents
topic: wagtail
slug: images-and-documents
title: "Wagtail Images and Documents"
type: doc
order: 8
status: ready
maturity: unverified
tags: [wagtail, images-and-documents]
related: [django/06-security, wagtail/12-deployment]
when_to_use: "Read when implementing or reviewing wagtail images and documents in a Wagtail project."
---
# Wagtail Images and Documents

## Purpose

Defines secure rendition and file handling.

## Rules

- Use Wagtail image renditions rather than ad hoc resizing and avoid unbounded user-controlled rendition specs.
- Validate upload size and type and configure storage permissions independently for public and private media.
- Do not treat filename extensions as trusted content types.
- Test focal points, missing renditions, remote storage, and private document access.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Use Wagtail image renditions rather than ad hoc resizing and avoid unbounded user-controlled rendition specs
- [ ] Validate upload size and type and configure storage permissions independently for public and private media
- [ ] Do not treat filename extensions as trusted content types
- [ ] Test focal points, missing renditions, remote storage, and private document access

## Related

- `django/06-security`
- `wagtail/12-deployment`
