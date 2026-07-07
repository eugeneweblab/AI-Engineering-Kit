---
id: nestjs/readme
topic: nestjs
slug: readme
title: "NestJS Engineering Standards"
type: index
order: -1
status: ready
tags: [nestjs]
related: []
when_to_use: "Read first when building, reviewing, or scaling a NestJS backend."
---
# NestJS Engineering Standards

## Purpose

This section defines the engineering standards, architectural principles, and best
practices for building backend applications with NestJS.

The objective is a consistent approach to scalable, testable, secure, and maintainable
services — from module boundaries and dependency injection to data access, messaging,
and production operations.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Application architecture and module design
- Dependency injection
- Controllers, services, and repositories
- DTOs and validation
- Guards, interceptors, exception filters, and pipes
- Middleware and configuration
- Authentication and authorization
- Database access and transactions
- Caching, queues, and events
- CQRS and distributed systems
- Observability
- Testing, security, and performance
- Deployment and maintenance
- Engineering principles

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. Overview
- 01. Architecture
- 02. Modules
- 03. Dependency Injection

## Request Lifecycle

- 04. Controllers
- 05. Services
- 06. Repositories
- 07. DTO
- 08. Validation
- 09. Guards
- 10. Interceptors
- 11. Exception Filters
- 12. Pipes
- 13. Middleware
- 14. Configuration

## Security & Data

- 15. Authentication
- 16. Authorization
- 17. Database
- 18. Transactions

## Scaling & Integration

- 19. Caching
- 20. Queues
- 21. Events
- 22. CQRS
- 23. Distributed Systems

## Production

- 24. Observability
- 25. Testing
- 26. Security
- 27. Performance
- 28. Deployment
- 29. Maintenance
- 30. Engineering Principles

## Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every NestJS feature should satisfy the following principles:

- Keep modules cohesive and boundaries explicit.
- Depend on abstractions; inject dependencies, do not construct them.
- Keep controllers thin; put business logic in services.
- Validate all input at the boundary with DTOs and pipes.
- Isolate data access behind repositories.
- Make failure modes explicit with filters and typed exceptions.
- Design for observability from the start.
- Write tests alongside the code, not after.
- Secure by default; never trust client input.
- Measure performance before optimizing.

---

## Intended Audience

These standards are intended for:

- Backend Engineers
- Fullstack Engineers
- Tech Leads
- Software Architects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps NestJS services consistent, testable, secure, and
maintainable as they grow from a single module into a distributed system.
