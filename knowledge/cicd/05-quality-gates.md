---
id: cicd/05-quality-gates
topic: cicd
slug: quality-gates
title: "Quality Gates"
type: doc
order: 5
status: ready
tags: [cicd, quality-gates]
related: [cicd/02-pipeline-design, cicd/04-test-stage, cicd/06-security-scanning, cicd/27-best-practices, cicd/100-common-antipatterns]
when_to_use: "Read before defining or changing the thresholds that block a merge or deploy."
---
# Quality Gates

## Purpose

This document defines quality gates: the automated pass/fail checks that decide whether a
change is allowed to merge or deploy. It covers what to gate on (tests, coverage, lint,
types, security), how to set thresholds that are meaningful, and how to make gates
blocking rather than advisory. Running the checks correctly is covered in
[Test Stage](04-test-stage.md) and [Security Scanning](06-security-scanning.md); this doc
is about turning their results into an enforced decision.

A quality gate is the pipeline's veto. Its whole value is that it cannot be bypassed by
tired humans on a Friday afternoon.

## Why It Matters

A check that reports but does not block is theater. Everyone can see coverage dropped or a
linter flagged an issue, and everyone can merge anyway — so over time nobody looks. The
only difference between a "quality gate" and a "quality suggestion" is enforcement: a gate
is a *required* status check that mechanically prevents merge. This matters most exactly
when discipline is lowest — during an incident, near a deadline, on a hotfix. Gates that
depend on humans choosing to honor them fail precisely when they are needed. And gates set
wrong — a coverage ratchet that only ever climbs, a zero-tolerance lint rule on a legacy
file — get disabled entirely, which is worse than no gate. Set gates that are strict,
meaningful, and enforced.

## Core Principles

- **A gate must block, not warn.** If a failing check can still be merged, it is not a
  gate. Wire it as a required status check on the protected branch.
- **Gate on outcomes, not vanity metrics.** Failing tests, new security findings, type
  errors, and lint violations are outcomes. A single coverage percentage in isolation is a
  proxy that is easy to game.
- **Prevent regressions, don't demand perfection.** Gate on *new* or *changed* code
  (diff coverage, new findings) so a legacy codebase can adopt strict gates without a
  giant upfront cleanup.
- **Thresholds are code — versioned and reviewed.** Lowering a gate should require a PR and
  a reason, not a quiet config edit.
- **Fast and deterministic, or it will be bypassed.** A gate that is slow or flaky trains
  the team to use the override. Keep gates quick and stable.

## Best Practices

- Configure required status checks on the protected branch so merge is *mechanically*
  blocked until every gate passes — do not rely on reviewer diligence.
- Gate on **diff coverage** (coverage of changed lines) rather than total project
  coverage; it prevents new untested code without punishing legacy files.
- Fail the build on lint and type errors (`eslint --max-warnings 0`, `tsc --noEmit`), not
  just print them, so violations cannot accumulate.
- Make gate thresholds explicit and version-controlled (a coverage config, a ruleset), and
  require a reviewed PR to weaken any of them.
- Break the glass rarely and loudly: if an emergency override exists, it must be logged,
  time-boxed, and auto-ticketed for follow-up — never a silent bypass.
- Keep the gate set minimal and meaningful; ten flaky gates get disabled, three solid ones
  get respected.

## Examples

**Good Example** — blocking gate on diff coverage, lint, and types

```yaml
# This job is a REQUIRED status check on main. A red result blocks merge, full stop.
quality-gate:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with: { fetch-depth: 0 }                 # need history for diff coverage
    - run: npm ci
    - run: npm run typecheck                   # fails the job on any type error
    - run: npx eslint . --max-warnings 0       # zero tolerance for NEW warnings
    - run: npm test -- --coverage
    - name: Enforce coverage on changed lines
      run: npx diff-cover coverage/lcov.info --compare-branch=origin/main --fail-under=90
      # Gates only the diff: new code must be 90% covered; legacy files are not punished.
```

**Bad Example** — advisory checks, gameable global threshold

```yaml
quality-gate:
  runs-on: ubuntu-latest
  continue-on-error: true            # failures never block merge → it's a suggestion
  steps:
    - run: npm run lint || true      # swallows lint failures entirely
    - run: npm test -- --coverage
    - name: Coverage
      run: |
        # Gates TOTAL coverage; adding one trivial test to a huge file keeps the number
        # up while the actual change ships untested. Easy to game, catches nothing new.
        pct=$(cat coverage/total)
        [ "$pct" -ge 80 ] && echo "ok"
```

## Common Mistakes

- Checks that report but are not required, so they are quietly ignored.
- `continue-on-error: true` or `|| true` that swallows the failure the gate exists to catch.
- Gating on total project coverage (gameable) instead of diff coverage (regression-proof).
- One-size zero-tolerance rules dumped onto a legacy repo, so the whole gate gets disabled.
- Overrides that are silent and permanent instead of logged, time-boxed, and ticketed.
- A pile of flaky gates that trains the team to reach for the merge-override button.

## Production Tips

- Audit override/bypass usage; a rising count means a gate is mis-tuned or too slow.
- Ratchet gently: raise thresholds in reviewed increments as the codebase improves, rather
  than setting an aspirational number nobody can meet.
- Surface the exact failing rule and line in the PR check output so a red gate is
  actionable in seconds, not a scavenger hunt.

## AI Review Checklist

- Is each gate a *required* status check that mechanically blocks merge, not advisory?
- Does coverage gating use diff/changed-line coverage rather than a gameable total?
- Do lint and type checks fail the build (`--max-warnings 0`), not just print warnings?
- Are `continue-on-error` / `|| true` absent from gate steps?
- Are thresholds version-controlled, and are overrides logged, time-boxed, and ticketed?

## Related

- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/04-test-stage.md`
- `knowledge/cicd/06-security-scanning.md`
- `knowledge/cicd/27-best-practices.md`
- `knowledge/cicd/100-common-antipatterns.md`
