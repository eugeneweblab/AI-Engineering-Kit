---
id: cicd/30-engineering-principles
topic: cicd
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [cicd, engineering-principles]
related: [cicd/02-pipeline-design, cicd/05-quality-gates, cicd/09-release-management, cicd/14-rollbacks, cicd/27-best-practices]
when_to_use: "Read before designing, refactoring, or reviewing any CI/CD pipeline or delivery workflow."
---
# Engineering Principles

## Purpose

This document defines the durable engineering principles behind a CI/CD system:
the properties a pipeline must have regardless of which tool runs it (GitHub Actions,
GitLab CI, Jenkins, Buildkite). It is written so an agent can design or review a
delivery pipeline and reason about *why* each stage exists, not just copy YAML.

CI (continuous integration) means every change is merged and verified on a shared
branch continuously. CD (continuous delivery/deployment) means every verified change
is packaged into a deployable artifact and released through an automated, repeatable
path. These principles apply from the first `git push` to the production rollout.

## Why It Matters

A pipeline is the only path code takes from a developer's machine to a user. If that
path is slow, flaky, or non-deterministic, it stops being a safety net and becomes a
bottleneck engineers route around — merging on red, disabling tests, deploying by hand.
Every such workaround removes a guarantee. A broken pipeline fails quietly: the build
still goes green, but it no longer proves anything. Because the pipeline gates every
release, a weakness here multiplies across every change that flows through it.

## Core Principles

- **A build is deterministic and reproducible.** The same commit must produce a
  byte-identical artifact on any runner, at any time. Pin versions; never build against
  a floating `latest`. Non-determinism turns "works in CI" into a coin flip.
- **Build once, promote the same artifact.** Compile and package a commit exactly one
  time, then move that identical artifact through staging to production. Rebuilding per
  environment means production runs code that was never tested.
- **Fail fast, fail loud.** Order stages cheapest-and-most-likely-to-fail first (lint,
  unit, then integration, then deploy). A pipeline that surfaces a failure in 90 seconds
  saves more than one that runs everything and reports after 40 minutes.
- **Every stage is a gate, not a suggestion.** A red pipeline blocks the merge or the
  deploy. Gates that can be clicked past are decoration.
- **Pipelines are code, reviewed like code.** Pipeline definitions live in the repo,
  are version-controlled, and change through pull requests — never edited live in a UI.
- **Every release is reversible.** Design the rollback path before the rollout path.
  If you cannot revert in one step, you cannot deploy safely.

## Best Practices

- Trigger CI on every push and every pull request; block merge on a required green check.
- Pin all inputs: base images by digest, actions/plugins by SHA or exact tag, and
  dependencies by lockfile. Cache by a hash of those inputs, not by branch name.
- Keep the critical-path pipeline under ~10 minutes; parallelize and shard tests to
  hold that budget as the suite grows.
- Make jobs idempotent and retry-safe — a re-run must not corrupt state or double-deploy.
- Store the build artifact in a registry with an immutable, commit-derived tag (see
  [versioning](08-versioning.md)); deploy by referencing that tag, never by rebuilding.
- Inject secrets at runtime from a secrets manager; never bake them into images or logs.
- Emit a deployment record (commit SHA, artifact digest, actor, timestamp) so any
  running version is traceable back to source.

## Examples

**Good Example** — build once, promote the same artifact by digest

```yaml
# One build produces one immutable, digest-addressed artifact.
build:
  script:
    - docker build -t $REGISTRY/app:$CI_COMMIT_SHA .   # tag by commit, not "latest"
    - docker push $REGISTRY/app:$CI_COMMIT_SHA
    - DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' $REGISTRY/app:$CI_COMMIT_SHA)
    - echo "$DIGEST" > artifact.txt                     # pin the exact bytes we tested

deploy_staging:
  script:
    - kubectl set image deploy/app app=$(cat artifact.txt)  # promote, don't rebuild

deploy_prod:
  needs: [deploy_staging]                               # prod uses the SAME digest
  when: manual                                          # explicit gate before release
  script:
    - kubectl set image deploy/app app=$(cat artifact.txt)
```

**Bad Example** — rebuilds per environment, floating tag, no gate

```yaml
deploy_staging:
  script:
    - docker build -t app:latest . && deploy staging app:latest  # build #1

deploy_prod:
  script:
    - docker build -t app:latest . && deploy prod app:latest     # build #2 — different bytes!
    # "latest" is mutable and each build re-resolves dependencies, so production
    # runs code that was never the code staging validated. No manual gate, no
    # traceable version: a bad release cannot be identified or reverted cleanly.
```

## Common Mistakes

- Rebuilding the artifact for each environment instead of promoting one build.
- Depending on `latest` or unpinned action/plugin versions, so builds drift over time.
- Treating a flaky test as acceptable and adding blanket retries that mask real bugs.
- Editing pipeline config directly in a CI web UI, leaving no review trail or history.
- Putting slow end-to-end tests before fast unit tests, so feedback takes 30+ minutes.
- Shipping a deploy path with no matching rollback path.

## Production Tips

- Track DORA metrics (deployment frequency, lead time, change-failure rate, MTTR) —
  they tell you whether the pipeline is actually improving delivery.
- Alert on pipeline health itself: rising duration, flake rate, and queue time are
  early signals of decay.
- Quarantine flaky tests to a separate non-blocking lane and fix them on a deadline,
  rather than letting them erode trust in the whole suite.

## AI Review Checklist

- Is the artifact built once and promoted unchanged to every environment?
- Are all inputs pinned (base image digest, action SHAs, dependency lockfile)?
- Do required checks actually block merge and deploy, or can they be bypassed?
- Is the pipeline definition version-controlled and changed via review?
- Does fast feedback come first (lint/unit before integration/e2e)?
- Is there a defined, one-step rollback for every deployment?

## Related

- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/05-quality-gates.md`
- `knowledge/cicd/09-release-management.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/27-best-practices.md`
