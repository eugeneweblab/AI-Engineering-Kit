---
id: django/99-ai-review-checklist
topic: django
slug: ai-review-checklist
title: "Django AI Review Checklist"
type: checklist
order: 99
status: ready
maturity: unverified
tags: [django, ai-review-checklist]
related: [django/98-production-checklist, django/100-common-antipatterns]
when_to_use: "Read when reviewing Django changes."
---
# Django AI Review Checklist

## Purpose

Use this as a mandatory, evidence-based gate.

## Version and architecture

**Rules:** [01-version-support](01-version-support.md) · [02-architecture](02-architecture.md)

- [ ] Installed framework and Python versions were detected from resolved dependencies.
- [ ] The selected versions are mutually supported.
- [ ] The change follows existing boundaries and conventions.

## Correctness and security

**Rules:** [06-security](06-security.md) · [07-testing](07-testing.md)

- [ ] Authorization and validation failure paths are tested.
- [ ] Schema, transaction, publishing, and concurrency effects were reviewed.
- [ ] Secrets and unsafe rendering or query sinks were reviewed.

## Release

**Rules:** [10-upgrades](10-upgrades.md) · [09-deployment](09-deployment.md)

- [ ] Upgrade notes and deprecations were checked.
- [ ] Production settings and deployment checks pass.
- [ ] Rollback, migrations, assets, media, and observability are covered.

