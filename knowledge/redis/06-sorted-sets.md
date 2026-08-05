---
id: redis/06-sorted-sets
topic: redis
slug: sorted-sets
title: "Sorted Sets"
type: doc
order: 6
status: ready
tags: [redis, sorted-sets, EXPIRE, LIMIT, ZREMRANGEBYSCORE, ZADD, zset-max-listpack-entries, ZRANGEBYSCORE]
related: [redis/05-sets, redis/07-hashes, redis/14-rate-limiting, redis/23-performance, redis/100-common-antipatterns]
when_to_use: "Read before building leaderboards, priority queues, rate limiters, or any range-by-rank/score query in Redis."
---
# Sorted Sets

## Purpose

This document defines how to use the Redis **sorted set** (`ZSET`): a collection of
unique members, each tied to a floating-point **score**, kept ordered by score. It is
written so an agent can pick a sorted set when — and only when — ordering by a numeric
key is the actual requirement, and can write commands that stay fast at scale.

A sorted set is a [set](05-sets.md) plus an ordering. Every member is unique (set
semantics), and Redis maintains members in score order so range queries by rank or by
score run in `O(log N)`. Reach for it when you need "top N", "items between two scores",
or "rank of X" — not merely for storing a group.

## Why It Matters

Sorted sets are the data type teams most often reimplement badly. The naive alternative —
load everything into the application and sort it — is `O(N)` memory and CPU per query and
falls over the moment the collection grows. A sorted set pushes ordering into Redis, where
inserts and range reads are logarithmic. Get the type right and a leaderboard over ten
million players answers in microseconds; get it wrong (a list you re-sort, a hash you scan)
and the same feature times out. Because sorted sets also underpin rate limiters and delay
queues, a mistake here is not cosmetic — it silently drops or double-counts events.

## Core Principles

- **Score is the sort key, member is the identity.** `ZADD key score member`. Two members
  with the same score break ties lexicographically by member. Design the score so the
  natural ordering falls out for free.
- **Members are unique; scores are not.** Re-adding an existing member updates its score in
  place, it does not create a duplicate. Use this for idempotent upserts.
- **Reads come in two families: by rank and by score.** `ZRANGE`/`ZREVRANGE` index by
  position; `ZRANGEBYSCORE`/`ZRANGE ... BYSCORE` filter by value. Know which you need.
- **Most operations are `O(log N)` plus the size of the result.** The cost you control is
  the *result count*, not the set size. Always bound ranges with `LIMIT` or explicit stops.
- **Prefer atomic combined commands.** `ZADD ... GT`, `ZINCRBY`, `ZPOPMIN`, and
  `ZRANGESTORE` do read-modify-write in one round trip — no race, no [transaction](10-transactions.md) needed.

## Best Practices

- Use `ZADD key GT score member` to keep only the **highest** score seen (leaderboards,
  high-water marks); `LT` for the lowest. This avoids a read-compare-write race entirely.
- Use `ZINCRBY` to accumulate counters (points, event counts) atomically instead of
  `ZSCORE` + `ZADD`, which races under concurrency.
- For "top N", use `ZRANGE key 0 N-1 REV WITHSCORES` (Redis 6.2+ unified syntax). It is
  `O(log N + M)` where M is N, not the set size.
- Bound every score range with a `LIMIT offset count`. An unbounded `ZRANGEBYSCORE -inf
  +inf` can return the whole set and block the server.
- Model **time-based queues** by using a timestamp as the score: `ZADD queue <due_ts> job`,
  then `ZRANGEBYSCORE queue -inf <now> LIMIT 0 N` to claim due jobs. Pair with `ZREM`.
- Set a TTL on the key with [`EXPIRE`](12-expiration.md) for sliding-window data (rate
  limiters, recent activity) so old sets do not accumulate unbounded memory.
- Prefer `ZPOPMIN`/`ZPOPMAX` (or the blocking `BZPOPMIN`) for priority-queue consumption —
  they read and remove the extreme member atomically.

## Examples

**Good Example** — atomic leaderboard update and bounded top-N read

```bash
# Keep the player's BEST score only; GT updates only if the new score is higher.
# One round trip, no read-modify-write race between concurrent game servers.
ZADD leaderboard GT 4200 player:42

# Top 10 with scores, highest first. O(log N + 10) — cost is the page, not the set.
ZRANGE leaderboard 0 9 REV WITHSCORES

# This player's rank (0-based from the top). O(log N).
ZREVRANK leaderboard player:42
```

**Bad Example** — read-modify-write race and an unbounded scan

```bash
# Two servers both read 4100, both write their +100 — one update is lost.
ZSCORE leaderboard player:42        # -> "4100"
ZADD   leaderboard 4200 player:42   # racy: clobbers a concurrent higher score

# Returns the ENTIRE set to the client, then the app sorts/slices in memory.
# O(N) transfer, O(N log N) app-side sort — melts at scale.
ZRANGEBYSCORE leaderboard -inf +inf
```

## Common Mistakes

- Using `ZSCORE` + `ZADD` to update a max instead of `ZADD ... GT` — loses concurrent updates.
- Unbounded `ZRANGEBYSCORE -inf +inf` (no `LIMIT`), pulling the whole set and blocking Redis.
- Storing large JSON blobs as members: the member string is copied on every range read.
  Store an id as the member and the payload in a [hash](07-hashes.md) keyed by that id.
- Assuming ranks are stable across concurrent writes — a rank is a snapshot, not a handle.
- Forgetting that equal scores sort lexicographically, then relying on insertion order.
- Letting sliding-window sets grow forever because no `EXPIRE` or trimming `ZREMRANGEBYSCORE`
  was set.

## Production Tips

- For very large sorted sets, watch the `zset-max-listpack-entries` threshold: below it Redis
  uses a compact listpack encoding; above it, a skiplist. Bulk-loading past the threshold
  changes memory profile — size it deliberately.
- Trim time-windowed sets on write: `ZREMRANGEBYSCORE key -inf <now - window>` keeps the set
  bounded and keeps range scans cheap.
- Combine sets with `ZUNIONSTORE`/`ZINTERSTORE` (with per-set `WEIGHTS`) for aggregate
  leaderboards, but write the result to a new key and `EXPIRE` it — these are `O(N)`.

## AI Review Checklist

- Is a sorted set actually needed, or would a plain [set](05-sets.md) or [hash](07-hashes.md) do?
- Are max/min updates done with `ZADD GT`/`LT` or `ZINCRBY`, not a read-modify-write pair?
- Does every score range carry a `LIMIT` (or a tight `min`/`max`) to bound the result?
- Are members small identifiers, with bulky payloads stored elsewhere?
- Do sliding-window keys have an `EXPIRE` or a trimming `ZREMRANGEBYSCORE`?
- Is queue consumption done atomically via `ZPOPMIN`/`BZPOPMIN` rather than range-then-`ZREM`?

## Related

- `knowledge/redis/05-sets.md`
- `knowledge/redis/07-hashes.md`
- `knowledge/redis/14-rate-limiting.md`
- `knowledge/redis/23-performance.md`
- `knowledge/redis/100-common-antipatterns.md`
