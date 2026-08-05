---
id: backend/readme
topic: backend
slug: readme
title: "Backend Engineering Standards"
type: index
order: -1
status: ready
tags: [backend, readme]
related: []
when_to_use: "Read first when starting any backend work, to see how this section's docs fit together."
---
# Backend Engineering Standards

## Purpose

This section defines the engineering standards for designing, building, and reviewing
server-side systems: how to structure code, model a domain, expose an API, persist data,
handle failure, and run in production. Backend code holds the data and enforces the rules,
so a wrong decision does not annoy one user — it corrupts shared state, leaks other people's
data, or takes the whole service down.

The docs move from architectural foundations, through the concrete concerns of API design,
validation, and error handling, into data, scaling, and production operations. An
architecture choice made in week one shapes every feature for years, so getting the
structure right up front is cheaper than any later refactor.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Backend architecture: layered, clean, hexagonal, DDD
- API design and business logic
- Domain modeling and validation
- Authentication and authorization
- Error handling, caching, events, and message brokers
- Background jobs and transactions
- Database design
- Performance, scalability, and security
- Observability, testing, and documentation
- Code organization, deployment, and production readiness

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. Overview
- 01. Backend Architecture
- 02. Layered Architecture
- 03. Clean Architecture
- 04. Hexagonal Architecture
- 05. DDD
- 30. Engineering Principles

## API & Domain

- 06. API Design
- 07. Business Logic
- 08. Domain Modeling
- 09. Validation

## Security & Reliability

- 10. Authentication
- 11. Authorization
- 12. Error Handling

## Data & Integration

- 13. Caching
- 14. Events
- 15. Message Brokers
- 16. Background Jobs
- 17. Transactions
- 18. Database Design

## Production

- 19. Performance
- 20. Scalability
- 21. Security
- 22. Observability
- 23. Testing
- 24. Documentation
- 25. Code Organization
- 26. Deployment
- 27. Production
- 28. Best Practices
- 29. Architecture Review

## Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every backend feature should satisfy the following principles:

- Separate policy from mechanism; keep business rules apart from HTTP, SQL, and queues.
- Depend on abstractions at every boundary, not on a specific database or framework.
- Make the domain the center; storage and transport are details that serve it.
- Design for failure — networks drop, disks fill, dependencies time out.
- Optimize for change first and speed second; most cost is in maintenance.
- Pick the simplest architecture that fits the problem, not the most sophisticated.
- Keep the domain free of framework, HTTP, and database imports.
- Make the same decision the same way everywhere for predictability.
- Wrap multi-step writes in transactions and reason about partial failure.

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

Following these standards keeps backend services correct, secure, and maintainable, so the
system that holds the data and enforces the rules stays trustworthy as it grows.
