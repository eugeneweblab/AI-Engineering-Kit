---
id: postgresql/02-configuration
topic: postgresql
slug: configuration
title: "Configuration"
type: doc
order: 2
status: ready
tags: [postgresql, configuration]
related: [postgresql/01-installation, postgresql/27-tuning, postgresql/16-performance, postgresql/18-security, postgresql/17-monitoring]
when_to_use: "Read before changing postgresql.conf, pg_hba.conf, or memory/connection settings."
---
# Configuration

## Purpose

This document defines how to configure a PostgreSQL instance: memory, connections,
durability, autovacuum, and client authentication. It focuses on the settings that
matter for correctness and stability and explains the trade-off behind each. Deep
workload-specific tuning lives in [tuning](27-tuning.md); this doc gets a server to
a safe, sane baseline.

## Why It Matters

The default `postgresql.conf` is deliberately conservative so PostgreSQL starts on
tiny hardware. On a real server it leaves most of the machine's memory unused and
caps connections in ways that surprise you under load. The riskiest settings are
the durability ones: a single careless change (`fsync = off`,
`synchronous_commit = off`) trades your data's safety for speed, silently, until a
crash loses committed transactions. Configuration is where "fast" and "correct"
collide, so every change needs a stated reason and a known cost.

## Core Principles

- **Change settings for a reason, with a measurement.** Do not copy a blog's numbers.
  Set a value, reload, and confirm the effect with metrics or `EXPLAIN`.
- **Never weaken durability to gain speed by default.** `fsync`, `full_page_writes`,
  and `synchronous_commit` protect committed data. Relax them only with eyes open.
- **Right-size memory to the machine and workload.** `shared_buffers`,
  `work_mem`, and `effective_cache_size` are the high-impact knobs.
- **Bound connections; pool the rest.** Each backend is a process. Thousands of
  connections thrash the scheduler — use a pooler (PgBouncer) instead of raising the cap.
- **Authentication is configuration.** `pg_hba.conf` decides who connects and how;
  a permissive line here is a security hole no application code can fix.

## Best Practices

- Set `shared_buffers` to ~25% of RAM and `effective_cache_size` to ~50–75% of RAM
  (the latter is a planner hint, not an allocation).
- Keep `work_mem` modest (e.g. 16–64MB) — it is allocated *per sort/hash node per
  query*, so a high value times many concurrent operations can exhaust RAM.
- Leave `fsync = on`, `full_page_writes = on`, and `synchronous_commit = on` unless
  you have an explicit, documented reason and accept the data-loss window.
- Keep autovacuum on and tune it to be *more* aggressive on hot tables, never off.
- Use `ALTER SYSTEM` (writes `postgresql.auto.conf`) or config management, then
  `SELECT pg_reload_conf();`; know which settings need a full restart.
- In `pg_hba.conf`, use `scram-sha-256`, scope by database/user/CIDR, and never `trust`
  over a network. Order matters — the first matching line wins.
- Set a bounded `statement_timeout` and `idle_in_transaction_session_timeout` to
  stop runaway queries and transactions from holding locks forever.

## Examples

**Good Example** — sized to the host, durable, bounded

```ini
# postgresql.conf on a 16 GB, 8-core dedicated DB host
shared_buffers = 4GB               # ~25% of RAM: PostgreSQL's own page cache
effective_cache_size = 12GB        # planner hint: OS + PG cache; not allocated
work_mem = 32MB                    # per node — deliberately modest, many can run at once
maintenance_work_mem = 1GB         # speeds VACUUM / CREATE INDEX; run one at a time
max_connections = 100              # bounded; app connects via PgBouncer pooler
synchronous_commit = on            # committed means durable — do not weaken lightly
idle_in_transaction_session_timeout = '30s'  # release locks from stuck transactions
statement_timeout = '30s'          # kill runaway queries before they pile up
```

```conf
# pg_hba.conf — explicit, scoped, encrypted
# TYPE  DATABASE  USER   ADDRESS         METHOD
host    app       app    10.0.0.0/24     scram-sha-256   # app subnet only, hashed auth
local   all       all                    scram-sha-256
```

**Bad Example** — oversized, unsafe, wide open

```ini
work_mem = 2GB            # per node: a few concurrent sorts OOM-kill the server
shared_buffers = 15GB     # ~94% of RAM: starves the OS cache and other processes
synchronous_commit = off  # silent: a crash loses recently "committed" transactions
fsync = off               # any crash can corrupt the entire cluster
max_connections = 5000    # 5000 processes thrash the CPU instead of pooling
```

```conf
# pg_hba.conf
host  all  all  0.0.0.0/0  trust   # anyone on any network connects with no password
```

## Common Mistakes

- Setting `work_mem` high globally; it multiplies per operation and OOMs the host.
- Turning off `fsync` or `synchronous_commit` for a benchmark and shipping it.
- Raising `max_connections` into the thousands instead of adding a connection pooler.
- Disabling autovacuum "to reduce load," causing table bloat and transaction-ID wraparound.
- Editing `postgresql.conf` but forgetting to reload — or reloading a restart-only setting.
- A `0.0.0.0/0 trust` or `md5` line in `pg_hba.conf` exposing the database.

## Production Tips

- Track config drift: keep `postgresql.conf`/`pg_hba.conf` in version control and diff
  against the running values in `pg_settings`.
- Watch `pg_stat_activity` for `idle in transaction` and long-running statements; the
  timeouts above are your safety net.
- Load `pg_stat_statements` (`shared_preload_libraries`) — it needs a restart, so set it
  during initial configuration, not during an incident.

## AI Review Checklist

- Are `shared_buffers`, `effective_cache_size`, and `work_mem` sized to the host and workload?
- Is `work_mem` low enough to survive peak concurrency without OOM?
- Are `fsync`, `full_page_writes`, and `synchronous_commit` left safe (or the risk documented)?
- Is autovacuum on and tuned, not disabled?
- Does `pg_hba.conf` use `scram-sha-256`, scoped by CIDR, with no network `trust`?
- Are `statement_timeout` and `idle_in_transaction_session_timeout` set?

## Related

- `knowledge/postgresql/01-installation.md`
- `knowledge/postgresql/27-tuning.md`
- `knowledge/postgresql/16-performance.md`
- `knowledge/postgresql/18-security.md`
- `knowledge/postgresql/17-monitoring.md`
