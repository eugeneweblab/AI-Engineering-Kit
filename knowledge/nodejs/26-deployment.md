---
id: nodejs/26-deployment
topic: nodejs
slug: deployment
title: "Deployment"
type: doc
order: 26
status: ready
tags: [nodejs, deployment]
related: [nodejs/13-cluster, nodejs/14-environment, nodejs/15-configuration, nodejs/27-monitoring, nodejs/29-tooling]
when_to_use: "Read before containerizing, shipping, or scaling a Node.js service to production."
---
# Deployment

## Purpose

This document defines how to package and run a Node.js application in production:
containers, process management, graceful lifecycle, scaling, and safe rollout. It is
written so an agent can ship a service that starts fast, survives restarts, and can be
scaled and rolled back without dropping traffic.

Deployment is everything between "the code passes tests" and "users are served." The code
being correct is necessary but not sufficient; how the process starts, stops, and
multiplies decides whether a deploy is invisible or an outage.

## Why It Matters

Node.js is single-threaded per process, so a naive deployment uses one core of a
many-core machine and blocks all users when one request hangs. A deploy that kills the old
process without draining connections returns errors to every in-flight request. Baking
secrets or `NODE_ENV=development` into the image leaks credentials and ships debug behavior
to production. The failures here are operational, not logical — the app "works" in every
test and still drops requests on every release. Deployment discipline is what makes
releases boring.

## Core Principles

- **Build once, promote the same artifact.** The image tested in staging is the image that
  runs in production. Rebuilding per environment reintroduces "works on my machine."
- **Configuration comes from the environment, never the image.** Secrets and per-environment
  values are injected at runtime (see [configuration](15-configuration.md) and
  [environment](14-environment.md)); no secret is ever baked into a layer.
- **The process must start and stop cleanly.** Respond to `SIGTERM` by draining, not dying —
  finish in-flight requests, then exit. A dirty stop drops traffic on every deploy.
- **Scale out, stay stateless.** Run one Node process per core and multiple replicas; keep
  no session or cache in process memory so any replica serves any request.
- **Roll out gradually and reversibly.** Health-gated rolling or blue-green deploys with a
  fast rollback beat a big-bang cutover you cannot undo.

## Best Practices

- Pin the Node version (`.nvmrc` / `engines` / a specific base image tag like
  `node:22.14.0-slim`), never `node:latest` — reproducibility over convenience.
- Use a multi-stage Docker build: install and build in a builder stage, copy only
  production `node_modules` (`npm ci --omit=dev`) and build output into a slim runtime image.
- Run as a non-root user, set `NODE_ENV=production`, and start `node server.js` directly
  (or via a proper init like `tini`) — not `npm start`, which swallows signals.
- Implement graceful shutdown: on `SIGTERM`, stop accepting new connections, finish
  in-flight work, close DB pools, then `process.exit(0)` within a deadline.
- Scale with the platform's orchestrator (Kubernetes, ECS) or [`cluster`](13-cluster.md)
  for a single host; do not put CPU-bound work on one process and call it done.
- Expose `/health` (liveness) and `/ready` (readiness) so the orchestrator only routes to
  instances that can actually serve.
- Keep `package-lock.json` in the repo and use `npm ci` in CI/CD for deterministic installs.
- Set container CPU/memory limits and align `--max-old-space-size` with the memory limit so
  the process is not OOM-killed without warning.

## Examples

**Good Example** — slim multi-stage image, non-root, graceful shutdown

```dockerfile
# Builder: full toolchain, dev deps, compile.
FROM node:22.14.0-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci                       # deterministic install from the lockfile
COPY . .
RUN npm run build

# Runtime: minimal, prod-only deps, unprivileged user.
FROM node:22.14.0-slim
ENV NODE_ENV=production
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev            # no dev deps in the shipped image
COPY --from=build /app/dist ./dist
USER node                        # never run as root
CMD ["node", "dist/server.js"]   # exec form: the process receives SIGTERM directly
```

```ts
// Drain instead of dying: finish in-flight requests, then exit.
process.on("SIGTERM", async () => {
  server.close(async () => {     // stop accepting new connections
    await db.end();              // release pooled resources
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 10_000).unref(); // hard cap so a stuck close can't hang forever
});
```

**Bad Example** — fat image, root, signal-swallowing start, secrets baked in

```dockerfile
FROM node:latest              # unpinned: today's "latest" is not tomorrow's
WORKDIR /app
COPY . .                      # copies .env, secrets, node_modules, .git into the image
RUN npm install               # non-deterministic; installs dev deps into production
ENV DATABASE_PASSWORD=hunter2 # secret baked into an image layer, readable by anyone
CMD ["npm", "start"]          # npm eats SIGTERM → no graceful shutdown, dropped requests
```

## Common Mistakes

- Using `node:latest` or an unpinned base, so a rebuild silently changes the runtime.
- Baking secrets or `.env` files into the image instead of injecting at runtime.
- Starting with `npm start`, which does not forward `SIGTERM`, so shutdown is a hard kill.
- No graceful drain, dropping in-flight requests on every deploy and scale-down.
- Running one process on a multi-core box, leaving throughput (and users) on the floor.
- Keeping session/cache state in process memory, breaking horizontal scaling.
- No readiness gate, so traffic routes to an instance still connecting to its database.

## Production Tips

- Configure liveness vs. readiness distinctly: liveness restarts a hung process; readiness
  pulls a warming-up process out of rotation without killing it.
- Set the orchestrator's termination grace period longer than your shutdown deadline, or
  the drain is cut short.
- Emit a version/build id at startup and in a header so you can confirm which build is live
  and correlate incidents to releases ([monitoring](27-monitoring.md)).
- Automate rollback on failed health checks; a deploy you cannot instantly revert is a bet.

## AI Review Checklist

- Is the base image pinned and the build multi-stage with prod-only dependencies?
- Does the container run as non-root with `NODE_ENV=production`?
- Are secrets injected at runtime, never baked into an image layer?
- Does the process start via exec form (not `npm start`) and drain on `SIGTERM`?
- Are there distinct liveness and readiness endpoints wired to the orchestrator?
- Is the app stateless and run as multiple replicas / one process per core?
- Are installs deterministic (`npm ci` + committed lockfile) and rollback automated?

## Related

- `knowledge/nodejs/13-cluster.md`
- `knowledge/nodejs/14-environment.md`
- `knowledge/nodejs/15-configuration.md`
- `knowledge/nodejs/27-monitoring.md`
- `knowledge/nodejs/29-tooling.md`
