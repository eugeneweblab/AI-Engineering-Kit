---
id: wagtail/10-testing
topic: wagtail
slug: testing
title: "Wagtail Testing"
type: doc
order: 10
status: ready
maturity: unverified
tags: [wagtail, testing, WagtailPageTests, save_revision, StreamField]
related: [wagtail/01-version-compatibility, django/07-testing]
when_to_use: "Read when writing tests for pages, StreamField, publish/preview, or tree factories."
---
# Wagtail Testing

## Purpose

Defines tests for content trees and editorial lifecycle.

## Rules

- Build pages through Wagtail APIs and factories that preserve tree invariants (`add_child`, `WagtailPageTests`).
- Test draft, preview, publish, unpublish, scheduled, locale, alias, and permission paths as applicable.
- Assert public responses and persisted revision state, not only mocked hook calls.
- Test StreamField migrations against representative serialized values.
- Run the matrix selected by the Wagtail/Django/Python compatibility document.

## Good Example

```python
from wagtail.test.utils import WagtailPageTests

class ArticlePageTests(WagtailPageTests):
    def test_can_create_under_home(self):
        self.assertCanCreateAt(HomePage, ArticlePage)

    def test_publish_makes_title_public(self):
        home = HomePage.objects.first()
        page = ArticlePage(title="Draft")
        home.add_child(instance=page)
        page.save_revision().publish()
        self.assertTrue(ArticlePage.objects.live().filter(pk=page.pk).exists())
```

The tree is built with `add_child`, and live state is asserted after publish.

## Bad Example

```python
Page.objects.create(title="Orphan", path="00010002", depth=2, numchild=0)
```

Inserting path/depth by hand creates pages the tree APIs will not traverse correctly.

## Checklist

- [ ] Pages are created through Wagtail APIs / `WagtailPageTests`
- [ ] Draft, preview, publish, and permission paths are tested as applicable
- [ ] Assertions cover HTTP and revision rows, not only mocks
- [ ] StreamField migrations are tested against stored JSON
- [ ] The version matrix from the compatibility doc is run

## Related

- `wagtail/01-version-compatibility`
- `django/07-testing`
