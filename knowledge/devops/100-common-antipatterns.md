---
id: devops/100-common-antipatterns
topic: devops
slug: common-antipatterns
title: "Common Antipatterns"
type: doc
order: 100
status: ready
tags: [devops, common-antipatterns]
related: [devops/08-infrastructure-as-code, devops/07-deployment-strategies, devops/17-secrets-management, devops/30-engineering-principles, devops/99-ai-review-checklist]
when_to_use: "Read before writing a pipeline, deploy config, or infra change, to check you are not walking into a known trap."
---
# Common Antipatterns

## Purpose

This document catalogs the recurring DevOps mistakes an agent is most likely to make or
approve, and for each one states *why it is wrong* and *the fix*. These are the patterns
that look reasonable in the moment and cost dearly during an incident. Recognizing the shape
of a trap is faster than re-deriving why it hurts, so use this as a lookup during design and
[review](99-ai-review-checklist.md).

## Why It Matters

DevOps antipatterns spread by imitation and hide until stressed. One hand-patched server
becomes the template for the next; one pipeline with a skipped test teaches the team that
green means nothing. Because each instance "works" right up until the deploy that breaks,
nothing stops the spread until an outage forces a reckoning. Naming the antipattern is what
lets a reviewer reject it early, while it is still one instance and cheap to undo.

## Infrastructure & Configuration Antipatterns

### Snowflake Servers / Configuration Drift

- **What it is:** Servers configured and patched by hand over time, each subtly unique, none
  reproducible from source.
- **Why it is wrong:** You cannot recreate the box after a failure, cannot reason about what
  is actually running, and every change is a gamble because the starting state is unknown.
- **The fix:** Define infrastructure as declarative code and rebuild from it; treat servers
  as [immutable and disposable](08-infrastructure-as-code.md), replaced rather than patched.

### Manual Deploys / ClickOps

- **What it is:** Releasing by hand — SSHing in, running commands, editing config in a
  console — instead of through an automated pipeline.
- **Why it is wrong:** Manual steps are skipped, mis-typed, and done differently under
  pressure; there is no audit trail and no repeatability.
- **The fix:** Automate the full path in a pipeline so every deploy runs identically and is
  logged (see [engineering principles](30-engineering-principles.md)).

### Secrets in the Repo

- **What it is:** API keys, passwords, or tokens committed to git, baked into images, or
  printed in build logs.
- **Why it is wrong:** Once a secret is in git history it is leaked permanently, even after
  deletion; anyone with repo or image access is now a credential holder.
- **The fix:** Source all secrets from a secrets manager at runtime, and rotate any that
  ever touched the repo (see [secrets management](17-secrets-management.md)).

## Pipeline Antipatterns

### Rebuild Per Environment

- **What it is:** Building a fresh artifact for staging and another for production instead of
  promoting one build.
- **Why it is wrong:** The thing you ship to production was never the thing you tested;
  dependency or toolchain drift between builds reintroduces bugs you thought were caught.
- **The fix:** Build once, store an immutable versioned artifact, and promote *that* through
  every environment (see [build pipelines](05-build-pipelines.md)).

### Flaky-Tolerant / Green-Means-Nothing Pipeline

- **What it is:** A pipeline riddled with intermittently failing tests that the team reruns
  until green, or gates marked "allowed to fail".
- **Why it is wrong:** A pipeline you do not trust is a pipeline you route around; it stops
  being a gate and becomes theater, and real failures hide among the noise.
- **The fix:** Quarantine and fix flaky tests, make gates required, and treat a red pipeline
  as a stop condition (see [quality gates](23-quality-gates.md)).

### Big Bang Release

- **What it is:** Batching weeks of change into one large, infrequent deploy.
- **Why it is wrong:** The blast radius is huge, the cause of any regression is buried among
  many changes, and rollback throws away good work with bad.
- **The fix:** Ship small, frequent, independently deployable changes; use canary or
  progressive rollout to limit exposure (see [deployment strategies](07-deployment-strategies.md)).

## Operational Antipatterns

### No Rollback Plan

- **What it is:** Deploying forward-only, with no rehearsed way to revert a bad release.
- **Why it is wrong:** When a deploy breaks production, "roll forward with a fix" turns a
  two-minute revert into a multi-hour outage under maximum stress.
- **The fix:** Make every deploy reversible and test the rollback; keep the previous artifact
  and make revert a single action.

### Alert Fatigue

- **What it is:** Alerting on everything, so the on-call inbox is a wall of noise with no
  clear signal.
- **Why it is wrong:** When most alerts are non-actionable, humans stop reading them, and the
  one real page gets ignored along with the noise.
- **The fix:** Alert only on user-facing symptoms and SLO breaches, each with a runbook;
  delete alerts nobody acts on (see [alerting](15-alerting.md)).

### Blameful Postmortems

- **What it is:** Treating an incident as someone's fault to be punished rather than a
  systemic weakness to fix.
- **Why it is wrong:** Blame drives problems underground — people stop reporting near-misses,
  so the system never learns and the same failure recurs.
- **The fix:** Run blameless postmortems focused on the systemic cause and the durable fix
  (see [postmortems](26-postmortems.md)).

## Example — the manual, unversioned deploy and its fix

```text
// Bad: release by hand, config edited live, nothing reproducible or reversible.
//   A typo or a missing step ships silently; the prior state is gone.
[engineer] --ssh--> [prod host] --hand-edit config, git pull, restart--> (hope)

// Good: the pipeline promotes one built artifact and can revert it.
//   Every deploy is identical, logged, health-gated, and reversible.
[commit] -> [CI: build + test once] -> [artifact vN] -> [CD: deploy vN, health check]
                                                            |-- fail --> auto-rollback to vN-1
```

## Common Mistakes

- Patching servers by hand and calling it "just a quick fix" — it is drift, and it compounds.
- Rebuilding artifacts per environment, so production runs untested bits.
- Committing a secret "temporarily" — git history makes it permanent.
- Trusting a green pipeline whose tests are flaky or non-blocking.
- Shipping forward-only with no rehearsed rollback.
- Alerting on causes and metrics instead of on actionable user-facing symptoms.

## AI Review Checklist

- Does any change edit a live server or resource by hand instead of via code? (Drift — reject.)
- Is an artifact rebuilt per environment rather than promoted once? (Untested release.)
- Is any secret present in the repo, image, or logs? (Leak — reject and rotate.)
- Does the deploy lack a tested, independent rollback? (No undo.)
- Are gates non-blocking or flaky-tolerated? (Green means nothing.)
- Do new alerts fire on symptoms with runbooks, not on noise? (Alert fatigue.)

## Related

- `knowledge/devops/08-infrastructure-as-code.md`
- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/17-secrets-management.md`
- `knowledge/devops/30-engineering-principles.md`
- `knowledge/devops/99-ai-review-checklist.md`
