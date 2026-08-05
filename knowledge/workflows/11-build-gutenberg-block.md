---
id: workflows/11-build-gutenberg-block
topic: workflows
slug: build-gutenberg-block
title: "Workflow — Build a Gutenberg Block"
type: doc
order: 11
status: ready
tags: [workflows, build-gutenberg-block]
related: [wordpress/16-block-editor, wordpress/17-block-themes, figma/08-figma-to-wordpress]
  - wordpress/01-wordpress-architecture
  - wordpress/03-best-practices
  - wordpress/06-security
  - wordpress/98-production-checklist
  - react/13-component-composition
  - react/05-props
  - accessibility/03-semantic-html
  - accessibility/07-aria
  - php/13-security
  - security/10-output-encoding
  - css/20-css-variables
  - figma/03-design-token-extraction
when_to_use: "Follow this workflow when creating or extending a Gutenberg block."
---
# Workflow — Build a Gutenberg Block

## Purpose

This workflow defines the standard engineering process for creating or extending a Gutenberg block.

The objective is to build blocks that integrate naturally into the WordPress Block Editor, follow project architecture, provide an excellent editing experience, and produce clean, semantic frontend output.

A Gutenberg block is not just a React component.

It is a content authoring experience, a frontend component, and a long-term content format.

---

## Goal

Build a Gutenberg block that:

- integrates seamlessly into the existing project;
- follows WordPress Block Editor conventions;
- provides an intuitive editing experience;
- produces semantic frontend markup;
- is reusable and maintainable;
- supports responsive layouts;
- remains backward compatible whenever possible.

---

## Workflow Overview

```
Understand Requirements
        ↓
Analyze Existing Blocks
        ↓
Inspect Project Architecture
        ↓
Design Block API
        ↓
Implement Edit Experience
        ↓
Implement Save / Render Logic
        ↓
Implement Styling
        ↓
Responsive Verification
        ↓
Accessibility Verification
        ↓
Complete
```

---

## Step 1 — Understand the Requirements

Before implementation determine:

- business objective;
- editor workflow;
- frontend behavior;
- supported layouts;
- dynamic content requirements;
- reusable functionality.

Understand both the editor experience and the visitor experience.

---

## Step 2 — Analyze Existing Blocks

Search the project for:

- existing custom blocks;
- reusable React components;
- shared controls;
- helper utilities;
- block variations;
- block patterns;
- design tokens.

Prefer extending existing solutions over creating new ones.

A block variation, a block style, or a block pattern often satisfies the requirement without
registering a new block type — and none of them create a new content format to maintain.

Relevant knowledge:

- [WordPress — Best Practices](../wordpress/03-best-practices.md) — core block APIs before custom code.
- [Frontend — Design Systems](../frontend/03-design-systems.md) — checking the shared component layer first.
- [Engineering — Engineering Principles](../engineering/00-engineering-principles.md) — reuse over duplication.

---

## Step 3 — Inspect the Project Architecture

Review:

- block registration;
- build system;
- component organization;
- styling approach;
- localization;
- REST API usage;
- server-side rendering (if applicable).

The new block should match the project's existing architecture.

Relevant knowledge:

- [WordPress — WordPress Architecture](../wordpress/01-wordpress-architecture.md) — where block registration happens in the load order.
- [WordPress — Project Structure](../wordpress/02-project-structure.md) — theme versus plugin ownership of a block.
- [PHP — Namespaces](../php/05-namespaces.md) and [PHP — Autoloading](../php/06-autoloading.md) — organizing the server side of the block.

---

## Step 4 — Design the Block API

Define:

Attributes

Inspector Controls

Toolbar Controls

InnerBlocks

Allowed Blocks

Templates

Block Supports

Responsive options

Every attribute should exist for a reason.

Avoid unnecessary editor settings.

Attributes are a content format, not just component props: every saved post carries them, so
removing or retyping an attribute later invalidates existing content and forces a deprecation
entry. Prefer block supports (spacing, color, typography) over hand-rolled attributes —
supports come with editor UI, theme integration, and forward compatibility for free.

Relevant knowledge:

- [React — Props](../react/05-props.md) — the same discipline applies to the attribute contract.
- [React — Component Composition](../react/13-component-composition.md) — `InnerBlocks` is composition; prefer it to an attribute for every nested value.
- [TypeScript — Interfaces](../typescript/06-interfaces.md) — typing the attribute shape when the project uses TypeScript.

---

## Step 5 — Implement the Editor Experience

The editor should provide:

- immediate visual feedback;
- intuitive controls;
- logical grouping of settings;
- sensible defaults;
- validation where appropriate;
- responsive editing.

The editor experience is part of the product.

Relevant knowledge:

- [React — Component Composition](../react/13-component-composition.md) and [React — Patterns](../react/14-patterns.md) — structuring `edit` from small reusable controls.
- [React — State](../react/06-state.md) — attributes are the source of truth; avoid a parallel copy in local state.
- [React — Performance](../react/12-performance.md) — a heavy `edit` render makes the whole editor feel slow.

---

## Step 6 — Implement Rendering

Determine whether the block should use:

Static rendering

or

Dynamic rendering

For dynamic blocks:

- keep rendering logic on the server;
- sanitize output;
- escape output;
- minimize database queries.

Rendering should remain predictable.

Choose deliberately: a **static** block serializes markup into post content and must ship a
deprecation entry whenever that markup changes, while a **dynamic** block renders through a
PHP callback on every request — content stays current, but the cost lands on page load.
Anything that depends on live data (queries, user state, current date) has to be dynamic.

Relevant knowledge:

- [Security — Output Encoding](../security/10-output-encoding.md) and [WordPress — Security](../wordpress/06-security.md) — escape in the render callback; attributes are user-authored content.
- [PHP — Security](../php/13-security.md) — the language-level rules behind the escaping helpers.
- [WordPress — Performance](../wordpress/05-performance.md) and [Performance — Caching](../performance/08-caching.md) — cache the expensive part of a dynamic render.
- [Databases — Query Optimization](../databases/08-query-optimization.md) — a `WP_Query` inside a render callback runs on every page view.

---

## Step 7 — Implement Styling

Follow the project's styling strategy.

Maintain consistency with:

- spacing;
- typography;
- colors;
- border radius;
- responsive breakpoints;
- design tokens.

Avoid introducing isolated styling systems.

Relevant knowledge:

- [CSS — CSS Variables](../css/20-css-variables.md) — consume `theme.json` values as custom properties instead of hardcoding.
- [CSS — Architecture](../css/21-architecture.md) and [Frontend — Styling](../frontend/15-styling.md) — where block styles live and how they are enqueued for editor and frontend.
- [Figma — Design Token Extraction](../figma/03-design-token-extraction.md) — the token source those values come from.

---

## Step 8 — Accessibility Review

Verify:

- semantic HTML;
- keyboard accessibility;
- heading hierarchy;
- ARIA attributes where needed;
- image alt text;
- color contrast;
- focus visibility.

Accessibility should be verified in both the editor and the frontend.

Relevant knowledge:

- [Accessibility — Semantic HTML](../accessibility/03-semantic-html.md) and [HTML — Semantic HTML](../html/02-semantic-html.md) — semantic output from `save`/`render_callback`.
- [Accessibility — ARIA](../accessibility/07-aria.md) — only where native semantics fall short.
- [Accessibility — Keyboard Navigation](../accessibility/04-keyboard-navigation.md) and [Accessibility — Focus Management](../accessibility/05-focus-management.md) — for interactive blocks.
- [Accessibility — Images](../accessibility/09-images.md) — alt text belongs in an attribute the editor can fill in.
- [Accessibility — Axe](../accessibility/21-axe.md) — automate the checkable portion.

---

## Step 9 — Responsive Review

Review:

Desktop

Tablet

Mobile

Verify:

- layout;
- spacing;
- typography;
- wrapping;
- overflow;
- touch targets.

Responsive behavior should be intentional rather than accidental.

Relevant knowledge:

- [CSS — Responsive Design](../css/17-responsive-design.md) and [CSS — Container Queries](../css/19-container-queries.md) — a block can land in a narrow column, so size it by its container.
- [Accessibility — Responsive Accessibility](../accessibility/13-responsive-accessibility.md) — touch targets and reflow.
- [Figma — Responsive Analysis](../figma/05-responsive-analysis.md) — the intended behavior at each breakpoint.

---

## Step 10 — Compatibility Review

Verify compatibility with:

- latest supported WordPress version;
- Gutenberg editor;
- Full Site Editing (if applicable);
- multilingual plugins;
- caching plugins;
- project build system;
- existing custom blocks.

The block should integrate without disrupting the editor ecosystem.

Content already published with an earlier version of a static block must keep rendering:
changing `save` output without a deprecation entry produces block-validation errors on every
existing post.

Relevant knowledge:

- [WordPress — Testing](../wordpress/07-testing.md) — verify against posts saved with the previous version.
- [PHP — Production](../php/27-production.md) — supported PHP and WordPress versions.
- [Workflow — Build a WordPress Feature](09-build-wordpress-feature.md) — the wider integration checklist this block sits inside.

---

## AI Execution Checklist

## Investigation

☐ Understand the requirements.

☐ Analyze existing blocks.

☐ Review project architecture.

☐ Search reusable components.

☐ Review design system.

---

## Planning

☐ Design block attributes.

☐ Design editor controls.

☐ Plan rendering strategy.

☐ Plan responsive behavior.

---

## Implementation

☐ Reuse existing components.

☐ Keep editor logic separated from rendering.

☐ Preserve project conventions.

☐ Avoid duplicate functionality.

☐ Follow WordPress Block APIs.

---

## Verification

☐ Verify editor experience.

☐ Verify frontend rendering.

☐ Verify responsive layouts.

☐ Verify accessibility.

☐ Verify localization.

☐ Verify compatibility.

☐ Update documentation.

---

## Gutenberg Engineering Principles

Prefer:

Reusable controls

Composable React components

Server-side rendering when appropriate

Semantic HTML

Shared design tokens

Small focused blocks

Consistent editor experience

Avoid:

Large monolithic blocks

Duplicate editor controls

Business logic inside React views

Hardcoded design values

Inconsistent inspector panels

Mixing editor state with business logic

---

## Common Mistakes

Avoid:

Creating blocks without reviewing existing ones.

Duplicating existing functionality.

Ignoring block supports.

Ignoring responsive editing.

Ignoring accessibility.

Using inconsistent naming.

Mixing rendering logic with editor logic.

Ignoring localization.

---

## Completion Criteria

The workflow is complete only if:

- requirements are satisfied;
- the editor experience is intuitive;
- frontend rendering is correct;
- accessibility has been verified;
- responsive behavior has been verified;
- project conventions have been respected;
- compatibility has been confirmed.

---

## Expected AI Output

After completing this workflow, the AI should explain:

- the block's purpose;
- its attributes;
- editor controls that were implemented;
- rendering strategy;
- reused components and utilities;
- accessibility considerations;
- responsive strategy;
- compatibility verification.

---

## Self-Verification — Topic Checklists

Before marking the block complete, run it through the checklists of the topics it touched:

- WordPress — [Production Checklist](../wordpress/98-production-checklist.md), [AI Review Checklist](../wordpress/99-ai-review-checklist.md), [Common Antipatterns](../wordpress/100-common-antipatterns.md).
- Accessibility — [Production Checklist](../accessibility/98-production-checklist.md), [AI Review Checklist](../accessibility/99-ai-review-checklist.md), [Common Antipatterns](../accessibility/100-common-antipatterns.md).
- React — [AI Review Checklist](../react/99-ai-review-checklist.md), [Common Antipatterns](../react/100-common-antipatterns.md) — for the `edit` implementation.

For a dynamic block, add [PHP — AI Review Checklist](../php/99-ai-review-checklist.md) and
[Security — Production Checklist](../security/98-production-checklist.md). Public-facing
blocks should also pass [SEO — Production Checklist](../seo/98-production-checklist.md), and
blocks built from a design close with
[Figma — Implementation Definition of Done](../figma/20-implementation-definition-of-done.md).

---

## Summary

A professional Gutenberg block is a complete editing experience rather than simply a UI component.

It should integrate naturally into the Block Editor, respect WordPress architecture, produce semantic frontend output, and remain maintainable throughout the lifetime of the project.

## Related

- `knowledge/wordpress/16-block-editor.md`
- `knowledge/wordpress/17-block-themes.md`
- `knowledge/figma/08-figma-to-wordpress.md`
