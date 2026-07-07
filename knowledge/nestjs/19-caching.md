---
id: nestjs/19-caching
topic: nestjs
slug: caching
title: "NestJS Caching"
type: doc
order: 19
status: ready
tags: [nestjs, caching]
related: []
when_to_use: ""
---
# NestJS Caching

## Purpose

This document defines the engineering standards for implementing caching in NestJS applications.

The objective is to improve application performance, reduce infrastructure load, and increase scalability while maintaining data consistency.

Caching is an optimization.

It must never become the source of truth.

---

## Core Principle

The database remains the primary source of truth.

Caches exist only to improve performance.

---

## Caching Goals

Every caching strategy should provide:

- predictable behavior;
- measurable performance improvements;
- controlled invalidation;
- high cache hit ratio;
- minimal stale data.

Never introduce caching without a measurable benefit.

---

## Responsibilities

Caching is responsible for:

- reducing repeated computation;
- reducing database load;
- reducing network latency;
- improving response times.

Caching should not:

- replace persistence;
- store permanent business data;
- implement business logic;
- guarantee consistency.

---

## Cache Flow

```
Request

↓

Cache Lookup

↓

Cache Hit?

↓

Yes → Return Cached Data

↓

No

↓

Repository

↓

Database

↓

Store in Cache

↓

Response
```

The application should always behave correctly when the cache is unavailable.

---

## Cache Levels

Typical cache layers include:

- in-memory cache;
- distributed cache;
- HTTP cache;
- CDN cache;
- browser cache.

Each layer solves different performance problems.

---

## Suitable Candidates

Cache data that is:

- frequently read;
- rarely changed;
- expensive to compute;
- expensive to retrieve.

Examples:

- product catalog;
- application settings;
- permissions;
- exchange rates;
- aggregated statistics.

---

## Poor Candidates

Avoid caching:

- highly volatile data;
- active financial balances;
- security-sensitive state;
- request-specific data;
- authentication state unless explicitly designed.

---

## Cache Keys

Cache keys should be:

- predictable;
- unique;
- versioned when appropriate;
- human-readable.

Example:

```
users:42

orders:123

products:list:page:2
```

Avoid ambiguous keys.

---

## Time-To-Live (TTL)

Every cache entry should define an expiration strategy.

Consider:

- update frequency;
- business tolerance for stale data;
- memory usage.

Avoid infinite TTL unless absolutely required.

---

## Cache Invalidation

Invalidation is often more important than caching itself.

Invalidate when:

- data changes;
- entities are deleted;
- permissions change;
- business events occur.

Stale caches cause incorrect application behavior.

---

## Cache-Aside Pattern

Preferred strategy:

```
Read Request

↓

Cache

↓

Miss

↓

Database

↓

Cache

↓

Response
```

Applications remain functional even if the cache becomes unavailable.

---

## Write Strategy

When data changes:

```
Database Update

↓

Commit

↓

Invalidate Cache

↓

Future Requests Rebuild Cache
```

Avoid updating cache before successful persistence.

---

## Distributed Cache

For multiple application instances, prefer a distributed cache.

Typical technologies:

- Redis;
- Memcached.

Application behavior should remain independent of cache implementation.

---

## Serialization

Cache serialized objects rather than ORM entities.

Avoid storing framework-specific objects.

---

## Stampede Prevention

Prevent many requests rebuilding the same cache simultaneously.

Possible strategies:

- locking;
- request coalescing;
- stale-while-revalidate;
- background refresh.

---

## Cache Warming

Preload frequently accessed data after deployment or startup when appropriate.

Avoid warming unnecessary data.

---

## Metrics

Measure:

- cache hit ratio;
- cache miss ratio;
- eviction rate;
- average lookup latency;
- memory usage.

Optimize based on metrics.

---

## Performance

Review:

- cache size;
- serialization cost;
- invalidation frequency;
- lookup latency.

Caching should improve measurable performance.

---

## Security

Never cache:

- passwords;
- JWT secrets;
- API keys;
- personally sensitive information unless encrypted and justified.

Review every cached object.

---

## Failure Handling

If the cache is unavailable:

- continue serving requests;
- fall back to the database;
- log cache failures;
- monitor degradation.

Cache outages should not make the application unavailable.

---

## Testing

Verify:

- cache hits;
- cache misses;
- invalidation;
- expiration;
- fallback behavior;
- concurrent access.

Caching behavior should remain predictable.

---

## AI Decision Matrix

Cache:

✓ Frequently read data

✓ Expensive queries

✓ Static configuration

✓ Aggregated results

Do **not** cache:

✗ Business workflows

✗ Frequently changing balances

✗ Authentication secrets

✗ Temporary request state

---

## AI Execution Checklist

## Investigation

☐ Identify performance bottleneck.

☐ Measure database load.

☐ Review update frequency.

☐ Review consistency requirements.

---

## Planning

☐ Choose cache strategy.

☐ Define TTL.

☐ Design invalidation.

☐ Plan fallback behavior.

---

## Verification

☐ Cache optional.

☐ Database remains source of truth.

☐ Invalidation implemented.

☐ Metrics collected.

☐ Sensitive data excluded.

☐ Cache independently testable.

---

## Common Mistakes

Avoid:

Caching everything.

Ignoring invalidation.

Infinite TTL.

Caching ORM entities.

Using cache as primary storage.

Skipping cache metrics.

Failing when cache is unavailable.

---

## Completion Criteria

Caching is complete when:

- performance improvements are measurable;
- invalidation is well defined;
- cache failures do not break the application;
- TTL strategy is documented;
- metrics are collected;
- cached data is appropriate and secure.

---

## Summary

Caching improves performance by reducing repeated work and database load.

By treating the cache as an optimization rather than a source of truth, implementing clear invalidation strategies, measuring effectiveness, and designing graceful fallback behavior, NestJS applications remain both fast and reliable.