---
id: wagtail/08-images-and-documents
topic: wagtail
slug: images-and-documents
title: "Wagtail Images and Documents"
type: doc
order: 8
status: ready
maturity: unverified
tags: [wagtail, images-and-documents, get_rendition, fill, Document, Collection]
related: [django/06-security, wagtail/12-deployment]
when_to_use: "Read when changing Image/Document uploads, renditions, or private media serving."
---
# Wagtail Images and Documents

## Purpose

Defines secure rendition and file handling.

## Rules

- Use Wagtail image renditions (`get_rendition`, `{% image %}`) rather than ad hoc resizing and avoid unbounded user-controlled rendition specs.
- Validate upload size and type and configure storage permissions independently for public and private media.
- Do not treat filename extensions as trusted content types.
- Test focal points, missing renditions, remote storage, and private document access.

## Good Example

```
{% load wagtailimages_tags %}
{% image page.hero fill-800x400 jpegquality-80 as hero %}
<img src="{{ hero.url }}" alt="{{ page.hero.title }}" width="{{ hero.width }}" height="{{ hero.height }}">
```

The rendition filter is a fixed spec, not a string from the query string.

## Bad Example

```python
spec = request.GET["spec"]
url = image.get_rendition(spec).url
```

A user-controlled spec can generate unbounded renditions and exhaust CPU and storage.

## Checklist

- [ ] Renditions use fixed specs, not user-controlled strings
- [ ] Upload size/type and public vs private storage are configured
- [ ] Filename extensions are not trusted as content types
- [ ] Focal points, missing files, remote storage, and private documents are tested

## Related

- `django/06-security`
- `wagtail/12-deployment`
