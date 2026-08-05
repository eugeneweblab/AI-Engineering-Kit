---
id: html/readme
topic: html
slug: readme
title: "HTML Engineering Standards"
type: index
order: -1
status: ready
tags: [html, readme]
related: []
when_to_use: "Read first when starting any html work, to see how this section's docs fit together."
---
# HTML Engineering Standards

## Purpose

This section defines the engineering standards and authoring practices for writing HTML
as the semantic foundation of the web. HTML is often treated as trivial, but it is the
layer that determines accessibility, SEO, performance, and how robustly a page degrades —
decisions made in the markup are difficult to fix later in CSS or JavaScript.

The objective is a consistent approach to correct, meaningful, and resilient markup:
proper document structure, semantic elements over generic containers, accessible forms
and media, and structured data that machines can consume. It covers the full surface from
text, links, images, tables, and forms to metadata, SEO, structured data, iframes, SVG,
canvas, web components, and the browser APIs that HTML exposes.

These standards apply to both human developers and AI coding assistants, so that
generated markup is as semantic, accessible, and standards-compliant as hand-authored HTML.

---

## Scope

This documentation covers:

- Document structure and semantic HTML
- Text elements, links, images, lists, and tables
- Forms and media
- Metadata, SEO, structured data, and microdata
- Accessibility and progressive enhancement
- Custom data attributes, iframes, SVG, and canvas
- Performance, security, and browser rendering
- Web components and HTML APIs
- HTML email and common patterns
- Validation, debugging, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations

- 00. Overview
- 01. Document Structure
- 02. Semantic HTML
- 03. Text Elements

### Content Elements

- 04. Links
- 05. Images
- 06. Lists
- 07. Tables
- 08. Forms
- 09. Media
- 10. Metadata

### Discoverability & Access

- 11. Accessibility
- 12. SEO
- 13. Structured Data
- 14. Custom Data Attributes
- 26. Microdata

### Rich & Embedded Content

- 15. Iframes
- 16. SVG
- 17. Canvas
- 25. Web Components
- 27. HTML APIs

### Quality & Hardening

- 18. Performance
- 19. Security
- 20. Browser Rendering
- 21. Best Practices
- 22. Validation
- 23. Progressive Enhancement
- 24. HTML Email
- 28. Common Patterns
- 29. Debugging
- 30. Engineering Principles

### Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every HTML document should satisfy the following principles:

- Choose the element that carries the correct meaning before reaching for a `div` or `span`.
- Structure the document with landmarks and a logical heading hierarchy.
- Make it accessible by default; semantics and ARIA serve assistive technology.
- Label every form control and associate errors with their inputs.
- Provide text alternatives for all non-text content.
- Build with progressive enhancement so core content works without JavaScript.
- Keep metadata and structured data accurate for search and social platforms.
- Treat untrusted content as hostile; escape and sandbox appropriately.
- Optimize the critical rendering path — defer, lazy-load, and size media responsibly.
- Validate markup and test against real assistive technology, not just linters.

---

## Intended Audience

These standards are intended for:

- Frontend Engineers
- Fullstack Engineers
- Accessibility Specialists
- Web Designers
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards makes HTML semantic, accessible, and durable — a foundation that
serves users, search engines, and assistive technology equally well.
