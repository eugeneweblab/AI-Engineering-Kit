---
id: nestjs/24-observability
topic: nestjs
slug: observability
title: "Observability"
type: doc
order: 24
status: ready
tags: [nestjs, observability]
related: [nestjs/10-interceptors, nestjs/29-maintenance, architecture/18-observability, nodejs/17-logging]
when_to_use: "Read before adding or reviewing logging, metrics, tracing, or health checks for a NestJS service."
---
# Observability

## Purpose

This document defines the engineering standards for implementing observability in NestJS applications.

The objective is to make every production system measurable, traceable, and debuggable by collecting meaningful telemetry.

Observability answers one question:

> What is happening inside the system?

Every production service should provide enough information to diagnose problems without reproducing them locally.

---

## Core Principle

If a system cannot be observed, it cannot be reliably operated.

Observability is a production requirement.

Not a debugging tool.

---

## Goals

Every application should provide:

- structured logging;
- distributed tracing;
- metrics;
- health monitoring;
- alerting;
- auditability.

These capabilities should work together.

---

## Three Pillars

Observability consists of three complementary pillars.

## Logs

Describe discrete events.

Examples:

- HTTP request;
- authentication;
- exception;
- deployment;
- background job.

---

## Metrics

Measure numerical values over time.

Examples:

- request rate;
- latency;
- memory usage;
- CPU utilization;
- queue depth.

---

## Traces

Show how requests travel across the system.

Example:

```
Client

↓

API Gateway

↓

Orders Service

↓

Payment Service

↓

Database

↓

Response
```

Tracing identifies bottlenecks across distributed systems.

---

## Structured Logging

Logs should always be structured.

Include:

- timestamp;
- log level;
- service name;
- correlation ID;
- request ID;
- user ID (when available);
- message.

Avoid free-form logging.

Implement structured logging by replacing the default logger with a class that
implements the `LoggerService` interface and emits one JSON object per line.
Machine-readable logs can be indexed, filtered, and correlated by a log platform;
interpolated strings cannot.

```ts
// observability/structured-logger.ts
import { Injectable, LoggerService } from '@nestjs/common';
import { getCorrelationId } from './request-context';

@Injectable()
export class StructuredLogger implements LoggerService {
  private write(level: string, message: unknown, context?: string): void {
    process.stdout.write(
      JSON.stringify({
        timestamp: new Date().toISOString(),
        level,
        service: process.env.SERVICE_NAME ?? 'orders-service',
        correlationId: getCorrelationId(),
        context,
        message,
      }) + '\n',
    );
  }

  log(message: unknown, context?: string): void {
    this.write('info', message, context);
  }

  error(message: unknown, stack?: string, context?: string): void {
    this.write('error', message, context);
  }

  warn(message: unknown, context?: string): void {
    this.write('warn', message, context);
  }

  debug(message: unknown, context?: string): void {
    this.write('debug', message, context);
  }

  verbose(message: unknown, context?: string): void {
    this.write('verbose', message, context);
  }
}
```

Install it globally in `main.ts`. `bufferLogs: true` holds startup logs until the
custom logger is registered so nothing is emitted in the wrong format:

```ts
// main.ts
const app = await NestFactory.create(AppModule, { bufferLogs: true });
app.useLogger(new StructuredLogger());
```

Good — a structured record with a stable schema and no secrets:

```ts
// inside a service (context is the class name)
this.logger.log(
  { event: 'order.created', orderId: order.id, userId: order.userId },
  OrdersService.name,
);
// => {"timestamp":"…","level":"info","correlationId":"…","message":{"event":"order.created", …}}
```

Bad — a free-form string that cannot be queried and leaks a token:

```ts
console.log(`Order ${order.id} created by ${order.userId}, token=${jwt}`);
```

---

## Log Levels

Use consistent levels.

```
TRACE

DEBUG

INFO

WARN

ERROR

FATAL
```

Choose the lowest level that accurately represents the event.

---

## Correlation IDs

Every request should receive a correlation ID.

Propagate it through:

- HTTP;
- queues;
- events;
- background jobs;
- scheduled tasks.

A single business operation should be traceable end-to-end.

Store the correlation ID in an `AsyncLocalStorage` so any provider — a service,
a repository, or the logger above — can read it without threading it through
every method signature:

```ts
// observability/request-context.ts
import { AsyncLocalStorage } from 'node:async_hooks';

interface RequestContext {
  correlationId: string;
}

export const requestContext = new AsyncLocalStorage<RequestContext>();

export function getCorrelationId(): string | undefined {
  return requestContext.getStore()?.correlationId;
}
```

Populate the store once at the edge. A global middleware reuses an inbound
`x-correlation-id` (so the ID survives across service hops) or mints a new one,
echoes it back on the response, and wraps the rest of the request in
`requestContext.run(...)`:

```ts
// main.ts (registered before app.listen)
import { randomUUID } from 'node:crypto';
import type { Request, Response, NextFunction } from 'express';
import { requestContext } from './observability/request-context';

app.use((req: Request, res: Response, next: NextFunction) => {
  const correlationId =
    (req.headers['x-correlation-id'] as string | undefined) ?? randomUUID();
  res.setHeader('x-correlation-id', correlationId);
  requestContext.run({ correlationId }, next);
});
```

Registering it with `app.use` applies it globally and works identically on
NestJS 10 (Express 4) and NestJS 11 (Express 5), avoiding the named-wildcard
route changes that affect `MiddlewareConsumer.forRoutes('*')` on v11.

---

## Distributed Tracing

Trace every significant operation.

Typical spans:

- HTTP request;
- SQL query;
- cache lookup;
- external API;
- queue publish;
- queue processing.

Every span should have meaningful names.

---

## Metrics

Collect metrics for:

- request count;
- error rate;
- response time;
- throughput;
- queue size;
- retry count;
- cache hit ratio.

Measure trends rather than isolated values.

---

## Health Checks

Health endpoints should report:

- application status;
- database connectivity;
- cache availability;
- queue availability;
- external dependencies.

Separate:

- liveness;
- readiness.

Use `@nestjs/terminus`, which provides ready-made health indicators and a
`@HealthCheck()` decorator that formats the aggregate result. Import
`TerminusModule` and expose a controller:

```ts
// health/health.module.ts
import { Module } from '@nestjs/common';
import { TerminusModule } from '@nestjs/terminus';
import { HealthController } from './health.controller';

@Module({
  imports: [TerminusModule],
  controllers: [HealthController],
})
export class HealthModule {}
```

Liveness answers "is the process alive?" and must stay cheap — checking a
dependency here can crash-loop a healthy pod. Readiness answers "can it serve
traffic?" and checks the dependencies the service actually needs:

```ts
// health/health.controller.ts
import { Controller, Get } from '@nestjs/common';
import {
  HealthCheck,
  HealthCheckService,
  MemoryHealthIndicator,
  TypeOrmHealthIndicator,
} from '@nestjs/terminus';

@Controller('health')
export class HealthController {
  constructor(
    private readonly health: HealthCheckService,
    private readonly db: TypeOrmHealthIndicator,
    private readonly memory: MemoryHealthIndicator,
  ) {}

  // Liveness: no external dependencies — only the process itself.
  @Get('live')
  @HealthCheck()
  liveness() {
    return this.health.check([
      () => this.memory.checkHeap('memory_heap', 512 * 1024 * 1024),
    ]);
  }

  // Readiness: the DB the service cannot serve requests without.
  @Get('ready')
  @HealthCheck()
  readiness() {
    return this.health.check([() => this.db.pingCheck('database')]);
  }
}
```

Each indicator returns a `503 Service Unavailable` with a per-check status when
it fails, so orchestrators (Kubernetes probes, load balancers) can route around
an unready instance.

---

## Audit Logs

Audit logs record security-sensitive actions.

Examples:

- login;
- permission changes;
- financial operations;
- user deletion;
- administrative actions.

Audit logs should be immutable.

---

## Error Tracking

Capture:

- exceptions;
- stack traces;
- request metadata;
- affected user;
- release version.

Every production exception should be traceable.

---

## OpenTelemetry

Prefer OpenTelemetry as the standard telemetry framework.

Benefits:

- vendor-neutral;
- standardized instrumentation;
- broad ecosystem support.

Application code should remain independent of monitoring vendors.

Initialize the OpenTelemetry SDK in its own module and import it **first**, before
`NestFactory` or any instrumented library is loaded — the auto-instrumentations
patch modules (`http`, `pg`, `ioredis`, `express`) at require time, so a late
start captures nothing:

```ts
// observability/tracing.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { resourceFromAttributes } from '@opentelemetry/resources';
import {
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
} from '@opentelemetry/semantic-conventions';

const sdk = new NodeSDK({
  resource: resourceFromAttributes({
    [ATTR_SERVICE_NAME]: process.env.SERVICE_NAME ?? 'orders-service',
    [ATTR_SERVICE_VERSION]: process.env.APP_VERSION ?? '0.0.0',
  }),
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT, // e.g. http://collector:4318/v1/traces
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

// Flush spans on shutdown so the last requests are not lost.
process.on('SIGTERM', () => {
  sdk.shutdown().finally(() => process.exit(0));
});
```

```ts
// main.ts — the FIRST import in the file
import './observability/tracing';
import { NestFactory } from '@nestjs/core';
// … remaining imports and bootstrap()
```

With auto-instrumentation active, incoming HTTP requests, outgoing calls, and DB
queries become spans automatically. Correlate them with the logs above by adding
the active `traceId` to each log line via
`trace.getActiveSpan()?.spanContext().traceId`.

---

## Dashboards

Dashboards should expose:

- service health;
- latency;
- error rate;
- infrastructure usage;
- queue status;
- deployment history.

Dashboards should support rapid diagnosis.

---

## Alerting

Alert on:

- elevated error rates;
- service unavailability;
- failed background jobs;
- excessive latency;
- resource exhaustion.

Avoid alert fatigue.

Alerts should be actionable.

---

## Performance

Observability introduces overhead.

Review:

- log volume;
- metric cardinality;
- trace sampling;
- storage costs.

Collect useful telemetry.

Avoid unnecessary telemetry.

---

## Security

Never log:

- passwords;
- JWT tokens;
- API keys;
- encryption keys;
- payment information.

Review log content regularly.

---

## Privacy

Protect personal information.

Follow applicable privacy regulations.

Log only what is operationally necessary.

---

## Testing

Verify:

- logs generated;
- traces propagated;
- metrics collected;
- health endpoints;
- alert rules.

Observability should be continuously validated.

---

## AI Decision Matrix

Always observe:

✓ HTTP requests

✓ Background jobs

✓ External API calls

✓ Database queries

✓ Cache operations

✓ Security events

Do **not** log:

✗ Passwords

✗ Tokens

✗ Secrets

✗ Sensitive personal data

---

## AI Execution Checklist

## Investigation

☐ Identify critical workflows.

☐ Review telemetry requirements.

☐ Review compliance requirements.

☐ Review operational needs.

---

## Planning

☐ Add structured logging.

☐ Add metrics.

☐ Add tracing.

☐ Configure health checks.

---

## Verification

☐ Correlation IDs propagated.

☐ Logs structured.

☐ Metrics collected.

☐ Traces complete.

☐ Sensitive data excluded.

☐ Dashboards available.

---

## Examples

**Good Example** — structured logs, a correlation id, and metrics that answer questions

```ts
// One logger configuration; every log line is a parseable object with context.
export const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  redact: ['req.headers.authorization', 'req.headers.cookie', '*.password'],
  formatters: { level: (label) => ({ level: label }) },
});

@Injectable()
export class OrdersService {
  async place(command: PlaceOrder): Promise<Order> {
    const { correlationId } = requestContext.getStore() ?? {};

    logger.info({ event: 'order.place.started', correlationId, userId: command.userId });

    try {
      const order = await this.orders.create(command);
      // The same correlation id appears on the HTTP access log, this line, the
      // queue job it enqueues, and the downstream service's logs.
      logger.info({ event: 'order.place.succeeded', correlationId, orderId: order.id });
      return order;
    } catch (err) {
      logger.error({ event: 'order.place.failed', correlationId, err });
      throw err;
    }
  }
}
```

```ts
// A health endpoint that checks dependencies, not just that the process is alive.
@Controller('health')
export class HealthController {
  constructor(
    private readonly health: HealthCheckService,
    private readonly db: TypeOrmHealthIndicator,
    private readonly memory: MemoryHealthIndicator,
  ) {}

  @Get('ready')
  @HealthCheck()
  readiness() {
    return this.health.check([
      () => this.db.pingCheck('database', { timeout: 1_000 }),
      () => this.memory.checkHeap('heap', 512 * 1024 * 1024),
    ]);
  }
}
```

**Bad Example** — free-text logs, no identifiers, a health check that always passes

```ts
@Injectable()
export class OrdersService {
  async place(command: PlaceOrder) {
    // Unstructured and unsearchable: no field to filter on, no id to join across
    // services, and the values are interpolated so they cannot be indexed.
    console.log('placing order for ' + command.userId + ' sku ' + command.sku);

    try {
      return await this.orders.create(command);
    } catch (e) {
      // The error is logged with no context and then swallowed, so the caller
      // sees success and the metric shows no failure.
      console.log('error!', e);
      return null;
    }
  }
}

@Controller('health')
export class HealthController {
  // Returns 200 while the database is unreachable, so the orchestrator keeps
  // routing traffic to an instance that cannot serve a single request.
  @Get()
  check() {
    return { status: 'ok' };
  }
}
```

---

## Common Mistakes

Avoid:

Logging secrets.

Using inconsistent log formats.

Ignoring distributed tracing.

Missing correlation IDs.

Creating excessive metric cardinality.

Logging every debug event in production.

Treating observability as optional.

---

## Completion Criteria

Observability is complete when:

- structured logs are available;
- metrics cover critical services;
- distributed tracing is implemented;
- health checks reflect application readiness;
- alerts detect operational failures;
- production incidents can be investigated without code changes.

---

## Summary

Observability provides visibility into the runtime behavior of an application.

By combining structured logging, metrics, distributed tracing, health monitoring, and actionable alerts, engineering teams can operate production systems with confidence, detect failures early, and diagnose incidents efficiently.

## Related

- `knowledge/nestjs/10-interceptors.md`
- `knowledge/nestjs/29-maintenance.md`
- `knowledge/architecture/18-observability.md`
- `knowledge/nodejs/17-logging.md`
