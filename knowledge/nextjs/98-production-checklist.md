---
id: nextjs/98-production-checklist
topic: nextjs
slug: production-checklist
title: "Next.js Production Checklist"
type: doc
order: 98
status: ready
tags: [nextjs, production-checklist]
related: []
when_to_use: ""
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

Verify:

☐ Server Components are used whenever possible.

☐ Client Components are limited to interactive UI.

☐ Feature boundaries are respected.

☐ Business logic is separated from presentation.

☐ Shared components remain reusable.

☐ State ownership is clear.

---

## Rendering

Verify:

☐ Appropriate rendering strategy selected.

☐ Static pages generated where appropriate.

☐ Dynamic rendering used only when required.

☐ Streaming implemented where beneficial.

☐ Suspense boundaries reviewed.

---

## Data Fetching

Verify:

☐ Data fetched on the server whenever possible.

☐ Parallel requests implemented where appropriate.

☐ Request waterfalls eliminated.

☐ Error handling implemented.

☐ Loading states reviewed.

---

## Server Actions

Verify:

☐ Input validation implemented.

☐ Authorization verified.

☐ Authentication verified.

☐ Cache invalidation configured.

☐ Errors handled safely.

---

## API Routes

Verify:

☐ Requests validated.

☐ Authentication enforced.

☐ Authorization enforced.

☐ HTTP status codes correct.

☐ Response format consistent.

---

## Caching

Verify:

☐ Cache strategy documented.

☐ Revalidation configured.

☐ Browser caching reviewed.

☐ CDN caching reviewed.

☐ Personalized content not publicly cached.

---

## Performance

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

Verify:

☐ Semantic HTML used.

☐ Keyboard navigation works.

☐ Alternative text provided.

☐ Color contrast reviewed.

☐ Focus management verified.

☐ Screen reader compatibility reviewed.

---

## SEO

Verify:

☐ Metadata complete.

☐ Canonical URLs configured.

☐ Open Graph configured.

☐ Structured data reviewed.

☐ Sitemap available.

☐ Robots directives correct.

---

## Security

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

Verify:

☐ Environment variables documented.

☐ Production configuration validated.

☐ Secrets loaded correctly.

☐ Debug mode disabled.

☐ Feature flags reviewed.

---

## Database

Verify:

☐ Migrations reviewed.

☐ Rollback available.

☐ Indexes verified.

☐ Slow queries reviewed.

☐ Backup strategy confirmed.

---

## Logging

Verify:

☐ Structured logging implemented.

☐ Error logging enabled.

☐ Sensitive data excluded.

☐ Request identifiers available.

---

## Monitoring

Verify:

☐ Metrics collected.

☐ Health checks operational.

☐ Alerts configured.

☐ Dashboards available.

☐ Error reporting active.

---

## Testing

Verify:

☐ Unit tests passing.

☐ Integration tests passing.

☐ End-to-end tests passing.

☐ Accessibility tests completed.

☐ Critical user journeys verified.

---

## Deployment

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

☐ Review architecture.

☐ Review performance.

☐ Review security.

☐ Review observability.

---

## Deployment

☐ Build successfully.

☐ Deploy successfully.

☐ Verify health checks.

☐ Review logs.

---

## After Deployment

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