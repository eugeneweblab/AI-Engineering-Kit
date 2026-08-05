---
id: workflows/10-build-divi-module
topic: workflows
slug: build-divi-module
title: "Workflow — Build a Divi Module"
type: doc
order: 10
status: ready
tags: [workflows, build-divi-module]
related: [divi/04-custom-modules, divi/03-modules, figma/09-figma-to-divi]
  - divi/01-architecture
  - divi/03-modules
  - divi/04-custom-modules
  - divi/09-custom-css
  - divi/11-responsive-design
  - divi/12-accessibility
  - divi/10-performance
  - divi/98-production-checklist
  - divi/99-ai-review-checklist
  - wordpress/06-security
  - php/13-security
  - figma/09-figma-to-divi
when_to_use: "Follow this workflow when creating or modifying a custom Divi module."
---
# Workflow — Build a Divi Module

## Purpose

This workflow defines the standard engineering process for creating or modifying a custom Divi module.

Unlike generic WordPress development, Divi development requires maintaining compatibility with the Divi Builder ecosystem, preserving editor stability, and ensuring that modules behave consistently in both the Visual Builder and the frontend.

The objective is to create production-ready Divi modules that are maintainable, reusable, performant, and compatible with future Divi updates.

---

## Goal

Deliver a Divi module that:

- integrates naturally into the existing project;
- follows Divi architecture;
- uses existing project components when possible;
- works identically in the Visual Builder and frontend;
- supports responsive editing;
- is performant;
- is maintainable.

---

## Workflow Overview

```
Understand Requirements
        ↓
Analyze Existing Divi Modules
        ↓
Inspect Existing Design System
        ↓
Design Module API
        ↓
Implement Module
        ↓
Implement Builder Controls
        ↓
Implement Frontend Rendering
        ↓
Responsive Verification
        ↓
Builder Verification
        ↓
Complete
```

---

## Step 1 — Understand the Requirements

Determine:

- business goal;
- editor workflow;
- frontend behavior;
- responsive requirements;
- dynamic content requirements;
- reusable functionality.

Think from both perspectives:

- Content editor
- Website visitor

---

## Step 2 — Analyze Existing Modules

Search the repository for existing:

- Divi modules;
- shared React components;
- PHP rendering functions;
- helper utilities;
- design tokens;
- responsive helpers.

Never create a module before understanding existing implementation patterns.

Relevant knowledge:

- [Divi — Modules](../divi/03-modules.md) — what the built-in modules already cover; extending one usually beats writing a new one.
- [Divi — Custom Modules](../divi/04-custom-modules.md) — the `ET_Builder_Module` lifecycle, `get_fields()`, and `render()`.
- [Divi — Architecture](../divi/01-architecture.md) — how the builder loads modules and when the shortcode is parsed.
- [Divi — Global Elements](../divi/06-global-elements.md) — a global module or preset may remove the need for code entirely.

---

## Step 3 — Understand the Design

Review the complete design before implementation.

Identify:

- layout;
- spacing;
- typography;
- responsive behavior;
- hover states;
- interactive states;
- animations;
- reusable UI patterns.

Treat Figma as the source of truth.

Relevant knowledge:

- [Figma — Figma to Divi](../figma/09-figma-to-divi.md) — mapping frames onto sections, rows, and modules.
- [Figma — Design Token Extraction](../figma/03-design-token-extraction.md) — pulling spacing, color, and type values as tokens instead of eyeballing them.
- [Figma — Responsive Analysis](../figma/05-responsive-analysis.md) — deriving the breakpoint behavior the module must support.
- [Workflow — Implement a Figma Design](01-implement-figma-design.md) — the full design-to-code process.

---

## Step 4 — Design the Module API

Design editor fields before implementation.

Determine:

- text fields;
- rich text fields;
- images;
- repeaters;
- toggles;
- selects;
- color controls;
- spacing controls;
- typography controls;
- responsive options.

Every option should have a clear purpose.

Avoid exposing unnecessary settings.

Every field declared in `get_fields()` becomes part of the module's contract: once an editor
saves a page with it, removing or renaming that field breaks existing content. Design the
field set as deliberately as a public API.

Relevant knowledge:

- [Divi — Custom Modules](../divi/04-custom-modules.md) — field types, `toggle_slug` grouping, and defaults.
- [Divi — Dynamic Content](../divi/07-dynamic-content.md) and [Divi — Custom Fields](../divi/15-custom-fields.md) — pull values from post meta instead of duplicating them in module settings.
- [Divi — Theme Builder](../divi/02-theme-builder.md) — when the requirement belongs in a template rather than a module.

---

## Step 5 — Reuse Existing Code

Search before creating:

- React components;
- helper functions;
- PHP utilities;
- CSS utilities;
- Tailwind utilities (if applicable);
- icons;
- animations.

Duplicate code should never become the default solution.

Relevant knowledge:

- [Divi — Custom CSS](../divi/09-custom-css.md) — where module styles belong and how they are enqueued.
- [CSS — CSS Variables](../css/20-css-variables.md) — reference design tokens rather than hardcoding hex values in `render()`.
- [PHP — Clean Code](../php/22-clean-code.md) — extract shared rendering helpers instead of copying markup between modules.

---

## Step 6 — Implement the Module

Separate responsibilities.

Builder

↓

Configuration

↓

Rendering

↓

Styling

↓

Business logic

↓

Utilities

Avoid mixing rendering logic with configuration logic.

Escape every attribute value on the way out — builder settings are stored content and are
edited by users, so `render()` must treat them as untrusted input.

Relevant knowledge:

- [Divi — Custom Modules](../divi/04-custom-modules.md) — keeping `render()` thin and delegating to services.
- [WordPress — Security](../wordpress/06-security.md) and [Security — Output Encoding](../security/10-output-encoding.md) — `esc_html`, `esc_attr`, `esc_url`, and `wp_kses_post` at output.
- [Divi — Security](../divi/19-security.md) — builder-specific pitfalls, including unescaped shortcode attributes.

---

## Step 7 — Implement Builder Experience

Verify:

- field grouping;
- labels;
- descriptions;
- sensible defaults;
- conditional fields;
- responsive controls;
- live preview behavior.

The editor experience should be intuitive.

Relevant knowledge:

- [Divi — Client Projects](../divi/27-client-projects.md) — controls a non-technical editor can use without breaking the layout.
- [Divi — Layouts](../divi/05-layouts.md) — how the module behaves once it is dropped into an existing row.
- [Divi — Debugging](../divi/20-debugging.md) — diagnosing a module that renders on the frontend but not in the Visual Builder.

---

## Step 8 — Verify Frontend Rendering

Review:

- semantic HTML;
- accessibility;
- responsive layout;
- typography;
- spacing;
- hover states;
- loading behavior;
- dynamic content.

Frontend output should match the design system.

Relevant knowledge:

- [Divi — Accessibility](../divi/12-accessibility.md) and [Accessibility — Semantic HTML](../accessibility/03-semantic-html.md) — headings, landmarks, and labels in generated markup.
- [Accessibility — Keyboard Navigation](../accessibility/04-keyboard-navigation.md) — interactive modules (tabs, accordions, sliders) must work without a mouse.
- [Divi — SEO](../divi/13-seo.md) and [SEO — Structured Data](../seo/09-structured-data.md) — heading hierarchy and markup that search engines can parse.
- [Divi — Responsive Design](../divi/11-responsive-design.md) — the breakpoint model the builder exposes.

---

## Step 9 — Performance Review

Review:

- unnecessary renders;
- duplicate API calls;
- duplicate CSS;
- unnecessary JavaScript;
- image optimization;
- lazy loading;
- asset loading.

Performance matters inside both the builder and the frontend.

Relevant knowledge:

- [Divi — Performance](../divi/10-performance.md) — Divi's own asset pipeline, dynamic CSS, and what a custom module adds to it.
- [Performance — Images](../performance/11-images.md) and [Figma — Image Assets](../figma/18-image-assets.md) — correctly sized, modern-format media.
- [Performance — Lazy Loading](../performance/09-lazy-loading.md) — deferring below-the-fold work.
- [Performance — Web Vitals](../performance/18-web-vitals.md) — a module that shifts layout after load will show up as CLS.

---

## Step 10 — Compatibility Review

Verify:

- Visual Builder;
- frontend rendering;
- responsive editing;
- multilingual plugins;
- caching plugins;
- latest supported Divi version;
- latest supported WordPress version.

Compatibility should be confirmed before completion.

Relevant knowledge:

- [Divi — Testing](../divi/21-testing.md) and [Divi — Maintenance](../divi/23-maintenance.md) — verifying the module survives a Divi update.
- [Divi — Deployment](../divi/22-deployment.md) — moving the module from staging to production without losing builder content.
- [Divi — WooCommerce](../divi/14-woocommerce.md) — extra surface to check when the site is a store.

---

## AI Execution Checklist

## Investigation

☐ Understand the requirements.

☐ Analyze existing Divi modules.

☐ Review project architecture.

☐ Review design system.

☐ Search reusable code.

---

## Planning

☐ Design module settings.

☐ Define reusable components.

☐ Plan responsive behavior.

☐ Plan builder experience.

---

## Implementation

☐ Follow existing architecture.

☐ Reuse components.

☐ Keep responsibilities separated.

☐ Match design system.

☐ Avoid duplicate logic.

---

## Verification

☐ Verify Visual Builder.

☐ Verify frontend.

☐ Verify responsive layouts.

☐ Verify accessibility.

☐ Verify performance.

☐ Verify editor experience.

☐ Verify translations.

---

## Divi Engineering Principles

Prefer:

Small focused modules

Reusable React components

Reusable PHP utilities

Shared styling

Consistent editor controls

Semantic HTML

Responsive-first implementation

Avoid:

Business logic inside rendering methods

Large monolithic modules

Duplicate controls

Duplicate CSS

Inline styles when avoidable

Hardcoded spacing values

Hardcoded colors

---

## Common Mistakes

Avoid:

Building modules without reviewing existing ones.

Creating duplicate editor controls.

Ignoring Visual Builder behavior.

Ignoring responsive editing.

Mixing frontend logic with builder configuration.

Hardcoding design values.

Ignoring accessibility.

Ignoring project conventions.

---

## Completion Criteria

The workflow is complete only if:

- requirements are satisfied;
- the module works correctly in the Visual Builder;
- the frontend matches the expected design;
- responsive behavior has been verified;
- existing project architecture has been respected;
- reusable code has been used where appropriate;
- documentation has been updated if necessary.

---

## Expected AI Output

After completing this workflow, the AI should explain:

- the module's purpose;
- the builder settings that were added;
- reused components and utilities;
- responsive strategy;
- accessibility considerations;
- compatibility verification;
- files that were modified.

---

## Self-Verification — Topic Checklists

Before marking the module complete, run it through the checklists of the topics it touched:

- Divi — [Production Checklist](../divi/98-production-checklist.md), [AI Review Checklist](../divi/99-ai-review-checklist.md), [Common Antipatterns](../divi/100-common-antipatterns.md).
- WordPress — [Production Checklist](../wordpress/98-production-checklist.md), [AI Review Checklist](../wordpress/99-ai-review-checklist.md), [Common Antipatterns](../wordpress/100-common-antipatterns.md).
- Accessibility — [Production Checklist](../accessibility/98-production-checklist.md), [AI Review Checklist](../accessibility/99-ai-review-checklist.md), [Common Antipatterns](../accessibility/100-common-antipatterns.md).

Add [PHP — AI Review Checklist](../php/99-ai-review-checklist.md) for the rendering code and
[Security — Production Checklist](../security/98-production-checklist.md) whenever the module
accepts editor input that reaches the page. When the module was built from a design, close
with [Figma — Implementation Definition of Done](../figma/20-implementation-definition-of-done.md).

---

## Summary

A professional Divi module is more than a custom block of content.

It is a reusable, editor-friendly, maintainable component that integrates seamlessly into the project's architecture, respects the design system, and provides a reliable editing experience in both the Visual Builder and the frontend.

## Related

- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/03-modules.md`
- `knowledge/figma/09-figma-to-divi.md`
