---
id: performance/readme
topic: performance
slug: readme
title: "Performance Engineering Standards"
type: index
order: -1
status: ready
tags: [performance]
related: []
when_to_use: "Read first when starting performance work, to see how this section's docs fit together and where to begin measuring."
---
# Performance Engineering Standards

## Purpose

This section defines the engineering standards for making systems fast and keeping them
fast: which metrics reflect user experience, how to find the actual bottleneck, and how to
prevent regressions from accumulating unnoticed.

The discipline this section enforces is measurement before action. Most performance work
performed on intuition optimizes something that was never the constraint — a memoized
component in an app that spends 90% of its time waiting on a query, a minified bundle on a
page blocked by an unoptimized hero image. The profiler is not an advanced tool; it is the
first step.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Fundamentals, metrics, and Core Web Vitals
- Resource-level performance: CPU, memory, network
- Frontend: rendering, loading, code splitting, lazy loading, images, fonts
- Backend and data: database performance, query optimization, API performance, caching
- Measurement: profiling, benchmarking, monitoring
- Scalability, capacity planning, and load testing
- Performance budgets and the optimization workflow
- Production monitoring, debugging, and review practice

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. [Overview](00-overview.md)
- 01. [Performance Fundamentals](01-performance-fundamentals.md)
- 02. [Metrics](02-metrics.md)
- 18. [Web Vitals](18-web-vitals.md)
- 30. [Engineering Principles](30-engineering-principles.md)

## Measuring First

- 16. [Profiling](16-profiling.md)
- 19. [Benchmarking](19-benchmarking.md)
- 24. [Optimization Workflow](24-optimization-workflow.md)
- 23. [Performance Budget](23-performance-budget.md)

## Resources

- 03. [CPU](03-cpu.md)
- 04. [Memory](04-memory.md)
- 05. [Network](05-network.md)

## Frontend

- 06. [Rendering](06-rendering.md)
- 07. [Loading](07-loading.md)
- 09. [Lazy Loading](09-lazy-loading.md)
- 10. [Code Splitting](10-code-splitting.md)
- 11. [Images](11-images.md)
- 12. [Fonts](12-fonts.md)

## Backend and Data

- 08. [Caching](08-caching.md)
- 13. [Database Performance](13-database-performance.md)
- 14. [API Performance](14-api-performance.md)
- 15. [Query Optimization](15-query-optimization.md)

## Scale

- 20. [Capacity Planning](20-capacity-planning.md)
- 21. [Scalability](21-scalability.md)
- 22. [Load Testing](22-load-testing.md)

## Production

- 17. [Monitoring](17-monitoring.md)
- 25. [Production Monitoring](25-production-monitoring.md)
- 26. [Debugging](26-debugging.md)
- 27. [Best Practices](27-best-practices.md)
- 28. [Real-World Patterns](28-real-world-patterns.md)
- 29. [Performance Review](29-performance-review.md)

## Verification

- 98. [Production Checklist](98-production-checklist.md)
- 99. [AI Review Checklist](99-ai-review-checklist.md)
- 100. [Common Antipatterns](100-common-antipatterns.md)

---

## Engineering Principles

Every performance change should satisfy the following principles:

- Measure before optimizing, and measure again after. An unmeasured optimization is a guess
  with a maintenance cost.
- Optimize the bottleneck, not the code you happen to be reading.
- Prefer doing less work to doing the same work faster: the fastest query is the one you do
  not run.
- Judge by user-perceived metrics — LCP, INP, CLS, time to first byte — not by machine
  metrics that no user experiences.
- Set a budget before building, so regressions are visible as failures rather than opinions.
- Cache deliberately, with an invalidation path; a cache without one trades speed for
  incorrectness.
- Bound everything that can grow: result sets, payloads, concurrency, retries.
- Measure at the percentiles that matter (p95, p99), because averages hide the users who
  suffer.
- Watch production, not just the lab — real devices and real networks are slower than yours.
- Trade complexity for speed only when the measurement justifies it, and record why.

---

## Intended Audience

These standards are intended for:

- Frontend and Backend Engineers
- Performance and SRE Engineers
- DevOps and Platform Engineers
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Performance work begins with measurement and ends with verification. Find the real
bottleneck, prefer eliminating work over speeding it up, set budgets so regressions announce
themselves, and judge results by what users actually experience.
