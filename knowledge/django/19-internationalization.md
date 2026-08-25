---
id: django/19-internationalization
topic: django
slug: internationalization
title: "Django Internationalization"
type: doc
order: 19
status: ready
maturity: unverified
tags: [django, internationalization, gettext, gettext_lazy, ugettext, makemessages]
related: [django/13-templates, django/03-settings]
when_to_use: "Read when adding translatable strings, locales, timezone handling, or gettext_lazy."
---
# Django Internationalization

## Purpose

Defines how user-facing strings and dates are localized.

## Rules

- Wrap user-facing Python strings in `gettext` (`_`) or `gettext_lazy` on model `verbose_name` and forms; never use the removed `ugettext`.
- Keep `USE_I18N` / `USE_TZ` aligned with the project; store datetimes in UTC when `USE_TZ` is on.
- Run `makemessages` / `compilemessages` in the translation workflow; do not edit `.mo` files by hand.
- Do not concatenate translated fragments if locale grammar needs a single format string.
- Locale middleware must sit in the documented `MIDDLEWARE` order.

## Good Example

```python
from django.utils.translation import gettext_lazy as _

class Invoice(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("invoice")
        verbose_name_plural = _("invoices")
```

Admin and forms pick up translations without evaluating them at import for every language.

## Bad Example

```python
from django.utils.translation import ugettext as _

message = _("Hello") + " " + user.name
```

`ugettext` is removed on current Django, and concatenating translations breaks word order.

## Checklist

- [ ] User-facing strings use `gettext` / `gettext_lazy`, not `ugettext`
- [ ] Model and form labels are lazy where they run at import
- [ ] Timezones follow `USE_TZ`; translations are compiled, not hand-edited `.mo`

## Related

- `django/13-templates`
- `django/03-settings`
