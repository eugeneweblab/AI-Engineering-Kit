---
id: wagtail/11-upgrades
topic: wagtail
slug: upgrades
title: "Wagtail Upgrades"
type: doc
order: 11
status: ready
maturity: unverified
tags: [wagtail, upgrades, update_index, release notes]
related: [wagtail/01-version-compatibility, wagtail/10-testing]
when_to_use: "Read when upgrading Wagtail, or when release notes mention StreamField, hooks, or search."
---
# Wagtail Upgrades

## Purpose

Defines safe Wagtail upgrades and content migrations.

## Rules

- Read every intervening release note and execute documented upgrade checks.
- Upgrade Wagtail separately from Django and Python.
- Audit removed imports, renamed hooks, editor component APIs, search backends, and StreamField serialization changes.
- Back up the database and media and rehearse migration and rollback on production-scale data.
- Verify admin editing, preview, publishing, search, images, redirects, and APIs after upgrade.

## Good Example

```python
# 1. Wagtail 7.2 -> 7.3 (tests + update_index)
# 2. Wagtail 7.3 -> 7.4 (tests + update_index)
# 3. Django 5.2 stays pinned until 7.4 is green
```

Each Wagtail minor line is a release with its own notes, migrations, and search rebuild.

## Bad Example

```python
# pip install 'wagtail==7.4' 'Django==6.1'
```

Jumping Wagtail and an unsupported Django line in one lockfile change hides which upgrade broke the tree.

## Checklist

- [ ] Every intervening release note and upgrade check was executed
- [ ] Wagtail was upgraded separately from Django and Python
- [ ] Hooks, search, and StreamField serialization were audited
- [ ] Database and media backups were rehearsed
- [ ] Admin, preview, publish, search, images, redirects, and APIs were verified

## Related

- `wagtail/01-version-compatibility`
- `wagtail/10-testing`
