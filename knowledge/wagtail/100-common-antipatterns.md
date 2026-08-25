---
id: wagtail/100-common-antipatterns
topic: wagtail
slug: common-antipatterns
title: "Common Wagtail Antipatterns"
type: antipatterns
order: 100
status: ready
maturity: unverified
tags: [wagtail, common-antipatterns]
related: [wagtail/99-ai-review-checklist]
when_to_use: "Read when reviewing Wagtail changes."
---
# Common Wagtail Antipatterns

## Purpose

Use this as a mandatory, evidence-based gate.

## Rules

**Rules:** [01-version-compatibility](01-version-compatibility.md) · [02-architecture](02-architecture.md)

- [ ] Do not guess versions from memory or use APIs from a different compatibility line.
- [ ] Do not bypass framework lifecycle APIs with direct table updates.
- [ ] Do not hide authorization only in templates or admin UI.
- [ ] Do not place core business behavior in signals, hooks, templates, or implicit callbacks.
- [ ] Do not deploy migrations or dependency upgrades without a tested forward and rollback plan.

