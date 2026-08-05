---
id: redis/29-tooling
topic: redis
slug: tooling
title: "Redis Tooling"
type: doc
order: 29
status: ready
tags: [redis, tooling]
related: [redis/01-installation, redis/23-performance, redis/25-debugging, redis/28-observability, redis/26-best-practices]
when_to_use: "Read when choosing a Redis client library, CLI, benchmark, or inspection tool for development or operations."
---
# Redis Tooling

## Purpose

This document defines the tools to use with Redis — client libraries, the CLI,
benchmarking, inspection, and dashboards — and which one fits which job. It exists
so an agent picks a maintained, correct tool (e.g. `SCAN`-based inspection, an async
client with pooling) instead of reinventing it or reaching for something unsafe.

## Why It Matters

The wrong tool with Redis is dangerous, not just inconvenient. A benchmark run
against the production instance adds load; a client without connection pooling
collapses throughput; `redis-cli KEYS` on a live server blocks it. Meanwhile the
right tool answers the question instantly: `--bigkeys` finds the memory hog,
`redis-benchmark` validates capacity, RedisInsight visualizes the keyspace. Choosing
maintained, purpose-built tooling is the difference between a safe five-minute check
and an accidental outage.

## Core Principles

- **Use a maintained, idiomatic client with pooling.** The official/community
  client for your language handles reconnection, pipelining, and Cluster routing far
  better than anything hand-rolled.
- **Use non-blocking inspection.** `redis-cli --bigkeys`, `--memkeys`, `--hotkeys`,
  and `SCAN` sample without freezing the server; `KEYS`/`MONITOR` do not.
- **Benchmark against a scratch instance, never production.** Load-generating tools
  compete with real traffic on the single thread.
- **Prefer the CLI's built-in analyzers over custom scripts.** They are tested and
  cluster-aware; a homemade loop of `MEMORY USAGE` is slow and easy to get wrong.
- **Pin tool and client versions to the server major version.** Cluster and command
  behaviour differs across versions.

## Best Practices

- Client libraries — pick the maintained one and enable pooling and timeouts:
  - Python: `redis-py` (async via `redis.asyncio`).
  - Node.js: `ioredis` (Cluster/Sentinel support) or `node-redis`.
  - Java: Lettuce (async/reactive, preferred) or Jedis.
  - Go: `go-redis`.
  Configure a connection pool, socket timeout, and command timeout on all of them.
- `redis-cli` for interactive work: `--bigkeys` (find large keys), `--memkeys`
  (memory by key), `--hotkeys` (needs LFU policy), `--scan --pattern` for safe
  iteration, and `--latency`/`--latency-history` for RTT sampling.
- `redis-benchmark` for capacity checks — always against a disposable instance, with
  a realistic pipeline depth (`-P`) and command mix, not the default `SET`/`GET` only.
- RedisInsight (official GUI) to browse the keyspace, inspect types/TTLs, run
  `SLOWLOG` and profiling visually during development or an incident.
- `redis_exporter` + Prometheus + Grafana for continuous metrics (see observability).
- For offline analysis, dump RDB and inspect with an RDB parser rather than scanning
  a live server; keep the analysis off the production node.

## Examples

**Good Example** — safe inspection and a scratch-instance benchmark

```bash
# Find the memory hogs without blocking the server (samples via SCAN internally).
redis-cli --bigkeys
redis-cli --memkeys                     # ranks keys by memory

# Iterate a pattern safely — cursor-based, never blocks like KEYS.
redis-cli --scan --pattern 'session:*' | head

# Benchmark a THROWAWAY instance with a realistic pipeline depth.
redis-benchmark -h 127.0.0.1 -p 6390 -P 16 -n 100000 -t get,set,lpush
```

```python
# Idiomatic pooled client — reconnection, timeouts, and pooling handled for you.
import redis
pool = redis.ConnectionPool(host="10.0.0.5", port=6379,
                            socket_timeout=1, socket_connect_timeout=1,
                            max_connections=50)     # bounded pool, explicit timeouts
r = redis.Redis(connection_pool=pool, decode_responses=True)
```

**Bad Example** — unsafe tooling on production

```bash
# Benchmarks the LIVE server, stealing capacity from real traffic on the single thread.
redis-benchmark -h prod-redis -n 1000000

# Blocks the server for the full scan — the command you should never run on prod.
redis-cli -h prod-redis KEYS '*' > keys.txt
```

```python
# New connection per call: no pool, no timeout -> throughput collapses under load,
# and a hung socket blocks the request forever.
def get(k):
    return redis.Redis(host="10.0.0.5").get(k)   # reconnects every call
```

## Common Mistakes

- Running `redis-benchmark` or `MONITOR` against production, adding load during triage.
- `redis-cli KEYS '*'` instead of `--scan`/`--bigkeys` for inspection.
- A hand-rolled client without pooling, reconnection, or timeouts.
- Benchmarking with only default `GET`/`SET` and no pipelining, then trusting numbers
  that do not reflect the real workload.
- Analyzing memory by looping `MEMORY USAGE` over a live keyspace instead of
  `--memkeys` or offline RDB analysis.
- Using a client version incompatible with the server's Cluster behaviour.

## Production Tips

- Keep RedisInsight or an equivalent read-only GUI available for incidents; visual
  `SLOWLOG` and keyspace inspection speeds diagnosis under pressure.
- Automate a periodic `--bigkeys`/`--memkeys` report against a replica (not the
  primary) to catch growing keys before they hurt.
- Standardize one client library and pool configuration across services so timeout
  and reconnection behaviour is uniform and reviewable.

## AI Review Checklist

- Does the app use a maintained client library with connection pooling and explicit timeouts?
- Is inspection done with `SCAN`/`--bigkeys`/`--memkeys`, never `KEYS` or `MONITOR` on prod?
- Are benchmarks run against a disposable instance with a realistic command mix and pipelining?
- Is memory analysis done via built-in analyzers or offline RDB parsing, not live loops?
- Are client and tool versions compatible with the server major version and Cluster mode?

## Related

- `knowledge/redis/01-installation.md`
- `knowledge/redis/23-performance.md`
- `knowledge/redis/25-debugging.md`
- `knowledge/redis/28-observability.md`
- `knowledge/redis/26-best-practices.md`
