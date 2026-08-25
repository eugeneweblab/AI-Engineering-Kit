---
id: wagtail/29-project-structure
topic: wagtail
slug: project-structure
title: "Wagtail Project Structure"
type: doc
order: 29
status: ready
maturity: unverified
tags: [wagtail, project-structure, home, wagtail_hooks]
related: [wagtail/02-architecture, django/02-architecture]
when_to_use: "Read when adding apps, splitting Page models, or placing wagtail_hooks.py."
---
# Wagtail Project Structure

## Purpose

Defines where pages, snippets, hooks, and Django domain code live.

## Rules

- Keep a small number of apps by capability (`home`, `blog`, `forms`), not one app per page type unless the project already does that.
- Put `wagtail_hooks.py` next to the app that owns the hook.
- Keep Django services (billing, identity) importable without Wagtail; do not put them in `models.py` of a `Page`.
- Templates follow the app that owns the page type (`blog/templates/blog/article_page.html`).
- Settings stay in the Django settings package; do not add a second Wagtail-only config root.

## Good Example

```python
# blog/models.py  -> ArticlePage
# blog/wagtail_hooks.py
# billing/services.py  -> charge_invoice() with no Page import
```

CMS types and domain billing do not share a module.

## Bad Example

```python
# home/models.py contains HomePage, ArticlePage, Author snippet,
# Celery tasks, and Stripe calls
```

One module becomes the entire product and cannot be tested without Wagtail.

## Checklist

- [ ] Apps follow capabilities, not one-class-per-app unless already conventional
- [ ] Hooks sit in the owning app
- [ ] Non-CMS services do not import `Page`

## Related

- `wagtail/02-architecture`
- `django/02-architecture`
