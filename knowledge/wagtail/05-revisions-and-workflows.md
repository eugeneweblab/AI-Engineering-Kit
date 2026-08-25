---
id: wagtail/05-revisions-and-workflows
topic: wagtail
slug: revisions-and-workflows
title: "Wagtail Revisions, Publishing, and Workflows"
type: doc
order: 5
status: ready
maturity: unverified
tags: [wagtail, revisions-and-workflows]
related: [wagtail/03-page-models, wagtail/06-permissions]
when_to_use: "Read when implementing or reviewing wagtail revisions, publishing, and workflows in a Wagtail project."
---
# Wagtail Revisions, Publishing, and Workflows

## Purpose

Defines editorial-state correctness.

## Rules

- Write editable Page content through revisions and publish APIs rather than direct live-table updates.
- Preserve moderation workflows, scheduled publication, and audit history.
- Test draft preview separately from live serving.
- Make bulk content operations explicit about whether they create revisions, publish, or leave drafts.
- Do not infer public visibility from row existence; apply live, locale, site, and privacy constraints.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Write editable Page content through revisions and publish APIs rather than direct live-table updates
- [ ] Preserve moderation workflows, scheduled publication, and audit history
- [ ] Test draft preview separately from live serving
- [ ] Make bulk content operations explicit about whether they create revisions, publish, or leave drafts
- [ ] Do not infer public visibility from row existence

## Related

- `wagtail/03-page-models`
- `wagtail/06-permissions`
