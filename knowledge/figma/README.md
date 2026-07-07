---
id: figma/readme
topic: figma
slug: readme
title: "Figma-to-Code Standards"
type: index
order: -1
status: ready
tags: [figma]
related: []
when_to_use: "Read first when translating a Figma design into code — analysis, token extraction, implementation targets, and design QA."
---
# Figma-to-Code Standards

## Purpose

This section defines how to translate a Figma design into production code accurately and
consistently — from reading the design and extracting tokens to implementation and
visual verification.

The objective is faithful, maintainable implementations that match the design intent
without guessing.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Reading and analyzing Figma files
- Layout, responsive, and component analysis
- Design token extraction
- Implementation targets (HTML, WordPress, Divi)
- Design QA and visual regression
- Accessibility, animation, and asset handling
- Handoff and definition of done

> **Structure note:** This is a focused section with a custom layout (`01`–`20`), not the
> standard `00`–`30 / 98 / 99 / 100` scheme. Order documents by the `order` field in each
> file's frontmatter.

---

## Learning Path

Study the documents in the following order.

## Analyze the Design

- 01. Figma Analysis
- 02. Layout Analysis
- 03. Design Token Extraction
- 04. Auto Layout
- 05. Responsive Analysis
- 06. Component Detection

## Implement

- 07. Figma to Semantic HTML
- 08. Figma to WordPress
- 09. Figma to Divi

## Review the AI Way

- 10. Design QA
- 11. AI Design Review Protocol
- 12. AI Prompts

## Verify

- 13. Visual Regression
- 14. Figma Inspection Checklist
- 15. Screenshot Comparison
- 16. Accessibility from Figma
- 17. Animation Analysis
- 18. Image Assets
- 19. Design Handoff
- 20. Implementation Definition of Done

---

## Core Principles

- Match the design; do not invent values. Extract tokens, don't eyeball them.
- Reuse existing components and design-system primitives.
- Preserve spacing, typography, and responsive behavior exactly.
- Build accessible markup from the start, not as an afterthought.
- Verify visually against the source before declaring done.

---

## Intended Audience

- Frontend Engineers
- WordPress and Divi Developers
- UI Engineers
- AI Coding Assistants
- Designers reviewing implementation

---

## Summary

Following these standards produces implementations that faithfully match Figma designs
and stay maintainable, with verification built into the process.
