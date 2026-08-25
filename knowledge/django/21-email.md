---
id: django/21-email
topic: django
slug: email
title: "Django Email"
type: doc
order: 21
status: ready
maturity: unverified
tags: [django, email, send_mail, EmailMessage, locmem, EMAIL_BACKEND]
related: [django/03-settings, django/07-testing]
when_to_use: "Read when sending email, changing EMAIL_BACKEND, or asserting outbox contents in tests."
---
# Django Email

## Purpose

Defines how the project sends mail without leaking data or blocking requests.

## Rules

- Send through Django's email API (`send_mail`, `EmailMessage`, `mail_admins`); do not open raw SMTP sockets.
- Set `EMAIL_BACKEND` per environment: locmem or console in tests, SMTP or the vendor backend in production.
- Do not send email inside `transaction.atomic` if a later rollback would still deliver; use `transaction.on_commit`.
- Do not log full message bodies, tokens, or recipient lists at INFO in production.
- Fail visibly when required `DEFAULT_FROM_EMAIL` / SMTP secrets are missing.

## Good Example

```python
from django.core.mail import EmailMessage
from django.db import transaction

def notify_owner(invoice):
    email = EmailMessage(
        subject="Invoice ready",
        body=f"Invoice {invoice.pk} is ready.",
        to=[invoice.owner.email],
    )
    transaction.on_commit(email.send)
```

The message is built with the email API and sent only after the invoice commit succeeds.

## Bad Example

```python
import smtplib

def notify_owner(invoice):
    smtp = smtplib.SMTP("localhost")
    smtp.sendmail("root@localhost", invoice.owner.email, invoice.secret_link)
```

Raw SMTP skips backends, tests, and `on_commit`, and puts a secret in the body with no audit trail.

## Checklist

- [ ] Mail goes through Django's email API and the configured `EMAIL_BACKEND`
- [ ] Sends that depend on a commit use `transaction.on_commit`
- [ ] Tests use the locmem backend and assert on `django.core.mail.outbox`

## Related

- `django/03-settings`
- `django/07-testing`
