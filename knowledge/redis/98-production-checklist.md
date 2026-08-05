---
id: redis/98-production-checklist
topic: redis
slug: production-checklist
title: "Redis Production Checklist"
type: doc
order: 98
status: ready
tags: [redis, production-checklist]
related: [redis/20-persistence, redis/18-replication, redis/21-security, redis/22-monitoring, redis/27-production]
when_to_use: "Read before promoting any Redis instance or Redis-backed feature to production."
---
# Redis Production Checklist

## Purpose

A verifiable, grouped checklist to run before a Redis deployment carries production
traffic. Every item is a yes/no fact you can confirm from config, `INFO`, or a client.
If any box is unchecked, the deployment is not production-ready. This complements the
[engineering principles](30-engineering-principles.md) with concrete operational gates.

## Why It Matters

Redis defaults favor speed and ease of local use, not production safety: no auth, no
memory cap, weak durability, and commands that can freeze the server. Shipping the
defaults means one bad key, one open port, or one restart can take the service down or
leak data. This checklist forces each unsafe default to be an explicit, reviewed decision.

## Memory and Eviction

**Rules:** [Expiration](12-expiration.md) · [Performance](23-performance.md)

- [ ] `maxmemory` is set to a value that leaves headroom below the host's RAM.
- [ ] An eviction policy is chosen deliberately (`allkeys-lru`/`allkeys-lfu` for caches,
      `noeviction` where losing keys corrupts state) — not left at default.
- [ ] Every key class has a TTL or a documented, enforced deletion path.
- [ ] `used_memory` under peak load stays comfortably under `maxmemory` (no eviction storm).
- [ ] No single key holds an unbounded collection or a multi-megabyte value.

## Durability and Persistence

**Rules:** [Persistence](20-persistence.md)

- [ ] Persistence mode (RDB, AOF, or both) is chosen to match the recovery requirement.
- [ ] If data must survive a crash, AOF with `appendfsync everysec` (or stricter) is on.
- [ ] Redis is not the sole source of truth for data that cannot be recomputed or reloaded.
- [ ] Backups (RDB snapshots or AOF) are shipped off-box and restore has been tested.
- [ ] Restart/failover has been rehearsed and the expected data-loss window is documented.

## Availability and Scaling

**Rules:** [Replication](18-replication.md) · [Clustering](19-clustering.md)

- [ ] Replication or Cluster is configured so a single node loss is survivable.
- [ ] Automatic failover (Sentinel or Cluster) is enabled and tested, not just configured.
- [ ] Clients use a topology-aware connection (Sentinel/Cluster aware) that reconnects on
      failover.
- [ ] For Cluster: multi-key operations use hash tags so keys land on the same slot.
- [ ] Connection pool size and client timeouts are set; connections are reused, not
      opened per request.

## Security

**Rules:** [Security](21-security.md)

- [ ] Authentication is required (`requirepass` or, preferably, ACL users with least
      privilege) — never an open, no-auth instance.
- [ ] Redis is not exposed to the public internet; it binds to a private interface/VPC.
- [ ] TLS is enabled for connections crossing any untrusted network.
- [ ] Dangerous commands (`FLUSHALL`, `FLUSHDB`, `KEYS`, `CONFIG`, `DEBUG`) are renamed or
      ACL-restricted for application users.
- [ ] Credentials come from a secrets manager, not from source or committed config.

## Performance and Safety

**Rules:** [Performance](23-performance.md) · [Lua Scripting](11-lua-scripting.md)

- [ ] No code path calls `KEYS`, `FLUSHALL`, or `FLUSHDB` against production.
- [ ] `slowlog-log-slower-than` is set and the slowlog is monitored.
- [ ] Multi-command atomic logic uses Lua or `MULTI`/`WATCH`, not client round trips.
- [ ] Pipelines and Lua scripts are size-bounded so no single unit blocks the server long.
- [ ] Lazy freeing (`lazyfree-lazy-eviction`/`-expire`/`-server-del`) is enabled to avoid
      blocking on large deletes.

## Observability

**Rules:** [Monitoring](22-monitoring.md) · [Observability](28-observability.md)

- [ ] `INFO` metrics (memory, evictions, `blocked_clients`, hit rate, connected clients)
      are scraped and dashboarded.
- [ ] Alerts fire on high memory, rising evictions, replication lag, and slowlog growth.
- [ ] Client-side errors (timeouts, connection resets, MOVED/ASK) are logged and alertable.
- [ ] Keyspace notifications or metrics reveal TTL/eviction behavior, not just guesswork.

## AI Review Checklist

- Is `maxmemory` plus an explicit eviction policy configured on every instance?
- Is authentication required and the instance closed to the public internet?
- Does the durability mode match what the data actually requires?
- Is a single node loss survivable via replication/Cluster with tested failover?
- Are `KEYS`/`FLUSHALL` blocked from production and the slowlog monitored?
- Are memory, evictions, and replication lag alerted on?

## Related

- `knowledge/redis/20-persistence.md`
- `knowledge/redis/18-replication.md`
- `knowledge/redis/21-security.md`
- `knowledge/redis/22-monitoring.md`
- `knowledge/redis/27-production.md`
