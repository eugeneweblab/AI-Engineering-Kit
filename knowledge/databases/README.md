---
id: databases/readme
topic: databases
slug: readme
title: "Databases Engineering Standards"
type: index
order: -1
status: ready
tags: [databases, readme]
related: []
when_to_use: "Read first when starting any databases work, to see how this section's docs fit together."
---
# Databases Engineering Standards

## Purpose

This section defines the engineering standards for the layer where correctness lives or dies.
Application code can crash and restart; corrupted or lost data is forever. Every doc here
exists to keep one property true: the data on disk is always a faithful, consistent record
of what actually happened.

Most production incidents that make the news are database incidents — a bad migration that
dropped a column, a missing index that melted the CPU, a partial write that left two tables
disagreeing, a backup that had never actually restored. The docs move from fundamentals and
data modeling, through runtime correctness and performance, into scaling, operations, and
the cross-cutting concerns that keep shared, long-lived data trustworthy.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Database fundamentals and choosing relational vs NoSQL
- Data modeling, normalization, denormalization, and schema design
- Indexing and query optimization
- Transactions, concurrency, locking, ACID, and eventual consistency
- Replication, sharding, and partitioning
- Migrations, backup and recovery, and high availability
- Security, monitoring, and performance
- Data integrity, soft delete, multi-tenancy, and auditing

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. Overview
- 01. Database Fundamentals
- 02. Relational vs NoSQL
- 30. Engineering Principles

## Design the Data

- 03. Data Modeling
- 04. Normalization
- 05. Denormalization
- 06. Schema Design

## Correct & Fast at Runtime

- 07. Indexing
- 08. Query Optimization
- 09. Transactions
- 10. Concurrency
- 11. Locking
- 12. ACID
- 13. Eventual Consistency

## Scale & Operate

- 14. Replication
- 15. Sharding
- 16. Partitioning
- 17. Migrations
- 18. Backup and Recovery
- 19. Security
- 20. Performance
- 21. Monitoring
- 22. High Availability

## Cross-Cutting Concerns

- 23. Data Integrity
- 24. Soft Delete
- 25. Multi-Tenancy
- 26. Auditing
- 27. Testing
- 28. Best Practices
- 29. Architecture

## Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every database change should satisfy the following principles:

- Treat the schema as a contract enforced by the engine, not just by application code.
- Push invariants — uniqueness, foreign keys, NOT NULL, CHECK — into the database.
- Model for the queries you will run, not for an abstract "clean" diagram.
- Pick the data store from the actual access pattern, not by default or hype.
- Treat every write as a transaction and reason about partial and concurrent failure.
- Make every schema change a reversible, tested migration.
- Make reads fast with indexes without breaking write performance.
- Design for backup and recovery, and verify restores actually work.
- Keep data changes auditable and reversible where the domain demands it.

---

## Intended Audience

These standards are intended for:

- Backend and Data Engineers
- Database Administrators
- Software Architects
- SRE and Platform Engineers
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps the data on disk a faithful, consistent record of what
happened, so the most expensive and least reversible failures are prevented before they ship.
