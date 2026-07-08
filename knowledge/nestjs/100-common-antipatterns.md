---
id: nestjs/100-common-antipatterns
topic: nestjs
slug: common-antipatterns
title: "Common Engineering Antipatterns"
type: doc
order: 100
status: ready
tags: [nestjs, common-antipatterns]
related: []
when_to_use: "Read when reviewing NestJS code to catch common antipatterns and design smells before they become technical debt."
---
# Common Engineering Antipatterns

## Purpose

This document defines common engineering antipatterns that reduce software quality, maintainability, reliability, and scalability.

The objective is to help engineers and AI recognize poor design decisions before they become long-term technical debt.

Avoiding antipatterns is as important as applying best practices.

---

## Core Principle

Every shortcut introduces future maintenance cost.

Engineering decisions should optimize long-term sustainability rather than short-term convenience.

---

## God Object

A single class or service becomes responsible for too many unrelated concerns.

Symptoms:

- excessive dependencies;
- thousands of lines of code;
- unrelated responsibilities.

Solution:

Split responsibilities into focused components.

---

## Fat Controller

Controllers contain business logic.

Symptoms:

- complex validation;
- database access;
- business rules;
- external API calls.

Solution:

Move business logic into services or domain components.

---

## Anemic Domain Model

Business objects contain only data.

All business logic is placed elsewhere.

Solution:

Business behavior should remain close to the business data it operates on.

---

## Spaghetti Code

Control flow becomes difficult to understand.

Symptoms:

- deeply nested conditions;
- duplicated logic;
- unpredictable dependencies.

Solution:

Refactor into smaller, well-defined units.

---

## Circular Dependencies

Components depend on each other directly or indirectly.

Consequences:

- fragile architecture;
- difficult testing;
- poor maintainability.

Solution:

Introduce abstractions or redesign module boundaries.

---

## Tight Coupling

Components know too much about each other.

Solution:

Depend on abstractions rather than implementations.

---

## Primitive Obsession

Primitive types replace meaningful domain concepts.

Example:

Using raw strings for currencies, emails, or identifiers.

Solution:

Create explicit value objects where appropriate.

---

## Magic Numbers

Hardcoded numeric values appear without explanation.

Solution:

Replace with named constants.

---

## Magic Strings

Business logic depends on hardcoded strings.

Solution:

Use enums, constants, or strongly typed objects.

---

## Copy-Paste Programming

Logic is duplicated across multiple locations.

Consequences:

- inconsistent behavior;
- expensive maintenance.

Solution:

Extract shared behavior carefully.

---

## Shotgun Surgery

A single change requires modifications in many files.

Solution:

Improve cohesion and responsibility boundaries.

---

## Over-Engineering

The solution is significantly more complex than the problem requires.

Examples:

- unnecessary abstractions;
- excessive patterns;
- speculative architecture.

Solution:

Apply KISS and YAGNI.

---

## Premature Optimization

Optimizing before identifying a real bottleneck.

Solution:

Measure first.

Optimize second.

---

## Leaky Abstraction

Implementation details escape through public interfaces.

Solution:

Hide internal implementation.

Expose only stable contracts.

---

## Hidden Side Effects

Functions unexpectedly modify state.

Solution:

Make side effects explicit.

Prefer predictable behavior.

---

## Shared Mutable State

Multiple components modify the same data.

Consequences:

- race conditions;
- unpredictable bugs.

Solution:

Reduce shared mutable state.

Prefer immutability when practical.

---

## Long Transactions

Transactions remain open longer than necessary.

Consequences:

- locking;
- reduced throughput;
- deadlocks.

Solution:

Keep transactions short.

---

## N+1 Queries

Applications repeatedly execute similar database queries.

Solution:

Use joins, eager loading, batching, or query optimization.

---

## Chatty APIs

Clients perform excessive network requests.

Solution:

Design APIs around business use cases.

Reduce unnecessary round trips.

---

## Shared Database

Multiple services directly share the same database.

Consequences:

- tight coupling;
- deployment limitations;
- ownership confusion.

Solution:

Each service owns its data.

---

## Synchronous Distributed Chains

One service waits on many downstream services.

Consequences:

- cascading failures;
- increased latency.

Solution:

Prefer asynchronous communication where appropriate.

---

## Missing Timeouts

Remote calls wait indefinitely.

Solution:

Every external request should define a timeout.

---

## Missing Retry Strategy

Transient failures immediately fail.

Solution:

Retry transient failures using exponential backoff.

Avoid infinite retries.

---

## Exception Swallowing

Errors are ignored without logging or handling.

Solution:

Handle, log, or propagate exceptions appropriately.

---

## Silent Failures

Operations fail without notifying users or operators.

Solution:

Implement meaningful error reporting and monitoring.

---

## Hardcoded Configuration

Environment-specific values appear in source code.

Solution:

Externalize configuration.

---

## Logging Sensitive Data

Logs contain:

- passwords;
- tokens;
- secrets;
- personal information.

Solution:

Log only operationally necessary information.

---

## Ignoring Observability

Applications lack logs, metrics, or traces.

Consequences:

- difficult debugging;
- slow incident response.

Solution:

Implement comprehensive observability.

---

## Ignoring Tests

Code changes are made without adequate automated testing.

Solution:

Maintain balanced test coverage focused on behavior.

---

## AI Decision Matrix

Immediately review when detecting:

✓ Large classes

✓ Deep nesting

✓ Duplicate logic

✓ Circular dependencies

✓ Missing validation

✓ Hardcoded values

✓ Long transactions

✓ Poor observability

Avoid introducing:

✗ Hidden complexity

✗ Fragile architecture

✗ Premature optimization

✗ Tight coupling

✗ Operational blind spots

---

## AI Execution Checklist

## Investigation

☐ Identify architectural smells.

☐ Review dependency graph.

☐ Review database access.

☐ Review configuration.

---

## Planning

☐ Simplify design.

☐ Reduce coupling.

☐ Improve cohesion.

☐ Remove duplication.

---

## Verification

☐ Responsibilities remain focused.

☐ Business logic correctly located.

☐ Dependencies simplified.

☐ Configuration externalized.

☐ Observability preserved.

☐ Tests continue to pass.

---

## Completion Criteria

An implementation avoids common engineering antipatterns when:

- responsibilities are well defined;
- architecture remains maintainable;
- dependencies are intentional;
- operational concerns are addressed;
- complexity matches business requirements;
- future changes can be implemented with confidence.

---

## Summary

Engineering antipatterns are recurring design mistakes that increase complexity, reduce maintainability, and create long-term operational risk.

Recognizing these patterns early allows engineers and AI to build systems that remain understandable, scalable, and reliable throughout their lifecycle.