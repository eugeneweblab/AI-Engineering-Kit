---
id: django/98-production-checklist
topic: django
slug: production-checklist
title: "Django Production Checklist"
type: checklist
order: 98
status: ready
maturity: unverified
tags: [django, production-checklist, check --deploy, collectstatic]
related: [django/99-ai-review-checklist]
when_to_use: "Read before considering Django work complete and ready to ship."
---
# Django Production Checklist

## Purpose

Use this as a mandatory, evidence-based gate before release.

## Version and architecture

**Rules:** [01-version-support](01-version-support.md) · [02-architecture](02-architecture.md)

- [ ] Installed framework and Python versions were detected from resolved dependencies.
- [ ] The selected versions are mutually supported.
- [ ] The change follows existing app boundaries and does not add signal-driven core writes.

## Correctness and security

**Rules:** [04-models-and-migrations](04-models-and-migrations.md) · [05-querysets-and-transactions](05-querysets-and-transactions.md) · [06-security](06-security.md)

- [ ] Authorization and validation failure paths are tested.
- [ ] Schema, `transaction.atomic`, and concurrency effects were reviewed.
- [ ] Secrets, `mark_safe`, raw SQL, uploads, and CSRF were reviewed.

## Release

**Rules:** [09-deployment](09-deployment.md) · [10-upgrades](10-upgrades.md)

- [ ] `check --deploy` and `collectstatic` pass against production settings.
- [ ] Migration order, rollback limits, static/media ownership, and health checks are covered.
- [ ] Upgrade notes and deprecations were checked when dependencies changed.
