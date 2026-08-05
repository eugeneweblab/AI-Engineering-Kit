---
id: nestjs/98-production-checklist
topic: nestjs
slug: production-checklist
title: "Production Readiness Checklist"
type: checklist
order: 98
status: ready
tags: [nestjs, production-checklist]
related: [nestjs/28-deployment, nestjs/26-security, nestjs/27-performance, nestjs/99-ai-review-checklist]
when_to_use: "Read before shipping a NestJS service to production."
---
# Production Readiness Checklist

## Purpose

This checklist verifies that a NestJS application is ready for production deployment.

The objective is to reduce operational risk by ensuring architecture, security, reliability, observability, and maintainability meet production standards.

A feature is not complete until it is production ready.

---

## Architecture

**Rules:** [Architecture](01-architecture.md) · [Modules](02-modules.md)

☐ Responsibilities are clearly separated.

☐ Modules have well-defined boundaries.

☐ Dependency Injection is used appropriately.

☐ Circular dependencies are eliminated.

☐ Business logic resides outside controllers.

☐ Code follows established engineering principles.

---

## API Design

**Rules:** [Controllers](04-controllers.md) · [Data Transfer Objects (DTO)](07-dto.md)

☐ REST or GraphQL contracts are consistent.

☐ DTOs validate all external input.

☐ API versioning strategy is defined.

☐ Error responses are standardized.

☐ Pagination is implemented where appropriate.

☐ API documentation is up to date.

---

## Authentication & Authorization

**Rules:** [Authentication](15-authentication.md) · [Authorization](16-authorization.md)

☐ Authentication is implemented.

☐ Authorization is enforced.

☐ Least privilege principle is applied.

☐ Sensitive endpoints require authentication.

☐ Tenant isolation is verified (if applicable).

---

## Validation

**Rules:** [Validation](08-validation.md) · [Pipes](12-pipes.md)

☐ Request validation is complete.

☐ Invalid input returns meaningful errors.

☐ Business rules are enforced.

☐ File uploads are validated.

---

## Database

**Rules:** [Database](17-database.md) · [Repositories](06-repositories.md)

☐ Database schema reviewed.

☐ Required indexes exist.

☐ Transactions protect consistency.

☐ N+1 queries eliminated.

☐ Slow queries reviewed.

☐ Migrations are backward compatible.

---

## Caching

**Rules:** [Caching](19-caching.md)

☐ Cache invalidation strategy defined.

☐ Cache expiration configured.

☐ Cache failures handled gracefully.

---

## Background Processing

**Rules:** [Queues](20-queues.md) · [Event-Driven Architecture](21-events.md)

☐ Queue retries configured.

☐ Dead-letter strategy defined.

☐ Idempotency verified.

☐ Failed jobs monitored.

---

## Distributed Systems

**Rules:** [Distributed Systems](23-distributed-systems.md)

☐ Service contracts documented.

☐ Timeouts configured.

☐ Retry policies implemented.

☐ Circuit breakers applied where appropriate.

☐ Correlation IDs propagated.

---

## Security

**Rules:** [Security](26-security.md)

☐ OWASP review completed.

☐ Secrets stored securely.

☐ TLS enforced.

☐ Dependencies scanned.

☐ Security headers configured.

☐ Sensitive data never logged.

☐ Rate limiting configured.

---

## Performance

**Rules:** [Performance Engineering](27-performance.md)

☐ Performance bottlenecks measured.

☐ Database optimized.

☐ Event loop remains responsive.

☐ Memory usage reviewed.

☐ Performance budgets satisfied.

---

## Observability

**Rules:** [Observability](24-observability.md)

☐ Structured logging enabled.

☐ Metrics collected.

☐ Distributed tracing available.

☐ Dashboards updated.

☐ Alerts configured.

☐ Health endpoints implemented.

---

## Testing

**Rules:** [Testing](25-testing.md)

☐ Unit tests pass.

☐ Integration tests pass.

☐ End-to-end tests pass.

☐ Failure scenarios tested.

☐ Edge cases verified.

☐ CI pipeline successful.

---

## Deployment

**Rules:** [Deployment](28-deployment.md)

☐ Deployment fully automated.

☐ Rollback tested.

☐ Infrastructure as Code used.

☐ Immutable artifacts generated.

☐ Feature flags reviewed.

☐ Production configuration validated.

---

## Maintenance

**Rules:** [Maintenance](29-maintenance.md)

☐ Documentation updated.

☐ ADRs created when required.

☐ Runbooks updated.

☐ Technical debt reviewed.

☐ Dependency updates reviewed.

---

## Documentation

☐ README updated.

☐ API documentation updated.

☐ Operational documentation current.

☐ Architecture diagrams reviewed.

---

## AI Final Verification

Before considering implementation complete, verify:

☐ Code is readable.

☐ Architecture remains simple.

☐ Security requirements satisfied.

☐ Performance validated.

☐ Observability implemented.

☐ Tests complete.

☐ Deployment safe.

☐ Documentation current.

☐ No known blockers remain.

---

## Completion Criteria

A feature is considered production ready only when every applicable checklist item has been reviewed and satisfied.

Skipping checklist items requires explicit engineering justification.

---

## Summary

Production readiness is achieved through disciplined engineering rather than successful compilation alone.

This checklist provides a consistent verification process that reduces deployment risk and increases confidence in production releases.

## Related

- `knowledge/nestjs/28-deployment.md`
- `knowledge/nestjs/26-security.md`
- `knowledge/nestjs/27-performance.md`
- `knowledge/nestjs/99-ai-review-checklist.md`
