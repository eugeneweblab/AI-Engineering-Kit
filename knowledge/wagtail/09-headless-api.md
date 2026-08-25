---
id: wagtail/09-headless-api
topic: wagtail
slug: headless-api
title: "Wagtail Headless API"
type: doc
order: 9
status: ready
maturity: unverified
tags: [wagtail, headless-api]
related: [rest-api/03-resource-design, wagtail/05-revisions-and-workflows]
when_to_use: "Read when implementing or reviewing wagtail headless api in a Wagtail project."
---
# Wagtail Headless API

## Purpose

Defines safe API exposure of CMS content.

## Rules

- Whitelist exposed fields and serializers; do not publish model internals by default.
- Filter by live state, site, locale, and permissions before serialization.
- Design preview authentication separately from the public API.
- Version response contracts and test cache invalidation after publish and unpublish events.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Whitelist exposed fields and serializers
- [ ] Filter by live state, site, locale, and permissions before serialization
- [ ] Design preview authentication separately from the public API
- [ ] Version response contracts and test cache invalidation after publish and unpublish events

## Related

- `rest-api/03-resource-design`
- `wagtail/05-revisions-and-workflows`
