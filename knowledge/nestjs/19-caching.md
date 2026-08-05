---
id: nestjs/19-caching
topic: nestjs
slug: caching
title: "NestJS Caching"
type: doc
order: 19
status: ready
tags: [nestjs, caching, rename, Injectable, Inject, findById, CACHE_MANAGER]
related: [nestjs/27-performance, nestjs/10-interceptors, redis/13-caching, architecture/19-caching-strategies]
when_to_use: "Read before adding or reviewing caching to improve performance, and when reasoning about cache invalidation and consistency."
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

Inject `CACHE_MANAGER`, read-through, and wrap cache calls so a cache outage
degrades to a plain database read instead of a failed request.

```ts
// product.service.ts
import { Inject, Injectable, Logger } from '@nestjs/common';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';
import { ProductRepository } from './product.repository';

// A plain, serializable view. Never cache the ORM entity itself.
export interface ProductView {
  id: string;
  name: string;
  priceCents: number;
}

@Injectable()
export class ProductService {
  private readonly logger = new Logger(ProductService.name);
  private readonly ttlMs = 60_000; // 60s; TTL is milliseconds in cache-manager v5+

  constructor(
    @Inject(CACHE_MANAGER) private readonly cache: Cache,
    private readonly products: ProductRepository,
  ) {}

  async findById(id: string): Promise<ProductView | null> {
    const key = `products:${id}`;

    try {
      const cached = await this.cache.get<ProductView>(key);
      if (cached) return cached;
    } catch (err) {
      // The cache is an optimization: log and fall through to the source of truth.
      this.logger.warn(`Cache read failed for ${key}: ${(err as Error).message}`);
    }

    const entity = await this.products.findById(id);
    if (!entity) return null;

    const view: ProductView = {
      id: entity.id,
      name: entity.name,
      priceCents: entity.priceCents,
    };

    try {
      await this.cache.set(key, view, this.ttlMs);
    } catch (err) {
      this.logger.warn(`Cache write failed for ${key}: ${(err as Error).message}`);
    }

    return view;
  }
}
```

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

Persist first, then invalidate. Let the next read rebuild the entry through the
cache-aside path above.

```ts
// GOOD: commit to the source of truth, then invalidate. Never pre-populate.
async rename(id: string, name: string): Promise<void> {
  await this.products.update(id, { name }); // committed to the database
  await this.cache.del(`products:${id}`);   // next read rebuilds from the DB
}
```

```ts
// BAD: writes the cache before persisting AND caches the ORM entity with no TTL.
async rename(id: string, name: string): Promise<void> {
  const entity = await this.products.findById(id);
  entity.name = name;
  // Omitting the TTL leaves the entry with no expiry, and the value is a live
  // ORM entity, not a serializable view.
  await this.cache.set(`products:${id}`, entity);
  // If this throws, the cache already advertises data that was never committed.
  await this.products.save(entity);
}
```

---

## Distributed Cache

For multiple application instances, prefer a distributed cache.

Typical technologies:

- Redis;
- Memcached.

Application behavior should remain independent of cache implementation.

On NestJS 10/11 use `@nestjs/cache-manager` (v3+, built on `cache-manager`
v6 / Keyv). Register a fast in-memory tier backed by a shared Redis tier so a
single node hit is served locally while all nodes share the same invalidation.

```ts
// app.module.ts
import { Module } from '@nestjs/common';
import { CacheModule } from '@nestjs/cache-manager';
import { createKeyv } from '@keyv/redis';
import { Keyv } from 'keyv';
import { CacheableMemory } from 'cacheable';
import { ConfigModule, ConfigService } from '@nestjs/config';

@Module({
  imports: [
    CacheModule.registerAsync({
      isGlobal: true,
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        // Read tiers front-to-back; writes fan out to every store.
        stores: [
          // L1: process-local LRU. ttl is milliseconds in cache-manager v5+.
          new Keyv({
            store: new CacheableMemory({ ttl: 30_000, lruSize: 5_000 }),
          }),
          // L2: shared Redis so every instance sees the same data.
          createKeyv(config.getOrThrow<string>('REDIS_URL')),
        ],
      }),
    }),
  ],
})
export class AppModule {}
```

`isGlobal: true` exposes the `CACHE_MANAGER` provider to every module without
re-importing `CacheModule`.

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

## Examples

**Good Example** — cache-aside, bounded TTL, invalidated after the write commits

```ts
@Injectable()
export class ProductsService {
  private static readonly TTL_SECONDS = 300;

  constructor(
    @Inject(CACHE_MANAGER) private readonly cache: Cache,
    private readonly products: ProductsRepository,
  ) {}

  async findById(id: string): Promise<ProductView | null> {
    const key = `product:v2:${id}`;          // version in the key: a shape change
    const cached = await this.cache.get<ProductView>(key);   // invalidates the old entries
    if (cached) {
      return cached;
    }

    const product = await this.products.findById(id);
    if (!product) {
      return null;                          // do not cache "not found" indefinitely
    }

    const view = toView(product);           // cache the projection, not the ORM entity
    await this.cache.set(key, view, ProductsService.TTL_SECONDS * 1000);
    return view;
  }

  async rename(id: string, name: string): Promise<void> {
    await this.products.rename(id, name);   // source of truth first
    await this.cache.del(`product:v2:${id}`); // then invalidate; never pre-populate
  }
}
```

**Bad Example** — write-through into the cache, no TTL, entity cached whole

```ts
@Injectable()
export class ProductsService {
  async rename(id: string, name: string): Promise<void> {
    const entity = await this.repo.findOne({ where: { id }, relations: { reviews: true } });
    entity.name = name;

    // Cache updated BEFORE the database. If the update below fails, every reader
    // now sees a name that was never persisted.
    await this.cache.set(`product:${id}`, entity);   // no TTL: stale forever

    await this.repo.save(entity);
  }

  async findById(id: string) {
    // Caching the ORM entity stores its relations, its private fields, and
    // whatever the next migration adds — then hands them back after a deploy
    // in which the class shape changed.
    const cached = await this.cache.get<ProductEntity>(`product:${id}`);
    return cached ?? this.repo.findOne({ where: { id } });
  }
}
```

An entry with no TTL and no invalidation path is not a cache; it is a second database that
nobody migrates.

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

## Related

- `knowledge/nestjs/27-performance.md`
- `knowledge/nestjs/10-interceptors.md`
- `knowledge/redis/13-caching.md`
- `knowledge/architecture/19-caching-strategies.md`
