---
id: wagtail/01-version-compatibility
topic: wagtail
slug: version-compatibility
title: "Wagtail and Django Version Compatibility"
type: doc
order: 1
status: ready
maturity: unverified
tags: [wagtail, version-compatibility, LTS]
related: [django/01-version-support, wagtail/11-upgrades]
when_to_use: "Read before choosing Wagtail, Django, or Python versions or changing those dependencies."
verified_against: "Wagtail 6.3 LTS through 7.4 LTS; Django 4.2 through 6.0"
source_urls: ["https://docs.wagtail.org/en/stable/releases/upgrading.html", "https://docs.wagtail.org/en/stable/releases/index.html"]
last_reviewed: "2026-08-25"
review_after: "2026-11-25"
---
# Wagtail and Django Version Compatibility

## Purpose

Defines the supported Wagtail, Django, and Python matrix.

## Rules

- Use the official compatibility matrix; never assume the newest Django works with an older Wagtail.
- Compatibility is not security support: reject Django 4.2, 5.0, and 5.1 for new deployments even when an older Wagtail release can import them.
- Wagtail 6.3 LTS supports Django 4.2, 5.0, 5.1, and 5.2 with the documented patch caveat; Wagtail 7.0 LTS supports Django 4.2, 5.1, and 5.2.
- Wagtail 7.2 supports Django 4.2, 5.1, 5.2, and 6.0; Wagtail 7.4 LTS supports Django 5.2 and 6.0.
- Wagtail 7.4 LTS does not list Django 6.1 as compatible; do not upgrade a Wagtail project to Django 6.1 until its installed Wagtail line adds support.
- Intersect Python as well: Wagtail 7.4 lists Python 3.10–3.14, but Django 6.0 and 6.1 require Python 3.12+. Wagtail 7.4 plus Django 6.0 means Python 3.12–3.14.
- Upgrade Wagtail, Django, and Python as separate tested steps.
- Read every intervening Wagtail upgrade note and use `wagtail update_index` / the upgrade-check command when available.

## Good Example

```python
# Wagtail 7.4.x + Django 5.2.x + Python 3.12
# All three are on the published matrix and still receive security fixes.
```

The lock file names a triple that exists in both the Wagtail matrix and Django's supported lines.

## Bad Example

```python
# Wagtail 7.4.x + Django 6.1.x + Python 3.10
```

Django 6.1 is not on the Wagtail 7.4 matrix, and Python 3.10 is below Django 6.x's floor even if Wagtail lists 3.10 for Django 5.2.

## Checklist

- [ ] Use the official compatibility matrix
- [ ] Every selected Django version is both Wagtail-compatible and still security-supported
- [ ] Python satisfies both Wagtail and the chosen Django line (Django 6.0 needs 3.12+)
- [ ] Django 6.1 is not selected with Wagtail 7.4 LTS
- [ ] Upgrade Wagtail, Django, and Python as separate tested steps
- [ ] Read every intervening Wagtail upgrade note and use the upgrade-check command when available

## Related

- `django/01-version-support`
- `wagtail/11-upgrades`
