---
id: wagtail/17-localization
topic: wagtail
slug: localization
title: "Wagtail Localization"
type: doc
order: 17
status: ready
maturity: unverified
tags: [wagtail, localization, Locale, alias, copy_for_translation]
related: [wagtail/03-page-models, django/19-internationalization]
when_to_use: "Read when adding locales, translated pages, aliases, or copy_for_translation."
---
# Wagtail Localization

## Purpose

Defines locale trees and translated pages.

## Rules

- Use Wagtail `Locale` and `copy_for_translation` / aliases rather than duplicating trees by hand.
- Filter public QuerySets by `locale` (and site) so a French URL does not serve English live pages.
- Do not share a single draft across locales unless the project uses aliases by design.
- Keep Django `gettext` for UI chrome; page content lives in translated pages, not in `.po` files.
- Test at least one translated page's live URL and an untranslated 404.

## Good Example

```python
from wagtail.models import Locale

def articles(request):
    locale = Locale.get_active()
    return ArticlePage.objects.live().public().filter(locale=locale)
```

The listing cannot mix locales.

## Bad Example

```python
ArticlePage.objects.live().filter(title__contains="Home")
```

Title matching is not locale isolation and will mix translations.

## Checklist

- [ ] Locales use Wagtail's locale/alias APIs
- [ ] Public querysets filter `locale` (and site)
- [ ] UI chrome uses Django i18n; page copy lives on translated pages

## Related

- `wagtail/03-page-models`
- `django/19-internationalization`
