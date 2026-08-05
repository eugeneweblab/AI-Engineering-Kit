---
id: nestjs/27-performance
topic: nestjs
slug: performance
title: "Performance Engineering"
type: doc
order: 27
status: ready
tags: [nestjs, performance]
related: [nestjs/19-caching, nestjs/17-database, performance/14-api-performance, nodejs/19-performance]
when_to_use: "Read before profiling, optimizing, or reviewing the performance and scalability of a NestJS application."
---
# Performance Engineering

## Purpose

This document defines the engineering standards for designing, measuring, and optimizing the performance of NestJS applications.

The objective is to maximize responsiveness, throughput, scalability, and resource efficiency while preserving correctness, maintainability, and reliability.

Performance is an engineering discipline.

Optimization should always be guided by measurements rather than assumptions.

---

## Core Principle

Measure first.

Optimize second.

Never optimize code without identifying the actual bottleneck.

---

## Performance Goals

Every production application should provide:

- low latency;
- high throughput;
- predictable response times;
- efficient resource usage;
- horizontal scalability;
- operational visibility.

Performance improvements should always be measurable.

---

## Performance Lifecycle

```
Measure

↓

Identify Bottleneck

↓

Optimize

↓

Validate

↓

Monitor
```

Every optimization should include before-and-after measurements.

---

## Common Bottlenecks

Typical bottlenecks include:

- database queries;
- network latency;
- synchronous CPU work;
- memory allocation;
- serialization;
- external APIs;
- locking;
- inefficient algorithms.

Never assume the bottleneck.

---

## Node.js Event Loop

NestJS runs on the Node.js event loop.

Avoid blocking operations such as:

- heavy calculations;
- synchronous file access;
- synchronous compression;
- large JSON processing.

Long-running CPU work should be moved to worker threads or background processing.

A synchronous CPU-bound call inside a request handler freezes the single event
loop thread, so every other in-flight request stalls until it returns. Prefer
the async variants that run on the libuv thread pool (or a worker thread).

```typescript
// report.controller.ts
import { Controller, Get } from '@nestjs/common';
import { promisify } from 'node:util';
import { pbkdf2, pbkdf2Sync } from 'node:crypto';

const pbkdf2Async = promisify(pbkdf2);

@Controller('reports')
export class ReportController {
  // BAD: pbkdf2Sync blocks the event loop for the whole computation. While it
  // runs, this Node process cannot accept or complete ANY other request.
  @Get('token-blocking')
  blocking(): { token: string } {
    const derived = pbkdf2Sync('seed', 'salt', 600_000, 64, 'sha512');
    return { token: derived.toString('hex') };
  }

  // GOOD: the async variant runs on the libuv thread pool, so the event loop
  // stays free to serve other requests while the hash is being derived.
  @Get('token')
  async nonBlocking(): Promise<{ token: string }> {
    const derived = await pbkdf2Async('seed', 'salt', 600_000, 64, 'sha512');
    return { token: derived.toString('hex') };
  }
}
```

---

## Database Performance

Optimize:

- indexes;
- query count;
- transaction duration;
- pagination;
- connection pooling.

Prevent:

- N+1 queries;
- full table scans;
- unnecessary joins.

Always inspect execution plans for slow queries.

The most common NestJS database bottleneck is the N+1 query: one query loads a
list, then one extra query fires per row to load its relation. Collapse it into
a single joined query, and page results with a bounded `take`.

```typescript
// order.service.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Order } from './order.entity';
import { OrderLine } from './order-line.entity';

@Injectable()
export class OrderService {
  constructor(
    @InjectRepository(Order) private readonly orders: Repository<Order>,
    @InjectRepository(OrderLine) private readonly lines: Repository<OrderLine>,
  ) {}

  // BAD: 1 query for the orders + 1 query PER order for its lines (N+1). With
  // 500 orders this is 501 round trips to the database.
  async listBad(): Promise<Order[]> {
    const orders = await this.orders.find();
    for (const order of orders) {
      order.lines = await this.lines.find({ where: { orderId: order.id } });
    }
    return orders;
  }

  // GOOD: a single joined query, bounded by `take`, with keyset pagination so
  // later pages stay fast instead of paying an OFFSET scan.
  async listGood(limit = 50, cursor?: string): Promise<Order[]> {
    const qb = this.orders
      .createQueryBuilder('order')
      .leftJoinAndSelect('order.lines', 'line')
      .orderBy('order.id', 'ASC')
      .take(limit);

    if (cursor) {
      qb.andWhere('order.id > :cursor', { cursor });
    }

    return qb.getMany();
  }
}
```

---

## Caching

Use caching only when it produces measurable improvements.

Examples:

- Redis;
- HTTP caching;
- CDN;
- in-memory cache.

The database remains the source of truth.

---

## API Performance

Review:

- payload size;
- serialization;
- compression;
- pagination;
- filtering.

Return only the data required by clients.

---

## Asynchronous Processing

Move expensive operations to queues.

Examples:

- emails;
- image processing;
- report generation;
- notifications.

Request latency should remain low.

---

## Memory Management

Monitor:

- heap usage;
- garbage collection;
- object allocation;
- memory leaks.

Memory consumption should remain predictable over time.

---

## CPU Utilization

Review:

- algorithm complexity;
- unnecessary loops;
- JSON transformations;
- encryption overhead.

High CPU usage often indicates inefficient algorithms.

---

## Network Performance

Reduce:

- unnecessary requests;
- payload size;
- request chaining;
- duplicate API calls.

Prefer batching where appropriate.

---

## Concurrency

Design for concurrent workloads.

Avoid:

- unnecessary locks;
- shared mutable state;
- long-running synchronous work.

Concurrency should improve throughput without compromising correctness.

---

## Horizontal Scaling

Applications should remain stateless whenever possible.

State should reside in:

- databases;
- distributed caches;
- message brokers.

Stateless services scale more effectively.

---

## Load Testing

Validate performance under realistic workloads.

Measure:

- latency;
- throughput;
- resource usage;
- failure rate.

Load testing should occur before production releases.

---

## Profiling

Use profilers to identify hotspots.

Typical areas:

- CPU;
- memory;
- SQL queries;
- event loop delays.

Optimize the largest bottleneck first.

---

## Observability

Monitor:

- response time;
- p95 latency;
- p99 latency;
- requests per second;
- queue depth;
- error rate.

Performance must remain observable.

Measure server-side latency at the framework boundary with a `NestInterceptor`.
Use a monotonic clock (`process.hrtime.bigint`), emit a structured measurement,
and forward it to a metrics backend that computes p95/p99 — do not eyeball
individual log lines.

```typescript
// latency.interceptor.ts
import {
  CallHandler,
  ExecutionContext,
  Injectable,
  Logger,
  NestInterceptor,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LatencyInterceptor implements NestInterceptor {
  private readonly logger = new Logger(LatencyInterceptor.name);

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const start = process.hrtime.bigint(); // monotonic; unaffected by clock drift
    const req = context.switchToHttp().getRequest<{ method: string; url: string }>();

    return next.handle().pipe(
      tap(() => {
        const elapsedMs = Number(process.hrtime.bigint() - start) / 1_000_000;
        this.logger.log(`${req.method} ${req.url} ${elapsedMs.toFixed(1)}ms`);
      }),
    );
  }
}
```

Register it globally so every route is measured:

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { LatencyInterceptor } from './latency.interceptor';

@Module({
  providers: [{ provide: APP_INTERCEPTOR, useClass: LatencyInterceptor }],
})
export class AppModule {}
```

---

## Performance Budgets

Define acceptable limits.

Examples:

- API latency;
- bundle size;
- startup time;
- memory usage.

Budgets prevent gradual performance degradation.

---

## Benchmarking

Benchmark critical operations after significant architectural changes.

Use consistent datasets and environments.

Compare results over time.

---

## Security vs Performance

Never sacrifice security solely for performance.

Examples:

- keep TLS enabled;
- validate input;
- preserve authorization checks.

Correctness and security always take priority.

---

## Testing

Verify:

- latency under load;
- concurrent execution;
- scalability;
- memory stability;
- throughput.

Performance tests should be repeatable.

---

## AI Decision Matrix

Optimize:

✓ Measured bottlenecks

✓ Database queries

✓ API latency

✓ CPU-intensive work

✓ Memory usage

Do **not** optimize:

✗ Unmeasured code

✗ Premature assumptions

✗ Readability at the expense of negligible gains

✗ Micro-optimizations without evidence

---

## AI Execution Checklist

## Investigation

☐ Measure baseline performance.

☐ Identify bottlenecks.

☐ Review infrastructure metrics.

☐ Review application metrics.

---

## Planning

☐ Optimize the largest bottleneck.

☐ Preserve readability.

☐ Validate improvements.

☐ Monitor production behavior.

---

## Verification

☐ Improvements measured.

☐ No regression introduced.

☐ Performance budgets satisfied.

☐ Event loop remains responsive.

☐ Database optimized.

☐ Observability updated.

---

## Examples

**Good Example** — measure first, then remove the round trips that dominate

```ts
@Injectable()
export class DashboardService {
  constructor(private readonly db: DataSource, @Inject(CACHE_MANAGER) private readonly cache: Cache) {}

  async summary(userId: string): Promise<DashboardSummary> {
    const key = `dashboard:v1:${userId}`;
    const cached = await this.cache.get<DashboardSummary>(key);
    if (cached) {
      return cached;
    }

    // Independent queries run concurrently rather than in sequence: the latency
    // is the slowest one, not their sum.
    const [orders, invoices, alerts] = await Promise.all([
      this.orders.countRecent(userId),
      this.invoices.sumOutstanding(userId),
      this.alerts.openFor(userId),
    ]);

    const summary = { orders, invoices, alerts };
    await this.cache.set(key, summary, 60_000);
    return summary;
  }
}
```

```ts
// CPU-bound work moved off the event loop, which otherwise blocks every request.
@Injectable()
export class ReportsService {
  private readonly pool = new Piscina({ filename: join(__dirname, 'render-report.worker.js') });

  render(rows: ReportRow[]): Promise<Buffer> {
    return this.pool.run(rows);
  }
}
```

**Bad Example** — sequential awaits and synchronous CPU work in the request path

```ts
@Injectable()
export class DashboardService {
  async summary(userId: string) {
    // Three independent queries, awaited one after another: 3× the latency for
    // no reason. Nothing here depends on the previous result.
    const orders = await this.orders.countRecent(userId);
    const invoices = await this.invoices.sumOutstanding(userId);
    const alerts = await this.alerts.openFor(userId);

    // Blocking CPU work on the event loop: while this runs, the process cannot
    // accept a connection, answer a health check, or serve any other request.
    const pdf = renderReportSync(orders, invoices, alerts);

    // An N+1 hidden behind a map: one query per alert, awaited serially.
    const enriched = [];
    for (const alert of alerts) {
      enriched.push(await this.users.findById(alert.assigneeId));
    }

    return { pdf, enriched };
  }
}
```

Profile before changing anything: the fix above is architectural — fewer round trips and work
moved off the loop — and no amount of micro-optimisation inside `renderReportSync` matches it.

---

## Common Mistakes

Avoid:

Premature optimization.

Ignoring profiling.

Blocking the event loop.

Optimizing without benchmarks.

Returning excessive data.

Ignoring slow database queries.

Treating caching as a universal solution.

---

## Completion Criteria

Performance engineering is complete when:

- bottlenecks are identified through measurements;
- optimizations produce measurable improvements;
- latency and throughput meet defined targets;
- resource usage remains predictable;
- observability supports ongoing monitoring;
- scalability requirements are satisfied.

---

## Summary

Performance engineering is the continuous process of measuring, optimizing, validating, and monitoring application behavior.

By focusing on measurable bottlenecks, protecting the Node.js event loop, optimizing persistence and networking, and continuously validating improvements, NestJS applications remain responsive, scalable, and efficient under production workloads.

## Related

- `knowledge/nestjs/19-caching.md`
- `knowledge/nestjs/17-database.md`
- `knowledge/performance/14-api-performance.md`
- `knowledge/nodejs/19-performance.md`
