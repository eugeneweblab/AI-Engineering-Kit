---
id: redis/20-persistence
topic: redis
slug: persistence
title: "Persistence"
type: doc
order: 20
status: ready
tags: [redis, persistence, fsync, "rdb_last_bgsave_status:err", bgsave, "aof_last_write_status:err", rdb_last_bgsave_status, aof_last_write_status]
related: [redis/18-replication, redis/13-caching, redis/22-monitoring, redis/27-production]
when_to_use: "Read before choosing RDB vs AOF, or when Redis holds data you cannot afford to lose on restart."
---
# Persistence

## Purpose

This document defines how Redis writes data to disk so it survives a restart or
crash: RDB snapshots, the AOF (append-only file), how they combine, and what
durability each actually guarantees. It covers the trade-off between performance
and how many seconds of writes you can lose. Persistence is disk durability; it is
not the same as [replication](18-replication.md) (copies on other nodes) or backup.

Persistence answers "if this process dies, what do I get back on restart?".

## Why It Matters

The default `appendfsync everysec` means Redis can lose **up to one second of
writes** on a crash, and a pure-RDB setup can lose **everything since the last
snapshot** — potentially minutes. Meanwhile, a naive fork for an RDB save on a
large dataset can double memory use and stall the server. People deploy Redis as a
cache, later start storing the only copy of something important, and never revisit
the persistence config. The gap between "I assumed it was durable" and what the
config actually guarantees is where data disappears.

## Core Principles

- **RDB is a point-in-time snapshot; AOF is a write log.** RDB restarts fast and is
  compact but loses everything since the last snapshot. AOF loses at most one second
  (with `everysec`) but is larger and replays slower.
- **`fsync` policy sets your durability, not the mere existence of AOF.**
  `always` = per-write durability (slow); `everysec` = ≤1s loss (default);
  `no` = OS decides (fast, weakest).
- **Saving forks the process.** RDB and AOF rewrites `fork()` a child; on a large
  dataset this spikes memory (copy-on-write) and can cause latency stalls.
- **A snapshot on the same box is not a backup.** Disk failure, region loss, or a
  bad `FLUSHALL` takes the local file with it. Copy dumps off-box.
- **Restart durability depends on a clean file.** A partially written AOF is
  recoverable (`redis-check-aof`), but an unmonitored failed `bgsave` means your
  "backups" silently stopped.

## Best Practices

- For data you cannot lose, enable **AOF with `appendfsync everysec`** and also keep
  RDB on (`aof-use-rdb-preamble yes`, the modern default) for fast restarts and
  compact files. This hybrid is the recommended production setup.
- Only use `appendfsync always` when the workload genuinely requires per-write
  durability and can absorb the throughput cost; measure it, do not assume.
- If Redis is a pure cache where loss is acceptable, you may run **RDB-only or even
  persistence-off** — but state that decision explicitly, do not let it be an
  accident.
- Keep `stop-writes-on-bgsave-error yes` so Redis **refuses writes** when snapshots
  are failing, surfacing a broken backup instead of silently continuing.
- Provision headroom for the fork: keep memory usage well under 50% so
  copy-on-write during a save cannot OOM the box.
- Enable `aof-rewrite-incremental-fsync` / `rdb-save-incremental-fsync` (defaults)
  to spread `fsync` and avoid latency spikes.
- **Copy RDB/AOF files off the host** on a schedule (object storage, another
  region) and periodically test restoring from them.

## Examples

**Good Example** — durable hybrid config, fails loud on backup errors

```conf
# redis.conf — durability-first setup for data of record.
appendonly yes
appendfsync everysec            # at most ~1s of writes lost on crash
aof-use-rdb-preamble yes        # compact AOF + fast restart
save 900 1                      # RDB snapshot as a secondary, restore-friendly copy
save 300 100
stop-writes-on-bgsave-error yes # WHY: if snapshots fail, refuse writes rather than
                                # pretend the data is safe. Broken backups get noticed.
```

**Bad Example** — assumes durability that the config does not provide

```conf
# "It's persistent, we have RDB on."
appendonly no
save 3600 1                     # snapshot at most once an hour...
stop-writes-on-bgsave-error no  # ...and if that save fails, keep accepting writes anyway
# Crash 59 minutes after the last snapshot -> ~1 hour of writes gone.
# And nobody was alerted because failed saves don't stop the server.
```

```bash
# The other failure: the only copy lives on the box that just died.
ls /var/lib/redis/dump.rdb   # never copied off-host -> disk loss = total loss
```

## Common Mistakes

- Believing "AOF is on" means durable, without checking `appendfsync` (could be
  `no`).
- RDB-only with an infrequent `save` rule, then being surprised by minutes of loss.
- Running with `stop-writes-on-bgsave-error no`, so a broken backup is invisible.
- No memory headroom, so the save fork OOM-kills Redis under load.
- Treating the local dump as a backup and never copying it off-box or test-restoring.
- Disabling persistence deliberately for a cache, then later storing the system of
  record in the same instance without revisiting the config.

## Production Tips

- Alert on `rdb_last_bgsave_status:err` and `aof_last_write_status:err` from
  `INFO persistence` — a failing backup must page someone.
- Watch `rdb_last_cog_time_sec` and latency during saves; if fork stalls hurt,
  offload snapshots to a replica (`save ""` on the primary, RDB on a replica).
- Version and lifecycle off-box backups; a corrupted snapshot faithfully copied is
  not a recovery plan. Test restores on a schedule.

## AI Review Checklist

- Does the durability config match the data's importance (AOF `everysec`+ for data
  of record; RDB-only only for disposable caches)?
- Is `appendfsync` explicitly set, not left at an assumed value?
- Is `stop-writes-on-bgsave-error yes` so failed backups halt writes?
- Is there memory headroom for the copy-on-write fork during saves?
- Are dump files copied off-host and restore-tested, not just present locally?
- Are `rdb_last_bgsave_status` / `aof_last_write_status` monitored?

## Related

- `knowledge/redis/18-replication.md`
- `knowledge/redis/13-caching.md`
- `knowledge/redis/22-monitoring.md`
- `knowledge/redis/27-production.md`
