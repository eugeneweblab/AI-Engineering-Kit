# Figma Inspection Checklist

## Purpose

This document defines the mandatory inspection checklist that must be completed before implementing any Figma design.

The objective is to fully understand the design before writing code, reducing implementation mistakes, unnecessary refactoring, and repeated design revisions.

This checklist should be completed for every new page, section, or significant redesign.

---

# Core Principle

Inspect first.

Implement second.

Every minute spent analyzing the design saves significantly more time during implementation and review.

---

# Inspection Workflow

Complete every phase before beginning development.

```
Project Overview
        ↓
Layout
        ↓
Components
        ↓
Typography
        ↓
Design Tokens
        ↓
Responsive Design
        ↓
Interactions
        ↓
Dynamic Content
        ↓
Assets
        ↓
Implementation Plan
```

---

# Phase 1 — Project Overview

Verify:

☐ Business purpose is understood.

☐ Primary user journey is clear.

☐ Scope of implementation is defined.

☐ Required pages are identified.

☐ Required sections are identified.

---

# Phase 2 — Layout

Verify:

☐ Overall page structure.

☐ Container widths.

☐ Grid system.

☐ Auto Layout usage.

☐ Alignment.

☐ Spacing.

☐ Nested layouts.

☐ Section hierarchy.

---

# Phase 3 — Components

Verify:

☐ Buttons.

☐ Cards.

☐ Forms.

☐ Navigation.

☐ Tables.

☐ Tabs.

☐ Accordions.

☐ Modals.

☐ Sliders.

☐ Badges.

☐ Icons.

☐ Existing reusable patterns.

---

# Phase 4 — Typography

Verify:

☐ Font families.

☐ Heading hierarchy.

☐ Font sizes.

☐ Font weights.

☐ Line heights.

☐ Letter spacing.

☐ Text alignment.

---

# Phase 5 — Design Tokens

Verify:

☐ Colors.

☐ Typography tokens.

☐ Spacing scale.

☐ Border radius.

☐ Shadows.

☐ Icon sizes.

☐ Breakpoints.

☐ Existing project tokens.

---

# Phase 6 — Responsive Design

Verify:

☐ Desktop layout.

☐ Laptop layout.

☐ Tablet layout.

☐ Mobile layout.

☐ Grid changes.

☐ Navigation changes.

☐ Component changes.

☐ Typography scaling.

☐ Section spacing.

---

# Phase 7 — Interactions

Verify:

☐ Hover states.

☐ Focus states.

☐ Active states.

☐ Disabled states.

☐ Loading states.

☐ Error states.

☐ Success states.

☐ Animations.

☐ Transitions.

---

# Phase 8 — Dynamic Content

Identify:

☐ CMS content.

☐ API content.

☐ User-generated content.

☐ WooCommerce data.

☐ Images.

☐ Videos.

☐ Icons.

☐ Links.

☐ Forms.

Nothing that should be dynamic may be hardcoded.

---

# Phase 9 — Assets

Verify:

☐ Images.

☐ SVG icons.

☐ Illustrations.

☐ Videos.

☐ Logos.

☐ Fonts.

☐ Export requirements.

☐ Image quality.

☐ Responsive assets.

---

# Phase 10 — Existing Project Review

Before implementation search for:

☐ Existing components.

☐ Existing layouts.

☐ Existing utilities.

☐ Existing styles.

☐ Existing templates.

☐ Existing helper functions.

☐ Existing design tokens.

Reuse existing implementations whenever possible.

---

# Phase 11 — Architecture

Determine:

☐ Component hierarchy.

☐ Folder structure.

☐ Data flow.

☐ Styling strategy.

☐ State management.

☐ Responsive strategy.

☐ Accessibility strategy.

---

# Phase 12 — Implementation Plan

Before coding define:

☐ Files to modify.

☐ Components to create.

☐ Components to reuse.

☐ Potential risks.

☐ Testing strategy.

☐ Validation strategy.

No implementation should begin without a clear plan.

---

# Final Readiness Checklist

Before implementation confirm:

☐ The complete design has been reviewed.

☐ All reusable components have been identified.

☐ Existing project components have been reviewed.

☐ Responsive behavior is understood.

☐ Dynamic content has been identified.

☐ Design tokens have been extracted.

☐ Accessibility requirements are understood.

☐ Implementation plan is complete.

---

# Common Mistakes

Avoid:

Inspecting only the visible section.

Ignoring responsive layouts.

Ignoring existing project components.

Ignoring Auto Layout.

Ignoring interaction states.

Ignoring accessibility.

Starting implementation before planning.

---

# Completion Criteria

Figma inspection is complete only when:

- the entire design has been reviewed;
- reusable patterns have been identified;
- responsive behavior is understood;
- implementation risks are documented;
- a complete implementation plan has been prepared.

---

# Summary

Thorough inspection is the foundation of successful implementation.

A disciplined inspection process minimizes rework, improves consistency, and enables AI coding assistants to generate more accurate, maintainable, and production-ready solutions.