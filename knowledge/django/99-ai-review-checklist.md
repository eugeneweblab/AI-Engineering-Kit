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
when_to_use: "Read when reviewing a Django diff for correctness before merge."
---
# Django AI Review Checklist

## Purpose

Use this as a mandatory review of the diff, not a second copy of the release gate.

## Version and architecture

**Rules:** [01-version-support](01-version-support.md) · [02-architecture](02-architecture.md)

- [ ] APIs in the diff exist on the installed Django line.
- [ ] Views stay thin; new business writes are explicit functions, not `post_save` hooks.
- [ ] No new repository layer was added without a real boundary beyond the ORM.

## Correctness and security

**Rules:** [05-querysets-and-transactions](05-querysets-and-transactions.md) · [06-security](06-security.md) · [07-testing](07-testing.md)

- [ ] Related-object access uses `select_related` or `prefetch_related` where the template or serializer walks relations.
- [ ] Every new mutation has a server-side authorization test, not only a 200-path test.
- [ ] The diff does not add `csrf_exempt`, `mark_safe`, or string-formatted SQL without a documented reason.

## Release

**Rules:** [04-models-and-migrations](04-models-and-migrations.md) · [09-deployment](09-deployment.md)

- [ ] New model fields shipped with a reviewed migration that was not edited after apply.
- [ ] Settings changes cannot enable `DEBUG` or weaken `ALLOWED_HOSTS` in production.
