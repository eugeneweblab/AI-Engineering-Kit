---
id: wagtail/19-redirects
topic: wagtail
slug: redirects
title: "Wagtail Redirects"
type: doc
order: 19
status: ready
maturity: unverified
tags: [wagtail, redirects, Redirect, RedirectFallbackMiddleware]
related: [wagtail/12-deployment, django/11-urls-and-views]
when_to_use: "Read when adding Redirect records, fallback middleware, or post-publish URL changes."
---
# Wagtail Redirects

## Purpose

Defines how old paths keep working after moves and republishes.

## Rules

- Create `Redirect` rows (or the project's redirect app) when a live URL changes; do not rely on editors remembering nginx-only rules.
- Enable `RedirectFallbackMiddleware` when the project uses Wagtail redirects as the last routing step.
- Prefer 301 for permanent content moves and 302 for temporary campaigns; do not 301 a URL that will be reused.
- Avoid duplicate sources of truth (Wagtail + CDN + nginx) without a documented winner.
- Test that the old path returns the new page after a move.

## Good Example

```python
from wagtail.contrib.redirects.models import Redirect

Redirect.add_redirect("/old-article/", page, permanent=True)
```

The old path is recorded in Wagtail and survives deploys.

## Bad Example

```python
# comments in nginx.conf only, no Redirect row
# rewrite ^/old-article$ /new-article permanent;
```

A CDN-only rewrite drifts from what editors see in admin and cannot be added at publish time.

## Checklist

- [ ] Live URL changes create a `Redirect` (or the documented equivalent)
- [ ] Status code matches permanence
- [ ] One system owns redirects; the old path is tested

## Related

- `wagtail/12-deployment`
- `django/11-urls-and-views`
