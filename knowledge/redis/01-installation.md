---
id: redis/01-installation
topic: redis
slug: installation
title: "Redis Installation"
type: doc
order: 1
status: ready
tags: [redis, installation]
related: [redis/00-overview, redis/21-security, redis/24-testing, redis/27-production, redis/20-persistence]
when_to_use: "Read before installing, containerizing, or connecting a client to Redis in dev, CI, or production."
---
# Redis Installation

## Purpose

This document defines how to run Redis and connect to it correctly across environments:
local development, CI, containers, and production. It covers version selection, a
secure-by-default configuration, and connecting a client without the mistakes that
turn a fresh install into an open door or a flaky test suite.

## Why It Matters

Redis ships with defaults tuned for a trusted local machine, not the internet. A Redis
bound to `0.0.0.0` with no password has been the root cause of countless data
breaches and crypto-mining incidents, because an unauthenticated Redis lets an attacker
run arbitrary commands and, via `CONFIG` and modules, sometimes the host. Installation
is where security, persistence, and resource limits are decided; getting it wrong here
is expensive to fix later.

## Core Principles

- **Pin a version.** Redis 7.x is the current stable line as of 2026. Never depend on
  "latest" in production or CI — behavior and defaults change across majors.
- **Bind and authenticate before exposing.** Redis must not accept remote connections
  until it requires a password (or ACL) and TLS. See [Security](21-security.md).
- **One connection model per process.** Use a client-managed connection pool; do not
  open a new connection per request. Connections are a finite server resource.
- **Match the environment to its job.** Ephemeral in-memory for tests, a real instance
  for staging, replicated/persistent for production.

## Best Practices

- Run Redis in Docker for reproducible dev and CI; run a managed service (or a hardened,
  replicated deployment) in production.
- Set `maxmemory` and a `maxmemory-policy` (e.g. `allkeys-lru` for a pure cache,
  `noeviction` when data loss is unacceptable) so Redis fails predictably instead of
  consuming the host.
- Require authentication in every non-throwaway environment: `requirepass` or ACL users.
- Health-check the connection at startup with `PING` and fail fast if Redis is
  unreachable — silent lazy connections hide misconfiguration until first use.
- Use a single shared client instance in the application; the client owns the pool.

## Examples

**Good Example** — reproducible, authenticated, resource-bounded container

```yaml
# docker-compose.yml — dev/CI Redis with sane, safe defaults
services:
  redis:
    image: redis:7.4          # pinned major.minor, not "latest"
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}   # auth on, even in dev
      --maxmemory 256mb                 # bounded so it can't eat the host
      --maxmemory-policy allkeys-lru    # cache semantics: evict, don't OOM
      --appendonly yes                  # AOF persistence for durability
    ports:
      - "127.0.0.1:6379:6379"           # loopback only — never 0.0.0.0
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 5s
```

```ts
// Client: one shared, pooled instance with an explicit connection check.
import { createClient } from "redis";

export const redis = createClient({ url: process.env.REDIS_URL }); // redis://:pw@host:6379
redis.on("error", (e) => logger.error({ err: e }, "redis client error"));
await redis.connect();
await redis.ping(); // fail fast at boot, not on the first user request
```

**Bad Example** — exposed, unauthenticated, unbounded

```yaml
services:
  redis:
    image: redis:latest       # unpinned — defaults drift between deploys
    ports:
      - "6379:6379"           # binds 0.0.0.0 → reachable from the internet
    # no requirepass  → any client can run FLUSHALL / CONFIG SET
    # no maxmemory    → grows until the host OOM-kills it
```

```ts
// A new connection per request exhausts server connection slots under load.
async function get(key: string) {
  const client = createClient({ url: process.env.REDIS_URL });
  await client.connect();       // handshake on every call
  const v = await client.get(key);
  await client.quit();
  return v;
}
```

## Common Mistakes

- Binding to `0.0.0.0` with no password "temporarily" and shipping it.
- Using the `latest` tag, then debugging a behavior change no one made.
- Opening a connection per request instead of reusing a pooled client.
- Leaving `maxmemory` unset, so a memory leak becomes a host outage.
- Running the production persistence config in tests, making them slow and flaky.
- Assuming the client connected because `createClient` didn't throw — connection is async.

## Production Tips

- Terminate client connections over TLS; put Redis on a private network with a firewall.
- Store the password/URL in a secrets manager, never in the image or `.env` committed to
  git.
- Disable or rename dangerous commands (`FLUSHALL`, `CONFIG`, `KEYS`) in production via
  ACL or `rename-command`.
- In CI, use an ephemeral container per run so tests never share state; see
  [Testing](24-testing.md).

## AI Review Checklist

- Is the Redis image/version pinned rather than `latest`?
- Is authentication (password or ACL) required in every non-throwaway environment?
- Is Redis bound to loopback or a private network, never `0.0.0.0` publicly?
- Are `maxmemory` and an eviction policy set?
- Does the app reuse one pooled client instead of connecting per request?
- Is there a startup `PING`/health check that fails fast?

## Related


- `knowledge/redis/00-overview.md`
- `knowledge/redis/21-security.md`
- `knowledge/redis/24-testing.md`
- `knowledge/redis/27-production.md`
- `knowledge/redis/20-persistence.md`
