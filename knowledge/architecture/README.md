---
id: architecture/readme
topic: architecture
slug: readme
title: "Architecture Engineering Standards"
type: index
order: -1
status: ready
tags: [architecture]
related: []
when_to_use: "Read first when starting any architecture work, to see how this section's docs fit together."
---
# Architecture Engineering Standards

## Purpose

This section defines the engineering standards for the decisions that are expensive to
change later: module boundaries, data ownership, synchronous versus asynchronous
communication, and deployment shape. Architecture is not diagrams for their own sake — it
is the set of load-bearing choices that every feature is later built on top of, and that
compound in cost when they are wrong.

The objective is to help you frame a problem, pick a structure that matches the actual
constraints rather than fashion, and record why you chose it. The docs move from framing a
problem, through structural and topological patterns, to the quality attributes a design
must satisfy and the governance that keeps decisions traceable.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Software architecture and system design fundamentals
- Structural patterns: clean, hexagonal, layered, DDD, CQRS
- System topology: event-driven, microservices, modular monolith, integration
- Quality attributes: scalability, performance, security, availability, fault tolerance
- Observability and caching strategies
- Distributed systems and message brokers
- Cloud architecture, infrastructure, and deployment
- Documentation, ADRs, and architecture review
- Engineering principles and real-world patterns

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. Overview
- 01. Software Architecture
- 02. System Design
- 30. Engineering Principles

## Structural Patterns

- 03. Clean Architecture
- 04. Hexagonal Architecture
- 05. Layered Architecture
- 06. Domain-Driven Design
- 07. CQRS

## System Topology

- 08. Event-Driven Architecture
- 09. Microservices
- 10. Modular Monolith
- 11. API-First
- 12. Integration Patterns
- 20. Message Brokers
- 21. Distributed Systems

## Quality Attributes

- 13. Scalability
- 14. Performance
- 15. Security
- 16. High Availability
- 17. Fault Tolerance
- 18. Observability
- 19. Caching Strategies

## Operate & Deliver

- 22. Cloud Architecture
- 23. Infrastructure
- 24. Deployment

## Practice & Governance

- 25. Documentation
- 26. Architecture Decision Records
- 27. Architecture Review
- 28. Best Practices
- 29. Real-World Patterns

## Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every architectural decision should satisfy the following principles:

- Match structure to real constraints, not to fashion or to another company's scale.
- Treat boundaries as the product; get the lines and data ownership right first.
- Point dependencies inward, from volatile components toward stable business rules.
- Default to a modular monolith; adopt microservices only when a real need proves it.
- Add structure when a constraint demands it, not speculatively.
- Design for current constraints plus one realistic step of growth.
- Record consequential choices as ADRs so they can be revisited with context.
- Treat every abstraction as having a cost; justify what you trade away.
- Revisit architecture as a set of decisions, not a one-time upfront phase.
- Route to the most specific doc for the decision in front of you.

---

## Intended Audience

These standards are intended for:

- Software Architects
- Backend and Fullstack Engineers
- Tech Leads and Staff Engineers
- Platform and Infrastructure Engineers
- AI Coding Assistants
- Code and Design Reviewers

---

## Summary

Following these standards keeps architectural decisions explicit, justified, and traceable,
so a system stays coherent as it grows from a single service into a distributed one.
