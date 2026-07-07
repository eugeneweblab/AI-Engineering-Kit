---
id: workflows/11-build-gutenberg-block
topic: workflows
slug: build-gutenberg-block
title: "Workflow — Build a Gutenberg Block"
type: doc
order: 11
status: ready
tags: [workflows, build-gutenberg-block]
related: []
when_to_use: ""
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

## Summary

A professional Gutenberg block is a complete editing experience rather than simply a UI component.

It should integrate naturally into the Block Editor, respect WordPress architecture, produce semantic frontend output, and remain maintainable throughout the lifetime of the project.