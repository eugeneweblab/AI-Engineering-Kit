---
id: nextjs/98-production-checklist
topic: nextjs
slug: production-checklist
title: "Next.js Production Checklist"
type: checklist
order: 98
status: ready
tags: [nextjs, production-checklist]
related: [nextjs/26-deployment, nextjs/24-security, nextjs/20-performance, nextjs/99-ai-review-checklist]
when_to_use: "Read before shipping a Next.js app to production."
---
# Next.js Production Checklist

## Purpose

This document provides the final verification checklist before deploying a Next.js application to production.

The objective is to ensure the application is secure, performant, maintainable, accessible, and operationally ready.

Every production release should pass this checklist.

---

## Core Principle

A successful deployment is not defined by a successful build.

It is defined by a healthy, secure, observable, and maintainable production system.

---

## Architecture

**Rules:** [Architecture](01-architecture.md) · [Project Structure](02-project-structure.md)

Verify:

☐ Server Components are used whenever possible.

☐ Client Components are limited to interactive UI.

☐ Feature boundaries are respected.

☐ Business logic is separated from presentation.

☐ Shared components remain reusable.

☐ State ownership is clear.

---

## Rendering

**Rules:** [Rendering Strategies](08-rendering-strategies.md) · [Server Components](06-server-components.md)

Verify:

☐ Appropriate rendering strategy selected.

☐ Static pages generated where appropriate.

☐ Dynamic rendering used only when required.

☐ Streaming implemented where beneficial.

☐ Suspense boundaries reviewed.

---

## Data Fetching

**Rules:** [Data Fetching](09-data-fetching.md)

Verify:

☐ Data fetched on the server whenever possible.

☐ Parallel requests implemented where appropriate.

☐ Request waterfalls eliminated.

☐ Error handling implemented.

☐ Loading states reviewed.

---

## Server Actions

**Rules:** [Server Actions](11-server-actions.md)

Verify:

☐ Input validation implemented.

☐ Authorization verified.

☐ Authentication verified.

☐ Cache invalidation configured.

☐ Errors handled safely.

---

## API Routes

**Rules:** [API Routes](12-api-routes.md)

Verify:

☐ Requests validated.

☐ Authentication enforced.

☐ Authorization enforced.

☐ HTTP status codes correct.

☐ Response format consistent.

---

## Caching

**Rules:** [Caching](10-caching.md)

Verify:

☐ Cache strategy documented.

☐ Revalidation configured.

☐ Browser caching reviewed.

☐ CDN caching reviewed.

☐ Personalized content not publicly cached.

---

## Performance

**Rules:** [Performance](20-performance.md) · [Images](16-images.md)

Verify:

☐ Core Web Vitals reviewed.

☐ Bundle size analyzed.

☐ Images optimized.

☐ Fonts optimized.

☐ JavaScript minimized.

☐ Third-party scripts reviewed.

☐ Lazy loading implemented.

☐ Dynamic imports reviewed.

---

## Accessibility

**Rules:** [Accessibility](25-accessibility.md)

Verify:

☐ Semantic HTML used.

☐ Keyboard navigation works.

☐ Alternative text provided.

☐ Color contrast reviewed.

☐ Focus management verified.

☐ Screen reader compatibility reviewed.

---

## SEO

**Rules:** [SEO](19-seo.md) · [Metadata](18-metadata.md)

Verify:

☐ Metadata complete.

☐ Canonical URLs configured.

☐ Open Graph configured.

☐ Structured data reviewed.

☐ Sitemap available.

☐ Robots directives correct.

---

## Security

**Rules:** [Security](24-security.md)

Verify:

☐ HTTPS enabled.

☐ Secrets protected.

☐ Environment variables validated.

☐ Security headers configured.

☐ Authentication reviewed.

☐ Authorization verified.

☐ Input validation implemented.

☐ Sensitive data protected.

---

## Environment

**Rules:** [Environment Variables](21-environment-variables.md)

Verify:

☐ Environment variables documented.

☐ Production configuration validated.

☐ Secrets loaded correctly.

☐ Debug mode disabled.

☐ Feature flags reviewed.

---

## Database

**Rules:** [Database Migrations](../databases/17-migrations.md) · [Prisma Client](../prisma/06-client.md)

Verify:

☐ Migrations reviewed.

☐ Rollback available.

☐ Indexes verified.

☐ Slow queries reviewed.

☐ Backup strategy confirmed.

---

## Logging

**Rules:** [Observability](23-observability.md)

Verify:

☐ Structured logging implemented.

☐ Error logging enabled.

☐ Sensitive data excluded.

☐ Request identifiers available.

---

## Monitoring

**Rules:** [Observability](23-observability.md)

Verify:

☐ Metrics collected.

☐ Health checks operational.

☐ Alerts configured.

☐ Dashboards available.

☐ Error reporting active.

---

## Testing

**Rules:** [Testing](22-testing.md)

Verify:

☐ Unit tests passing.

☐ Integration tests passing.

☐ End-to-end tests passing.

☐ Accessibility tests completed.

☐ Critical user journeys verified.

---

## Deployment

**Rules:** [Deployment](26-deployment.md)

Verify:

☐ Production build successful.

☐ CI pipeline passed.

☐ Deployment automated.

☐ Rollback procedure available.

☐ Deployment verified after release.

---

## Documentation

Verify:

☐ Public APIs documented.

☐ Environment variables documented.

☐ Deployment process documented.

☐ Architecture documented.

☐ Operational procedures documented.

---

## AI Execution Checklist

## Before Deployment

**Rules:** [Deployment](26-deployment.md) · [Production Checklist](98-production-checklist.md)

☐ Review architecture.

☐ Review performance.

☐ Review security.

☐ Review observability.

---

## Deployment

**Rules:** [Deployment](26-deployment.md) · [Observability](23-observability.md)

☐ Build successfully.

☐ Deploy successfully.

☐ Verify health checks.

☐ Review logs.

---

## After Deployment

**Rules:** [Observability](23-observability.md)

☐ Verify production functionality.

☐ Monitor metrics.

☐ Review error reporting.

☐ Confirm performance.

---

## Release Criteria

A release is production-ready when:

- all automated verification succeeds;
- critical functionality is validated;
- monitoring is operational;
- rollback is available;
- security review is complete;
- performance objectives are satisfied.

---

## Common Release Risks

Review carefully for:

- missing environment variables;
- incorrect cache configuration;
- broken authentication;
- missing migrations;
- oversized JavaScript bundles;
- SEO regressions;
- accessibility regressions;
- production-only configuration issues.

---

## Summary

Production readiness is achieved through disciplined engineering rather than a successful deployment alone.

By verifying architecture, performance, accessibility, security, testing, observability, deployment, and operational readiness before every release, teams significantly reduce production risk and improve long-term maintainability.

## Related

- `knowledge/nextjs/26-deployment.md`
- `knowledge/nextjs/24-security.md`
- `knowledge/nextjs/20-performance.md`
- `knowledge/nextjs/99-ai-review-checklist.md`
