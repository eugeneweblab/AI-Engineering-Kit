---
id: postgresql/13-high-availability
topic: postgresql
slug: high-availability
title: "PostgreSQL High Availability"
type: doc
order: 13
status: ready
tags: [postgresql, high-availability, DATABASE_URL, promotion, loss, survive]
related: [postgresql/12-replication, postgresql/14-backups, postgresql/17-monitoring, postgresql/26-production]
when_to_use: "Read before designing automatic failover, promotion, or connection routing for a PostgreSQL cluster that must survive node loss."
---
# PostgreSQL High Availability

## Purpose

This document defines how to keep a PostgreSQL service reachable and correct when a
node fails: automated failover, promotion of a standby, fencing the old primary, and
routing clients to the current primary. It is written so an agent can design or review
an HA topology without introducing the failure that HA is supposed to prevent — two
primaries accepting writes at once.

HA builds on [replication](12-replication.md): replication keeps a standby current;
HA decides *when* to promote it and *how* to send traffic there. This doc is about that
decision and its safety, not about copying bytes.

## Why It Matters

The whole point of HA is to reduce downtime, yet a badly designed HA setup causes worse
outages than no HA at all. Two failure modes dominate. **Split-brain**: a network
partition promotes a standby while the old primary is still alive and taking writes, so
two nodes diverge and you permanently lose data on whichever you discard. **Flapping**:
an over-eager health check promotes on a transient blip, triggering an unnecessary
failover storm. Both come from trusting a single signal and skipping fencing. Because
the damage — divergent data — is often unrecoverable, HA logic must be conservative,
quorum-based, and tested under real partition conditions.

## Core Principles

- **A cluster must have at most one primary. Enforce it, don't assume it.** Correct HA
  guarantees the old primary cannot accept writes before a new one is promoted. That
  guarantee is called fencing (STONITH); without it you get split-brain.
- **Decisions need a quorum, not a single watcher.** Promotion must be agreed by a
  majority of an odd number of nodes (3 or 5). A single failover agent can itself be the
  thing that is partitioned.
- **Failover is a data-durability event.** With async replication, promoting a lagging
  standby discards the primary's un-shipped WAL. Your RPO is your lag at failover time.
- **Clients must find the new primary without a redeploy.** Automatic promotion is
  useless if apps still connect to the dead node. Route through a VIP, a proxy, or
  multi-host connection strings with `target_session_attrs`.
- **Untested HA is not HA.** A failover path that has never run in anger will fail when
  it finally runs. Rehearse it on a schedule.

## Best Practices

- Use a proven cluster manager — **Patroni** (with etcd/Consul/Kubernetes as the DCS) or
  **repmgr** — instead of hand-rolled promotion scripts. They implement quorum, leader
  leases, and fencing correctly.
- Run an **odd number** of DCS/consensus nodes (3 or 5) so a partition always has a
  majority side.
- Enable **fencing**: the demoted primary must be stopped, network-isolated, or
  self-demoted (Patroni does this via a leader lease TTL) before promotion completes.
- Route clients through a layer that follows the primary: HAProxy checking Patroni's REST
  health endpoint, a VIP, or `postgresql://h1,h2,h3/db?target_session_attrs=primary`.
- Set health-check thresholds to tolerate transient blips (require N consecutive failures)
  so a one-second network hiccup does not trigger a failover.
- Use synchronous or quorum replication when the RPO must be zero, and accept the write
  latency and availability trade-off (see [replication](12-replication.md)).
- Keep the promoted standby's own standbys reattaching automatically so you are not left
  with a single node after one failover.

## Examples

**Good Example** — client routing that follows the primary automatically

```ini
# Patroni pins one leader via a short-TTL lease in the DCS; only the lease holder is primary.
# A demoted node loses its lease and self-fences before any standby is promoted.
bootstrap:
  dcs:
    ttl: 30                 # leader lease lifetime
    loop_wait: 10
    retry_timeout: 10
    synchronous_mode: true  # promote only a standby known to be caught up -> bounded RPO
```

```bash
# App connects with multiple hosts and asks libpq for the writable node.
# On failover the driver transparently reconnects to whoever is now primary.
export DATABASE_URL="postgresql://h1,h2,h3/app?target_session_attrs=primary&sslmode=require"
```

**Bad Example** — DIY promotion with no fencing and no quorum

```bash
#!/bin/sh
# A cron health check that promotes on a single failed ping. DANGEROUS.
if ! pg_isready -h primary.internal; then      # one transient blip = "primary is down"
  ssh standby.internal 'pg_ctl promote'         # promote with no quorum, no fencing
fi
# If the primary is merely partitioned from THIS checker, it stays alive and keeps
# taking writes while the standby is promoted -> two primaries -> split-brain -> data loss.
# Fix: use Patroni/repmgr with a 3-node DCS and fencing of the old primary.
```

## Common Mistakes

- No fencing, so a partitioned old primary keeps accepting writes after promotion
  (split-brain).
- An even number of consensus nodes (or a single failover agent), so no side can claim a
  clean majority during a partition.
- Health checks so twitchy they fail over on transient latency (flapping).
- Hard-coding the primary's hostname in the app, so promotion succeeds but clients never
  reconnect to the new primary.
- Promoting the most-lagged standby and silently losing transactions because RPO was
  never considered.
- Never rehearsing failover, so the first real one exposes broken automation.
- Assuming a managed provider gives zero-RPO failover — most default to async; verify.

## Production Tips

- Track two numbers per drill: **RTO** (time from failure to writable primary) and
  **RPO** (data lost). Both must meet the SLO you promised, measured, not assumed.
- Run a scheduled game day that kills the primary in a non-prod-identical environment and
  confirms automatic promotion, fencing, and client reconnection end to end.
- After any failover, the old primary must be re-cloned or `pg_rewind`-ed before it
  rejoins — never let it come back as a second primary.
- HA does not remove the need for [backups](14-backups.md): a bad `DELETE` replicates to
  every standby instantly. Failover cannot undo logical corruption.

## AI Review Checklist

- Is there a mechanism that guarantees at most one primary (fencing / STONITH)?
- Are failover decisions made by a quorum over an odd number of nodes (3 or 5)?
- Do clients reach the new primary automatically (proxy, VIP, or `target_session_attrs`)?
- Are health-check thresholds tolerant of transient blips to prevent flapping?
- Is the RPO at failover understood and does the replication mode match it?
- Is the demoted primary re-cloned or rewound before it can rejoin the cluster?
- Has the failover path been tested end to end recently?

## Related

- `knowledge/postgresql/12-replication.md`
- `knowledge/postgresql/14-backups.md`
- `knowledge/postgresql/17-monitoring.md`
- `knowledge/postgresql/26-production.md`
