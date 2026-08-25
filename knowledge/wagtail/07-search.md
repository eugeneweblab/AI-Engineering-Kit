---
id: wagtail/07-search
topic: wagtail
slug: search
title: "Wagtail Search"
type: doc
order: 7
status: ready
maturity: unverified
tags: [wagtail, search]
related: [wagtail/03-page-models, wagtail/12-deployment]
when_to_use: "Read when implementing or reviewing wagtail search in a Wagtail project."
---
# Wagtail Search

## Purpose

Defines predictable indexing and querying.

## Rules

- Declare search_fields deliberately and rebuild indexes after incompatible schema changes.
- Use the configured backend's supported operators; database and Elasticsearch/OpenSearch behavior can differ.
- Apply live, site, locale, and permission filters before returning results.
- Measure query counts and index freshness, and define behavior while indexing is delayed.

## Good Example

A compliant change records the detected framework versions, follows the existing project conventions, keeps policy at the correct boundary, and adds a regression test for the failure path.

## Bad Example

Copying an example from another major version without checking release notes or installed dependencies can produce code that imports successfully but behaves incorrectly in production.

## Checklist

- [ ] Declare search_fields deliberately and rebuild indexes after incompatible schema changes
- [ ] Use the configured backend's supported operators
- [ ] Apply live, site, locale, and permission filters before returning results
- [ ] Measure query counts and index freshness, and define behavior while indexing is delayed

## Related

- `wagtail/03-page-models`
- `wagtail/12-deployment`
