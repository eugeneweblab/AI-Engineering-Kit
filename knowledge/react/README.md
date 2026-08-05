---
id: react/readme
topic: react
slug: readme
title: "React Engineering Standards"
type: index
order: -1
status: ready
tags: [react, readme]
related: []
when_to_use: "Read first when starting any React work, to see how this section's docs fit together."
---
# React Engineering Standards

## Purpose

This section defines the engineering standards, mental models, and best practices for
building user interfaces with React. React composes UIs out of declarative components, and
its mental model is small but unforgiving: the same code can be correct JavaScript and
still be wrong React — a state mutation that never re-renders, an effect that fires twice, a
key that reuses the wrong DOM node. Those bugs pass review because they look reasonable and
only surface as flicker, stale data, or lost input under real use.

The objective is React that renders correctly, updates predictably, and performs well.
Getting the core model right — components, props, state, rendering, effects — prevents an
entire class of defects that are hard to reproduce and expensive to debug in production.
From philosophy and JSX through hooks, data fetching, routing, accessibility, and
production concerns, these docs point to the sibling document that owns each concern so you
read the right rules before writing or reviewing code.

These standards are written for both human engineers and AI coding assistants, so that
either can build, review, and ship React to the same bar.

---

## Scope

This documentation covers:

- React philosophy, component architecture, and JSX
- Components, props, state, and lifecycle
- Hooks, custom hooks, context, rendering, and performance
- Composition, patterns, and design patterns
- Forms, data fetching, routing, and state management
- Error handling and accessibility
- Testing, folder structure, code style, and security
- Best practices, debugging, production, and tooling
- Engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations
- [00. Overview](00-overview.md)
- [01. React Philosophy](01-react-philosophy.md)
- [02. Component Architecture](02-component-architecture.md)
- [03. JSX](03-jsx.md)

### Building Blocks
- [04. Components](04-components.md)
- [05. Props](05-props.md)
- [06. State](06-state.md)
- [07. Lifecycle](07-lifecycle.md)

### Behavior
- [08. Hooks](08-hooks.md)
- [09. Custom Hooks](09-custom-hooks.md)
- [10. Context API](10-context-api.md)
- [11. Rendering](11-rendering.md)
- [12. Performance](12-performance.md)

### Composition & Patterns
- [13. Component Composition](13-component-composition.md)
- [14. Patterns](14-patterns.md)
- [24. Design Patterns](24-design-patterns.md)

### Application Concerns
- [15. Forms](15-forms.md)
- [16. Data Fetching](16-data-fetching.md)
- [17. Routing](17-routing.md)
- [18. State Management](18-state-management.md)
- [19. Error Handling](19-error-handling.md)
- [20. Accessibility](20-accessibility.md)

### Engineering
- [21. Testing](21-testing.md)
- [22. Folder Structure](22-folder-structure.md)
- [23. Code Style](23-code-style.md)
- [25. Security](25-security.md)
- [26. Best Practices](26-best-practices.md)
- [27. Debugging](27-debugging.md)
- [28. Production](28-production.md)
- [29. Tooling](29-tooling.md)
- [30. Engineering Principles](30-engineering-principles.md)

### Verification
- [98. Production Checklist](98-production-checklist.md)
- [99. AI Review Checklist](99-ai-review-checklist.md)
- [100. Common Anti-Patterns](100-common-antipatterns.md)

---

## Engineering Principles

Every React change should satisfy the following principles:

- Treat the UI as a pure function of props and state; never mutate the DOM directly.
- Flow data down through props and requests up through callbacks — one-way and traceable.
- Keep rendering pure: same props and state produce the same output with no side effects.
- Put side effects in event handlers or effects, not in render.
- Store the minimal source of truth and derive the rest during render.
- Prefer function components and hooks; do not write new class components.
- Keep components small and single-purpose, and extract when concerns diverge.
- Set stable, identity-based keys on lists; never use array index as a key for dynamic lists.
- Measure with the profiler before reaching for memoization.
- Consult the topic-specific doc for the concern touched before improvising.

---

## Intended Audience

These standards are intended for:

- Frontend Engineers
- Fullstack Engineers
- UI/UX Engineers
- Tech Leads
- Software Architects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps React UIs a pure function of state — correct, predictable,
and performant — and avoids the rendering and effect bugs that hide until production.
