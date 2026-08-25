---
id: wagtail/16-multisite
topic: wagtail
slug: multisite
title: "Wagtail Multisite"
type: doc
order: 16
status: ready
maturity: unverified
tags: [wagtail, multisite, Site, root_page, hostname]
related: [wagtail/03-page-models, wagtail/06-permissions]
when_to_use: "Read when adding Site records, hostnames, or scoping pages to a site root."
---
# Wagtail Multisite

## Purpose

Defines how multiple hostnames share one Wagtail tree.

## Rules

- Resolve the current site with Wagtail's site middleware / `Site.find_for_request(request)`, not by parsing `Host` ad hoc.
- Scope public QuerySets to the site root (`descendant_of`, `in_site`) so one hostname cannot serve another's pages.
- Give each `Site` a `root_page` and hostname/port that match the reverse proxy.
- Permissions and workflows can differ per subtree; do not assume superuser-only is enough for a second brand.
- Test at least two hostnames in CI when the project is multi-site.

## Good Example

```python
from wagtail.models import Site

def home(request):
    site = Site.find_for_request(request)
    page = site.root_page.specific
    return page.serve(request)
```

The served homepage is the root of the `Site` that matched the request host.

## Bad Example

```python
def home(request):
    page = Page.objects.filter(title="Home").first()
    return page.serve(request)
```

`title="Home"` is ambiguous across sites and ignores hostname routing.

## Checklist

- [ ] Site resolution uses `Site.find_for_request` (or equivalent)
- [ ] Public queries are scoped to the site root
- [ ] Hostname/port match the proxy; a second host is tested if multi-site

## Related

- `wagtail/03-page-models`
- `wagtail/06-permissions`
