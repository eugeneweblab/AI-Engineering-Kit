---
id: nestjs/29-maintenance
topic: nestjs
slug: maintenance
title: "NestJS Maintenance"
type: doc
order: 29
status: ready
tags: [nestjs, maintenance, Controller, Header, UseInterceptors, Param, Injectable, findAll]
related: [nestjs/28-deployment, nestjs/24-observability, nestjs/25-testing]
when_to_use: "Read when maintaining, upgrading, or managing technical debt in a NestJS application after deployment."
---
# NestJS Maintenance

## Purpose

This document defines the engineering standards for maintaining NestJS applications throughout their operational lifecycle.

The objective is to ensure applications remain reliable, secure, maintainable, and adaptable as requirements, technologies, and business priorities evolve.

Maintenance begins after deployment.

It is a continuous engineering activity.

---

## Core Principle

Every production system is expected to evolve.

Design applications so they can be safely modified over time.

---

## Maintenance Goals

Every application should support:

- long-term maintainability;
- predictable upgrades;
- continuous improvement;
- operational stability;
- technical debt management;
- knowledge sharing.

Maintenance should be proactive rather than reactive.

---

## Maintenance Lifecycle

```
Deploy

↓

Monitor

↓

Detect Issues

↓

Analyze

↓

Improve

↓

Deploy
```

Maintenance is an iterative process.

---

## Version Management

Track:

- application versions;
- API versions;
- dependency versions;
- database schema versions;
- infrastructure versions.

Version history should be traceable.

---

## Dependency Management

Review dependencies regularly.

Monitor for:

- security vulnerabilities;
- deprecated packages;
- breaking changes;
- abandoned projects.

Prefer frequent small updates over infrequent major upgrades.

---

## API Evolution

APIs should evolve without unnecessarily breaking clients.

Prefer:

- backward compatibility;
- explicit versioning;
- gradual deprecation.

Breaking changes should be planned.

NestJS has first-class API versioning. Enable it once during bootstrap, then run
`v1` and `v2` side by side so existing clients keep working while new clients
adopt the improved contract.

```ts
// main.ts
import { NestFactory } from '@nestjs/core';
import { VersioningType } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Routes become /v1/users, /v2/users, ...
  app.enableVersioning({
    type: VersioningType.URI,
    defaultVersion: '1',
  });

  await app.listen(3000);
}
bootstrap();
```

```ts
// users.controller.ts
import { Controller, Get, Version } from '@nestjs/common';
import { UsersService } from './users.service';

@Controller({ path: 'users', version: '1' })
export class UsersControllerV1 {
  constructor(private readonly users: UsersService) {}

  // GET /v1/users -> stable legacy shape, kept for existing clients
  @Get()
  findAll() {
    return this.users.findAllLegacy();
  }
}

@Controller({ path: 'users', version: '2' })
export class UsersControllerV2 {
  constructor(private readonly users: UsersService) {}

  // GET /v2/users -> new paginated shape
  @Get()
  findAll() {
    return this.users.findAllPaginated();
  }
}
```

A single method can also opt into multiple versions with `@Version(['1', '2'])`
when the behavior is genuinely shared, avoiding duplicated handlers.

---

## Deprecation Policy

Every deprecated feature should define:

- announcement date;
- replacement;
- migration guide;
- removal date.

Deprecation should never surprise consumers.

Signal deprecation in-band so clients can detect it programmatically. The
standard mechanism is the `Deprecation` and `Sunset` HTTP headers (RFC 8594)
plus a `Link` to the migration guide. Encapsulate this in an interceptor rather
than sprinkling `res.setHeader` calls through controllers.

**Good — deprecation is announced through headers and documented:**

```ts
// deprecation.interceptor.ts
import {
  CallHandler,
  ExecutionContext,
  Injectable,
  NestInterceptor,
} from '@nestjs/common';
import { Response } from 'express';
import { Observable } from 'rxjs';

@Injectable()
export class DeprecationInterceptor implements NestInterceptor {
  constructor(
    private readonly sunset: string, // e.g. 'Wed, 31 Dec 2026 23:59:59 GMT'
    private readonly migrationUrl: string,
  ) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const res = context.switchToHttp().getResponse<Response>();
    res.setHeader('Deprecation', 'true');
    res.setHeader('Sunset', this.sunset);
    res.setHeader('Link', `<${this.migrationUrl}>; rel="deprecation"`);
    return next.handle();
  }
}
```

```ts
// legacy-reports.controller.ts
import { Controller, Get, UseInterceptors } from '@nestjs/common';
import { DeprecationInterceptor } from './deprecation.interceptor';

@Controller({ path: 'reports', version: '1' })
@UseInterceptors(
  new DeprecationInterceptor(
    'Wed, 31 Dec 2026 23:59:59 GMT',
    'https://docs.example.com/migrations/reports-v2',
  ),
)
export class LegacyReportsController {
  @Get()
  findAll() {
    return { data: [] };
  }
}
```

**Bad — the endpoint is simply deleted, breaking clients with no warning:**

```ts
// The v1 handler is removed in a patch release. Clients that still call
// GET /v1/reports now get 404s with no Deprecation header, no Sunset date,
// and no migration path. This is exactly the surprise the policy forbids.
@Controller({ path: 'reports', version: '1' })
export class LegacyReportsController {}
```

---

## Technical Debt

Technical debt should be:

- documented;
- prioritized;
- measurable;
- reviewed regularly.

Ignoring technical debt increases long-term costs.

---

## Refactoring

Refactor to improve:

- readability;
- maintainability;
- architecture;
- performance;
- testability.

Refactoring should preserve observable behavior.

---

## Architecture Decision Records (ADR)

Significant architectural decisions should be documented.

Each ADR should explain:

- context;
- decision;
- alternatives considered;
- consequences.

Architecture knowledge should survive team changes.

---

## Runbooks

Create runbooks for common operational tasks.

Examples:

- service restart;
- database recovery;
- cache invalidation;
- queue recovery;
- incident response.

Runbooks reduce operational uncertainty.

---

## Incident Management

Every significant incident should include:

- timeline;
- root cause;
- impact;
- corrective actions;
- preventive actions.

Focus on learning rather than blame.

---

## Postmortems

Conduct postmortems after major incidents.

A postmortem should answer:

- What happened?
- Why did it happen?
- How was it detected?
- How can recurrence be prevented?

Postmortems should improve systems and processes.

---

## SLI, SLO and SLA

Define service quality objectives.

Examples:

SLI (Service Level Indicator)

- request latency;
- availability;
- error rate.

SLO (Service Level Objective)

- 99.9% availability;
- p95 latency below 250 ms.

SLA (Service Level Agreement)

External commitment to customers.

Operational goals should be measurable.

---

## Monitoring Reviews

Review periodically:

- alerts;
- dashboards;
- log quality;
- tracing coverage;
- capacity trends.

Monitoring should evolve with the application.

---

## Capacity Planning

Forecast future resource requirements.

Review:

- CPU usage;
- memory usage;
- storage growth;
- database growth;
- traffic trends.

Scale before capacity becomes a problem.

---

## Backup Strategy

Verify:

- backup frequency;
- retention policy;
- restore procedures;
- recovery time.

Backups that cannot be restored are ineffective.

---

## Disaster Recovery

Prepare for:

- infrastructure failure;
- database corruption;
- regional outages;
- credential compromise.

Recovery procedures should be tested regularly.

Safe recovery and zero-downtime rolling deploys both depend on the application
shutting down cleanly: draining in-flight requests, closing database pools, and
disconnecting from brokers before the process exits. NestJS exposes lifecycle
hooks for this, but they only fire when shutdown hooks are explicitly enabled.

```ts
// main.ts
const app = await NestFactory.create(AppModule);

// Required — without this, OnApplicationShutdown never runs on SIGTERM/SIGINT.
app.enableShutdownHooks();

await app.listen(3000);
```

```ts
// database.service.ts
import { Injectable, Logger, OnApplicationShutdown } from '@nestjs/common';
import { DataSource } from 'typeorm';

@Injectable()
export class DatabaseService implements OnApplicationShutdown {
  private readonly logger = new Logger(DatabaseService.name);

  constructor(private readonly dataSource: DataSource) {}

  async onApplicationShutdown(signal?: string): Promise<void> {
    this.logger.log(`Shutting down on ${signal}; closing DB connections`);
    if (this.dataSource.isInitialized) {
      await this.dataSource.destroy();
    }
  }
}
```

The orchestrator (Kubernetes, systemd, etc.) sends `SIGTERM`; the hook receives
the signal name so cleanup can be logged and correlated during an incident.

---

## Documentation

Documentation should remain current.

Review:

- architecture;
- APIs;
- deployment;
- operational procedures;
- onboarding guides.

Outdated documentation reduces engineering efficiency.

---

## Knowledge Sharing

Encourage:

- code reviews;
- architecture discussions;
- technical documentation;
- internal workshops.

Knowledge should not depend on individuals.

---

## Security Maintenance

Review regularly:

- access permissions;
- secrets;
- certificates;
- dependencies;
- audit logs.

Security maintenance is continuous.

---

## Testing

Maintenance activities should preserve:

- automated testing;
- integration testing;
- deployment verification;
- rollback validation.

Refactoring without testing increases risk.

---

## AI Decision Matrix

Maintain continuously:

✓ Dependencies

✓ Documentation

✓ Monitoring

✓ Technical debt

✓ Security

✓ Backups

Do **not** ignore:

✗ Deprecated APIs

✗ Failing alerts

✗ Outdated documentation

✗ Growing technical debt

---

## AI Execution Checklist

## Investigation

☐ Review application health.

☐ Review dependencies.

☐ Review technical debt.

☐ Review operational metrics.

---

## Planning

☐ Prioritize improvements.

☐ Schedule upgrades.

☐ Update documentation.

☐ Review architecture decisions.

---

## Verification

☐ Monitoring current.

☐ Documentation updated.

☐ Dependencies supported.

☐ Technical debt reviewed.

☐ Backups verified.

☐ Recovery procedures tested.

---

## Examples

**Good Example** — deprecate on a schedule, with the data to know when it is safe

```ts
@Controller({ path: 'orders', version: '1' })
export class OrdersV1Controller {
  constructor(private readonly orders: OrdersService, private readonly metrics: MetricsService) {}

  @Get(':id')
  @Header('Deprecation', 'true')
  @Header('Sunset', 'Wed, 01 Oct 2026 00:00:00 GMT')
  @Header('Link', '</v2/orders>; rel="successor-version"')
  async findOne(@Param('id') id: string, @Req() req: Request) {
    // Count who is still on v1, by client. Removal becomes a decision with
    // evidence rather than a guess.
    this.metrics.increment('api.deprecated.v1', {
      route: 'orders.findOne',
      client: (req.headers['x-client-id'] as string) ?? 'unknown',
    });

    return OrderResponseV1Dto.from(await this.orders.findById(id));
  }
}
```

```json
{
  "scripts": {
    "deps:check": "npm outdated && npm audit --audit-level=high",
    "deps:update": "npx npm-check-updates --target minor -u && npm install && npm test"
  }
}
```

**Bad Example** — the endpoint removed without notice, dependencies frozen

```ts
// v1 deleted in the same release that shipped v2. Every client that had not
// migrated started receiving 404s in production, with no deprecation window
// and no metric that would have shown who was still calling it.
@Controller({ path: 'orders', version: '2' })
export class OrdersController {
  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.orders.findById(id);
  }
}
```

```json
{
  "dependencies": {
    "@nestjs/core": "9.0.0",
    "typeorm": "0.2.45"
  }
}
```

Pinned to exact versions and never updated, the project accumulates two major versions of
debt. The eventual upgrade is a multi-week project rather than a weekly ten-minute one, and
security advisories in between go unpatched.

---

## Common Mistakes

Avoid:

Ignoring technical debt.

Skipping dependency updates.

Keeping obsolete documentation.

Operating without runbooks.

Performing blame-oriented postmortems.

Neglecting backup testing.

Treating maintenance as optional.

---

## Completion Criteria

Maintenance processes are complete when:

- dependencies are regularly updated;
- documentation remains accurate;
- operational procedures are documented;
- technical debt is actively managed;
- incidents produce actionable improvements;
- recovery procedures are tested.

---

## Summary

Maintenance ensures software remains reliable, secure, and adaptable throughout its lifecycle.

By continuously improving architecture, managing technical debt, updating dependencies, documenting operational knowledge, and validating recovery processes, engineering teams can sustain production systems for many years while minimizing operational risk.

## Related

- `knowledge/nestjs/28-deployment.md`
- `knowledge/nestjs/24-observability.md`
- `knowledge/nestjs/25-testing.md`
