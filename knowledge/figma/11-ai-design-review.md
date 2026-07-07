---
id: figma/11-ai-design-review
topic: figma
slug: ai-design-review
title: "AI Design Review Protocol"
type: doc
order: 11
status: ready
tags: [figma, ai-design-review]
related: []
when_to_use: ""
---
# AI Design Review Protocol

## Purpose

This document defines the mandatory reasoning process that every AI coding assistant must follow before implementing a Figma design.

The objective is to ensure that implementation is based on analysis, planning, reuse, and verification rather than immediate code generation.

Implementation without analysis is considered incomplete.

---

## Core Principle

Think before writing code.

The first response to a Figma design should never be code.

The first response should always be analysis.

---

## Primary Rule

When receiving a Figma task:

DO NOT immediately generate HTML, React, PHP, CSS or JavaScript.

Instead, complete the full review process described below.

Only after every phase has been completed may implementation begin.

---

## Mandatory Review Pipeline

Every implementation must follow this exact order.

```
Receive Design

        ↓

Understand Requirements

        ↓

Analyze Entire Page

        ↓

Identify Sections

        ↓

Identify Existing Components

        ↓

Identify Dynamic Content

        ↓

Identify Design Tokens

        ↓

Analyze Auto Layout

        ↓

Analyze Responsive Behavior

        ↓

Choose Architecture

        ↓

Implementation Plan

        ↓

Search Existing Code

        ↓

Implementation

        ↓

Self Review

        ↓

Compare Against Figma

        ↓

Fix Differences

        ↓

Final Verification
```

Skipping any phase is considered an implementation failure.

---

## Phase 1 — Understand Requirements

Determine:

- business objective;
- user goal;
- expected functionality;
- editing requirements;
- supported devices;
- accessibility expectations.

Never implement assumptions.

---

## Phase 2 — Analyze the Entire Design

Review the complete page before inspecting individual components.

Identify:

- page hierarchy;
- visual hierarchy;
- repeated sections;
- interaction patterns;
- navigation;
- layout consistency.

Never begin implementation after reviewing only one section.

---

## Phase 3 — Detect Existing Components

Search the project for:

- React components;
- WordPress templates;
- Gutenberg blocks;
- Divi modules;
- shared utilities;
- CSS components;
- design system elements.

The preferred solution is almost always reuse.

---

## Phase 4 — Detect Dynamic Content

Classify every visible element.

Categories include:

- static content;
- WordPress content;
- API data;
- WooCommerce data;
- user-generated content;
- configuration values.

Never hardcode data that belongs to a CMS or API.

---

## Phase 5 — Detect Design Tokens

Extract:

- typography;
- spacing;
- colors;
- border radius;
- shadows;
- breakpoints;
- icon sizes.

Always search for existing tokens before creating new ones.

---

## Phase 6 — Analyze Layout

Review:

- containers;
- grid;
- Auto Layout;
- nesting;
- alignment;
- constraints.

Reproduce behavior instead of appearance.

---

## Phase 7 — Analyze Responsive Behavior

Review:

Desktop

↓

Laptop

↓

Tablet

↓

Mobile

Document:

- layout changes;
- stacking;
- spacing;
- typography;
- interactions.

Never invent responsive behavior unnecessarily.

---

## Phase 8 — Select Architecture

Choose:

- semantic HTML;
- reusable components;
- state management;
- data flow;
- WordPress architecture;
- React architecture.

Architecture decisions should precede implementation.

---

## Phase 9 — Create an Implementation Plan

Before writing code define:

- reusable components;
- file structure;
- implementation order;
- dependencies;
- risks;
- validation strategy.

Implementation should never be improvised.

---

## Phase 10 — Search Existing Code

Before creating anything new search for:

- similar layouts;
- shared utilities;
- helper functions;
- UI components;
- CSS utilities;
- templates.

Avoid duplicate implementations.

---

## Phase 11 — Implement

Only after all previous phases have been completed.

Implementation priorities:

1. correctness;
2. maintainability;
3. readability;
4. accessibility;
5. performance.

Speed is never the primary objective.

---

## Phase 12 — Self Review

After implementation review:

- HTML;
- CSS;
- JavaScript;
- responsiveness;
- accessibility;
- naming;
- architecture.

Review your own work before presenting it.

---

## Phase 13 — Compare With Figma

Review:

- layout;
- spacing;
- typography;
- colors;
- interactions;
- responsive behavior.

Every visual difference should have a justification.

---

## Phase 14 — Fix Differences

Before completing the task:

Correct:

- layout differences;
- spacing issues;
- responsive issues;
- accessibility issues;
- duplicated code;
- inconsistent naming.

Do not leave known problems unresolved.

---

## Phase 15 — Final Verification

Confirm:

☐ Requirements satisfied.

☐ Existing components reused.

☐ Responsive implementation complete.

☐ Accessibility verified.

☐ Performance acceptable.

☐ Design accurately reproduced.

☐ Code follows project standards.

Only then is the task complete.

---

## Expected AI Output

Before implementation, provide a concise summary covering:

## Design Analysis

- Sections identified
- Reusable components
- Dynamic content
- Responsive observations

## Implementation Plan

- Files to modify
- Components to reuse
- Components to create
- Potential risks

## Completion Report

- Completed work
- Design deviations (if any)
- Performance considerations
- Accessibility considerations

This creates transparency and reduces unnecessary revisions.

---

## AI Self-Questions

Before writing code ask:

- Do I understand the entire page?
- Have I searched for existing components?
- Am I duplicating existing functionality?
- Have I identified all reusable patterns?
- Have I planned responsive behavior?
- Can this solution be simplified?
- Would another engineer understand this implementation?

If any answer is uncertain, continue analysis.

---

## Common Failures

Never:

Generate code immediately.

Copy Figma layer hierarchy.

Hardcode repeated values.

Ignore the design system.

Ignore accessibility.

Ignore responsiveness.

Duplicate existing components.

Implement before planning.

---

## Completion Criteria

The protocol has been successfully followed when:

- all review phases are completed;
- implementation follows the project architecture;
- reusable components are prioritized;
- design differences have been reviewed;
- self-review has been completed;
- the implementation is considered production-ready.

---

## Summary

Professional engineering is defined not by how quickly code is written, but by how systematically problems are analyzed before implementation.

This review protocol transforms AI coding assistants from reactive code generators into disciplined engineering collaborators capable of producing predictable, maintainable, high-quality implementations.