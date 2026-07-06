# WordPress Performance

## Purpose

This document defines the engineering principles for building high-performance WordPress applications.

Performance is not achieved by applying isolated optimizations after development is complete.

Performance should be considered during architecture, implementation, deployment, and long-term maintenance.

The objective is to deliver fast, scalable, and efficient applications that remain performant as content, traffic, and features grow.

---

# Core Principle

Optimize architecture before optimizing code.

The largest performance improvements usually come from better system design rather than micro-optimizations.

Always identify the real bottleneck before implementing changes.

---

# Performance Mindset

Every implementation should consider:

- CPU usage;
- memory usage;
- database load;
- network requests;
- rendering time;
- cache efficiency;
- frontend performance.

Avoid optimizing areas that are not measurable bottlenecks.

---

# Measure Before Optimizing

Before making performance changes:

- reproduce the issue;
- collect performance metrics;
- identify the bottleneck;
- establish a baseline.

Never optimize based on assumptions.

---

# Database Performance

Prefer:

- WordPress APIs;
- indexed queries;
- WP_Query;
- lazy loading;
- pagination;
- object caching.

Avoid:

- repeated database queries;
- querying inside loops;
- unnecessary JOIN operations;
- loading entire datasets.

Every database query should have a clear purpose.

---

# Query Optimization

Before writing a query ask:

- Can existing data be reused?
- Can the result be cached?
- Is every selected field required?
- Can pagination be applied?
- Is this query executed repeatedly?

Duplicate queries should be eliminated whenever possible.

---

# Object Caching

Use object caching for frequently requested data.

Suitable examples:

- settings;
- navigation;
- taxonomy data;
- expensive calculations;
- API responses.

Avoid caching data that changes frequently unless invalidation is well defined.

---

# Transients

Use transients for temporary cached data.

Suitable examples:

- remote API responses;
- expensive reports;
- computed statistics;
- third-party integrations.

Always define an expiration strategy.

---

# REST API Performance

Review:

- response size;
- number of requests;
- unnecessary fields;
- repeated computations;
- authentication overhead.

Return only the data required by the client.

---

# Asset Loading

Load only required assets.

Review:

- CSS bundles;
- JavaScript bundles;
- fonts;
- icons;
- images;
- third-party libraries.

Avoid loading assets globally when they are page-specific.

---

# Image Optimization

Prefer:

- modern image formats;
- responsive images;
- lazy loading;
- appropriate image dimensions;
- optimized compression.

Avoid serving oversized images.

---

# JavaScript Performance

Reduce:

- unnecessary renders;
- duplicate event listeners;
- unnecessary API requests;
- unused libraries;
- blocking scripts.

Move expensive work away from the critical rendering path.

---

# CSS Performance

Maintain:

- reusable utility classes;
- consistent design tokens;
- minimal specificity;
- small bundle size.

Avoid duplicated styles across components.

---

# External APIs

External services introduce latency.

Before adding an integration:

- determine timeout strategy;
- define retry behavior;
- define fallback behavior;
- consider caching responses.

External dependencies should degrade gracefully.

---

# Background Processing

Long-running tasks should execute outside the request lifecycle whenever possible.

Examples:

- imports;
- exports;
- image processing;
- email delivery;
- synchronization jobs.

Keep page requests fast.

---

# Monitoring

Continuously monitor:

- response times;
- slow queries;
- error rates;
- cache hit ratio;
- memory usage;
- CPU usage.

Performance is an ongoing engineering activity.

---

# AI Execution Checklist

## Investigation

☐ Identify the bottleneck.

☐ Collect performance metrics.

☐ Review database queries.

☐ Review network requests.

☐ Review asset loading.

---

## Planning

☐ Identify optimization opportunities.

☐ Estimate implementation impact.

☐ Preserve existing behavior.

☐ Define verification strategy.

---

## Implementation

☐ Minimize database queries.

☐ Reuse cached data.

☐ Reduce unnecessary rendering.

☐ Optimize asset loading.

☐ Preserve maintainability.

---

## Verification

☐ Compare before and after.

☐ Review response times.

☐ Review cache usage.

☐ Review memory usage.

☐ Verify functionality.

---

# Common Mistakes

Avoid:

Optimizing without measurement.

Querying inside loops.

Loading unnecessary assets.

Ignoring caching.

Returning excessive API data.

Premature optimization.

Optimizing code instead of architecture.

Ignoring long-term scalability.

---

# Completion Criteria

Performance work is complete only if:

- the bottleneck has been verified;
- measurable improvements have been achieved;
- functionality remains unchanged;
- maintainability has not been reduced;
- documentation has been updated when appropriate.

---

# Summary

Performance is the result of good architecture, efficient data access, responsible resource usage, and continuous measurement.

The fastest code is often the code that never executes because unnecessary work has been eliminated.