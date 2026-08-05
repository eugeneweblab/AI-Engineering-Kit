---
id: typescript/readme
topic: typescript
slug: readme
title: "TypeScript Engineering Standards"
type: index
order: -1
status: ready
tags: [typescript, readme, strict, unknown, readonly]
related: []
when_to_use: "Read first when starting any TypeScript work, to see how this section's docs fit together."
---
# TypeScript Engineering Standards

## Purpose

This section defines the engineering standards and best practices for writing TypeScript.
TypeScript is JavaScript with a static type system checked at compile time and erased at
runtime. The runtime is still JavaScript; the value TypeScript adds is a compiler that
catches type errors — `undefined is not a function`, `cannot read property of null`, silent
`NaN` propagation — before code ships, moving those failures from production to the editor.

The objective is to keep the type layer honest, so the green checkmark actually means
something. The compiler only helps if the types match runtime reality: a codebase full of
`any`, `as` casts, and `@ts-ignore` has the syntax of TypeScript with the safety of
JavaScript — worse, because it lies. From the type system and inference through generics,
utility types, narrowing, modules, configuration, and library design, these docs assume
`strict: true` as the floor and teach an agent to use the compiler rather than silence it.

These standards are written for both human engineers and AI coding assistants, so that
either can write and review TypeScript to the same bar.

---

## Scope

This documentation covers:

- Language fundamentals, the type system, and inference
- Functions, objects, interfaces, and type aliases
- Generics, utility types, enums and literals, unions and intersections, and type guards
- Advanced types, modules, decorators, and configuration
- Error handling, asynchronous programming, collections, and immutability
- Functional programming, design patterns, and clean code
- Testing, performance, security, and library design
- Best practices, tooling, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations
- [00. Overview](00-overview.md)
- [01. Language Fundamentals](01-language-fundamentals.md)
- [02. Type System](02-type-system.md)
- [03. Type Inference](03-type-inference.md)

### Building Blocks
- [04. Functions](04-functions.md)
- [05. Objects](05-objects.md)
- [06. Interfaces](06-interfaces.md)
- [07. Type Aliases](07-type-aliases.md)

### Composition
- [08. Generics](08-generics.md)
- [09. Utility Types](09-utility-types.md)
- [10. Enums and Literals](10-enums-and-literals.md)
- [11. Unions and Intersections](11-unions-and-intersections.md)
- [12. Type Guards](12-type-guards.md)
- [13. Advanced Types](13-advanced-types.md)

### Systems
- [14. Modules](14-modules.md)
- [15. Decorators](15-decorators.md)
- [16. Configuration](16-configuration.md)
- [17. Error Handling](17-error-handling.md)
- [18. Asynchronous Programming](18-asynchronous-programming.md)
- [19. Collections](19-collections.md)

### Craft
- [20. Immutability](20-immutability.md)
- [21. Functional Programming](21-functional-programming.md)
- [22. Design Patterns](22-design-patterns.md)
- [23. Clean Code](23-clean-code.md)
- [24. Testing](24-testing.md)
- [25. Performance](25-performance.md)
- [26. Security](26-security.md)
- [27. Library Design](27-library-design.md)
- [28. Best Practices](28-best-practices.md)
- [29. Tooling](29-tooling.md)
- [30. Engineering Principles](30-engineering-principles.md)

### Verification
- [98. Production Checklist](98-production-checklist.md)
- [99. AI Review Checklist](99-ai-review-checklist.md)
- [100. Common Anti-Patterns](100-common-antipatterns.md)

---

## Engineering Principles

Every TypeScript change should satisfy the following principles:

- Types describe reality, not wishes; a cast that isn't true is a bug the compiler can no longer catch.
- Prefer inference for locals; annotate public boundaries — signatures, exports, module edges.
- Treat `strict` mode as the floor, not a goal; every new warning is a defect.
- Make illegal states unrepresentable with unions, literals, and narrow types.
- Keep `any` out of the codebase; use `unknown` at untyped edges and narrow it.
- Reach for narrow types first and widen only when a concrete use forces it.
- Never silence errors with `@ts-ignore`; fix the underlying type.
- Model fallible operations as explicit result types rather than thrown surprises.
- Prefer `readonly` and immutable data where mutation is not required.
- Consult the topic-specific doc for the concern touched before improvising.

---

## Intended Audience

These standards are intended for:

- Frontend Engineers
- Backend Engineers
- Fullstack Engineers
- Library and SDK Authors
- Tech Leads
- Software Architects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps the TypeScript type layer honest under `strict` mode, so a
clean compile is a real guarantee rather than a comforting lie.
