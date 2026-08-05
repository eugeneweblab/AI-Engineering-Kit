---
id: devops/30-engineering-principles
topic: devops
slug: engineering-principles
title: "DevOps Engineering Principles"
type: doc
order: 30
status: ready
tags: [devops, engineering-principles]
related: [devops/28-best-practices, devops/27-sre-principles, devops/08-infrastructure-as-code, devops/07-deployment-strategies, devops/100-common-antipatterns]
when_to_use: "Read before designing a pipeline, deployment, or operational change, so the delivery trade-offs are reasoned rather than guessed."
---
# DevOps Engineering Principles

## Purpose

This document defines the durable principles that govern *how* to make DevOps decisions —
the reasoning an agent applies before writing a pipeline, choosing a deploy strategy, or
changing infrastructure. Tools change constantly; these principles decide when a tool or
practice earns its place. Read this before the concrete practice docs
([build pipelines](05-build-pipelines.md), [deployment strategies](07-deployment-strategies.md),
[infrastructure as code](08-infrastructure-as-code.md)); they tell you *what*, this tells
you *whether* and *why*.

## Why It Matters

Most delivery pain is not one bad outage — it is a hundred small, unreasoned defaults that
compound: a manual step nobody automated, a pipeline that is green but untrustworthy, a
server patched by hand that no one can reproduce. Each looks harmless in isolation and each
raises the cost and risk of every future change. Principles matter because they force the
trade-off to be explicit *at the moment of the decision*, when it is cheap to choose
differently, instead of at 3 a.m. during an incident when it is not.

## Core Principles

- **Automate everything you do more than twice.** A manual step is a step that will
  eventually be skipped, mis-typed, or done differently under pressure. Automate it because
  humans are unreliable at repetition; the cost is upfront scripting time, the payoff is a
  process that runs the same way every time and is auditable.
- **The commit is the source of truth.** Everything that defines the system — code, infra,
  config, pipeline — lives in version control and is applied from there, never edited live.
  The cost is discipline; the payoff is that the state of production is knowable and
  reproducible from a `git checkout`.
- **Build once, promote the same artifact.** Compile and package a single immutable
  artifact, then move *that* artifact through dev, staging, and prod. Rebuilding per
  environment means you never actually tested what you ship.
- **Make it reversible before you make it fast.** Every deploy must have a known,
  rehearsed rollback. Ship velocity is only safe when the undo button works; the cost of a
  bad deploy should be minutes, not an outage.
- **Fail closed and loudly.** A pipeline that hides a failure is worse than one that stops.
  When a gate cannot verify success, it must block, not pass — a silent green is how broken
  code reaches production.
- **You build it, you run it.** The team that writes the code owns its operation, alerts,
  and on-call. Ownership is what aligns the incentive to make software operable, not just
  shippable (see [SRE principles](27-sre-principles.md)).

## Best Practices

- Treat infrastructure as code: declarative, reviewed, and applied by a pipeline — never
  `ssh` in and change a running box (see [infrastructure as code](08-infrastructure-as-code.md)).
- Keep pipelines fast and trustworthy. A slow or flaky pipeline gets bypassed; sub-10-minute
  feedback and zero tolerance for flaky tests are reliability features, not luxuries.
- Externalize configuration per environment; the artifact is identical, only the injected
  config differs (see [configuration management](09-configuration-management.md)).
- Prefer small, frequent, independently deployable changes over large batched releases —
  small changes are easier to review, test, and roll back, and shrink the blast radius.
- Make every change observable: emit logs, metrics, and traces so you can answer "did that
  deploy make things worse?" from data, not opinion (see [observability](13-observability.md)).
- Never store secrets in code, images, or plain config. Source them from a secrets manager
  so they are rotatable and auditable (see [secrets management](17-secrets-management.md)).
- Design for the failure you have not imagined: health checks, graceful shutdown, and
  bounded resource limits are table stakes, not extras.

## Examples

**Good Example** — one immutable artifact, promoted by config, with a rollback path

```yaml
# The same image digest built once in CI is promoted to each environment.
# Only the injected config changes. Rollback is redeploying the previous digest.
deploy:
  image: registry.example.com/api@sha256:9f2c...   # pinned digest, built once
  env_from:
    - secretRef: api-prod-secrets                   # secrets injected, never baked in
  strategy:
    type: RollingUpdate
    rollback:
      onFailure: true                               # automatic revert if health check fails
```

**Bad Example** — rebuild per environment, mutable server, no undo

```bash
# Anti-pattern: build a fresh (untested) artifact straight on the prod host,
# edit config in place, and leave no way back.
ssh prod-01 'cd /app && git pull && npm run build'   # what ran in staging? unknown.
ssh prod-01 'nano /app/config.json'                  # hand-edited, unversioned, unreproducible
# No previous artifact kept -> a bad deploy means a scramble, not a rollback.
```

## Common Mistakes

- Automating the happy path but leaving the recovery/rollback path manual — the one you
  need most under stress.
- Rebuilding artifacts per environment, so staging never validated the production binary.
- Editing running servers by hand ("configuration drift"), making prod impossible to
  reproduce or reason about.
- Treating a green pipeline as proof of correctness when its tests are flaky or shallow.
- Storing secrets in the repo or the image "temporarily" — temporary secrets leak
  permanently once they are in git history.
- Optimizing deploy speed before the rollback works, so fast becomes fast-to-break.

## Production Tips

- Rehearse rollback and disaster recovery regularly; an untested restore or revert is a
  hope, not a plan (see [disaster recovery](18-disaster-recovery.md)).
- Track lead time, deploy frequency, change-failure rate, and time-to-restore (the DORA
  metrics) to know whether your delivery is actually improving, not just busier.
- When two principles conflict (e.g., speed vs. safety), state which you prioritized and
  why in the change record, so the trade-off is auditable.

## AI Review Checklist

- Is every repeated operation automated and applied from version control, not by hand?
- Is a single immutable artifact built once and promoted, with config injected per
  environment?
- Does the change have a tested, automatic rollback path?
- Are secrets sourced from a manager and absent from code, images, and config?
- Does the pipeline fail closed — blocking on any unverifiable step rather than passing?
- Is the change small, independently deployable, and observable after it ships?

## Related

- `knowledge/devops/28-best-practices.md`
- `knowledge/devops/27-sre-principles.md`
- `knowledge/devops/08-infrastructure-as-code.md`
- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/100-common-antipatterns.md`
