---
id: nextjs/26-deployment
topic: nextjs
slug: deployment
title: "Next.js Deployment"
type: doc
order: 26
status: ready
tags: [nextjs, deployment, NextConfig, NextResponse, DATABASE_URL, connect, NODE_ENV]
related: [nextjs/21-environment-variables, nextjs/23-observability, nextjs/10-caching, cicd/10-deployment]
when_to_use: "Read before deploying a Next.js app to a hosting platform or production environment."
---
# Next.js Deployment

## Purpose

This document defines the engineering standards for deploying Next.js applications into production environments.

The objective is to deliver applications that are reliable, secure, reproducible, and easy to operate across different hosting platforms.

Deployment should be automated, predictable, and repeatable.

---

## Core Principle

Every deployment should be:

- reproducible;
- automated;
- observable;
- reversible.

Manual production deployments should be avoided whenever practical.

---

## Deployment Goals

Every deployment should provide:

- zero or minimal downtime;
- repeatable builds;
- environment isolation;
- automated verification;
- rapid rollback capability.

Production deployments should be routine rather than high-risk events.

---

## Deployment Workflow

Every deployment should follow a predictable pipeline.

```
Commit

↓

Pull Request

↓

Code Review

↓

Automated Tests

↓

Build

↓

Deploy

↓

Health Checks

↓

Production
```

Each step should succeed before proceeding to the next.

---

## Environments

Maintain separate environments.

Typical environments include:

- Development;
- Testing;
- Staging;
- Production.

Each environment should have an independent configuration.

---

## Build Process

Production builds should:

- execute successfully without warnings that indicate defects;
- generate optimized assets;
- validate environment variables;
- fail immediately when critical configuration is missing.

Never modify generated build artifacts manually.

For containerized or self-hosted deployments, emit a self-contained server with `output: "standalone"`. This traces only the files the server needs into `.next/standalone`, producing a small, reproducible image.

```ts
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emit a minimal, self-contained server (.next/standalone/server.js)
  // for container images. Omit on platforms that build/run for you.
  output: "standalone",
  images: {
    // Only these hosts may be optimized by next/image.
    remotePatterns: [{ protocol: "https", hostname: "cdn.example.com" }],
  },
};

export default nextConfig;
```

The standalone output does not copy `public/` or `.next/static/`; the runtime image must include them explicitly.

```dockerfile
# Dockerfile — multi-stage build for output: "standalone"
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

**Build-time vs request-time data.** Do not require runtime-only secrets during the build. A route that reads per-request state (cookies, headers, an uncached `fetch`) is rendered dynamically and will not be prerendered — that is expected. Since `fetch()` is uncached by default in Next.js 15+, a page that fetches without opting into caching stays dynamic unless every request is statically analyzable. Opt into static data explicitly when a page should be prerendered at build time:

```tsx
// app/blog/[slug]/page.tsx — cached fetch keeps this route prerenderable
export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const res = await fetch(`https://cms.example.com/posts/${slug}`, {
    // Opt in: revalidate at most once per hour (ISR).
    next: { revalidate: 3600 },
  });
  const post = await res.json();
  return <article>{post.title}</article>;
}
```

---

## Configuration

Keep deployment configuration outside application code.

Examples:

- environment variables;
- infrastructure configuration;
- secrets;
- feature flags.

Application behavior should remain configurable without code changes.

---

## Environment Variables

Use environment variables for:

- API endpoints;
- database connections;
- authentication secrets;
- third-party integrations.

Never hardcode environment-specific values.

Validate configuration once, at module load, through a centralized module. A schema that throws on import fails the build or boot immediately instead of surfacing an undefined value during a request in production.

**Good — validated, typed, fails fast:**

```ts
// config/env.ts
import { z } from "zod";

const schema = z.object({
  DATABASE_URL: z.string().url(),
  STRIPE_SECRET_KEY: z.string().min(1),
  NEXT_PUBLIC_APP_URL: z.string().url(),
});

// Throws at import time if anything is missing or malformed.
export const env = schema.parse(process.env);
```

```ts
// usage anywhere on the server
import { env } from "@/config/env";
const db = connect(env.DATABASE_URL);
```

**Bad — unvalidated access scattered across the app:**

```ts
// Silently undefined in production; the failure appears far from the cause.
const db = connect(process.env.DATABASE_URL!);
```

Only variables prefixed with `NEXT_PUBLIC_` are inlined into the client bundle at build time. Because that value is baked into the build, a public URL that differs per environment must be set before `next build`, not at container start.

---

## Secrets

Protect:

- API keys;
- database credentials;
- signing keys;
- access tokens.

Secrets should be managed by a secure secret management solution.

Never commit secrets to version control.

---

## Static Assets

Serve static assets efficiently.

Review:

- caching;
- compression;
- CDN usage;
- cache invalidation.

Static resources should be optimized before deployment.

---

## Database Migrations

Run database migrations in a controlled manner.

Verify:

- compatibility;
- rollback strategy;
- execution order.

Avoid destructive schema changes without migration planning.

---

## Health Checks

Expose health endpoints where appropriate.

Typical checks include:

- application availability;
- database connectivity;
- external service availability;
- cache connectivity.

Health checks should execute quickly.

Implement the endpoint as a Route Handler. A health check must reflect live state, so force dynamic rendering — otherwise the response could be cached and report stale health. Return `503` (not `200`) when a dependency is down so load balancers can drain the instance.

```ts
// app/health/route.ts
import { NextResponse } from "next/server";
import { checkDatabase } from "@/lib/db";

// Never cache: always evaluate dependencies at request time.
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    await checkDatabase(); // fast, lightweight probe (e.g. SELECT 1)
    return NextResponse.json({ status: "ok" }, { status: 200 });
  } catch {
    return NextResponse.json({ status: "unhealthy" }, { status: 503 });
  }
}
```

---

## Logging

Centralize production logs.

Logs should include:

- startup events;
- deployment information;
- application errors;
- unexpected failures.

Avoid logging sensitive information.

---

## Monitoring

Monitor:

- application availability;
- response time;
- error rate;
- resource usage;
- deployment success.

Production deployments should always be observable.

---

## Rollback Strategy

Every deployment should have a rollback plan.

Rollback should be:

- documented;
- tested;
- executable quickly.

Recovery should not depend on manual code modifications.

---

## Zero-Downtime Deployment

When infrastructure permits, prefer deployment strategies that avoid service interruption.

Examples:

- rolling deployment;
- blue-green deployment;
- canary deployment.

Choose the strategy appropriate for the application.

---

## CDN

Use a CDN for:

- static assets;
- optimized images;
- public downloads.

Review cache invalidation after each deployment.

To serve `/_next/static/*` from a CDN origin, set `assetPrefix`. Build-output assets are content-hashed, so they can be cached immutably; the hash changes on every build, which invalidates them automatically.

```ts
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Serve hashed build assets from the CDN; HTML still comes from the app.
  assetPrefix:
    process.env.NODE_ENV === "production" ? "https://cdn.example.com" : undefined,
};

export default nextConfig;
```

Do not front dynamic, per-user routes with a shared public CDN cache. Cache only prerendered pages and static assets.

---

## Performance Verification

After deployment verify:

- application startup;
- page rendering;
- Core Web Vitals;
- API performance;
- cache behavior.

Deployment is complete only after successful verification.

---

## Security

Verify:

- HTTPS enabled;
- security headers configured;
- secrets loaded correctly;
- debug mode disabled;
- production logging configured.

Security validation should be part of every deployment.

---

## Accessibility

Deployment should not introduce regressions affecting accessibility.

Verify:

- keyboard navigation;
- page rendering;
- accessible forms;
- focus management.

Accessibility verification belongs in release validation.

---

## AI Execution Checklist

## Investigation

☐ Review deployment target.

☐ Review environment configuration.

☐ Review migration requirements.

☐ Review monitoring.

---

## Planning

☐ Build production artifacts.

☐ Validate configuration.

☐ Execute deployment.

☐ Verify health checks.

---

## Verification

☐ Deployment successful.

☐ Health checks passed.

☐ Monitoring active.

☐ Rollback available.

☐ Performance verified.

☐ Security reviewed.

---

## Examples

**Good Example** — a standalone image, built once, configured per environment

```ts
// next.config.ts
export default {
  output: 'standalone',      // emits .next/standalone with only the used dependencies
};
```

```dockerfile
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
# standalone bundles the server and its dependencies: a fraction of the image size.
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public

USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

```yaml
# Runtime configuration is injected, so the same digest runs in every environment.
env:
  - name: DATABASE_URL
    valueFrom: { secretKeyRef: { name: app-secrets, key: database-url } }
  - name: API_URL
    value: https://api.example.com
readinessProbe:
  httpGet: { path: /api/health, port: 3000 }
```

**Bad Example** — a build per environment, with configuration compiled in

```dockerfile
FROM node:latest
WORKDIR /app
COPY . .                              # including .env.production and node_modules
RUN npm install

# Public values inlined at build time bind the artifact to one environment.
# Staging and production now run different builds, so what was tested is not
# what ships.
ENV NEXT_PUBLIC_API_URL=https://api.example.com
RUN npm run build

# Runs as root, ships the full source tree and dev dependencies, and npm
# swallows SIGTERM so in-flight requests are killed rather than drained.
CMD ["npm", "start"]
```

---

## Common Mistakes

Avoid:

Deploying directly from local machines.

Hardcoding secrets.

Skipping automated testing.

Running unverified database migrations.

Ignoring rollback planning.

Deploying without monitoring.

Leaving debug configuration enabled.

Failing to validate production configuration.

---

## Completion Criteria

A deployment process is complete when:

- builds are reproducible;
- deployments are automated;
- environments are isolated;
- health checks pass;
- monitoring is active;
- rollback procedures are available and documented.

---

## Summary

Reliable deployment is the foundation of stable software delivery.

By automating builds, protecting configuration, validating production environments, monitoring application health, and maintaining rollback procedures, Next.js applications can be deployed confidently and consistently across environments.

## Related

- `knowledge/nextjs/21-environment-variables.md`
- `knowledge/nextjs/23-observability.md`
- `knowledge/nextjs/10-caching.md`
- `knowledge/cicd/10-deployment.md`
