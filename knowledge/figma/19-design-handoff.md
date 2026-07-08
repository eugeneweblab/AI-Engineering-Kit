---
id: figma/19-design-handoff
topic: figma
slug: design-handoff
title: "Design Handoff"
type: doc
order: 19
status: ready
tags: [figma, design-handoff]
related: []
when_to_use: "Read when handing off a Figma design to engineering, to align designers, developers, and QA before implementation."
---
# Design Handoff

## Purpose

This document defines the standard process for handing off a Figma design to engineering.

The objective is to ensure that designers, developers, QA engineers, and AI coding assistants share the same understanding before implementation begins.

A successful handoff minimizes ambiguity, reduces implementation iterations, and improves delivery quality.

---

## Core Principle

A design handoff is a knowledge transfer process.

It is not simply sharing a Figma file.

Every implementation should begin only after the design has been fully understood.

---

## Handoff Workflow

Every handoff should follow this sequence.

```
Project Overview
        ↓
Business Requirements
        ↓
Design Review
        ↓
Technical Review
        ↓
Asset Review
        ↓
Responsive Review
        ↓
Accessibility Review
        ↓
Implementation Planning
        ↓
Approval
```

---

## Step 1 — Project Overview

Document:

- project name;
- feature name;
- implementation scope;
- stakeholders;
- delivery priorities.

Every participant should understand the business objective before discussing implementation details.

---

## Step 2 — Business Requirements

Clarify:

- target audience;
- primary user flow;
- business goals;
- expected outcomes;
- success criteria.

Engineering decisions should support business requirements.

---

## Step 3 — Design Review

Review the complete design.

Verify:

- page hierarchy;
- section order;
- reusable components;
- design system usage;
- typography;
- spacing;
- color system.

Implementation should never begin after reviewing only isolated sections.

---

## Step 4 — Responsive Review

Review every supported breakpoint.

Verify:

- desktop layout;
- laptop layout;
- tablet layout;
- mobile layout.

Discuss expected behavior when a breakpoint is not explicitly defined.

Avoid guessing responsive behavior.

---

## Step 5 — Component Review

Identify:

- reusable components;
- shared layouts;
- repeated UI patterns;
- interactive components;
- complex components.

Determine whether existing project components can be reused.

Reuse is preferred over creating new implementations.

---

## Step 6 — Dynamic Content

Identify all content sources.

Examples:

- WordPress content;
- WooCommerce data;
- REST API;
- GraphQL;
- configuration values;
- user-generated content.

Nothing intended to be editable should be hardcoded.

---

## Step 7 — Asset Review

Verify:

- images;
- illustrations;
- icons;
- logos;
- videos;
- fonts.

Confirm:

- export formats;
- naming conventions;
- optimization strategy.

Missing assets should be identified before implementation.

---

## Step 8 — Accessibility Review

Verify:

- semantic structure;
- heading hierarchy;
- image requirements;
- keyboard navigation;
- form accessibility;
- focus behavior;
- color contrast.

Accessibility requirements should be documented before development.

---

## Step 9 — Technical Review

Determine:

- project architecture;
- reusable components;
- framework-specific requirements;
- CMS integration;
- styling strategy;
- performance considerations.

The implementation approach should be agreed before coding begins.

---

## Step 10 — Implementation Plan

Document:

- implementation order;
- files to modify;
- reusable components;
- expected risks;
- testing strategy;
- review process.

Implementation should follow a documented plan.

---

## AI Handoff Requirements

Before implementation, AI should identify:

- reusable project components;
- design tokens;
- dynamic content;
- responsive behavior;
- accessibility requirements;
- implementation risks.

AI should summarize this information before generating code.

---

## Handoff Deliverables

A complete handoff should include:

- approved Figma design;
- design system references;
- required assets;
- responsive layouts;
- interaction specifications;
- implementation notes;
- acceptance criteria.

---

## AI Execution Checklist

## Investigation

☐ Business requirements understood.

☐ Complete design reviewed.

☐ Components identified.

☐ Dynamic content identified.

☐ Assets reviewed.

☐ Responsive behavior reviewed.

☐ Accessibility reviewed.

---

## Planning

☐ Existing components identified.

☐ Architecture selected.

☐ Implementation plan created.

☐ Risks documented.

---

## Verification

☐ Handoff is complete.

☐ Missing information identified.

☐ Open questions documented.

☐ Implementation can begin confidently.

---

## Common Mistakes

Avoid:

Starting implementation before reviewing the complete design.

Ignoring business requirements.

Ignoring reusable project components.

Guessing responsive behavior.

Implementing missing assets.

Hardcoding editable content.

Skipping accessibility discussions.

Beginning development without an implementation plan.

---

## Completion Criteria

A design handoff is complete when:

- business objectives are understood;
- implementation scope is clearly defined;
- reusable components have been identified;
- assets are available;
- responsive behavior has been reviewed;
- accessibility requirements have been documented;
- implementation risks have been discussed;
- all participants are ready to begin development.

---

## Summary

An effective design handoff creates a shared understanding between design and engineering.

A structured handoff process reduces ambiguity, prevents unnecessary revisions, and enables developers and AI coding assistants to implement designs efficiently and consistently.