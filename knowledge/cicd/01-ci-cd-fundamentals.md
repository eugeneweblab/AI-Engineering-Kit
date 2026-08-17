---
id: cicd/01-ci-cd-fundamentals
topic: cicd
slug: ci-cd-fundamentals
title: "CI CD Fundamentals"
type: doc
order: 1
status: ready
tags: [cicd, ci-cd-fundamentals, runs-on]
related: [cicd/00-overview, cicd/02-pipeline-design, cicd/05-quality-gates, cicd/08-versioning, cicd/10-deployment]
when_to_use: "Read before setting up a repo's pipeline or when deciding what CI vs CD should do for a project."
---
# CI CD Fundamentals

## Purpose

This document defines the vocabulary and the model behind CI/CD so an agent can make
correct decisions about *what* automation to build and *why*. It draws the line between
Continuous Integration, Continuous Delivery, and Continuous Deployment, and describes the
trigger model, branching strategy, and feedback loop that make them work.

Get these definitions right before writing pipeline config. Most broken pipelines are
broken because someone automated the wrong thing at the wrong stage.

## Why It Matters

CI/CD is the mechanism that lets many people change one codebase without breaking it and
without stepping on each other. Without it, integration is a painful, batched event and
"works on my machine" is the only guarantee. With a correct pipeline, integration happens
continuously and every change carries a fresh, automated proof that the system still
builds, passes tests, and is safe to ship. The cost of getting the model wrong is not a
style issue — it is bad code reaching users or the team losing trust in the one gate that
protects them.

## Core Principles

- **Continuous Integration = prove every change.** Every commit to a shared branch is
  automatically built and tested. The goal is to catch integration failures within
  minutes of introducing them, while the change is small.
- **Continuous Delivery = always shippable.** Every green commit produces a
  deployable artifact; a human decides *when* to release, but never *whether* it is
  ready — the pipeline already proved that.
- **Continuous Deployment = ship automatically.** Every green commit deploys to
  production with no human step. This requires strong tests, gates, and safe rollout.
- **Integrate small and often.** Long-lived branches defeat CI: they defer integration,
  so failures surface late and large. Prefer trunk-based development with short branches.
- **The pipeline is the source of truth.** "It passed locally" is not a proof; only a run
  on the shared, reproducible CI environment counts.

## Best Practices

- Trigger CI on every push and every pull request; trigger CD from merges to the
  protected branch (or from tags for release-gated flows).
- Keep feature branches short-lived (hours to a couple of days) and merge behind
  required status checks so nothing lands red.
- Make the "green build" the definition of done: build + tests + lint + type +
  security all pass, or the change does not merge.
- Give each commit a durable identity — a version or tag tied to the commit SHA — so a
  deployed artifact can always be traced back to its source. See [Versioning](08-versioning.md).
- Choose the right ambition: Continuous *Delivery* (human approves release) is the safe
  default; adopt Continuous *Deployment* only once tests and rollback are trustworthy.

## Examples

**Good Example** — CI on PRs, CD gated on the protected branch (GitHub Actions)

```yaml
# Runs on every PR to prove the change; runs deploy only after merge to main.
on:
  pull_request:            # CI: prove the change before it can merge
    branches: [main]
  push:
    branches: [main]       # CD: only the merged, proven commit deploys

jobs:
  verify:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - run: npm ci         # exact, locked dependencies — reproducible
      - run: npm run build
      - run: npm test

  deploy:
    needs: verify                                   # never deploy an unproven commit
    if: github.event_name == 'push'                 # only on merge to main, not on PRs
    runs-on: ubuntu-24.04
    steps:
      - run: ./scripts/deploy.sh                    # promotes the artifact verify built
```

**Bad Example** — deploy runs regardless of tests, on any branch

```yaml
on: push                         # fires on every branch, including experiments

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install         # unlocked deps → non-reproducible build
      - run: ./scripts/deploy.sh # no build/test dependency: ships untested code
```

## Common Mistakes

- Conflating Continuous Delivery with Continuous Deployment and enabling auto-deploy
  before tests and rollback are trustworthy.
- Long-lived feature branches that turn "continuous" integration into a quarterly merge.
- Deploy jobs that do not depend on the verify jobs, so a red build still ships.
- Treating a local pass as sufficient and skipping the required CI check.
- Triggering deploys from arbitrary branches instead of the single protected branch.

## AI Review Checklist

- Does CI run on both pull requests and the protected branch?
- Does the deploy job depend on build+test passing, and only fire on the protected branch?
- Are dependencies installed from a lockfile (`npm ci`, `pip install -r ... --require-hashes`)?
- Is the branching model short-lived branches merged behind required checks?
- Is auto-deploy (Continuous Deployment) used only where tests and rollback justify it?

## Related

- `knowledge/cicd/00-overview.md`
- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/05-quality-gates.md`
- `knowledge/cicd/08-versioning.md`
- `knowledge/cicd/10-deployment.md`
