---
id: javascript/readme
topic: javascript
slug: readme
title: "JavaScript Engineering Standards"
type: index
order: -1
status: ready
tags: [javascript]
related: []
when_to_use: "Read first when starting any javascript work, to see how this section's docs fit together."
---
# JavaScript Engineering Standards

## Purpose

This section defines the engineering standards and mental models for writing JavaScript
that is correct, maintainable, and fast. Much of JavaScript's reputation for surprising
behavior disappears once its core mechanics are internalized: execution context, scope
and closures, the prototype chain, `this` binding, and the single-threaded event loop.

The objective is a consistent approach across the language and its runtimes: from the
foundations of functions, objects, classes, and modules to asynchronous programming with
promises and the event loop, and on to the browser surface — the DOM, Fetch, and browser
APIs. It also covers the meta-programming tools (iterators, generators, symbols, proxies),
paradigm choices (functional programming, design patterns, clean code), and the
production concerns of testing, performance, security, and tooling.

These standards apply to both human developers and AI coding assistants, so that
generated code respects the same async correctness, memory discipline, and clean-code
rules as hand-written JavaScript.

---

## Scope

This documentation covers:

- Language fundamentals, execution context, scope, and closures
- Functions, objects, prototypes, and classes
- Modules and the `this` keyword
- Asynchronous JavaScript, promises, and the event loop
- Browser APIs, the DOM, and the Fetch API
- Error handling and memory management
- ES6+ features, iterators, generators, symbols, proxies, and Reflect
- Functional programming, design patterns, and clean code
- Testing, performance, security, and tooling
- Engineering principles

---

## Learning Path

Study the documents in the following order.

### Language Core

- 00. Overview
- 01. Language Fundamentals
- 02. Execution Context
- 03. Scope and Closures
- 04. Functions
- 05. Objects and Prototypes
- 06. Classes
- 07. Modules
- 16. The `this` Keyword

### Asynchrony

- 08. Asynchronous JavaScript
- 09. Promises
- 10. Event Loop

### Browser Runtime

- 11. Browser API
- 12. DOM
- 13. Fetch API

### Robustness & Memory

- 14. Error Handling
- 15. Memory Management

### Advanced Language

- 17. ES6 Features
- 18. Iterators and Generators
- 19. Symbols
- 20. Proxies and Reflect

### Craft & Quality

- 21. Functional Programming
- 22. Design Patterns
- 23. Clean Code
- 24. Testing
- 25. Performance
- 26. Security
- 27. Browser Performance
- 28. Best Practices
- 29. Tooling
- 30. Engineering Principles

### Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every piece of JavaScript should satisfy the following principles:

- Understand `this`, scope, and closures before relying on them.
- Prefer immutability and pure functions; isolate and name side effects.
- Model asynchrony with promises and `async`/`await`; never leave rejections unhandled.
- Respect the single-threaded event loop; keep the main thread responsive.
- Handle errors explicitly and fail loudly rather than silently swallowing them.
- Guard against memory leaks — clean up listeners, timers, and references.
- Favor modules and small, composable units over large stateful objects.
- Validate and sanitize all external input; never trust the client or the network.
- Measure before optimizing; profile real bottlenecks, don't guess.
- Write tests alongside the code and keep them fast and deterministic.

---

## Intended Audience

These standards are intended for:

- Frontend Engineers
- Backend (Node.js) Engineers
- Fullstack Engineers
- Tech Leads
- Software Architects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards makes JavaScript predictable, memory-safe, and performant — so
the language's flexibility becomes an asset rather than a source of subtle bugs.
