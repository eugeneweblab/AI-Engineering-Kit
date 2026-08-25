---
id: wagtail/18-forms
topic: wagtail
slug: forms
title: "Wagtail Forms"
type: doc
order: 18
status: ready
maturity: unverified
tags: [wagtail, forms, AbstractEmailForm, FormPage, FormSubmission]
related: [django/12-forms-and-validation, wagtail/06-permissions]
when_to_use: "Read when adding FormPage, AbstractEmailForm, or storing FormSubmission rows."
---
# Wagtail Forms

## Purpose

Defines editor-built forms and their submissions.

## Rules

- Use Wagtail form pages (`AbstractEmailForm` / `FormPage`) when editors must change fields; use Django `Form` when the schema is owned by developers.
- Store submissions as `FormSubmission` (or the project's store); do not email-only without a retention policy.
- Validate and escape submission values; treat them as untrusted input in templates and CSV exports.
- Protect form pages with CSRF and, where needed, captcha/rate limits at the edge.
- Restrict who can export submissions; exports are personal data.

## Good Example

```python
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from modelcluster.fields import ParentalKey

class FormField(AbstractFormField):
    page = ParentalKey("FormPage", on_delete=models.CASCADE, related_name="form_fields")

class FormPage(AbstractEmailForm):
    content_panels = AbstractEmailForm.content_panels
```

Editors add fields in admin; submissions go through Wagtail's form pipeline.

## Bad Example

```python
def contact(request):
    send_mail("Contact", str(request.POST), "from@x", ["to@x"])
    return HttpResponse("ok")
```

Raw POST is emailed with no CSRF-aware form, no storage policy, and no field validation.

## Checklist

- [ ] Editor-owned forms use Wagtail form pages; developer-owned forms use Django `Form`
- [ ] Submissions are stored and treated as untrusted
- [ ] Exports are permissioned; CSRF remains on

## Related

- `django/12-forms-and-validation`
- `wagtail/06-permissions`
