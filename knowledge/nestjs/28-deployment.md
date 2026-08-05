---
id: nestjs/28-deployment
topic: nestjs
slug: deployment
title: "NestJS Deployment"
type: doc
order: 28
status: ready
tags: [nestjs, deployment, HealthCheck, Controller, enableShutdownHooks, TypeOrmHealthIndicator, OnApplicationShutdown, HealthController]
related: [nestjs/14-configuration, nestjs/29-maintenance, docker/11-multi-stage-builds, cicd/10-deployment]
when_to_use: "Read before setting up or reviewing build, containerization, CI/CD, or release processes for a NestJS application."
---
# NestJS Deployment

## Purpose

This document defines the engineering standards for deploying NestJS applications into production environments.

The objective is to ensure deployments are predictable, repeatable, observable, secure, and reversible while minimizing downtime and operational risk.

Deployment is an engineering process.

It should never depend on manual steps.

---

## Core Principle

Every deployment should be:

- automated;
- repeatable;
- observable;
- reversible.

Manual production changes should be avoided whenever possible.

---

## Deployment Goals

Every deployment pipeline should provide:

- reproducibility;
- consistency;
- security;
- rollback capability;
- deployment visibility;
- minimal downtime.

Deployments should produce identical results regardless of who initiates them.

---

## Deployment Lifecycle

```
Developer

↓

Commit

↓

CI

↓

Build

↓

Automated Tests

↓

Security Scans

↓

Artifact

↓

CD

↓

Staging

↓

Production
```

Every deployment should follow the same pipeline.

---

## Build Artifacts

Applications should be built once.

The same immutable artifact should be promoted through:

- Development
- Testing
- Staging
- Production

Avoid rebuilding the application for each environment.

---

## Infrastructure

Infrastructure should be defined as code.

Examples:

- Terraform
- Pulumi
- CloudFormation

Infrastructure changes should follow the same review process as application code.

---

## Containers

Prefer containerized deployments.

Containers should be:

- immutable;
- minimal;
- reproducible;
- versioned.

Avoid installing unnecessary software inside runtime images.

---

## Docker Images

Images should:

- use official base images when practical;
- minimize attack surface;
- avoid running as root;
- pin dependency versions;
- include only runtime dependencies.

Smaller images deploy faster and reduce security risks.

A multi-stage build for a NestJS application compiles TypeScript in a throwaway
build stage, installs only production dependencies in a separate stage, and
copies just `dist/` and `node_modules` into a minimal runtime image. The image
is built once and promoted unchanged through every environment.

```dockerfile
# ---- build stage: compile TypeScript to dist/ ----
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci                      # reproducible install pinned by package-lock.json
COPY . .
RUN npm run build               # runs `nest build` -> dist/main.js

# ---- deps stage: runtime dependencies only ----
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev           # no devDependencies in the runtime image

# ---- runtime stage: minimal, non-root ----
FROM node:22-alpine AS runtime
ENV NODE_ENV=production
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json ./
USER node                       # never run the application as root
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

Run the compiled entrypoint directly with `node dist/main.js`. Do not ship
`nest start`, `ts-node`, or the Nest CLI into the runtime image.

---

## Environment Configuration

Separate configuration from code.

Configuration includes:

- database connections;
- API endpoints;
- feature flags;
- secrets;
- logging levels.

Never hardcode environment-specific values.

---

## Secrets

Secrets should be injected securely during deployment.

Never:

- commit secrets;
- bake secrets into images;
- expose secrets in logs.

Rotate secrets regularly.

---

## Database Migrations

Migration strategy should be defined before deployment.

Typical order:

```
Deploy Application

↓

Run Safe Migration

↓

Verify

↓

Enable Feature
```

Backward-compatible migrations reduce deployment risk.

---

## Blue-Green Deployment

Maintain two production environments.

```
Blue

↓

Green

↓

Switch Traffic
```

Rollback becomes immediate.

---

## Canary Deployment

Gradually expose new versions.

Example:

```
5%

↓

20%

↓

50%

↓

100%
```

Monitor system behavior before full rollout.

---

## Rolling Deployment

Replace instances incrementally.

Benefits:

- minimal downtime;
- controlled rollout;
- continuous availability.

Monitor each deployment stage.

Rolling, blue-green, and canary strategies all send `SIGTERM` to the outgoing
instances. Without graceful shutdown, the process exits immediately and drops
in-flight requests, unfinished jobs, and open connections. Call
`enableShutdownHooks()` so NestJS routes `SIGTERM`/`SIGINT` through its
lifecycle: built-in modules (TypeORM, BullMQ, Terminus) drain automatically, and
your own providers can implement `OnApplicationShutdown` for custom resources.

```ts
// main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // BAD (omitting this): SIGTERM kills the process instantly during a rolling
  // deploy, aborting active requests and leaking connections.
  // GOOD: wire OS signals into Nest's shutdown lifecycle so providers drain.
  app.enableShutdownHooks();

  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
```

```ts
// metrics/metrics-flusher.service.ts
import {
  Injectable,
  OnApplicationBootstrap,
  OnApplicationShutdown,
} from '@nestjs/common';

@Injectable()
export class MetricsFlusher
  implements OnApplicationBootstrap, OnApplicationShutdown
{
  private timer?: NodeJS.Timeout;

  onApplicationBootstrap(): void {
    this.timer = setInterval(() => this.flush(), 5000);
  }

  // Runs after enableShutdownHooks() receives the signal, before the process
  // exits. Stop background work and flush once more so nothing buffered is lost.
  async onApplicationShutdown(signal?: string): Promise<void> {
    if (this.timer) {
      clearInterval(this.timer);
    }
    await this.flush();
  }

  private async flush(): Promise<void> {
    // push buffered metrics to the collector
  }
}
```

---

## Rollback

Every deployment must define a rollback strategy.

Rollback should be:

- tested;
- automated;
- documented.

Recovery should not depend on manual debugging.

---

## Health Checks

Verify:

- application startup;
- database connectivity;
- cache connectivity;
- queue connectivity.

Traffic should reach only healthy instances.

NestJS exposes health endpoints through `@nestjs/terminus`. Separate
**liveness** (is the process alive? — a failure tells the orchestrator to
restart the pod) from **readiness** (can it serve traffic? — a failure tells the
load balancer to stop routing to this instance). Liveness must stay cheap and
must not call downstream dependencies; readiness is where you verify them.

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

  // Liveness: process-local only. Restarting fixes it; a DB outage must not.
  @Get('live')
  @HealthCheck()
  liveness() {
    return this.health.check([
      () => this.memory.checkHeap('memory_heap', 300 * 1024 * 1024),
    ]);
  }

  // Readiness: verify dependencies. Failing here drains traffic, not the pod.
  @Get('ready')
  @HealthCheck()
  readiness() {
    return this.health.check([
      () => this.db.pingCheck('database', { timeout: 1500 }),
    ]);
  }
}
```

```ts
// health/health.module.ts
import { Module } from '@nestjs/common';
import { TerminusModule } from '@nestjs/terminus';
import { HealthController } from './health.controller';

@Module({
  imports: [TerminusModule], // TypeOrmModule must be available for TypeOrmHealthIndicator
  controllers: [HealthController],
})
export class HealthModule {}
```

Point the orchestrator's liveness probe at `/health/live` and its readiness
probe at `/health/ready`.

---

## CI/CD

Deployment pipelines should include:

- linting;
- testing;
- security scanning;
- dependency scanning;
- artifact creation;
- deployment verification.

No production deployment should bypass CI/CD.

---

## Feature Flags

Separate deployment from feature release.

Feature flags allow:

- gradual rollout;
- experimentation;
- emergency disablement.

Deploying code should not automatically expose new functionality.

---

## Versioning

Every deployment should include:

- application version;
- Git commit hash;
- build identifier;
- deployment timestamp.

Production systems should always identify the running version.

Inject build metadata as environment variables at build time (from CI: the Git
SHA, semantic version, build id) and expose them through a small controller so
any running instance can report exactly which artifact it is. Read them through
`ConfigService`, never `process.env` scattered across the codebase.

```ts
// info/info.controller.ts
import { Controller, Get } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Controller('info')
export class InfoController {
  // captured once when the module is instantiated, i.e. at process start
  private static readonly startedAt = new Date().toISOString();

  constructor(private readonly config: ConfigService) {}

  @Get()
  version() {
    return {
      version: this.config.get<string>('APP_VERSION', '0.0.0'),
      commit: this.config.get<string>('GIT_SHA', 'unknown'),
      buildId: this.config.get<string>('BUILD_ID', 'unknown'),
      startedAt: InfoController.startedAt,
    };
  }
}
```

A `GET /info` response now uniquely identifies the deployed build, which makes
rollbacks and incident triage unambiguous.

---

## Monitoring

Monitor immediately after deployment.

Review:

- error rate;
- response latency;
- CPU usage;
- memory usage;
- queue health;
- deployment success.

Deployments should remain observable.

---

## Security

Verify:

- signed artifacts where applicable;
- dependency integrity;
- image vulnerabilities;
- secret handling.

Deployment pipelines are part of the application's security boundary.

---

## Disaster Recovery

Prepare procedures for:

- failed deployments;
- infrastructure outages;
- database failures;
- accidental rollbacks.

Recovery procedures should be rehearsed regularly.

---

## Documentation

Every deployment process should document:

- prerequisites;
- deployment steps;
- rollback procedure;
- migration strategy;
- verification checklist.

Documentation should remain current.

---

## Testing

Verify:

- deployment automation;
- rollback;
- migrations;
- startup health;
- feature flags;
- monitoring integration.

Deployment procedures should be validated before production use.

---

## AI Decision Matrix

Always automate:

✓ Build

✓ Testing

✓ Security checks

✓ Deployment

✓ Rollback

Never rely on:

✗ Manual production edits

✗ Environment-specific code

✗ Undocumented deployment steps

✗ Unverified releases

---

## AI Execution Checklist

## Investigation

☐ Review deployment pipeline.

☐ Review infrastructure.

☐ Review migration strategy.

☐ Review rollback process.

---

## Planning

☐ Build immutable artifact.

☐ Configure environment.

☐ Automate deployment.

☐ Enable monitoring.

---

## Verification

☐ Tests passed.

☐ Security checks completed.

☐ Health checks passed.

☐ Rollback available.

☐ Deployment observable.

☐ Version recorded.

---

## Examples

**Good Example** — a small image, a non-root user, and probes that mean something

```dockerfile
# Build stage: dev dependencies and the compiler stay here.
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --omit=dev

# Runtime stage: production dependencies and compiled output only.
FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist

USER node
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

```ts
// main.ts — shut down cleanly so in-flight requests finish and the pool closes.
const app = await NestFactory.create(AppModule);
app.enableShutdownHooks();            // SIGTERM triggers onModuleDestroy
await app.listen(process.env.PORT ?? 3000);
```

```yaml
readinessProbe:
  httpGet: { path: /health/ready, port: 3000 }   # checks the database
  periodSeconds: 5
livenessProbe:
  httpGet: { path: /health/live, port: 3000 }    # process is responsive
  periodSeconds: 10
  failureThreshold: 3
```

**Bad Example** — the build image shipped, running as root, no graceful shutdown

```dockerfile
FROM node:latest                 # floating tag: the build is not reproducible
WORKDIR /app
COPY . .                         # includes .git, tests, and node_modules from the host
RUN npm install                  # dev dependencies in the runtime image

# Secrets baked into a layer, readable by anyone who can pull the image.
ENV DATABASE_URL=postgres://app:hunter2@db:5432/app

# Runs as root, and npm swallows SIGTERM so the container is killed after the
# grace period with requests still in flight.
CMD ["npm", "run", "start:prod"]
```

---

## Common Mistakes

Avoid:

Manual production deployments.

Embedding secrets in images.

Skipping rollback planning.

Running untested migrations.

Deploying without monitoring.

Rebuilding artifacts for every environment.

Ignoring deployment verification.

---

## Completion Criteria

Deployment is complete when:

- the pipeline is fully automated;
- artifacts are immutable;
- infrastructure is reproducible;
- rollback is documented and tested;
- monitoring verifies deployment health;
- production releases are repeatable and observable.

---

## Summary

Deployment is the controlled delivery of software into production.

By automating the entire deployment pipeline, separating configuration from code, treating infrastructure as code, validating every release, and preparing reliable rollback strategies, NestJS applications can be deployed safely, consistently, and with minimal operational risk.

## Related

- `knowledge/nestjs/14-configuration.md`
- `knowledge/nestjs/29-maintenance.md`
- `knowledge/docker/11-multi-stage-builds.md`
- `knowledge/cicd/10-deployment.md`
