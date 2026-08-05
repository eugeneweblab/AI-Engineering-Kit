---
id: mysql/02-configuration
topic: mysql
slug: configuration
title: "MySQL Configuration"
type: doc
order: 2
status: ready
tags: [mysql, configuration]
related: [mysql/01-installation, mysql/06-transactions, mysql/14-performance, mysql/20-production, mysql/15-monitoring]
when_to_use: "Read before editing my.cnf or tuning buffer pool, durability, or charset settings."
---
# MySQL Configuration

## Purpose

This document defines how to configure a MySQL server through `my.cnf`: the handful of
settings that actually matter (memory, durability, connections, charset), what each one
trades off, and how to change them safely. The goal is a configuration an agent can reason
about, not a copied-in wall of tuning flags nobody understands.

## Why It Matters

MySQL's defaults are conservative and general-purpose; they are not tuned for your
hardware or workload. The single most impactful setting — `innodb_buffer_pool_size` —
defaults to 128 MB, which means a server with 32 GB of RAM caches almost nothing and
reads from disk constantly. Conversely, one wrong durability flag (`innodb_flush_log_at_trx_commit`)
can silently trade away crash safety for speed, so a power loss loses committed
transactions. Configuration is where correctness and performance are both won and lost,
and the effects are invisible until load or a crash reveals them.

## Core Principles

- **Version and review `my.cnf` like code.** Configuration is infrastructure; it belongs in
  the repo, in review, and applied by automation — not typed into a live server by hand.
- **Change one thing at a time and measure.** Tuning is empirical. Alter a single setting,
  observe the metric it targets, then decide. Bulk-pasting "optimized configs" hides regressions.
- **Understand durability before touching it.** The defaults are safe. Any change that speeds
  writes by relaxing flushing is a deliberate correctness trade — document why.
- **Set memory relative to the machine's RAM, not a magic number.** The buffer pool should be
  the largest consumer; everything else is secondary.

## Best Practices

- Set `innodb_buffer_pool_size` to roughly **60–75%** of available RAM on a dedicated database
  host. This is the cache for data and indexes; bigger means fewer disk reads. The cost is
  leaving headroom for the OS and connections.
- Keep `innodb_flush_log_at_trx_commit = 1` (the default) for full ACID durability: every commit
  is flushed to disk. Only set `2` if losing ~1 second of transactions on a crash is acceptable.
- Set `character_set_server = utf8mb4` and `collation_server = utf8mb4_0900_ai_ci` so new schemas
  default to real UTF-8.
- Size `max_connections` to what the app pool actually needs (often 150–500), not the maximum.
  Each connection reserves memory; too many can exhaust RAM under a connection spike.
- Set a `sql_mode` that includes `STRICT_TRANS_TABLES` so bad data (out-of-range, truncation)
  errors instead of being silently coerced. This is the default in 8.0+ — do not remove it.
- Enable the slow query log (`slow_query_log = 1`, `long_query_time = 1`) in production to
  surface queries worth optimizing.

## Examples

**Good Example** — minimal, reasoned `my.cnf`

```ini
[mysqld]
# Memory: buffer pool is the main cache. ~70% of a 16 GB dedicated host.
innodb_buffer_pool_size = 11G

# Durability: flush every commit to disk. Full ACID — do not relax without a reason.
innodb_flush_log_at_trx_commit = 1
sync_binlog = 1                       # binlog durable too, needed for safe replication

# Correctness: strict mode rejects out-of-range and truncated values.
sql_mode = STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION

# Charset: real UTF-8 for all new schemas.
character_set_server = utf8mb4
collation_server     = utf8mb4_0900_ai_ci

# Connections: sized to the app pool, not the theoretical max.
max_connections = 300

# Observability: log queries slower than 1s for later optimization.
slow_query_log  = 1
long_query_time = 1
```

**Bad Example** — copied tuning, durability silently broken

```ini
[mysqld]
innodb_buffer_pool_size = 128M        # default: caches almost nothing on a big host
innodb_flush_log_at_trx_commit = 0    # commits not flushed: a crash loses transactions
sql_mode =                            # strict mode disabled: bad data silently truncated
max_connections = 10000               # each connection reserves RAM: OOM under a spike
character_set = utf8                   # 3-byte "utf8": corrupts emoji and some CJK
```

## Common Mistakes

- Leaving `innodb_buffer_pool_size` at the 128 MB default on a server with plenty of RAM.
- Setting `innodb_flush_log_at_trx_commit = 0` or `2` for speed without accepting the data-loss risk.
- Clearing `sql_mode`, so out-of-range numbers and over-long strings are silently truncated.
- Setting `max_connections` absurdly high, so a connection storm exhausts memory instead of queuing.
- Editing `my.cnf` on a live box by hand, leaving dev and production silently divergent.
- Changing several settings at once, so a regression can't be attributed to any one of them.

## Production Tips

- Apply config through your provisioning tool (Ansible, Terraform, a container image), so the
  running config always matches the repo. Drift is a source of "works on the old box" incidents.
- Most `innodb_*` and buffer-pool changes require a restart; plan a maintenance window and know
  which settings are dynamic (`SET GLOBAL`) versus which need a bounce.
- Track buffer pool hit ratio and slow query volume as metrics; they tell you when the current
  config no longer fits the workload.

## AI Review Checklist

- Is `innodb_buffer_pool_size` sized to the host's RAM (~60–75%), not left at 128 MB?
- Is `innodb_flush_log_at_trx_commit = 1` unless data-loss risk is explicitly accepted?
- Does `sql_mode` include `STRICT_TRANS_TABLES` so bad data errors instead of truncating?
- Is the server charset `utf8mb4`, not the 3-byte `utf8`?
- Is `max_connections` sized to the actual pool, not an arbitrarily large number?
- Is `my.cnf` in version control and applied by automation, not hand-edited on the server?

## Related


- `knowledge/mysql/01-installation.md`
- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/14-performance.md`
- `knowledge/mysql/20-production.md`
- `knowledge/mysql/15-monitoring.md`
