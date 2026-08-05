---
id: postgresql/12-replication
topic: postgresql
slug: replication
title: "PostgreSQL Replication"
type: doc
order: 12
status: ready
tags: [postgresql, replication, sent, pg_stat_replication]
related: [postgresql/13-high-availability, postgresql/14-backups, postgresql/17-monitoring, postgresql/02-configuration]
when_to_use: "Read before setting up read replicas, streaming standbys, or logical replication between PostgreSQL clusters."
---
# PostgreSQL Replication

## Purpose

This document defines how to copy data from one PostgreSQL cluster to another and
keep the copy current: physical (streaming) replication of the whole cluster and
logical replication of selected tables. It is written so an agent can stand up, tune,
or review a replica without silently losing data or serving stale reads as if they
were fresh.

Replication is the mechanism; [high availability](13-high-availability.md) is the goal
it serves. Replication alone does not give you failover — a replica that nobody
promotes is just a warm copy. Keep the two concerns distinct.

## Why It Matters

A replica is your fastest recovery path and your read-scaling lever, but only if it
is genuinely caught up. The dangerous failure mode is invisible: replication silently
falls behind or breaks, monitoring does not catch it, and you fail over to a standby
that is minutes or hours stale — losing every transaction in that gap. The second
trap is the mirror image: a synchronous standby that goes offline can freeze every
commit on the primary. Both outcomes come from not understanding the durability and
lag trade-off, so treat replication configuration as a correctness concern, not an
ops afterthought.

## Core Principles

- **Physical replicates the whole cluster; logical replicates chosen tables.** Physical
  (streaming) ships WAL byte-for-byte — same major version, identical binary copy.
  Logical decodes WAL into row changes — selective, cross-version, but no DDL.
- **Asynchronous is the default and it can lose data.** With async replication a commit
  returns before the standby has it. A primary crash loses un-shipped WAL. Accept that,
  or pay for synchronous.
- **Synchronous trades availability for durability.** `synchronous_commit=on` with a
  named standby means a commit waits for that standby's ack. If the standby is gone and
  you have no quorum, commits block. Never point synchronous replication at a single
  standby.
- **Replicas are read-only and lag.** A hot standby serves reads but returns data as of
  its replay position, not the primary's `now()`. Route only lag-tolerant reads there.
- **Slots prevent WAL loss but can fill the disk.** A replication slot guarantees the
  primary keeps WAL until the standby consumes it. An abandoned slot pins WAL forever
  and fills the primary's disk. Always bound it with `max_slot_wal_keep_size`.

## Best Practices

- Use a dedicated replication role (`REPLICATION` privilege, not superuser) and require
  TLS on the replication connection.
- Create standbys with `pg_basebackup -R` so the connection info and slot are written
  into the standby's config automatically.
- Give every physical standby a **permanent replication slot** so needed WAL is retained,
  and cap it with `max_slot_wal_keep_size` so a dead standby cannot fill the primary.
- Monitor lag continuously as **bytes**, not just time: compare `pg_current_wal_lsn()`
  on the primary to `sent`/`replay` LSNs in `pg_stat_replication`. Alert on both a byte
  threshold and stale/absent rows.
- For synchronous durability use `synchronous_standby_names = 'ANY 1 (s1, s2)'` (quorum)
  so losing one standby does not block the primary.
- For logical replication, ensure every replicated table has a replica identity (a
  primary key, or `REPLICA IDENTITY FULL`) or UPDATE/DELETE will fail to apply.
- Set `hot_standby_feedback = on` when standbys run long read queries, to stop the
  primary from vacuuming rows the standby still needs — at the cost of some primary bloat.

## Examples

**Good Example** — provision a physical standby with a slot and bounded WAL retention

```sql
-- On the primary: bounded WAL retention so a dead slot cannot fill the disk.
ALTER SYSTEM SET max_slot_wal_keep_size = '64GB';  -- primary drops WAL past this, breaking a stuck slot instead of crashing
SELECT pg_reload_conf();

-- Dedicated, least-privilege replication role.
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'set-via-secrets-manager';
```

```bash
# On the standby host: base backup writes standby.signal + primary_conninfo for you.
pg_basebackup \
  --host=primary.internal --port=5432 --username=replicator \
  --pgdata=/var/lib/postgresql/data \
  --wal-method=stream \
  --create-slot --slot=standby_1 \
  --write-recovery-conf   # -R: standby comes up already pointed at the primary via a slot
# Verify from the primary AFTER start: pg_stat_replication.state should read 'streaming'.
```

**Bad Example** — synchronous replication against a single standby

```sql
-- One named synchronous standby and nothing else.
ALTER SYSTEM SET synchronous_standby_names = 'standby_1';  -- BAD: single point of failure for WRITES
ALTER SYSTEM SET synchronous_commit = 'on';
-- The moment standby_1 restarts or its network blips, EVERY commit on the
-- primary blocks indefinitely. You have coupled write availability to one replica.
-- Fix: 'ANY 1 (standby_1, standby_2)' so losing one standby still lets commits proceed.
```

## Common Mistakes

- Treating an async replica as a zero-data-loss backup — a primary crash loses the
  un-shipped tail of WAL.
- Creating a replication slot and never monitoring it, so an offline standby silently
  fills the primary's disk.
- Pointing `synchronous_standby_names` at exactly one standby, making writes fail when
  that standby restarts.
- Sending read-your-own-write queries to a replica and getting stale data because of
  replay lag.
- Using logical replication and expecting DDL (schema changes) or sequences to
  replicate — they do not; you must apply them out of band.
- Forgetting a replica identity on a logically replicated table, so UPDATE/DELETE
  changes error out on the subscriber.
- Mixing major versions on physical replication — it requires identical major versions.

## Production Tips

- Measure Recovery Point Objective directly: run a canary write on the primary and time
  its appearance on each standby. That number, not config, is your real data-loss window.
- Keep `wal_keep_size` modest and rely on slots plus `max_slot_wal_keep_size` for
  retention; large `wal_keep_size` just wastes primary disk.
- Cascade replicas (standby feeding standby) to offload replication bandwidth from the
  primary when you have many read replicas.
- Test failover regularly (see [high availability](13-high-availability.md)); a standby
  you have never promoted is an untested standby.

## AI Review Checklist

- Is replication async or synchronous, and does the choice match the stated RPO?
- If synchronous, is it quorum-based (`ANY n (...)`) rather than a single standby?
- Does every physical standby have a slot, and is that slot bounded by
  `max_slot_wal_keep_size`?
- Is replication lag monitored in bytes with an alert on staleness and on missing rows?
- Are lag-tolerant reads the only ones routed to replicas?
- For logical replication, does every replicated table have a replica identity, and is
  DDL handled separately?
- Does the replication connection use a least-privilege role over TLS?

## Related

- `knowledge/postgresql/13-high-availability.md`
- `knowledge/postgresql/14-backups.md`
- `knowledge/postgresql/17-monitoring.md`
- `knowledge/postgresql/02-configuration.md`
