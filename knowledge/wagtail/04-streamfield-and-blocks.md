---
id: wagtail/04-streamfield-and-blocks
topic: wagtail
slug: streamfield-and-blocks
title: "Wagtail StreamField and Blocks"
type: doc
order: 4
status: ready
maturity: unverified
tags: [wagtail, streamfield-and-blocks]
related: [wagtail/03-page-models, wagtail/10-testing]
when_to_use: "Read when implementing or reviewing wagtail streamfield and blocks in a Wagtail project."
---
# Wagtail StreamField and Blocks

## Purpose

Defines stable structured-content schemas.

## Rules

- Give every block a stable name and preserve stored block shape across refactors.
- Use StructBlock, ListBlock, and StreamBlock to express structure instead of parsing free-form rich text.
- Write and test data migrations before renaming, moving, or changing block types.
- Validate external choices and references without making historical revisions unreadable.
- Keep rendering logic small and escape or sanitize editor-provided HTML at the correct boundary.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Give every block a stable name and preserve stored block shape across refactors
- [ ] Use StructBlock, ListBlock, and StreamBlock to express structure instead of parsing free-form rich text
- [ ] Write and test data migrations before renaming, moving, or changing block types
- [ ] Validate external choices and references without making historical revisions unreadable
- [ ] Keep rendering logic small and escape or sanitize editor-provided HTML at the correct boundary

## Related

- `wagtail/03-page-models`
- `wagtail/10-testing`
