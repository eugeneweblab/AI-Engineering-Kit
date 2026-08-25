---
id: django/100-common-antipatterns
topic: django
slug: common-antipatterns
title: "Common Django Antipatterns"
type: antipatterns
order: 100
status: ready
maturity: unverified
tags: [django, common-antipatterns, csrf_exempt, mark_safe, post_save]
related: [django/99-ai-review-checklist]
when_to_use: "Read when reviewing Django changes for known failure modes."
---
# Common Django Antipatterns

## Purpose

Use this as a mandatory, evidence-based gate against known Django mistakes.

## Rules

**Rules:** [02-architecture](02-architecture.md) · [05-querysets-and-transactions](05-querysets-and-transactions.md) · [06-security](06-security.md)

- [ ] Do not guess versions from memory or use APIs from a different compatibility line.
- [ ] Do not iterate a QuerySet and touch `obj.foreign` without `select_related` or `prefetch_related`.
- [ ] Do not hide authorization only in templates or admin UI.
- [ ] Do not place core business behavior in `pre_save`, `post_save`, templates, or implicit callbacks.
- [ ] Do not add `csrf_exempt` or `mark_safe` around request data.
- [ ] Do not edit an applied migration or deploy schema changes without a tested forward and rollback plan.
