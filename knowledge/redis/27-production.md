---
id: redis/27-production
topic: redis
slug: production
title: "Production"
type: doc
order: 27
status: ready
tags: [redis, production]
related: [redis/18-replication, redis/19-clustering, redis/20-persistence, redis/21-security, redis/98-production-checklist]
when_to_use: "Read before deploying Redis to production or changing its memory, persistence, HA, or security configuration."
---
# Production

## Purpose

This document defines how to run Redis in production safely: memory limits and
eviction, persistence and durability, high availability, security, and safe
upgrades. It is the operational contract that keeps a Redis deployment from losing
data, running out of memory, or becoming a single point of failure.

## Why It Matters

Default Redis is tuned for a developer laptop, not a production node: no memory
cap, `protected-mode` assumptions, and persistence settings that may not match your
durability needs. Ship those defaults and you get an unbounded process the OOM
killer eventually reaps, or a "cache" that silently becomes the only copy of data
and then loses it on restart. Redis holds live state in RAM, so a misconfiguration
here is not a slow degradation — it is data loss or a hard outage. Decisions must be
made deliberately, per deployment, not inherited from `redis.conf` defaults.

## Core Principles

- **Decide: cache or datastore.** A cache uses `maxmemory` + LRU/LFU eviction and
  tolerates loss. A datastore uses persistence, replication, and `noeviction`.
  Configure for exactly one; the middle ground loses data unexpectedly.
- **Always cap memory.** Set `maxmemory` and a policy so Redis has defined behaviour
  under pressure instead of being killed by the OS.
- **No single point of failure.** Production Redis is replicated with automatic
  failover (Sentinel) or clustered — never one standalone node holding real state.
- **Lock it down.** Require authentication, bind to private interfaces, and use TLS.
  An open Redis on the internet is compromised within minutes.
- **Change config safely.** Test persistence and failover in staging; a wrong AOF or
  `maxmemory-policy` value is discovered too late during an incident.

## Best Practices

- Set `maxmemory` to leave headroom (typically ~50-70% of RAM) for replication
  buffers and the copy-on-write fork used by snapshotting; running to the RAM limit
  makes `BGSAVE` fail or the OOM killer strike.
- Choose eviction deliberately: `allkeys-lru`/`allkeys-lfu` for a cache,
  `noeviction` for a datastore (writes error instead of silently dropping data).
- For durability, enable AOF with `appendfsync everysec` (bounded ~1s loss) rather
  than relying on RDB snapshots alone, which lose everything since the last save.
  Keep RDB too for fast restarts and backups.
- Run at least one replica and Sentinel (or Cluster) so a primary failure fails over
  automatically. Verify failover in a game day, not during the first real outage.
- Require a strong password via the ACL system (`requirepass`/`user` rules), keep
  `protected-mode yes`, bind to internal IPs, and enable TLS for client and
  replication traffic.
- Disable or rename dangerous commands (`FLUSHALL`, `KEYS`, `CONFIG`, `DEBUG`) via
  ACLs for application users so a bug or breach cannot wipe or stall the server.
- Pin the Redis version, and upgrade replicas first, then fail over — never upgrade a
  lone primary in place.

## Examples

**Good Example** — bounded, durable, secured cache/datastore config

```ini
# redis.conf — datastore of record
maxmemory 12gb                 # cap well below host RAM to leave fork headroom
maxmemory-policy noeviction    # error on write when full, never silently drop data
appendonly yes                 # AOF: at most ~1s of writes lost
appendfsync everysec
save 900 1                     # keep RDB snapshots for fast restart + backups
protected-mode yes
bind 10.0.0.5 127.0.0.1        # private interfaces only, never 0.0.0.0 unauthenticated
requirepass "<from-secrets-manager>"
tls-port 6379
port 0                         # disable the plaintext port
rename-command FLUSHALL ""     # neuter accidental/malicious full wipes
```

**Bad Example** — defaults shipped to production

```ini
# maxmemory unset      -> grows until the OOM killer terminates the process
# appendonly no        -> RDB only; a crash loses everything since last snapshot
bind 0.0.0.0           # reachable from anywhere...
# requirepass unset    # ...with no authentication -> compromised within minutes
maxmemory-policy noeviction   # but it's used as a cache -> writes start failing under load
```

## Common Mistakes

- Leaving `maxmemory` unset, so the process is OOM-killed instead of evicting.
- Using Redis as the system of record with only RDB snapshots, losing recent writes on crash.
- Setting `maxmemory` to nearly all host RAM, causing `BGSAVE`/AOF-rewrite fork to fail.
- A single standalone node with no replica or failover.
- Binding to `0.0.0.0` with no password or TLS.
- Applying an eviction policy that contradicts the use case (`allkeys-lru` on a datastore evicts real data).
- Upgrading or restarting the primary directly instead of failing over to a replica first.

## Production Tips

- Rehearse failover and restore-from-backup regularly; an untested backup is not a backup.
- Alert on `used_memory` approaching `maxmemory`, rising `evicted_keys`, and replica
  lag — these precede the outage rather than follow it.
- Keep `stop-writes-on-bgsave-error yes` so you learn about failing snapshots
  immediately instead of discovering an old backup during recovery.

## AI Review Checklist

- Is `maxmemory` set with headroom for fork/replication, and an eviction policy that matches cache-vs-datastore?
- If Redis holds data of record, is AOF enabled (`appendfsync everysec`) and a replica present?
- Is there automatic failover via Sentinel or Cluster, not a single node?
- Is authentication required, plaintext port disabled, TLS on, and binding restricted to private IPs?
- Are destructive commands disabled/renamed for the application ACL user?
- Do upgrades fail over to a replica rather than touching the live primary?

## Related

- `knowledge/redis/18-replication.md`
- `knowledge/redis/19-clustering.md`
- `knowledge/redis/20-persistence.md`
- `knowledge/redis/21-security.md`
- `knowledge/redis/98-production-checklist.md`
