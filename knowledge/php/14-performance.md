---
id: php/14-performance
topic: php
slug: performance
title: "PHP Performance"
type: doc
order: 14
status: ready
tags: [php, performance]
related: [php/12-database, php/18-generators, php/27-production, php/15-testing]
when_to_use: "Read before optimizing PHP code or diagnosing a slow request, high memory use, or a scaling problem."
---
# PHP Performance

## Purpose

This document defines how to make PHP fast and memory-efficient without guessing: what
the runtime does per request, which patterns cost the most, and how to measure before
you change anything. It covers OPcache, the request lifecycle, database round-trips,
memory-streaming with generators, and caching. The goal is correct optimization —
faster code that still produces the same result.

## Why It Matters

PHP's share-nothing model rebuilds the world on every request, so small per-request
costs multiply by traffic and by workers. A single unindexed query, an N+1 loop, or a
`fetchAll()` on a large table will not show up on a developer's machine but will exhaust
memory or saturate the pool in production. Optimizing the wrong thing is worse than
doing nothing: it adds complexity and risk for no gain. The discipline that matters is
measuring first — real bottlenecks are almost never where intuition points.

## Core Principles

- **Measure before you optimize.** Profile with real data (Xdebug, XHProf, Blackfire,
  or Tideways) and change only what the profile proves is hot.
- **The database is almost always the bottleneck, not PHP.** One extra round-trip costs
  more than thousands of lines of PHP. Fix query count and indexes first.
- **OPcache is mandatory in production.** Without it, PHP recompiles every file on every
  request. This is the single biggest, cheapest win.
- **Stream, don't accumulate.** Process large datasets with generators so memory stays
  flat instead of growing with input size.
- **Cache the expensive and stable.** Cache results of costly, rarely-changing work — but
  only with a correct invalidation story, or you trade speed for stale bugs.

## Best Practices

- Enable OPcache with `opcache.enable=1`, a generous `opcache.memory_consumption`, and
  `opcache.validate_timestamps=0` in production (revalidate only on deploy). Consider
  `opcache.jit` for CPU-bound workloads; it rarely helps typical I/O-bound web requests.
- Eliminate N+1 queries: load related rows in one query (`JOIN` or `WHERE id IN (...)`),
  never inside a loop. This is the most common real PHP performance bug.
- Return a `Generator` (`yield`) from functions that produce large sequences so callers
  process one item at a time instead of materializing a full array.
- Prefer `foreach` over building intermediate arrays; avoid `array_merge()` inside loops
  (it reallocates each iteration — `O(n^2)`). Append with `$out[] =` instead.
- Use built-in array/string functions (`array_column`, `array_map`) — they run in C and
  beat hand-rolled PHP loops, but do not sacrifice readability for micro-gains.
- Add a cache layer (APCu for per-node, Redis/Memcached for shared) for expensive reads;
  always pair it with an explicit TTL and invalidation on write.
- Batch external calls and set timeouts; a slow third-party API blocks the whole worker.
- Release large variables (`unset()`) inside long-running CLI/queue workers to keep the
  memory ceiling flat over many jobs.

## Examples

**Good Example** — generator streams a large file at flat memory

```php
// Yields one row at a time; memory stays constant no matter how big the file is.
function readRows(string $path): Generator
{
    $fh = fopen($path, 'rb');
    try {
        while (($line = fgets($fh)) !== false) {
            yield str_getcsv($line);
        }
    } finally {
        fclose($fh); // always released, even on early break/exception
    }
}

foreach (readRows('huge.csv') as $row) {
    process($row); // handles millions of rows without loading them all
}
```

**Bad Example** — loads everything, then N+1 queries

```php
// Reads the entire file into RAM — a 2GB file needs 2GB+ before the loop even starts.
$rows = array_map('str_getcsv', file('huge.csv'));

foreach ($rows as $row) {
    // A separate query per row: 10,000 rows = 10,000 round-trips.
    $user = $pdo->query("SELECT * FROM users WHERE id = {$row[0]}")->fetch();
    process($user);
}
```

## Common Mistakes

- Running production without OPcache, paying full recompilation on every request.
- N+1 queries: one query per loop iteration instead of one query for the whole set.
- `fetchAll()` or `file()` on unbounded data, blowing the memory limit.
- `array_merge()` (or string `.=` on huge buffers) inside a loop, creating quadratic cost.
- Optimizing PHP micro-details (loop unrolling, `++$i` vs `$i++`) while a slow query or
  missing index dominates the request — effort spent where it does not matter.
- Caching without invalidation, serving stale data that reads as a correctness bug.
- Adding a cache to hide a query that a single index would make instantly fast.

## Production Tips

- Keep OPcache statistics under watch; a full or thrashing cache silently slows every
  request. Warm it and reset it as part of deploy, not lazily under traffic.
- Profile a representative production trace periodically, not just when something breaks —
  regressions creep in with features.
- Set `memory_limit`, `max_execution_time`, and per-query timeouts so one pathological
  request degrades gracefully instead of taking down the pool.
- Move slow, non-interactive work (email, image processing, reports) to a queue so web
  requests return fast.

## AI Review Checklist

- Is there a profile or benchmark justifying this optimization, or is it a guess?
- Does any loop issue a query per iteration (N+1) instead of a single batched query?
- Are large datasets streamed with generators rather than loaded fully into memory?
- Is OPcache assumed enabled, and does the change respect its deploy-time revalidation?
- Are `array_merge`/string concatenation kept out of hot loops?
- Does every cache have an explicit TTL and a correct invalidation path?
- Are external calls timed out and, where slow, offloaded to a queue?

## Related

- `knowledge/php/12-database.md`
- `knowledge/php/18-generators.md`
- `knowledge/php/27-production.md`
- `knowledge/php/15-testing.md`
