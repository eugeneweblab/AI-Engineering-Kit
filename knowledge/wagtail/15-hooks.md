---
id: wagtail/15-hooks
topic: wagtail
slug: hooks
title: "Wagtail Hooks"
type: doc
order: 15
status: ready
maturity: unverified
tags: [wagtail, hooks, register_hook, hooks.register, wagtail_hooks]
related: [wagtail/02-architecture, wagtail/06-permissions]
when_to_use: "Read when adding wagtail_hooks.py, register_page_listing_buttons, or after_create_page."
---
# Wagtail Hooks

## Purpose

Defines extension points that must stay thin and explicit.

## Rules

- Put hooks in `wagtail_hooks.py` (or the project's agreed module); register with `@hooks.register`.
- Keep hooks as adapters: enqueue work, add a button, or filter a queryset. Do not hide checkout, tree moves, or publishes inside a hook.
- Re-check permissions inside hook handlers; listing buttons are not authorization.
- Prefer documented hook names; do not patch private Wagtail modules.
- Test hooks through an admin request or page operation, not only by calling the function.

## Good Example

```python
from wagtail import hooks
from wagtail.admin.menu import MenuItem

@hooks.register("register_admin_menu_item")
def register_reports_menu_item():
    return MenuItem("Reports", "/admin/reports/", icon_name="doc-full")
```

The hook adds navigation; the report view still enforces staff permissions.

## Bad Example

```python
@hooks.register("after_create_page")
def publish_everything(request, page):
    page.save_revision().publish()
```

Auto-publishing on create bypasses workflows and the editor's draft intent.

## Checklist

- [ ] Hooks live in the agreed module and use `@hooks.register`
- [ ] Core business writes are not implemented only inside a hook
- [ ] Hook actions re-check permissions and are covered by an admin/page test

## Related

- `wagtail/02-architecture`
- `wagtail/06-permissions`
