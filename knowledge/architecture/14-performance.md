---
id: architecture/14-performance
topic: architecture
slug: performance
title: "Performance"
type: doc
order: 14
status: ready
tags: [architecture, performance]
related: [architecture/13-scalability, architecture/19-caching-strategies, architecture/18-observability, architecture/21-distributed-systems, architecture/20-message-brokers]
when_to_use: "Read before optimizing latency or throughput, or when a system feels slow and you need to find why."
---
# Performance

## Purpose

This document defines how to make a single request fast and a system efficient:
measuring latency and throughput, finding the real bottleneck, and avoiding the
patterns that quietly make code slow. It is written so an agent can improve
performance based on evidence rather than folklore, and stop when it is fast enough.

Performance (speed of one request) is distinct from [scalability](13-scalability.md)
(capacity under load). A fast system can still fail to scale, and a scalable system can
still be slow. This doc is about latency and efficiency; that one is about growth.

## Why It Matters

Latency is a feature users feel on every interaction — added milliseconds directly cost
conversions and retention, and a slow tail (p99) is what people remember. Beyond user
experience, wasted CPU and I/O are wasted money at scale. But the more dangerous failure
is optimizing blind: engineers routinely spend days speeding up code that was never the
bottleneck while the real culprit — usually a database query or a network round trip —
goes untouched. Performance work without measurement is guessing, and guessing is how you
add complexity for no gain. Measure first, always.

## Core Principles

- **Measure before you optimize.** Profile the real workload and find where time actually
  goes. Intuition about hot spots is wrong often enough that acting on it wastes effort
  and adds risk.
- **Optimize the bottleneck, not the easy part.** By Amdahl's law, speeding up code that
  is 5% of runtime can help by at most 5%. Fix the dominant cost first.
- **Most latency is I/O, not CPU.** Database queries, network calls, and disk dominate.
  Reducing round trips beats micro-optimizing loops almost every time.
- **Watch the tail, not just the average.** The mean hides the p99 that determines whether
  the system feels fast. Optimize and alert on percentiles.
- **Set a target, then stop.** "Fast enough" is a number (e.g. p99 < 200ms). Past it,
  further optimization trades real complexity for invisible gains.

## Best Practices

- Fix N+1 queries: fetch related data in one query (join or batched `IN`), never one query
  per row in a loop. This is the single most common source of avoidable latency.
- Cache expensive, repeatable computations and reads, but only after measuring — a cache
  adds invalidation complexity and staleness (see [caching-strategies](19-caching-strategies.md)).
- Index the columns you filter and join on; verify with the query planner (`EXPLAIN`) that
  indexes are actually used, and remove indexes that only slow writes.
- Do slow, non-critical work asynchronously (email, thumbnails, analytics) so it stays off
  the request's critical path.
- Batch and paginate: never load an unbounded result set into memory; stream or page it.
- Set explicit timeouts and budgets per downstream call so one slow dependency cannot
  blow the whole request's latency target.
- Benchmark on representative data volumes. Code that is fast on 100 rows can be quadratic
  and unusable on 100,000.

## Examples

**Good Example** — one batched query, work off the critical path

```python
# Fetch all authors in ONE query keyed by the posts we have. WHY: constant number
# of round trips regardless of post count, so latency stays flat as data grows.
def list_posts() -> list[PostView]:
    posts = db.query("SELECT id, author_id, title FROM posts LIMIT 50")
    author_ids = {p.author_id for p in posts}
    authors = db.query(
        "SELECT id, name FROM authors WHERE id = ANY(%s)", [list(author_ids)]
    )
    by_id = {a.id: a for a in authors}
    enqueue_view_analytics(posts)  # non-critical work moved off the request path
    return [PostView(p, by_id[p.author_id]) for p in posts]
```

**Bad Example** — N+1 queries, synchronous side work

```python
def list_posts():
    posts = db.query("SELECT id, author_id, title FROM posts LIMIT 50")
    views = []
    for p in posts:
        # One query PER post: 50 posts = 51 round trips. Latency grows linearly
        # with result size and the DB becomes the bottleneck.
        author = db.query("SELECT name FROM authors WHERE id = %s", [p.author_id])
        log_analytics_sync(p)  # blocks the response on non-critical work
        views.append(PostView(p, author))
    return views
```

## Common Mistakes

- Optimizing without profiling, then discovering the "hot" code was 2% of runtime.
- N+1 query loops hidden behind a lazy-loading ORM relationship.
- Caching to hide a slow query instead of fixing the query or its index.
- Reading percentages of the mean while the p99 tail — the number users feel — is ignored.
- Loading entire tables into application memory instead of paginating or streaming.
- Premature micro-optimization (bit tricks, manual loops) that adds complexity while I/O
  dominates the actual time.
- Benchmarking on toy data, so a quadratic algorithm ships and only fails in production.

## Production Tips

- Instrument latency as histograms and alert on p95/p99, not averages
  (see [observability](18-observability.md)).
- Capture slow-query logs and trace spans so a regression points to a specific query or hop.
- Add a performance budget check in CI for critical endpoints so a regression fails the
  build instead of reaching users.
- Re-profile after each optimization; the bottleneck moves, and the next fix is somewhere new.

## AI Review Checklist

- Was the bottleneck identified by measurement (profile, trace, EXPLAIN) before optimizing?
- Are there N+1 query loops that should be a single batched query?
- Are filtered/joined columns indexed, and are the indexes actually used?
- Is non-critical work moved off the request's critical path (async)?
- Are result sets bounded (pagination/streaming) rather than fully loaded into memory?
- Are latency targets defined as percentiles (p99), and does the design meet them?
- Was the change validated against representative data volumes?

## Related

- `knowledge/architecture/13-scalability.md`
- `knowledge/architecture/19-caching-strategies.md`
- `knowledge/architecture/18-observability.md`
- `knowledge/architecture/21-distributed-systems.md`
- `knowledge/architecture/20-message-brokers.md`
