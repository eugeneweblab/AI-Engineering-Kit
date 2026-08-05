---
id: figma/09-figma-to-divi
topic: figma
slug: figma-to-divi
title: "Figma to Divi Builder"
type: doc
order: 9
status: ready
tags: [figma, figma-to-divi, preset]
related: [figma/07-figma-to-html, divi/05-layouts, divi/04-custom-modules, workflows/10-build-divi-module]
when_to_use: "Read before building a Figma design as an editable layout in the Divi Builder."
---
# Figma to Divi Builder

## Purpose

This document defines the engineering workflow for converting Figma designs into maintainable Divi Builder implementations.

The objective is to build layouts that accurately reproduce the design while remaining editable, reusable, performant, and easy for content editors to maintain.

Divi should be treated as a visual page builder—not as a replacement for software architecture.

---

## Core Principle

Use Divi for content composition.

Use custom code for engineering.

Every implementation should balance editor flexibility with code quality.

---

## AI Mindset

Before implementing a section, determine:

- Should this be built using native Divi modules?
- Does the project already contain a custom Divi module?
- Should this become a reusable layout?
- Should this be implemented as a Theme Builder template?
- Is custom JavaScript required?
- Is custom CSS required?
- Is PHP customization required?

Never implement everything with standard Divi modules if a cleaner engineering solution exists.

---

## Implementation Workflow

```
Analyze Figma
        ↓
Identify Sections
        ↓
Identify Existing Divi Modules
        ↓
Determine Required Custom Modules
        ↓
Implement Layout
        ↓
Add Responsive Behavior
        ↓
Optimize Performance
        ↓
Verify Editor Experience
```

---

## Step 1 — Split the Page Into Sections

Typical sections:

- Hero
- Features
- Services
- CTA
- Testimonials
- FAQ
- Pricing
- Contact
- Footer

Each section should become an independent Divi section.

Avoid building an entire page inside a single section.

---

## Step 2 — Prefer Native Modules

Always check whether Divi already provides an appropriate module.

Examples:

Use native modules for:

- Text
- Image
- Button
- Video
- Gallery
- Accordion
- Tabs
- Slider
- Form
- Blurb

Do not create custom modules without justification.

---

## Step 3 — Create Custom Modules Only When Necessary

Custom modules are appropriate when:

- complex layouts repeat across the project;
- business logic is required;
- third-party integrations are needed;
- native modules become difficult to maintain.

Custom modules should solve engineering problems—not visual preferences.

---

## Step 4 — Reuse Global Elements

Before creating new layouts, search for:

- Global Modules
- Theme Builder Templates
- Saved Sections
- Saved Rows
- Saved Layouts

Reuse existing assets whenever possible.

---

## Step 5 — Keep Styling Centralized

Prefer:

- Theme Options
- Child Theme CSS
- CSS variables
- Shared utility classes

Avoid:

- large amounts of inline CSS;
- duplicated module styling;
- page-specific hacks.

Styling should remain consistent across the project.

---

## Step 6 — Preserve the Design System

Do not recreate typography for every page.

Reuse:

- heading styles;
- button styles;
- spacing scale;
- colors;
- border radius;
- shadows.

The design system should exist outside individual layouts.

---

## Step 7 — Dynamic Content

Determine which content should be editable.

Typical examples:

- headings;
- body text;
- images;
- buttons;
- repeaters;
- testimonials;
- WooCommerce products;
- blog posts.

Content should come from WordPress whenever possible.

---

## Step 8 — Responsive Implementation

Review:

- section spacing;
- row stacking;
- typography scaling;
- image resizing;
- button widths;
- navigation behavior.

Avoid fixing responsive issues with excessive custom CSS.

---

## Step 9 — Performance

Review:

- unnecessary modules;
- duplicate assets;
- JavaScript execution;
- CSS size;
- image optimization;
- animation usage.

Every additional Divi module increases page complexity.

Use only what is necessary.

---

## Step 10 — Editor Experience

A content editor should be able to:

- edit text;
- replace images;
- change links;
- duplicate sections;
- reorder sections;
- publish changes.

Editors should not need to modify custom code.

---

## Recommended Engineering Strategy

Prefer this order:

```
Native Divi Module

        ↓

Existing Custom Module

        ↓

Shared Component

        ↓

New Custom Module
```

Always search before creating.

---

## When Custom Development Is Better

Prefer custom development for:

- advanced forms;
- API integrations;
- interactive applications;
- complex animations;
- account dashboards;
- search interfaces;
- booking systems;
- business logic.

Divi should manage layout—not application logic.

---

## AI Execution Checklist

## Investigation

☐ Review the Figma design.

☐ Identify reusable sections.

☐ Review existing Divi modules.

☐ Review existing custom modules.

☐ Review Theme Builder templates.

---

## Planning

☐ Minimize custom modules.

☐ Preserve the design system.

☐ Plan responsive behavior.

☐ Plan editor workflow.

---

## Verification

☐ Layout matches Figma.

☐ Native modules are reused.

☐ Custom modules are justified.

☐ Responsive behavior is correct.

☐ Content is editable.

☐ Performance remains acceptable.

---

## Common Mistakes

Avoid:

Creating custom modules for simple layouts.

Duplicating module styles.

Hardcoding content.

Embedding business logic inside templates.

Adding excessive custom CSS.

Using unnecessary animations.

Ignoring existing reusable layouts.

Building pages that only developers can maintain.

---

## Examples

**Good Example** — global presets carry the design, layouts carry the structure

```text
Design decision            Divi mechanism
─────────────────────────  ────────────────────────────────────────────
Colour palette             Theme Options → global colours
Type scale                 Theme Builder → global body/heading presets
Repeated card              Library layout, referenced globally
Section spacing            Module preset (padding/margin), applied by name
One-off tweak              Custom CSS on that module only, documented
```

```css
/* Divi > Theme Options > Custom CSS — tokens once, referenced everywhere. */
:root {
	--acme-surface: #ffffff;
	--acme-ink: #111827;
	--acme-accent: #2563eb;
	--acme-space-md: 1rem;
}

.acme-card .et_pb_text_inner {
	color: var(--acme-ink);
	padding: var(--acme-space-md);
}
```

A global library layout means the card is edited once. A preset means a spacing change does
not require opening forty modules.

**Bad Example** — every value typed into every module

```css
/* Custom CSS added per module, in the module's own settings panel, with
   !important to beat the inline styles Divi generates. Forty copies of this
   exist across the site and none of them can be found by searching the repo. */
.et_pb_text_0 { color: #111827 !important; padding: 17px !important; }
.et_pb_text_1 { color: #111827 !important; padding: 16px !important; }
.et_pb_text_2 { color: #111828 !important; padding: 17px !important; }
```

The numbered selectors also change when a module is reordered, so the styling silently detaches
from the element it was written for.

---

## Completion Criteria

A Figma-to-Divi implementation is complete when:

- the design is reproduced accurately;
- editors can manage content easily;
- native modules have been reused whenever appropriate;
- custom modules are introduced only when necessary;
- the implementation remains maintainable, performant, and scalable.

---

## Summary

Professional Divi development is not measured by how little custom code is written.

It is measured by how effectively Divi, WordPress, and custom engineering work together to create a maintainable product.

## Related

- `knowledge/figma/07-figma-to-html.md`
- `knowledge/divi/05-layouts.md`
- `knowledge/divi/04-custom-modules.md`
- `knowledge/workflows/10-build-divi-module.md`
