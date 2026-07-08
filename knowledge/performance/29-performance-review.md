---
id: performance/29-performance-review
topic: performance
slug: performance-review
title: "Performance Review"
type: doc
order: 29
status: ready
tags: [performance, performance-review]
related: [performance/27-best-practices, performance/24-optimization-workflow, performance/99-ai-review-checklist, performance/23-performance-budget, performance/100-common-antipatterns]
when_to_use: "Read before reviewing a pull request for performance impact so you catch regressions and unfounded optimizations."
---
# Performance Review

## Purpose

This document defines how to review code for performance: what to look for, what evidence
to demand, and how to give feedback that improves speed without blocking good work. It is
written so an agent reviewing a change can catch regressions and reject unfounded
optimizations before they reach production.

Performance review is scope-based, not paranoid. Judge a change against the load its code
will actually see, and require measurement for any claim — in either direction.

## Why It Matters

Performance regressions slip through ordinary review because the code is *correct*, just
slow — tests pass, output is right, and the cost only appears under production load or at
scale. A quadratic loop or an N+1 query looks innocent on a three-row fixture. Review is
the last cheap gate before that reaches users. Equally, review is where speculative
"optimizations" — clever, unmeasured, complexity-adding — should be stopped, because they
cost readability for a benefit nobody proved.

## Core Principles

- **Scale the scrutiny to the load.** A quadratic loop over a fixed 3-item config is fine;
  the same loop over user-supplied input is a bug. Review against realistic input size.
- **Demand evidence for optimizations.** A change justified by speed needs a before/after
  number. "Should be faster" is not a reason to accept added complexity.
- **Look for the big-O and the I/O, not the micro.** The wins and the regressions live in
  algorithmic complexity and I/O patterns, not in loop-body micro-tweaks.
- **Correctness and clarity outrank speed.** Reject optimizations that trade correctness,
  safety, or readability for an unmeasured gain.
- **Check the boundaries, not just the happy path.** Performance bugs hide at large inputs,
  cold caches, and high concurrency — the cases fixtures rarely cover.

## Best Practices

- Scan every new loop and query for **complexity and N+1**: is work per-item that should be
  batched? Is a collection scanned inside a loop? See [best practices](27-best-practices.md).
- Check that **result sets, payloads, and loops are bounded** — a missing `LIMIT` or
  pagination is a latent incident.
- For any change claiming a speedup, require a **reproducible benchmark** and confirm the
  gain exceeds noise. See [optimization workflow](24-optimization-workflow.md).
- Verify **new I/O on the request path** is necessary and cannot be batched, cached, or
  deferred to a background job.
- Confirm hot paths keep or improve their **budget/SLO**; ask for the number when a change
  touches a critical endpoint. See [performance budget](23-performance-budget.md).
- Watch for **regressions disguised as features**: an added join, a synchronous external
  call, an eager load, a serialization of a big object.
- Give **actionable, prioritized** feedback: name the input size that breaks it and the
  cheaper alternative, not "this feels slow."

## Examples

**Good Example** — a review comment that localizes and prioritizes

```text
BLOCKING — N+1 on the request path.
`load_comments()` runs one query per post (line 42). On the feed endpoint this is
50-200 posts => 50-200 serial round trips; p99 will blow the 300 ms budget under load.
Fix: batch with `WHERE post_id = ANY($ids)` and group in memory (see 13-database-performance).
Evidence to add: a benchmark on a 100-post feed before/after.
```

```python
# The change under review — the reviewer correctly flags this:
for post in feed:
    post.comments = db.query(                     # N+1: fires per post, serially
        "SELECT * FROM comments WHERE post_id = $1", post.id
    )
```

**Bad Example** — approving an unmeasured optimization

```text
LGTM, looks faster!  # <- no benchmark, no input size, no reasoning
```

```python
# Approved without evidence: replaces a clear list comp with a manual loop
# plus a hand-rolled cache "for speed" — added complexity, zero measured gain,
# and a new unbounded dict that leaks. Review should have demanded a number
# and rejected the complexity, not rubber-stamped it.
_memo = {}
def transform(items):
    out = []
    for x in items:
        if x not in _memo:                        # unbounded, never evicted
            _memo[x] = expensive(x)
        out.append(_memo[x])
    return out
```

## Common Mistakes

- Reviewing only the happy path on tiny fixtures, missing the large-input blowup.
- Approving "optimizations" with no before/after measurement.
- Flagging micro-optimizations while missing the N+1 or O(n^2) in the same diff.
- Blocking on speed at the expense of correctness, safety, or readability.
- Giving vague feedback ("this seems slow") instead of the failing input and a fix.
- Ignoring cold-cache and high-concurrency behavior because tests only run warm and serial.
- Missing new unbounded state (caches, queues, buffers) added in the name of speed.

## Production Tips

- Ask for the endpoint's current p95/p99 when a change touches a hot path; a review
  anchored to a real number beats opinion.
- Encourage a CI benchmark or budget gate so routine regressions are caught before review,
  leaving humans to judge the genuine trade-offs. See [ai review checklist](99-ai-review-checklist.md).

## AI Review Checklist

- Is each new loop/query checked for complexity and N+1 against realistic input size?
- Are result sets, payloads, and loops bounded (LIMIT/pagination present)?
- Does every speed claim come with a reproducible before/after benchmark?
- Is new request-path I/O necessary, or could it be batched/cached/deferred?
- Do hot paths still meet their budget/SLO after the change?
- Was any optimization rejected that traded correctness or clarity for an unmeasured gain?
- Is feedback specific — naming the breaking input and the concrete fix?

## Related

- `knowledge/performance/27-best-practices.md`
- `knowledge/performance/24-optimization-workflow.md`
- `knowledge/performance/99-ai-review-checklist.md`
- `knowledge/performance/23-performance-budget.md`
- `knowledge/performance/100-common-antipatterns.md`
