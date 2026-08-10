---
id: sql/readme
topic: sql
slug: readme
title: "SQL Engineering Standards"
type: index
order: -1
status: ready
tags: [sql, readme, HAVING, LIMIT, see, fit, docs]
related: []
when_to_use: "Read first when starting any SQL work, to see how this section's docs fit together."
---
# SQL Engineering Standards

## Purpose

This section defines the engineering standards and best practices for writing and reviewing
SQL. SQL is declarative: you describe the result you want and the engine decides how to
produce it. That gap between what you write and what runs is where correctness and
performance bugs hide — a duplicated row from a bad join, a dropped row from a `NULL`
comparison, an average over the wrong set.

The objective is queries that are both correct and fast. A single query can return silently
wrong results with no error raised, and unlike a crash, a wrong query looks like it worked;
its blast radius is every downstream report, API response, and business decision. SQL is
also the layer where a full table scan turns a 10 ms request into a 10 s one. From `SELECT`
and filtering through joins, window functions, indexes, and optimization, these docs close
the gap by teaching the rules the engine actually enforces.

These standards are written for both human engineers and AI coding assistants, so that
either can write and review SQL to the same bar.

---

## Scope

This documentation covers:

- SELECT, filtering, sorting, grouping, and joins
- Subqueries, CTEs, window functions, and aggregate/scalar functions
- Data types, DDL, DML, and transactions
- Indexes, query planning, and query optimization
- Views, materialized views, stored procedures, and triggers
- Security, performance, testing, and debugging
- Best practices, portability, architecture, tooling, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Core Query
- [00. Overview](00-overview.md)
- [01. Select](01-select.md)
- [02. Filtering](02-filtering.md)
- [03. Sorting](03-sorting.md)
- [04. Grouping](04-grouping.md)
- [05. Joins](05-joins.md)

### Composing Queries
- [06. Subqueries](06-subqueries.md)
- [07. Common Table Expressions](07-common-table-expressions.md)
- [08. Window Functions](08-window-functions.md)
- [09. Aggregate Functions](09-aggregate-functions.md)
- [10. Functions](10-functions.md)

### Data & Schema
- [11. Data Types](11-data-types.md)
- [12. DDL](12-ddl.md)
- [13. DML](13-dml.md)
- [14. Transactions](14-transactions.md)

### Performance
- [15. Indexes](15-indexes.md)
- [16. Query Planning](16-query-planning.md)
- [17. Query Optimization](17-query-optimization.md)
- [23. Performance](23-performance.md)

### Database Objects
- [18. Views](18-views.md)
- [19. Materialized Views](19-materialized-views.md)
- [20. Stored Procedures](20-stored-procedures.md)
- [21. Triggers](21-triggers.md)

### Quality & Discipline
- [22. Security](22-security.md)
- [24. Testing](24-testing.md)
- [25. Debugging](25-debugging.md)
- [26. Best Practices](26-best-practices.md)
- [27. Portability](27-portability.md)
- [28. Architecture](28-architecture.md)
- [29. Tooling](29-tooling.md)
- [30. Engineering Principles](30-engineering-principles.md)

### Verification
- [98. Production Checklist](98-production-checklist.md)
- [99. AI Review Checklist](99-ai-review-checklist.md)
- [100. Common Anti-Patterns](100-common-antipatterns.md)

---

## Engineering Principles

Every SQL change should satisfy the following principles:

- Know the logical evaluation order (`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`).
- Treat `NULL` as "unknown"; handle it explicitly wherever a column can be null.
- Never rely on result order without an explicit `ORDER BY`.
- Write clear, sargable predicates and let the optimizer and indexes do their job.
- Prefer explicit `JOIN ... ON` over comma joins, and name columns instead of `SELECT *`.
- Verify with `EXPLAIN (ANALYZE)`, not intuition, on any query touching a large table.
- Test queries against `NULL`s, duplicates, and empty result sets — the cases that expose most bugs.
- Target one SQL dialect deliberately; call out portability differences.
- Guard writes with transactions where multiple statements must be atomic.
- Scope each change to the right sub-topic and apply that doc's rules.

---

## Intended Audience

These standards are intended for:

- Backend Engineers
- Data Engineers and Analysts
- Database Engineers and DBAs
- Tech Leads
- Software Architects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps SQL queries verifiably correct and fast, closing the gap
between the declarative query you write and the execution the engine actually runs.
