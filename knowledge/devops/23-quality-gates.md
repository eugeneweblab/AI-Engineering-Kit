---
id: devops/23-quality-gates
topic: devops
slug: quality-gates
title: "DevOps Quality Gates"
type: doc
order: 23
status: ready
tags: [devops, quality-gates, continue-on-error, merge, quality-gate]
related: [devops/22-testing, devops/05-build-pipelines, devops/16-security, devops/07-deployment-strategies, devops/06-release-management]
when_to_use: "Read before adding CI checks, merge requirements, or release gates to a pipeline."
---
# DevOps Quality Gates

## Purpose

This document defines quality gates: the automated, enforced checks a change must pass
before it can merge or deploy. It covers what to gate on, how to make gates fast and
trustworthy, and how to avoid the two failure modes — gates so weak they let bugs through,
and gates so noisy that teams disable or bypass them. It is written so an agent can design
or review a gating strategy that raises quality without grinding delivery to a halt.

A quality gate is the *decision* layer that consumes evidence from [testing](22-testing.md),
linting, and security scans and returns a hard pass/fail inside the
[build pipeline](05-build-pipelines.md). Tests produce the signal; gates enforce it.

## Why It Matters

A gate is only as good as its enforcement. A "required" check that reviewers can override,
that is advisory, or that flakes and gets marked "skip" is not a gate — it is a suggestion,
and standards decay to whatever the most rushed engineer will accept on a Friday. Automated
gates replace human vigilance (which erodes under deadline pressure) with a consistent,
unarguable rule. Done well, they let a team move fast *because* the machine, not a stressed
reviewer, guarantees the floor.

## Core Principles

- **Gates must be automated and blocking.** A gate a human can wave through is not a gate.
  Enforce it in CI/branch protection so passing is the only path to merge.
- **Fail fast and cheap.** Order gates cheapest-first (lint → unit → build → integration →
  security → E2E) so a lint error costs seconds, not a 20-minute pipeline.
- **Every gate must be trustworthy.** A flaky or noisy gate gets bypassed, which disables
  every gate behind it. Zero tolerance for flaky required checks.
- **Gate on deltas, not just absolutes.** Block regressions (coverage dropped, new critical
  vuln, new lint error) rather than demanding perfection on legacy code you cannot fix now.
- **Make the failure actionable.** A gate must tell you exactly what failed and how to fix
  it. An opaque red X trains people to rerun until green instead of fixing the cause.

## Best Practices

- Enforce gates via **branch protection / required status checks**, not convention. No
  merge without green; no admin override as routine practice. The cost is discipline —
  that is the point.
- **Gate the essentials**: build succeeds, tests pass, linter/formatter clean, type check
  clean, security scan (SAST + dependency audit) with no new criticals, and coverage that
  does not drop below the module floor.
- **Order stages cheapest-to-most-expensive** and fail the pipeline on the first failure, so
  feedback is fast and compute is not wasted running E2E after a lint break.
- **Pin thresholds to prevent regression**: fail if new code lowers coverage or introduces a
  new high/critical vulnerability, rather than blocking on pre-existing debt.
- **Keep gates fast** (target < 10–15 min to merge) with caching, parallelism, and running
  the heavy suite only where it adds signal. Slow gates create pressure to bypass them.
- **Deduplicate: one source of truth.** Run the same gate the same way locally (pre-commit)
  and in CI so failures don't surprise people only at the merge button.
- **Distinguish blocking from advisory.** Correctness/security block; style suggestions can
  warn. Blocking on nits burns the credibility you need for the checks that matter.
- **Separate merge gates from deploy gates.** Merge gates protect the main branch; deploy
  gates (smoke tests, canary health, migration checks) protect production.

## Examples

**Good Example** — blocking, ordered, delta-based CI gate

```yaml
# Cheapest checks first; the job FAILS the merge (required status check) on any red step.
jobs:
  quality-gate:
    steps:
      - run: npm run lint        # seconds — catches the most, costs the least
      - run: npm run typecheck   # fast, high signal
      - run: npm test -- --coverage
      - run: npx coverage-delta --min 80 --no-decrease  # block REGRESSION, not legacy debt
      - run: npm audit --audit-level=high               # fail on NEW high/critical vulns
      - run: npm run test:integration                   # most expensive, runs last
# Branch protection requires this job to pass → there is no merge path around it.
```

**Bad Example** — advisory, unordered, bypassable

```yaml
jobs:
  checks:
    continue-on-error: true        # failures do not block → the gate is decorative
    steps:
      - run: npm run test:e2e      # slowest suite first: 20 min before a lint typo is caught
      - run: npm run lint || true  # swallows the error; red never means red
      - run: npm test
# Not a required check; reviewers "merge anyway." Standards decay to zero over time.
```

## Common Mistakes

- Advisory checks (`continue-on-error`, `|| true`) that report but never block.
- Not marking the check "required" in branch protection, so merges route around it.
- Running the slowest suite first, making every failure expensive and feedback slow.
- Gating on absolute coverage/quality of legacy code, blocking unrelated work.
- Tolerating a flaky required gate until the team habitually bypasses all gates.
- Blocking on cosmetic nits, spending gate credibility on things that don't matter.
- Only gating merges, with no deploy-time gate (smoke/canary) protecting production.

## Production Tips

- Track **gate pass rate, flake rate, and time-to-green**; a gate that is red 40% of the
  time from flake, not defects, is actively harmful and must be fixed or removed.
- Reserve **admin override for genuine emergencies** and log every use — a routine override
  means the gate is miscalibrated, not that the rule is wrong.
- Add **deploy gates** (post-deploy smoke tests, canary error-rate thresholds, auto-rollback)
  so a change that passed CI but breaks in prod is caught before full rollout.

## AI Review Checklist

- Is every quality gate automated and blocking via required status checks?
- Are stages ordered cheapest-first with fail-fast on the first failure?
- Do gates cover build, tests, lint/format, types, security scan, and coverage?
- Do gates block regressions (coverage drop, new vulns) rather than legacy debt?
- Are required gates free of flake, or quarantined until fixed?
- Do failures produce an actionable message pointing at the fix?
- Are there deploy-time gates (smoke/canary) distinct from merge gates?

## Related

- `knowledge/devops/22-testing.md`
- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/16-security.md`
- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/06-release-management.md`
