---
id: php/18-generators
topic: php
slug: generators
title: "Generators"
type: doc
order: 18
status: ready
tags: [php, generators, Generator, fopen, RuntimeException, yield, fclose]
related: [php/03-functions, php/14-performance, php/10-files, php/12-database]
when_to_use: "Read before iterating over large datasets, streaming files, or building lazy pipelines in PHP."
---
# Generators

## Purpose

This document defines when and how to use PHP generators — functions that `yield`
values one at a time instead of building a full array in memory. It is written so an
agent can replace memory-hungry array code with lazy iteration without changing the
consumer, and can recognize the cases where a generator is the wrong tool.

A generator is any function containing `yield`. Calling it does not run the body; it
returns a `Generator` object that produces values on demand as you iterate.

## Why It Matters

The difference between a generator and an array is memory. An array of one million
rows holds all million in RAM at once; a generator holds one. For file streaming, large
database result sets, and API pagination, that is the difference between a stable process
and an out-of-memory fatal. Generators also express intent: they make "this is a stream,
consume it as you go" explicit, which prevents the accidental `foreach` that materializes
gigabytes. The cost is that a generator can be walked only once and cannot be indexed —
so choosing it is a real trade-off, not a free optimization.

## Core Principles

- **Yield when the full result set need not exist at once.** Generators trade random
  access for constant memory. If the caller only iterates forward, prefer a generator.
- **A generator is single-use.** Once iterated to the end, it is exhausted. You cannot
  rewind it or count it without consuming it. Do not pass one where an array is expected.
- **Laziness is deferred, not free.** The body runs only as the consumer pulls values,
  so exceptions and side effects surface during iteration, not at call time.
- **`yield from` delegates.** Use it to compose generators or flatten nested sources
  without manually re-yielding each element.
- **Return type is `Generator` or `iterable`.** Type-hint producers as `iterable` so
  callers may pass either an array or a generator interchangeably.

## Best Practices

- Type producers that stream as `: iterable` and consumers as `iterable $items`, so the
  contract does not lock the caller into arrays.
- Use generators for unbounded or externally-bounded sequences: reading a file line by
  line, cursoring a DB result, walking paginated API responses.
- Prefer `yield from` over nested loops when merging sub-sequences; it also forwards keys.
- Wrap resource acquisition so the resource is closed even if the consumer stops early —
  a `finally` inside the generator runs when the generator is destroyed.
- When you genuinely need an array (to count, sort, or index), convert explicitly with
  `iterator_to_array()` and accept the memory cost consciously.
- Keep a generator's keys meaningful, or expect duplicate keys: `iterator_to_array()`
  preserves keys by default and will silently collapse collisions unless you pass `false`.

## Examples

**Good Example** — constant-memory streaming with guaranteed cleanup

```php
/**
 * Streams a CSV one row at a time. Memory stays flat regardless of file size.
 * @return iterable<int, array<string>>
 */
function readCsv(string $path): iterable
{
    $handle = fopen($path, 'rb');
    if ($handle === false) {
        throw new RuntimeException("Cannot open {$path}");
    }
    try {
        while (($row = fgetcsv($handle)) !== false) {
            yield $row; // one row in memory at a time, not the whole file
        }
    } finally {
        fclose($handle); // runs even if the consumer breaks out of the loop early
    }
}

foreach (readCsv('huge.csv') as $row) {
    process($row);
}
```

**Bad Example** — materializes the whole file, leaks the handle

```php
function readCsv(string $path): array
{
    $handle = fopen($path, 'rb');
    $rows = [];
    while (($row = fgetcsv($handle)) !== false) {
        $rows[] = $row; // every row held in RAM — OOM on large files
    }
    // no fclose: the handle leaks until GC, and there is no early-exit cleanup
    return $rows;
}
```

## Common Mistakes

- Calling `count()`, `array_map()`, or indexing (`$gen[0]`) on a generator — these do
  not work; the generator must be consumed with `foreach` or `iterator_*` helpers.
- Iterating the same generator twice and getting nothing the second time, because it is
  exhausted. Rebuild it or convert to an array first.
- Returning a generator from a method typed `: array`, which fatals at runtime.
- Forgetting `finally`, so a `break` in the consumer leaves file handles or DB cursors open.
- Using `iterator_to_array()` on an unbounded generator, reintroducing the OOM you avoided.
- Ignoring that keys can repeat, then losing rows when converting to an array.

## Production Tips

- For streaming HTTP responses or CLI output, generators pair well with `flush()` so
  the client sees data before the full set is computed.
- Profile with `memory_get_peak_usage()` before and after switching to a generator to
  confirm the win, and to catch an accidental `iterator_to_array()` upstream.
- A generator's `finally` runs on destruction; in long-lived workers, unset the generator
  or let it fall out of scope promptly so cleanup happens deterministically.

## AI Review Checklist

- Is the producer typed `iterable`/`Generator`, and does no consumer index or `count()` it?
- Are file handles, DB cursors, and locks released in a `finally` inside the generator?
- Is the generator iterated exactly once, or explicitly converted when reuse is needed?
- Does any `iterator_to_array()` call run on a bounded sequence only?
- Would an array have been simpler here, and is the laziness actually needed?

## Related

- `knowledge/php/03-functions.md`
- `knowledge/php/14-performance.md`
- `knowledge/php/10-files.md`
- `knowledge/php/12-database.md`
