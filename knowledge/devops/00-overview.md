---
id: devops/00-overview
topic: devops
slug: overview
title: "DevOps Overview"
type: doc
order: 0
status: ready
tags: [devops, overview]
related: [devops/01-devops-culture, devops/02-development-lifecycle, devops/03-git-workflow, devops/05-build-pipelines, devops/07-deployment-strategies]
when_to_use: "Read first to understand how the devops docs fit together and where to go next."
---
# DevOps Overview

## Purpose

This is the map for the `devops` topic. DevOps is the practice of shortening the
distance between a code change and that change running safely in production — and
keeping it running. These documents teach an AI agent how to reason about that path:
how work flows from a branch, through a pipeline, into an environment, and how you
detect and recover when something breaks.

Read this page to learn what each sibling document covers and which one to open for
the task in front of you. It is a directory, not a concept doc.

## Why It Matters

Most production incidents are not caused by exotic bugs — they are caused by *process*:
an untested change merged straight to `main`, a manual deploy step someone forgot, a
secret committed to Git, a rollback that didn't work because nobody tested it. DevOps
turns those fragile human rituals into automated, repeatable, observable systems. An
agent that writes application code but ignores how it ships will produce work that
cannot be delivered or recovered.

## Core Principles

- **Automate the path to production.** Every manual step is a step that will eventually
  be skipped, mis-typed, or done at 3 a.m. by someone tired. Encode it in a pipeline.
- **Make changes small and reversible.** Small diffs are easier to review, test, and
  roll back. Reversibility is a feature you build, not a hope you hold.
- **Everything is versioned.** Code, infrastructure, configuration, and pipelines all
  live in Git so every change is reviewable, auditable, and revertible.
- **Feedback fast, feedback loud.** The sooner a failure surfaces — in a linter, a test,
  a canary — the cheaper it is to fix. Push detection left.

## How These Documents Fit Together

The topic follows the lifecycle of a change from culture to production:

- **Culture and process** — [01 DevOps Culture](01-devops-culture.md) sets the shared
  ownership model; [02 Development Lifecycle](02-development-lifecycle.md) frames the
  end-to-end flow from idea to running software.
- **Source control** — [03 Git Workflow](03-git-workflow.md) covers commits, reviews,
  and history hygiene; [04 Branching Strategies](04-branching-strategies.md) covers how
  teams integrate work (trunk-based vs. release branches).
- **Build and ship** — [05 Build Pipelines](05-build-pipelines.md) turns source into a
  tested artifact; [06 Release Management](06-release-management.md) and
  [07 Deployment Strategies](07-deployment-strategies.md) get that artifact into
  production safely (blue-green, canary, rollback).
- **Infrastructure** — [08 Infrastructure as Code](08-infrastructure-as-code.md),
  [09 Configuration Management](09-configuration-management.md),
  [10 Containerization](10-containerization.md), and [11 Orchestration](11-orchestration.md)
  define the environments that run the artifact.
- **Operate** — [12 Monitoring](12-monitoring.md) through [15 Alerting](15-alerting.md),
  plus [25 Incident Management](25-incident-management.md) and
  [27 SRE Principles](27-sre-principles.md), keep it healthy and recover it when it fails.

## Best Practices

- Start from the [development lifecycle](02-development-lifecycle.md) to see the whole
  flow, then drill into the stage you are working on.
- When writing CI/CD config, read [05 Build Pipelines](05-build-pipelines.md) and
  [23 Quality Gates](23-quality-gates.md) together — the pipeline enforces the gates.
- Treat [98 Production Checklist](98-production-checklist.md) as the pre-launch gate and
  [99 AI Review Checklist](99-ai-review-checklist.md) as the per-change gate.

## Common Mistakes

- Treating DevOps as a tool ("we have Jenkins, so we do DevOps") instead of a practice
  of automation, ownership, and fast feedback.
- Optimizing the build pipeline while leaving deploys and rollbacks manual — the risk
  just moves downstream to the least-tested step.
- Reading a single doc in isolation. Delivery is a chain; a weak link anywhere breaks it.

## AI Review Checklist

- Does the change have an automated path to production, or does it rely on manual steps?
- Is every artifact (code, infra, config, pipeline) versioned in Git?
- Is the change small and reversible, with a tested rollback?
- Have you consulted the specific sibling doc for the stage you are modifying?

## Related

- `knowledge/devops/01-devops-culture.md`
- `knowledge/devops/02-development-lifecycle.md`
- `knowledge/devops/03-git-workflow.md`
- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/07-deployment-strategies.md`
