---
id: mysql/readme
topic: mysql
slug: readme
title: "MySQL Engineering Standards"
type: index
order: -1
status: ready
tags: [mysql, readme, EXPLAIN, see, fit, docs]
related: []
when_to_use: "Read first when starting any mysql work, to see how this section's docs fit together."
---
# MySQL Engineering Standards

## Purpose

This section defines the engineering standards and operational practices for designing,
querying, and running MySQL databases. Most database problems — slow queries, lock
contention, data anomalies, painful migrations — originate in a handful of decisions:
data types, indexing, transaction and isolation choices, and the storage engine. Getting
these right early is what keeps a database fast and correct as data grows.

The objective is a consistent approach to production MySQL: sound schema and data-type
design, effective indexing and query optimization, correct transactional behavior and
lock awareness, and safe evolution through migrations. It extends to operating the
database reliably — replication, clustering, high availability, backups, security,
monitoring, and partitioning — along with the advanced features (JSON, full-text search,
events, triggers, stored procedures) that MySQL provides.

These standards apply to both human developers and AI coding assistants, so that
generated schemas, queries, and migrations respect the same indexing, transaction, and
safety rules as hand-authored ones.

---

## Scope

This documentation covers:

- Installation, configuration, and data types
- Indexes and query optimization
- Transactions, locking, and storage engines
- Replication, clustering, and high availability
- Backups, security, users, and roles
- Performance, monitoring, and migrations
- Testing and debugging
- Partitioning, full-text search, and JSON
- Events, triggers, and stored procedures
- Architecture, tooling, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations

- 00. Overview
- 01. Installation
- 02. Configuration
- 03. Data Types

### Query & Correctness

- 04. Indexes
- 05. Query Optimization
- 06. Transactions
- 07. Locking
- 08. Storage Engines

### Scale & Availability

- 09. Replication
- 10. Clustering
- 21. High Availability
- 22. Partitioning

### Operations & Safety

- 11. Backups
- 12. Security
- 13. Users and Roles
- 14. Performance
- 15. Monitoring
- 16. Migrations
- 17. Testing
- 18. Debugging

### Advanced Features

- 23. Full-Text Search
- 24. JSON
- 25. Events
- 26. Triggers
- 27. Procedures

### Practice & Architecture

- 19. Best Practices
- 20. Production
- 28. Architecture
- 29. Tooling
- 30. Engineering Principles

### Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every MySQL change should satisfy the following principles:

- Choose the smallest correct data type; precise schemas prevent whole classes of bugs.
- Index for the queries you actually run; verify with `EXPLAIN`, not intuition.
- Keep transactions short and understand the isolation level you rely on.
- Be lock-aware; know what your writes block and for how long.
- Prefer InnoDB and design for its row-level locking and foreign-key semantics.
- Treat schema migrations as reversible, online, and tested against production-like data.
- Never store secrets or PII unprotected; enforce least-privilege user grants.
- Back up regularly and rehearse restores and point-in-time recovery.
- Monitor slow queries, replication lag, and connection saturation continuously.
- Push set-based work into SQL; avoid row-by-row logic in the application.

---

## Intended Audience

These standards are intended for:

- Backend Engineers
- Database Administrators
- Data Engineers
- Site Reliability Engineers
- Software Architects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps MySQL fast, correct, and recoverable — so the database
scales with the application instead of becoming its bottleneck.
