---
id: django/13-templates
topic: django
slug: templates
title: "Django Templates"
type: doc
order: 13
status: ready
maturity: unverified
tags: [django, templates, autoescape, csrf_token, safe, url]
related: [django/06-security, django/12-forms-and-validation]
when_to_use: "Read when changing Django templates, context processors, or custom template tags."
---
# Django Templates

## Purpose

Defines safe rendering and keeps queries out of the presentation layer.

## Rules

- Leave auto-escaping on; use `|safe` or `{% autoescape off %}` only for trusted, already-sanitized HTML.
- Resolve routes with `{% url %}` / `reverse()`, not hardcoded paths.
- Include `{% csrf_token %}` on POST forms that use cookie authentication.
- Do not run QuerySets, permission policy, or writes inside templates or custom tags.
- Prefetch relations in the view when the template walks `obj.related`.

## Good Example

```
<form method="post" action="{% url 'invoice-create' %}">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Save</button>
</form>
```

The action stays named, CSRF is present, and field values are escaped by default.

## Bad Example

```
{% for invoice in invoices %}
  <p>{{ invoice.owner.email|safe }}</p>
  <a href="/invoices/{{ invoice.pk }}/delete">delete</a>
{% endfor %}
```

`|safe` on user-adjacent data is XSS, the loop can N+1 `owner`, and the delete URL is a CSRF-less GET.

## Checklist

- [ ] Auto-escaping stays on except for documented trusted HTML
- [ ] Links and form actions use `{% url %}`
- [ ] Cookie-authenticated POST forms include `{% csrf_token %}`
- [ ] Templates do not issue queries or authorization decisions

## Related

- `django/06-security`
- `django/12-forms-and-validation`
