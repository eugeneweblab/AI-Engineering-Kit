---
id: prisma/readme
topic: prisma
slug: readme
title: "Prisma Engineering Standards"
type: index
order: -1
status: ready
tags: [prisma, readme, schema.prisma, migrate, prisma, PrismaClient]
related: []
when_to_use: "Read first when starting any Prisma work, to see how this section's docs fit together."
---
# Prisma Engineering Standards

## Purpose

This section defines the engineering standards and best practices for using Prisma, the
type-safe ORM for Node.js and TypeScript. Prisma has three moving parts an agent must keep
straight: the schema (`schema.prisma`, the single source of truth), Migrate (which turns
schema changes into versioned SQL), and Client (the generated, type-safe query API). The
guarantees only hold when you respect the workflow.

The objective is to prevent the whole class of failures that come from breaking that
workflow — editing the schema without regenerating the Client, or pushing schema changes to
production without a migration — which produce code that compiles locally but corrupts data
or drifts from the live database. From installation and schema modeling through querying at
scale, transactions, performance, and multi-tenancy, these docs keep the schema, the
migrations, and the database in agreement.

These standards are written for both human engineers and AI coding assistants, so that
either can model data, migrate, and query with Prisma to the same bar.

---

## Scope

This documentation covers:

- Installation, schema, and models
- Relations and migrations
- The generated Client and CRUD operations
- Transactions, filtering, pagination, and relation loading
- Seeding, middleware, and Client extensions
- Performance, indexes, and raw SQL
- Error handling, testing, and debugging
- Security, multi-tenancy, and soft delete
- Patterns, architecture, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations
- [00. Overview](00-overview.md)
- [01. Installation](01-installation.md)
- [02. Schema](02-schema.md)
- [03. Models](03-models.md)
- [04. Relations](04-relations.md)

### The Change Loop
- [05. Migrations](05-migrations.md)
- [06. Client](06-client.md)
- [07. CRUD](07-crud.md)
- [12. Seeding](12-seeding.md)

### Querying at Scale
- [08. Transactions](08-transactions.md)
- [09. Filtering](09-filtering.md)
- [10. Pagination](10-pagination.md)
- [11. Relations Loading](11-relations-loading.md)

### Extending Prisma
- [13. Middleware](13-middleware.md)
- [14. Extensions](14-extensions.md)
- [17. Raw SQL](17-raw-sql.md)

### Performance & Hardening
- [15. Performance](15-performance.md)
- [16. Indexes](16-indexes.md)
- [21. Security](21-security.md)
- [22. Multi-Tenancy](22-multi-tenancy.md)
- [23. Soft Delete](23-soft-delete.md)

### Operations
- [18. Error Handling](18-error-handling.md)
- [19. Testing](19-testing.md)
- [20. Debugging](20-debugging.md)
- [25. Production](25-production.md)
- [26. Observability](26-observability.md)

### Discipline
- [24. Best Practices](24-best-practices.md)
- [27. Tooling](27-tooling.md)
- [28. Patterns](28-patterns.md)
- [29. Architecture](29-architecture.md)
- [30. Engineering Principles](30-engineering-principles.md)

### Verification
- [98. Production Checklist](98-production-checklist.md)
- [99. AI Review Checklist](99-ai-review-checklist.md)
- [100. Common Anti-Patterns](100-common-antipatterns.md)

---

## Engineering Principles

Every Prisma change should satisfy the following principles:

- Treat `schema.prisma` as the single source of truth; never hand-edit the generated Client or the database out of band.
- Follow the loop every time: schema change → migration → `prisma generate`.
- Commit the migration alongside the schema edit that caused it, and keep both in version control.
- Never treat `prisma db push` as a substitute for `migrate` in shared or production databases.
- Instantiate exactly one `PrismaClient` per process; it owns a connection pool.
- Pin `prisma` and `@prisma/client` to the same version to avoid confusing runtime errors.
- Lean on the type-safe Client; do not cast away its types with `as any`.
- Push filtering, pagination, and selection into the query rather than into application memory.
- Handle Prisma's typed errors explicitly instead of swallowing them.
- Route each task to the specific sibling doc rather than guessing at the API.

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

Following these standards keeps the Prisma schema, migrations, and generated Client in
agreement, so type safety holds and the database never silently drifts.
