# Workflow — Build a Divi Module

## Purpose

This workflow defines the standard engineering process for creating or modifying a custom Divi module.

Unlike generic WordPress development, Divi development requires maintaining compatibility with the Divi Builder ecosystem, preserving editor stability, and ensuring that modules behave consistently in both the Visual Builder and the frontend.

The objective is to create production-ready Divi modules that are maintainable, reusable, performant, and compatible with future Divi updates.

---

# Goal

Deliver a Divi module that:

- integrates naturally into the existing project;
- follows Divi architecture;
- uses existing project components when possible;
- works identically in the Visual Builder and frontend;
- supports responsive editing;
- is performant;
- is maintainable.

---

# Workflow Overview

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

# Step 1 — Understand the Requirements

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

# Step 2 — Analyze Existing Modules

Search the repository for existing:

- Divi modules;
- shared React components;
- PHP rendering functions;
- helper utilities;
- design tokens;
- responsive helpers.

Never create a module before understanding existing implementation patterns.

---

# Step 3 — Understand the Design

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

---

# Step 4 — Design the Module API

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

---

# Step 5 — Reuse Existing Code

Search before creating:

- React components;
- helper functions;
- PHP utilities;
- CSS utilities;
- Tailwind utilities (if applicable);
- icons;
- animations.

Duplicate code should never become the default solution.

---

# Step 6 — Implement the Module

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

---

# Step 7 — Implement Builder Experience

Verify:

- field grouping;
- labels;
- descriptions;
- sensible defaults;
- conditional fields;
- responsive controls;
- live preview behavior.

The editor experience should be intuitive.

---

# Step 8 — Verify Frontend Rendering

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

---

# Step 9 — Performance Review

Review:

- unnecessary renders;
- duplicate API calls;
- duplicate CSS;
- unnecessary JavaScript;
- image optimization;
- lazy loading;
- asset loading.

Performance matters inside both the builder and the frontend.

---

# Step 10 — Compatibility Review

Verify:

- Visual Builder;
- frontend rendering;
- responsive editing;
- multilingual plugins;
- caching plugins;
- latest supported Divi version;
- latest supported WordPress version.

Compatibility should be confirmed before completion.

---

# AI Execution Checklist

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

# Divi Engineering Principles

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

# Common Mistakes

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

# Completion Criteria

The workflow is complete only if:

- requirements are satisfied;
- the module works correctly in the Visual Builder;
- the frontend matches the expected design;
- responsive behavior has been verified;
- existing project architecture has been respected;
- reusable code has been used where appropriate;
- documentation has been updated if necessary.

---

# Expected AI Output

After completing this workflow, the AI should explain:

- the module's purpose;
- the builder settings that were added;
- reused components and utilities;
- responsive strategy;
- accessibility considerations;
- compatibility verification;
- files that were modified.

---

# Summary

A professional Divi module is more than a custom block of content.

It is a reusable, editor-friendly, maintainable component that integrates seamlessly into the project's architecture, respects the design system, and provides a reliable editing experience in both the Visual Builder and the frontend.