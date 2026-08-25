---
id: wagtail/98-production-checklist
topic: wagtail
slug: production-checklist
title: "Wagtail Production Checklist"
type: checklist
order: 98
status: ready
maturity: unverified
tags: [wagtail, production-checklist, update_index, collectstatic]
related: [wagtail/99-ai-review-checklist]
when_to_use: "Read before considering Wagtail work complete and ready to ship."
---
# Wagtail Production Checklist

## Purpose

Use this as a mandatory, evidence-based gate before release.

## Version and architecture

**Rules:** [01-version-compatibility](01-version-compatibility.md) · [02-architecture](02-architecture.md)

- [ ] Wagtail, Django, and Python versions were detected from the lock file and intersected.
- [ ] Python satisfies both Wagtail and the chosen Django line (Django 6.0 needs 3.12+).
- [ ] Tree mutations use Wagtail APIs, not `path` / `depth` / `numchild`.

## Correctness and security

**Rules:** [05-revisions-and-workflows](05-revisions-and-workflows.md) · [06-permissions](06-permissions.md) · [22-security](22-security.md)

- [ ] Programmatic edits use `save_revision` / publish; live vs draft vs private is tested.
- [ ] Custom queries use `live().public()` (or an equivalent restriction).
- [ ] Django CSRF/XSS/auth rules still apply.

## Release

**Rules:** [12-deployment](12-deployment.md) · [django/09-deployment](../django/09-deployment.md)

- [ ] `migrate`, `collectstatic`, `wagtail update_index`, and `check --deploy` run in the pipeline.
- [ ] Media is on durable storage; cache purge on publish is defined.
- [ ] Smoke tests cover admin, preview, publish, images, search, and public routing.
