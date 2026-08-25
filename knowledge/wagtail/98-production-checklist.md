---
id: wagtail/98-production-checklist
topic: wagtail
slug: production-checklist
title: "Wagtail Production Checklist"
type: checklist
order: 98
status: ready
maturity: unverified
tags: [wagtail, production-checklist]
related: [wagtail/99-ai-review-checklist]
when_to_use: "Read before considering Wagtail work complete."
---
# Wagtail Production Checklist

## Purpose

Use this as a mandatory, evidence-based gate.

## Version and architecture

**Rules:** [01-version-compatibility](01-version-compatibility.md) · [02-architecture](02-architecture.md)

- [ ] Installed framework and Python versions were detected from resolved dependencies.
- [ ] The selected versions are mutually supported.
- [ ] The change follows existing boundaries and conventions.

## Correctness and security

**Rules:** [06-permissions](06-permissions.md) · [10-testing](10-testing.md)

- [ ] Authorization and validation failure paths are tested.
- [ ] Schema, transaction, publishing, and concurrency effects were reviewed.
- [ ] Secrets and unsafe rendering or query sinks were reviewed.

## Release

**Rules:** [11-upgrades](11-upgrades.md) · [12-deployment](12-deployment.md)

- [ ] Upgrade notes and deprecations were checked.
- [ ] Production settings and deployment checks pass.
- [ ] Rollback, migrations, assets, media, and observability are covered.

