---
id: nestjs/03-dependency-injection
topic: nestjs
slug: dependency-injection
title: "NestJS Dependency Injection"
type: doc
order: 3
status: ready
tags: [nestjs, dependency-injection]
related: []
when_to_use: "Read before wiring providers, tokens, scopes, or custom factories, or when debugging DI resolution errors."
---
# NestJS Dependency Injection

## Purpose

This document defines the engineering standards for using Dependency Injection (DI) in NestJS applications.

The objective is to build loosely coupled, testable, and maintainable applications by relying on NestJS's Inversion of Control (IoC) container instead of manual dependency management.

Dependency Injection should simplify architecture rather than complicate it.

---

## Core Principle

Depend on abstractions.

Not implementations.

Dependencies should be injected, never created manually inside business logic.

---

## Dependency Injection Goals

Every application should strive for:

- loose coupling;
- high cohesion;
- testability;
- explicit dependencies;
- reusable services;
- maintainable architecture.

---

## Dependency Flow

Dependencies should flow in one direction.

```
Controller

↓

Service

↓

Repository

↓

Infrastructure
```

Lower layers must never depend on higher layers.

---

## Constructor Injection

Prefer constructor injection for all dependencies.

Example:

```
Controller

↓

Service

↓

Repository
```

Dependencies should be explicit and immutable after object creation.

Avoid property injection.

---

## Providers

Providers are the primary mechanism for dependency injection.

Typical providers include:

- services;
- repositories;
- factories;
- adapters;
- clients;
- utilities.

Providers should encapsulate a single responsibility.

---

## Provider Registration

Register providers inside the owning module.

Example:

```
@Module({

    providers: [

        UsersService,

        UsersRepository

    ]

})
```

Avoid registering unrelated providers in the same module.

---

## Injection Tokens

Use injection tokens when:

- injecting interfaces;
- supporting multiple implementations;
- building reusable libraries;
- decoupling infrastructure.

Prefer descriptive token names.

---

## Custom Providers

Use custom providers for:

- external SDKs;
- third-party clients;
- adapters;
- runtime configuration.

Keep custom provider configuration centralized.

---

## Factory Providers

Use factory providers when object creation requires:

- configuration;
- asynchronous initialization;
- conditional behavior;
- dependency composition.

Factory logic should remain simple and predictable.

---

## Value Providers

Use value providers for:

- configuration objects;
- constants;
- immutable shared values.

Avoid placing business logic inside value providers.

---

## Existing Providers

Reuse existing providers when multiple tokens should resolve to the same implementation.

Avoid creating duplicate service instances unnecessarily.

---

## Provider Scope

Prefer singleton providers.

Use request-scoped providers only when request-specific state is required.

Use transient providers only when independent instances are necessary.

Choose the simplest scope that satisfies the requirement.

---

## Optional Dependencies

Mark dependencies as optional only when the application can function correctly without them.

Avoid excessive optional dependencies.

---

## Circular Dependencies

Avoid circular dependencies between providers.

If encountered:

- extract shared logic;
- redesign ownership;
- introduce abstractions.

Using circular dependency workarounds should be a last resort.

---

## Service Design

Services should:

- expose clear public methods;
- avoid framework-specific logic;
- remain independently testable;
- encapsulate business rules.

Services should not create other services directly.

---

## Repository Injection

Repositories should be injected rather than instantiated manually.

Persistence concerns should remain isolated from business logic.

---

## Configuration Injection

Inject configuration through dedicated configuration providers.

Avoid reading environment variables directly throughout the application.

---

## External Integrations

Inject external services such as:

- email providers;
- payment gateways;
- storage providers;
- messaging systems.

Infrastructure should remain replaceable.

---

## Testing

Dependency Injection should simplify testing.

Replace dependencies with:

- mocks;
- stubs;
- fakes;
- test providers.

Tests should isolate the component under verification.

---

## Performance

Avoid unnecessary request-scoped providers.

Review:

- provider lifetime;
- initialization cost;
- dependency graph.

Dependency Injection should not introduce avoidable overhead.

---

## Security

Inject security-related services through well-defined providers.

Examples:

- authentication;
- authorization;
- encryption;
- secret management.

Sensitive functionality should remain centralized.

---

## AI Execution Checklist

## Investigation

☐ Identify required dependencies.

☐ Review provider ownership.

☐ Review module boundaries.

☐ Review provider scope.

---

## Planning

☐ Use constructor injection.

☐ Register providers correctly.

☐ Centralize configuration.

☐ Minimize coupling.

---

## Verification

☐ Dependencies explicit.

☐ No manual instantiation.

☐ Providers independently testable.

☐ No circular dependencies.

☐ Appropriate provider scope selected.

☐ Architecture remains maintainable.

---

## Common Mistakes

Avoid:

Creating dependencies with `new`.

Using property injection.

Making every provider request-scoped.

Creating circular dependencies.

Reading configuration directly from environment variables throughout the codebase.

Placing business logic inside provider factories.

Injecting unnecessary dependencies.

---

## Completion Criteria

Dependency Injection is implemented correctly when:

- dependencies are injected through constructors;
- providers remain focused and reusable;
- abstractions separate business logic from infrastructure;
- configuration is centralized;
- testing is simplified through dependency replacement;
- the dependency graph remains easy to understand.

---

## Summary

Dependency Injection is one of the core architectural strengths of NestJS.

By depending on abstractions, using constructor injection consistently, organizing providers within their owning modules, and keeping dependencies explicit, applications become more modular, testable, scalable, and easier to maintain.