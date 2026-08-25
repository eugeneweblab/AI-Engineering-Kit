---
id: wagtail/30-engineering-principles
topic: wagtail
slug: engineering-principles
title: "Wagtail Engineering Principles"
type: doc
order: 30
status: ready
maturity: unverified
tags: [wagtail, engineering-principles]
related: [wagtail/00-overview, wagtail/02-architecture, django/30-engineering-principles]
when_to_use: "Read when a Wagtail change spans pages, Django, and deploy and you need the default decision order."
---
# Wagtail Engineering Principles

## Purpose

States the decision order for Wagtail work when several documents could apply.

## Rules

- Detect Wagtail, Django, and Python versions first and intersect the matrix.
- Apply Django rules to settings, ORM, auth, and deploy; apply Wagtail rules to tree, revisions, StreamField, and admin.
- Prefer `Page` APIs (`add_child`, `save_revision`, `live().public()`) over table updates.
- Editorial state is part of correctness: draft vs live vs scheduled vs private.
- Finish with the Wagtail production checklist, AI review checklist, and antipatterns list.

## Good Example

```python
page = ArticlePage(title=title)
home.add_child(instance=page)
page.save_revision(user=editor).publish()
```

The page is in the tree, has a revision, and is live only after publish.

## Bad Example

```python
ArticlePage.objects.create(title=title, live=True, path="00010003", depth=2)
```

Create-with-path skips tree APIs, revisions, and site/locale filters.

## Checklist

- [ ] Version matrix was intersected
- [ ] Django and Wagtail rules both applied
- [ ] Tree and revision APIs were used
- [ ] Checklists 98, 99, and 100 were run

## Related

- `wagtail/00-overview`
- `wagtail/02-architecture`
- `django/30-engineering-principles`
