---
id: performance/05-network
topic: performance
slug: network
title: "Network"
type: doc
order: 5
status: ready
tags: [performance, network]
related: [performance/01-performance-fundamentals, performance/14-api-performance, performance/08-caching, performance/13-database-performance, performance/07-loading]
when_to_use: "Read when a profile shows the process is waiting on I/O — round-trips, payload size, or connection setup dominate."
---
# Network

## Purpose

This document covers network-bound performance: reducing the number of round-trips, the
size of payloads, and the cost of connection setup. It applies whenever a system is *waiting*
rather than *working* — calling databases, services, or third-party APIs, and shipping bytes
to browsers.

On the network, latency is dominated by round-trips, not bandwidth. The core skill is
making fewer, larger, reusable, well-cached calls.

## Why It Matters

Network waiting is the most common bottleneck in real backends, and it hides from CPU
profilers — the process looks idle while the request sits at 800ms. Round-trips are
brutal because they *serialize*: ten sequential 20ms calls is 200ms of pure waiting no
faster CPU can help. Worse, the classic N+1 pattern turns one logical operation into
hundreds of round-trips, and it scales with data, so it passes tests and melts in
production. Fixing network shape is usually the largest single latency win available.

## Core Principles

- **Round-trips dominate.** Each request pays latency once regardless of size. Reducing
  *count* beats reducing *bytes* for most latency problems.
- **Batch and parallelize.** Combine N calls into one (batch endpoint, `IN` query,
  multi-get); when calls are independent, issue them concurrently instead of in series.
- **Reuse connections.** TCP + TLS setup is several round-trips. Use keep-alive / pooled
  connections and HTTP/2 multiplexing; never open a fresh connection per call.
- **Cache to eliminate the call entirely.** The fastest request is the one not made — see
  [caching](08-caching.md).
- **Shrink and compress payloads.** Return only needed fields; enable gzip/brotli;
  paginate. Smaller bodies help the tail on slow links.
- **Fail fast and isolate.** Every remote call needs a timeout and a retry/backoff policy;
  a slow dependency must not hang the caller indefinitely.

## Best Practices

- Eliminate **N+1** calls: fetch related data in one batched request, not one per item.
  This is the highest-value network fix in most services.
- Run **independent** remote calls concurrently (`Promise.all`, `asyncio.gather`,
  goroutines) so their latencies overlap instead of summing.
- Use a **connection pool** with keep-alive for DBs and HTTP clients; size it and reuse it.
- Set an explicit **timeout** on every call and a bounded **retry with jittered backoff**;
  never retry non-idempotent calls blindly.
- **Compress** responses and request only the fields you need (projection, GraphQL
  selection, sparse fieldsets). Paginate large collections.
- Cache at the right layer (CDN, HTTP cache headers, application cache) with correct
  `Cache-Control` / `ETag`. See [api-performance](14-api-performance.md).
- Add a **circuit breaker** so a failing dependency sheds load instead of amplifying it.

## Examples

**Good Example** — one batched call, then concurrent independent calls

```js
// Batch: one round-trip for all users instead of one per id.
const users = await db.query("SELECT * FROM users WHERE id = ANY($1)", [ids]);

// Independent calls run concurrently — total time ≈ the slowest, not the sum.
const [profile, prefs] = await Promise.all([
  api.get(`/profile/${userId}`, { timeout: 500 }),
  api.get(`/prefs/${userId}`, { timeout: 500 }),
]);
```

**Bad Example** — N+1 and serialized round-trips

```js
const users = [];
for (const id of ids) {
  // One round-trip per id: N sequential waits that sum. 200 ids × 20ms = 4s.
  users.push(await db.query("SELECT * FROM users WHERE id = $1", [id]));
}

// These do not depend on each other but run in series, doubling the latency.
const profile = await api.get(`/profile/${userId}`); // no timeout: can hang forever
const prefs = await api.get(`/prefs/${userId}`);
```

## Common Mistakes

- **N+1** queries or API calls — one round-trip per item instead of one batched call.
- Awaiting independent calls sequentially instead of running them concurrently.
- Opening a new connection per request instead of using a keep-alive pool.
- No timeout on remote calls, so one slow dependency hangs every request.
- Retrying aggressively without backoff/jitter, turning a blip into a retry storm.
- Shipping full objects and uncompressed payloads when a projection would do.
- Chatty designs that require many small calls where one coarse-grained call fits.

## Production Tips

- Trace requests end-to-end (distributed tracing) to see where the round-trips actually go;
  a waterfall view exposes serial calls that should be parallel.
- Set client-side timeouts *below* the caller's own SLA so failures surface as errors, not
  hangs.
- Guard critical dependencies with circuit breakers and bulkheads so one slow service does
  not exhaust the connection pool for all traffic.

## AI Review Checklist

- Are related fetches batched into one call rather than N+1 per-item calls?
- Do independent remote calls run concurrently instead of in series?
- Are connections pooled/kept-alive rather than opened per request?
- Does every remote call have an explicit timeout and a bounded, jittered retry?
- Are responses compressed and projected to only the needed fields?
- Is caching applied where the same request repeats, and is a circuit breaker present for
  critical dependencies?

## Related

- `knowledge/performance/01-performance-fundamentals.md`
- `knowledge/performance/14-api-performance.md`
- `knowledge/performance/08-caching.md`
- `knowledge/performance/13-database-performance.md`
- `knowledge/performance/07-loading.md`
