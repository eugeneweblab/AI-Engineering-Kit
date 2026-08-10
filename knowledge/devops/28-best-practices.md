---
id: devops/28-best-practices
topic: devops
slug: best-practices
title: "DevOps Best Practices"
type: doc
order: 28
status: ready
tags: [devops, best-practices, GIT_SHA, DB_PASSWORD, delivery, auditing, baseline]
related: [devops/00-overview, devops/08-infrastructure-as-code, devops/27-sre-principles, devops/24-change-management, devops/100-common-antipatterns]
when_to_use: "Read when setting up a delivery pipeline from scratch or auditing an existing DevOps practice against a baseline."
---
# DevOps Best Practices

## Purpose

This document distills the cross-cutting practices that make a DevOps setup healthy,
gathering the highest-leverage rules from across this topic into one baseline. It is
written so an agent can sanity-check any pipeline, environment, or operational process
against a known-good standard, and so a review can cite a single reference.

This is a synthesis, not a substitute. Each rule here links to the doc that treats it in
depth. Use it as a checklist of *what good looks like*; go to the specific doc for *how*.

## Why It Matters

DevOps failures are rarely one dramatic mistake. They are the accumulation of small
compromises — a manual deploy step here, a snowflake server there, a secret in an env
file — each defensible alone, together producing a system nobody can safely change. The
value of an explicit baseline is that it catches these compromises at review time, while
they are cheap to fix, instead of during the 3am incident they eventually cause. A good
baseline also lets a team move *faster*: when the safe path is well-defined and
automated, engineers stop deliberating over routine changes.

## Core Principles

- **Automate everything you do twice.** A manual step is a step that will eventually be
  skipped, mistyped, or forgotten during an incident. Codify it — in
  [IaC](08-infrastructure-as-code.md), a pipeline, or a script under version control.
- **Everything in version control.** Application code, infrastructure, configuration,
  pipelines, and runbooks all live in Git. If it is not in Git, it cannot be reviewed,
  reverted, or reproduced.
- **Build once, promote the same artifact.** Compile/package a single immutable artifact
  and move *that* through dev → staging → prod. Rebuilding per environment means prod
  runs bits nothing tested.
- **Fast feedback.** The pipeline should tell you it is broken in minutes, not hours. Run
  cheap checks first; fail fast. Slow feedback pushes people to batch and skip.
- **Reproducible and disposable.** Any environment must be rebuildable from code. Treat
  servers as cattle, not pets — replace, don't hand-patch.
- **Reliability is measured, not assumed.** Use SLOs and error budgets
  ([SRE principles](27-sre-principles.md)) instead of gut feel.

## Best Practices

- Keep pipelines idempotent and safe to re-run; a re-run should converge, never corrupt.
- Gate merges on automated quality checks — tests, linters, security scans, IaC plan —
  so the default branch is always deployable. See [quality gates](23-quality-gates.md).
- Manage secrets in a dedicated store, injected at runtime, never committed. See
  [secrets management](17-secrets-management.md).
- Decouple deploy from release with feature flags so exposure and rollback are instant.
- Make rollback a first-class, tested path — not an afterthought discovered mid-incident.
- Instrument for observability from the start: structured logs, metrics, traces, and
  SLO-based alerts on user-facing symptoms.
- Enforce least privilege for humans and machines; scope CI/CD credentials tightly.
- Document runbooks for known failures and link them from the alerts that fire.

## Examples

**Good Example** — build-once artifact promoted across environments

```yaml
build:
  script: docker build -t app:${GIT_SHA} .   # one immutable, SHA-tagged image
  push: registry/app:${GIT_SHA}
deploy_staging:
  image: registry/app:${GIT_SHA}             # promote the SAME bits
deploy_prod:
  image: registry/app:${GIT_SHA}             # exactly what staging validated
  when: manual                                # human gate only at the risky step
# WHY: prod runs the identical artifact that passed staging — no rebuild drift.
```

**Bad Example** — rebuild per environment, config baked in

```yaml
deploy_prod:
  script:
    - git pull                                # source, not a pinned artifact
    - docker build -t app:latest .            # NEW build — untested bits
    - export DB_PASSWORD=hunter2              # secret in the pipeline, in Git
    - docker run app:latest
# WHY WRONG: `latest` and a fresh build mean prod != staging. `git pull` is not a
# reproducible artifact. The secret is now in version control forever.
```

## Common Mistakes

- Manual, undocumented deploy steps that only one person knows how to run.
- Rebuilding artifacts per environment, so prod runs code nothing tested.
- Configuration or secrets committed to the repo or baked into images.
- Snowflake servers patched by hand and impossible to reproduce.
- No rollback plan; "roll forward" is the only option when things break.
- Alerting on internal causes instead of user-facing symptoms, drowning real signals.
- Skipping quality gates "just this once", which quickly becomes the norm.

## Production Tips

- Periodically rebuild a production-equivalent environment from code alone; if you
  cannot, your IaC has drifted and disaster recovery will fail when you need it.
- Track the DORA four (deploy frequency, lead time, change-failure rate, MTTR) as a
  health signal for the whole practice.
- Review CI/CD permissions on a schedule — pipelines accumulate over-broad access.

## AI Review Checklist

- Is every repeated operation automated and stored in version control?
- Is a single immutable artifact built once and promoted, not rebuilt per environment?
- Are secrets injected from a store at runtime, never committed?
- Does the default branch stay deployable behind automated quality gates?
- Is rollback a defined, tested path, and is deploy decoupled from release?
- Are environments reproducible from code, with servers treated as disposable?
- Do alerts and SLOs track user-facing symptoms?

## Related

- `knowledge/devops/00-overview.md`
- `knowledge/devops/08-infrastructure-as-code.md`
- `knowledge/devops/27-sre-principles.md`
- `knowledge/devops/24-change-management.md`
- `knowledge/devops/100-common-antipatterns.md`
