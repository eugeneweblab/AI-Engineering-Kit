---
id: wagtail/26-frontend-assets
topic: wagtail
slug: frontend-assets
title: "Wagtail Frontend Assets"
type: doc
order: 26
status: ready
maturity: unverified
tags: [wagtail, frontend-assets, static, collectstatic, ManifestStaticFilesStorage]
related: [django/14-static-and-media, wagtail/08-images-and-documents]
when_to_use: "Read when bundling CSS/JS for Wagtail templates or the admin frontend."
---
# Wagtail Frontend Assets

## Purpose

Defines site CSS/JS versus Wagtail admin assets.

## Rules

- Serve site CSS/JS through Django staticfiles (`{% static %}`, `collectstatic`); do not commit compiled files unless the project already does.
- Do not edit Wagtail's vendored admin static in `site-packages`. Override via documented hooks or a small extra stylesheet.
- Keep image renditions in Wagtail's image pipeline; CSS background URLs still go through staticfiles.
- Hash static files in production (`ManifestStaticFilesStorage` or the project's CDN hasher).
- Admin custom JS must not assume undocumented DOM structure without a test.

## Good Example

```
{% load static %}
<link rel="stylesheet" href="{% static 'css/site.css' %}">
```

The hashed file is collected at deploy; templates do not point at `/static/css/site.css` by hand.

## Bad Example

```
<link rel="stylesheet" href="/static/wagtailadmin/css/core.css">
```

Pinning a private admin path breaks on the next Wagtail upgrade and bypasses collectstatic hashing.

## Checklist

- [ ] Site assets use `{% static %}` and `collectstatic`
- [ ] Admin CSS/JS is not patched in `site-packages`
- [ ] Production static files are hashed

## Related

- `django/14-static-and-media`
- `wagtail/08-images-and-documents`
