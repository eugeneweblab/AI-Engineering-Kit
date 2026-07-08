---
id: performance/19-benchmarking
topic: performance
slug: benchmarking
title: "Benchmarking"
type: doc
order: 19
status: ready
tags: [performance, benchmarking]
related: [performance/16-profiling, performance/02-metrics, performance/22-load-testing, performance/03-cpu, performance/24-optimization-workflow]
when_to_use: "Read before writing a microbenchmark or claiming one implementation is faster than another."
---
# Benchmarking

## Purpose

This document defines how to measure the performance of a specific piece of code
*correctly*: warmup, repetition, statistical comparison, and controlling the environment.
It exists so an agent can prove a change is faster with a number that survives scrutiny,
instead of a single noisy run that means nothing.

Benchmarking is narrow by design. It answers "is version A faster than version B for this
operation?" It does not tell you *what* to optimize — that is [profiling](16-profiling.md)
— and it does not model real traffic — that is [load testing](22-load-testing.md).

## Why It Matters

A naive benchmark lies confidently. Run a function once and it includes JIT warmup, a cold
cache, and whatever the OS scheduler happened to do — variance easily larger than the
effect you are measuring. Engineers then "optimize" based on noise, ship a change that is
actually slower, and trust the wrong number for years. A benchmark is only useful if its
signal exceeds its noise; getting there requires deliberate method, not just a timer
around a loop.

## Core Principles

- **Warm up before you measure.** Managed runtimes (JIT, JVM, V8) and CPU caches need
  iterations before reaching steady state. Discard warmup runs or the first result is
  measuring the compiler, not the code.
- **Repeat and report a distribution.** One run is an anecdote. Run many, report median
  and variance, and only believe a difference that exceeds the noise.
- **Compare, don't just measure.** An absolute nanosecond count is meaningless across
  machines. Benchmark A and B on the *same* box in the *same* run and compare relatively.
- **Isolate the environment.** No background load, fixed CPU frequency (disable
  turbo/thermal throttling where possible), and pinned dependencies. An unstable machine
  produces unstable numbers.
- **Beware dead-code elimination.** If a benchmark's result is unused, the optimizer may
  delete the very code you are timing. Consume the output so it cannot be removed.
- **Benchmark realistic inputs.** A hash map is fast on 10 keys and different on 10
  million. Measure at the size and distribution you actually run at.

## Best Practices

- Use a real benchmarking harness (`pytest-benchmark`, JMH, `Benchmark.js`, Go's
  `testing.B`, Criterion) — it handles warmup, iteration count, and statistics for you.
  Do not hand-roll a `time()` loop.
- Report **relative** change with a confidence interval ("B is 1.8x ± 0.05 faster"), not
  a bare number, so a reviewer can judge significance.
- Pin the input, the machine, and the dependency versions; record them beside the result
  so it is reproducible.
- Run the two variants **interleaved**, not A-then-B, so a mid-run thermal or scheduler
  drift affects both equally.
- Keep microbenchmarks aligned with reality: verify the win survives at production input
  sizes and, ideally, in an end-to-end [load test](22-load-testing.md).
- Store benchmark results and track them over time so a regression is a diff, not a
  surprise.

## Examples

**Good Example** — harness handles warmup, stats, and prevents elimination

```python
# pytest-benchmark: warms up, runs many rounds, reports median + stddev automatically.
def test_parse_speed(benchmark):
    data = load_fixture("realistic_100k.json")  # production-scale input, not a toy
    result = benchmark(parse, data)             # return value is consumed → not optimized away
    assert result.count == 100_000              # correctness gate: a fast wrong answer is still wrong
# Compare against baseline: pytest-benchmark compare --fail=median:5%
```

**Bad Example** — one cold run, absolute number, dead code

```python
import time

start = time.time()
for _ in range(1000):
    parse(data)          # result discarded → JIT/optimizer may elide the call entirely
elapsed = time.time() - start
print(f"took {elapsed:.3f}s")  # single cold run: includes warmup, one sample, no variance.
# "0.42s" tells you nothing — no baseline, no repetition, no confidence it beats version B.
```

## Common Mistakes

- Measuring the first run, which times JIT/JVM warmup and cold caches, not steady state.
- Reporting a single sample with no variance, so noise reads as signal.
- Comparing absolute times across different machines or runs.
- Letting the optimizer delete unused benchmark code, timing nothing.
- Benchmarking a toy input, then being surprised by production data sizes.
- Winning a microbenchmark that never mattered — the code was not the bottleneck (profile
  first).

## Production Tips

- Run benchmarks in CI on a dedicated, quiet runner and fail the build on a regression
  beyond a threshold (e.g. median +5%). Shared CI runners are too noisy for tight bounds.
- Keep a committed baseline file; compare each run against it rather than a floating
  "yesterday."
- When results are noisy, increase iterations before increasing suspicion — most variance
  is measurement, not the code.

## AI Review Checklist

- Does the benchmark warm up (or use a harness that does) before measuring?
- Are results reported as a distribution (median + variance), not a single run?
- Is the comparison relative, on the same machine, ideally interleaved?
- Is the benchmark output consumed so it cannot be optimized away?
- Are inputs realistic in size and shape for production?
- Was the benchmarked code confirmed to be a real bottleneck (via a profile) first?

## Related

- `knowledge/performance/16-profiling.md`
- `knowledge/performance/02-metrics.md`
- `knowledge/performance/22-load-testing.md`
- `knowledge/performance/03-cpu.md`
- `knowledge/performance/24-optimization-workflow.md`
