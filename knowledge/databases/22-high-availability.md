---
id: databases/22-high-availability
topic: databases
slug: high-availability
title: "High Availability"
type: doc
order: 22
status: ready
tags: [databases, high-availability]
related: [databases/14-replication, databases/18-backup-and-recovery, databases/13-eventual-consistency, databases/15-sharding, databases/21-monitoring]
when_to_use: "Read before designing failover, choosing sync vs async replication, or reviewing whether a database survives the loss of a node or a region."
---
# High Availability

## Purpose

This document defines how to keep a database serving through the failure of a node, a
zone, or a region: replication topologies, failover, synchronous vs asynchronous
trade-offs, and the split-brain hazard. It is written so an agent can design or review an
HA setup that survives real failures without silently corrupting or losing data.

High availability is about *staying up*. It is closely related to, but distinct from,
[backup and recovery](18-backup-and-recovery.md) (getting data *back*) — you need both.
HA does not protect against a bad `DELETE`; it faithfully replicates it.

## Why It Matters

Every component fails eventually — disks die, zones lose power, networks partition. A
single-node database means every one of those events is a total outage, and outages cost
revenue, trust, and, during a disorderly failover, data. But HA is deceptively dangerous:
a naive setup can be *worse* than a single node, because two nodes that both think they are
primary (split-brain) accept conflicting writes and silently corrupt the data. The failure
mode is invisible until you try to reconcile. Because HA sits directly on the correctness
of the data and the tolerance you can offer customers, it is held to a higher bar than
ordinary infrastructure — the design must reason explicitly about what happens the moment
a node disappears.

## Core Principles

- **Decide your consistency vs availability trade-off explicitly (CAP).** During a network
  partition you get consistency or availability, not both. Choose per system and write it
  down; the default of "hope it doesn't happen" is a choice to lose data.
- **Synchronous replication protects data; asynchronous protects latency.** Sync means no
  acknowledged write is lost on failover (RPO≈0) at the cost of write latency; async is
  fast but a failover can lose the un-replicated tail. Pick per the data's value.
- **Automatic failover needs a fencing mechanism.** The old primary must be provably
  demoted (STONITH/fencing) before a new one is promoted, or both accept writes —
  split-brain. Never promote on a hunch.
- **Use a quorum/consensus to decide who leads.** An odd number of voters (3, 5) with a
  majority prevents two partitions from each electing a leader.
- **Test failover regularly.** An untested failover has an unknown success rate; the first
  real one should not be the first one you have ever run.

## Best Practices

- Run the primary and at least one replica in **separate availability zones**; for
  region-level resilience, keep a replica in another region.
- Use a **managed HA setup or a proven coordinator** (Patroni, managed RDS/Aurora
  Multi-AZ, orchestrator) rather than hand-rolled promotion scripts — split-brain
  avoidance is subtle and easy to get wrong.
- Choose **synchronous (or quorum) replication** for financial and other must-not-lose
  data; accept the latency. Use async for high-write, loss-tolerant workloads and state the
  RPO. See [replication](14-replication.md).
- Route clients through a **connection endpoint that follows the primary** (virtual IP,
  DNS with low TTL, service discovery, proxy) so failover does not require an app redeploy.
- **Fence the old primary** before promotion and require a **majority quorum** to elect —
  never allow a minority partition to promote.
- Monitor **replication lag** and treat high lag as an HA risk: async lag is exactly the
  data you lose on failover. See [monitoring](21-monitoring.md).
- Have applications **retry on failover** with idempotent operations and backoff; a
  failover is a brief blip of errors, not a crash.
- Keep independent **backups** — HA covers node loss, backups cover deletion and
  corruption. They are not substitutes.

## Examples

**Good Example** — quorum failover with synchronous commit and fencing

```ini
# PostgreSQL primary: synchronous_commit guarantees an acknowledged write is on a
# replica before the client sees success. Failover cannot lose acknowledged data (RPO≈0).
synchronous_standby_names = 'ANY 1 (replica_a, replica_b)'
synchronous_commit = on

# Failover is managed by Patroni, which uses a distributed consensus store (etcd) so ONLY
# a node holding the leader lock — won by majority quorum — is primary. The demoted node
# is fenced (rejects writes) before the new primary is promoted → no split-brain.
# Clients connect to a single endpoint that always points at the current leader.
```

**Bad Example** — script-based promotion, no fencing, async only

```bash
# A cron/healthcheck script pings the primary; on timeout it promotes a replica.
if ! pg_isready -h primary; then
  ssh replica "pg_ctl promote"     # promotes on a HUNCH — the "dead" primary may be
fi                                 # merely unreachable and still taking writes.
# Result during a network partition: BOTH nodes are primary. Clients on each side write
# conflicting data → split-brain → silent, unrecoverable corruption.
# Async replication also means any un-shipped writes are simply lost. No quorum, no fence.
```

## Common Mistakes

- Promoting a new primary without fencing the old one, causing split-brain corruption.
- Deciding failover with a single healthchecker instead of a majority quorum.
- Using async replication for must-not-lose data without acknowledging the RPO gap.
- Placing all nodes in one availability zone, so a zone outage is still total downtime.
- Hardcoding the primary's address so failover requires an application redeploy.
- Treating replicas as backups — a `DROP TABLE` replicates instantly to all of them.
- Never testing failover, so its real behavior is unknown until a live incident.
- Ignoring replication lag, then losing exactly that lagged data on the next failover.

## Production Tips

- Run scheduled **game-day failovers** in production (or a prod-like environment) and
  measure real RTO; rehearsed numbers are the only ones you can promise.
- Make application writes **idempotent** so retries across a failover do not double-apply.
- Alert on **loss of quorum** and on a replica falling out of the synchronous set — both
  silently erode your availability and RPO guarantees.
- Document the exact failover and failback runbook, including how to safely re-add a fenced
  node without it clobbering newer data.

## AI Review Checklist

- Is the consistency-vs-availability trade-off during a partition decided explicitly?
- Is replication synchronous/quorum for must-not-lose data, with the RPO stated for async?
- Does automatic failover fence the old primary and require a majority quorum to promote?
- Are nodes spread across availability zones (and regions if region-resilience is required)?
- Do clients reach the primary through a moving endpoint, so failover needs no redeploy?
- Are replicas explicitly *not* treated as a substitute for backups?
- Has failover been tested recently, with a measured RTO and a written runbook?

## Related

- `knowledge/databases/14-replication.md`
- `knowledge/databases/18-backup-and-recovery.md`
- `knowledge/databases/13-eventual-consistency.md`
- `knowledge/databases/15-sharding.md`
- `knowledge/databases/21-monitoring.md`
