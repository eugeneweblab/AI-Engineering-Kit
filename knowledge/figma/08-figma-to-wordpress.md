---
id: figma/08-figma-to-wordpress
topic: figma
slug: figma-to-wordpress
title: "Figma to WordPress"
type: doc
order: 8
status: ready
tags: [figma, figma-to-wordpress]
related: []
when_to_use: ""
---
# Figma to WordPress

## Purpose

This document defines the engineering workflow for converting Figma designs into professional WordPress implementations.

The objective is not to reproduce the design as static HTML, but to create maintainable, reusable, editable WordPress solutions that integrate naturally with the CMS.

The final result should allow content editors to manage the website without modifying code.

---

## Core Principle

Design the editing experience first.

Every visual element should be evaluated from two perspectives:

- frontend rendering;
- content management.

A successful WordPress implementation is both visually accurate and editor-friendly.

---

## AI Mindset

Before writing code, ask:

- Which content should be editable?
- Which content is static?
- Which data belongs in WordPress?
- Which UI should become a reusable block?
- Which elements should be configurable?
- How will the client update this section?

Never optimize only for developers.

Optimize for content editors as well.

---

## Implementation Workflow

Every page should follow this sequence:

```
Analyze Figma
        ↓
Identify Dynamic Content
        ↓
Identify Reusable Sections
        ↓
Choose WordPress Architecture
        ↓
Plan Editor Experience
        ↓
Implement Frontend
        ↓
Connect Dynamic Data
        ↓
Verify Editor Workflow
```

---

## Step 1 — Identify Dynamic Content

Every visible element should be classified.

Examples:

Dynamic:

- headings;
- paragraphs;
- images;
- buttons;
- links;
- videos;
- testimonials;
- products;
- posts.

Usually Static:

- decorative graphics;
- layout structure;
- icons;
- animations;
- spacing.

Dynamic content should never be hardcoded.

---

## Step 2 — Identify Reusable Sections

Review the page.

Typical reusable sections include:

- Hero
- Features
- CTA
- FAQ
- Testimonials
- Team
- Pricing
- Contact
- Statistics

Repeated sections should become reusable editor components.

---

## Step 3 — Determine Data Source

For every piece of content determine its source.

Possible sources:

- Post Title
- Post Content
- Featured Image
- Custom Fields
- Taxonomies
- Menus
- Options
- REST API
- WooCommerce
- External API

Never hardcode content that already exists inside WordPress.

---

## Step 4 — Plan Editor Experience

Every editable field should answer:

Who edits this?

Examples:

Marketing Team

↓

Heading

↓

Rich Text

---

Content Editor

↓

Image

↓

Media Library

---

Administrator

↓

CTA Button

↓

Link Picker

The editing experience should be intuitive.

---

## Step 5 — Reuse Existing Components

Before building anything search for:

- Gutenberg blocks;
- template parts;
- patterns;
- shared components;
- custom fields;
- reusable PHP templates;
- existing React components.

Reuse before creating.

---

## Step 6 — Preserve Design System

Do not recreate styles per page.

Reuse:

- typography;
- spacing;
- colors;
- buttons;
- forms;
- cards;
- layout components.

A design system should grow, not fragment.

---

## Step 7 — Separate Responsibilities

Recommended architecture:

```
Template

        ↓

View

        ↓

Component

        ↓

Business Logic

        ↓

WordPress API
```

Templates should not contain business logic.

---

## Step 8 — Accessibility

Verify:

- semantic HTML;
- heading hierarchy;
- image alt text;
- keyboard navigation;
- focus visibility;
- form labels.

Accessibility should not depend on WordPress.

---

## Step 9 — Performance

Review:

- image sizes;
- lazy loading;
- responsive images;
- query count;
- asset loading;
- cache opportunities.

The CMS should not become a performance bottleneck.

---

## Step 10 — Verify Editor Workflow

Before completing implementation ask:

Can a non-technical editor:

- update text?
- replace images?
- change links?
- reorder sections?
- publish content?

If not, improve the editor experience.

---

## WordPress Mapping

Typical mapping:

```
Heading

↓

Post Title

or

Custom Field

--------------------------------

Paragraph

↓

Post Content

or

Rich Text Field

--------------------------------

Image

↓

Featured Image

or

Media Field

--------------------------------

Button

↓

Link Field

--------------------------------

Cards

↓

Repeater

or

Query Loop

--------------------------------

Testimonials

↓

Custom Post Type

--------------------------------

FAQ

↓

Repeater

--------------------------------

Products

↓

WooCommerce
```

Choose the simplest structure that satisfies the requirements.

---

## AI Execution Checklist

## Investigation

☐ Identify editable content.

☐ Identify reusable sections.

☐ Identify data sources.

☐ Review existing components.

☐ Review editor workflow.

---

## Planning

☐ Minimize hardcoded content.

☐ Reuse WordPress features.

☐ Preserve design system.

☐ Keep templates clean.

---

## Verification

☐ Content is editable.

☐ Components are reusable.

☐ Design matches Figma.

☐ Performance is acceptable.

☐ Accessibility is preserved.

☐ Architecture remains maintainable.

---

## Common Mistakes

Avoid:

Hardcoding text.

Hardcoding images.

Duplicating templates.

Creating page-specific components.

Ignoring editor usability.

Embedding business logic inside templates.

Ignoring reusable sections.

Building layouts that only developers can maintain.

---

## Completion Criteria

A Figma-to-WordPress implementation is complete when:

- editors can manage all intended content;
- reusable components have been created where appropriate;
- existing WordPress functionality has been reused;
- architecture remains clean;
- the implementation is scalable;
- the visual result accurately reflects the design.

---

## Summary

Professional WordPress development is not about converting pixels into HTML.

It is about transforming a design into a maintainable content management experience that remains flexible as the website evolves.