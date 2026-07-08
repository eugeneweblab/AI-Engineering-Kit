---
id: devops/02-development-lifecycle
topic: devops
slug: development-lifecycle
title: "Development Lifecycle"
type: doc
order: 2
status: ready
tags: [devops, development-lifecycle]
related: [devops/00-overview, devops/03-git-workflow, devops/05-build-pipelines, devops/22-testing, devops/24-change-management]
when_to_use: "Read before designing or reviewing how work moves from idea to running software across environments."
---
# Development Lifecycle

## Purpose

This document describes the software development lifecycle (SDLC) as DevOps runs it: the
end-to-end path a change takes from an idea, through code and review, into build, test,
and release. It is the connective tissue between the sibling docs — each stage here maps
to a deeper document. Use it to reason about *where* a given concern belongs and what
must be true before a change advances to the next stage.

## Why It Matters

A change that is correct in isolation can still cause an outage if the *lifecycle* around
it is broken: no review caught a design flaw, no test covered the edge case, no staging
environment revealed the config mismatch, no gate stopped it. The lifecycle is a series
of filters, each cheaper than the one after it. Catching a bug in review costs minutes;
catching it in production costs an incident. Skipping stages doesn't save time — it moves
the cost downstream and multiplies it.

## Core Principles

- **Shift left.** Move validation as early as possible. A failing lint or unit test in
  seconds beats a failed deploy in an hour. Every stage should catch what the next stage
  would otherwise catch, more expensively.
- **One artifact, promoted through environments.** Build once, then promote the *same*
  immutable artifact through dev → staging → production. Rebuilding per environment means
  you never actually tested what you ship.
- **Environment parity.** Keep environments as similar as practical so behavior in staging
  predicts behavior in production. Divergence hides bugs until the worst moment.
- **Every stage has an entry gate.** A change only advances when defined criteria pass
  (tests green, review approved, checks clean). Gates are automated, not opinions.

## The Stages

1. **Plan** — define the change as a small, well-scoped unit of work with acceptance
   criteria. Small scope is what makes every later stage tractable.
2. **Develop** — write code on a short-lived branch with tests. See
   [03 Git Workflow](03-git-workflow.md).
3. **Review** — a peer (or an agent) reviews the diff for correctness, security, and
   design before merge.
4. **Build** — compile, package, and produce a single versioned artifact. See
   [05 Build Pipelines](05-build-pipelines.md).
5. **Test** — run unit, integration, and end-to-end suites against the artifact. See
   [22 Testing](22-testing.md) and [23 Quality Gates](23-quality-gates.md).
6. **Release** — promote the artifact to production via a controlled strategy. See
   [07 Deployment Strategies](07-deployment-strategies.md).
7. **Operate & observe** — monitor, alert, and feed learnings back into planning. See
   [12 Monitoring](12-monitoring.md).

## Best Practices

- Keep units of work small enough to finish, review, and ship within a day or two —
  long-lived work rots against a moving `main`.
- Automate the gate between every stage so promotion is deterministic, not a judgment call
  under deadline pressure.
- Promote the byte-identical artifact you built; inject only environment-specific *config*
  at deploy time, never new code. See [09 Configuration Management](09-configuration-management.md).
- Make the pipeline the single path to production. If there's a manual side door, it will
  be used, and it will skip the gates.
- Feed production signals (errors, latency, incidents) back into planning so the loop
  actually closes.

## Examples

**Good Example** — same artifact promoted, config injected per environment

```yaml
# Build once, tag by immutable content, promote the SAME image.
build:
  run: docker build -t registry/app:${GIT_SHA} .   # one artifact, keyed to the commit
  run: docker push registry/app:${GIT_SHA}

deploy-staging:
  run: deploy registry/app:${GIT_SHA} --env staging   # same image
deploy-production:
  needs: [deploy-staging]                              # gate: staging must pass first
  run: deploy registry/app:${GIT_SHA} --env production # SAME image, prod config injected
```

**Bad Example** — rebuild per environment

```yaml
deploy-staging:
  run: docker build -t app:staging . && deploy app:staging   # build #1
deploy-production:
  run: docker build -t app:prod . && deploy app:prod
  # Rebuilds from source at deploy time. A dependency could resolve to a new
  # version between builds, so production runs code that staging never tested.
```

## Common Mistakes

- Building a fresh artifact for each environment, so "tested in staging" guarantees
  nothing about production.
- Long-lived feature branches that drift far from `main` and produce painful merges.
- A staging environment that differs materially from production (different DB, no TLS,
  fake data), giving false confidence.
- Manual promotion paths that bypass the automated gates when someone is in a hurry.

## Production Tips

- Give each artifact a traceable version (Git SHA or semver) so you can tie any running
  instance back to the exact commit and pipeline run.
- Record which artifact version is live in each environment; it is the first question
  during an incident.

## AI Review Checklist

- Is the change scoped small enough to move through the whole lifecycle quickly?
- Is a single immutable artifact built once and promoted, not rebuilt per environment?
- Does an automated gate guard the entry to each stage (build, test, release)?
- Are staging and production close enough that staging results are predictive?
- Is config injected at deploy time rather than baked differently per environment?

## Related

- `knowledge/devops/00-overview.md`
- `knowledge/devops/03-git-workflow.md`
- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/22-testing.md`
- `knowledge/devops/24-change-management.md`
