---
id: django/98-production-checklist
topic: django
slug: production-checklist
title: "Django Production Checklist"
type: checklist
order: 98
status: ready
maturity: unverified
tags: [django, production-checklist]
related: [django/99-ai-review-checklist]
when_to_use: "Read before considering Django work complete."
---
# Django Production Checklist

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

