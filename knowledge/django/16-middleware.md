---
id: django/16-middleware
topic: django
slug: middleware
title: "Django Middleware"
type: doc
order: 16
status: ready
maturity: unverified
tags: [django, middleware, MIDDLEWARE, process_request, SecurityMiddleware]
related: [django/03-settings, django/06-security]
when_to_use: "Read when adding or reordering middleware, or changing request/response wrappers."
---
# Django Middleware

## Purpose

Defines where cross-cutting request policy belongs.

## Rules

- Keep `MIDDLEWARE` order intentional: security, session, locale, common, CSRF, auth, messages, clickjacking. Do not insert custom middleware before `SecurityMiddleware` without a reason.
- Custom middleware must implement the `__init__(get_response)` / `__call__(request)` contract (or `MiddlewareMixin` if the project already uses it).
- Do not query the database or call remote APIs on every request unless the project already accepts that cost.
- Short-circuit with a `HttpResponse` only when the request is fully handled; otherwise call `get_response(request)`.
- Test middleware with the real stack (`Client`) so CSRF and auth still run.

## Good Example

```python
class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = request.headers.get("X-Request-ID", "")
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response
```

The middleware is stateless, does not hit the database, and always calls `get_response`.

## Bad Example

```python
class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        Audit.objects.create(path=request.path, user=request.user)
        return self.get_response(request)
```

Writing a row on every request (including health checks) and reading `request.user` before `AuthenticationMiddleware` is expensive and order-dependent.

## Checklist

- [ ] `MIDDLEWARE` order keeps security, CSRF, and auth in their required positions
- [ ] Custom middleware uses the `__init__` / `__call__` contract
- [ ] Per-request work is cheap and tested through `Client`

## Related

- `django/03-settings`
- `django/06-security`
