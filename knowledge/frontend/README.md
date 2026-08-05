---
id: frontend/readme
topic: frontend
slug: readme
title: "Frontend Engineering Standards"
type: index
order: -1
status: ready
tags: [frontend, readme]
related: []
when_to_use: "Read first when starting any frontend work, to see how this section's docs fit together."
---
# Frontend Engineering Standards

## Purpose

This section defines the engineering standards for building the frontend — the part of the
system a human actually touches. It runs on a device you do not control, over a network you
cannot trust, and must stay correct, fast, and accessible while doing so. These docs teach
how to build that layer deliberately rather than by accretion.

Frontend defects are the ones users see directly, and because the frontend ships to every
browser and device, mistakes scale to the entire audience at once. It also carries real
security weight: it renders untrusted data, holds session state, and is the first target for
XSS and injection. The docs move from architecture and component design, through state,
routing, and data, into performance, accessibility, and production concerns.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Frontend architecture and component-driven development
- Design systems and state management
- Routing, data fetching, and rendering strategy
- Performance, accessibility, and responsive design
- SEO, forms, and error handling
- Security and rendering untrusted data safely
- Styling, CSS architecture, animations, and assets
- Build tools, bundling, code splitting, and testing
- Monitoring, folder structure, UI patterns, and production readiness

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. Overview
- 01. Frontend Architecture
- 02. Component-Driven Development
- 03. Design Systems
- 30. Engineering Principles

## State, Routing & Data

- 04. State Management
- 05. Routing
- 06. Data Fetching
- 07. Rendering

## Quality Requirements

- 08. Performance
- 09. Accessibility
- 10. Responsive Design
- 11. SEO
- 12. Forms
- 13. Error Handling
- 14. Security

## Styling & Assets

- 15. Styling
- 16. CSS Architecture
- 17. Animations
- 18. Assets

## Build & Ship

- 19. Build Tools
- 20. Bundling
- 21. Code Splitting
- 22. Testing
- 23. Monitoring
- 24. Documentation
- 25. Folder Structure
- 26. Production
- 27. Best Practices
- 28. UI Patterns
- 29. Design Review

## Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every frontend feature should satisfy the following principles:

- Decide structure before styling; component boundaries and data flow come first.
- Give every piece of state exactly one owner, as close as possible to where it is used.
- Treat the server as the source of truth; the client mirrors, it does not become authority.
- Treat accessibility and performance as requirements built in from the start, not polish.
- Render all untrusted, user-supplied data safely; escape before rendering.
- Keep the four kinds of state distinct: server, URL, local UI, and form state.
- Choose the least powerful tool that solves the problem.
- Ship a working skeleton — routes, layout, data flow — before adding visual detail.

---

## Intended Audience

These standards are intended for:

- Frontend Engineers
- Fullstack Engineers
- UI and Design-System Engineers
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps the frontend correct, fast, accessible, and secure, so the
layer users touch directly is built deliberately instead of by accretion.
