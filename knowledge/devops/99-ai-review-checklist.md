---
id: devops/99-ai-review-checklist
topic: devops
slug: ai-review-checklist
title: "DevOps AI Review Checklist"
type: doc
order: 99
status: ready
tags: [devops, ai-review-checklist]
related: [devops/05-build-pipelines, devops/08-infrastructure-as-code, devops/30-engineering-principles, devops/100-common-antipatterns, devops/98-production-checklist]
when_to_use: "Read before reviewing or generating any change to a pipeline, deployment, or infrastructure definition."
---
# DevOps AI Review Checklist

## Purpose

This is the checklist an AI agent runs when reviewing (or self-reviewing) a DevOps change:
a pipeline edit, a deployment config, an infrastructure definition, a script. Every item is
a verifiable yes/no about the *delivery design*. It is the design counterpart to the
[production checklist](98-production-checklist.md), which covers operational readiness of a
release. Use this during code review and before merging any change that touches how software
is built, shipped, or run.

## Why It Matters

DevOps mistakes are the silent kind: the pipeline is green, the deploy "worked", and the
gap only surfaces during an incident, when the rollback is missing or the secret is in the
git history. Because a broken automation still runs, tests do not catch these — a human or
agent reviewer is the last gate. A concrete checklist catches the defect at the one moment
it is cheap to fix, before merge, and gives the agent a reason to reject, not just a vibe.

## Reproducibility & Artifacts

**Rules:** [Build Pipelines](05-build-pipelines.md) · [Containerization](10-containerization.md)

- [ ] Is a **single artifact** built once and promoted across environments, rather than
  rebuilt per stage (see [build pipelines](05-build-pipelines.md))?
- [ ] Are dependencies **locked/pinned** so the build is reproducible from a clean checkout?
- [ ] Is the artifact **immutable and versioned**, traceable to the exact commit it came
  from?

## Infrastructure & Configuration

**Rules:** [Infrastructure As Code](08-infrastructure-as-code.md) · [Configuration Management](09-configuration-management.md)

- [ ] Is all infrastructure change expressed as **declarative code** and applied by a
  pipeline, with no manual, out-of-band edits to live resources (see
  [infrastructure as code](08-infrastructure-as-code.md))?
- [ ] Is configuration **externalized per environment**, so the same artifact runs
  everywhere with only injected config differing?
- [ ] Would this change cause **configuration drift** — a state that cannot be reproduced
  from version control? (If yes, reject.)

## Secrets & Security

**Rules:** [Secrets Management](17-secrets-management.md) · [Security](16-security.md)

- [ ] Are there **no secrets** in code, images, logs, or committed config? Every secret
  comes from a manager (see [secrets management](17-secrets-management.md)).
- [ ] Does the pipeline avoid printing secrets to logs or exposing them to untrusted
  pull-request builds?
- [ ] Do images and jobs run with **least privilege** (non-root, scoped credentials)?

## Safety & Reversibility

**Rules:** [Deployment Strategies](07-deployment-strategies.md) · [Change Management](24-change-management.md)

- [ ] Does the deploy have a **tested rollback** and a real health/readiness gate (see
  [deployment strategies](07-deployment-strategies.md))?
- [ ] Is any schema migration **backward-compatible** and decoupled from the code deploy?
- [ ] Can the change be rolled back **independently**, without a coordinated multi-service
  release?

## Pipeline Quality

**Rules:** [Quality Gates](23-quality-gates.md) · [Testing](22-testing.md)

- [ ] Does the pipeline **fail closed** — blocking on any unverifiable or failed step rather
  than passing (see [engineering principles](30-engineering-principles.md))?
- [ ] Are quality gates (tests, lint, security scan) **required**, not optional or
  flaky-ignored (see [quality gates](23-quality-gates.md))?
- [ ] Is the feedback loop **fast enough** (roughly under 10 minutes) that it will not be
  bypassed?

## Observability & Ownership

**Rules:** [Observability](13-observability.md) · [SRE Principles](27-sre-principles.md)

- [ ] Does the change stay **observable** — logs, metrics, and traces emitted so a
  regression is diagnosable from data (see [observability](13-observability.md))?
- [ ] Are new failure modes covered by an **actionable alert** with a runbook?
- [ ] Is there a **named owner / on-call** for what this change deploys?

## How to Use This Checklist

Treat any "no" as a finding, not a formality. For each "no", either change the design or
write down why the exception is acceptable — an unexplained "no" blocks the merge. Rank
findings by blast radius: a missing rollback or a leaked secret outranks a naming nit,
because it costs far more when it fails.

## Related

- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/08-infrastructure-as-code.md`
- `knowledge/devops/30-engineering-principles.md`
- `knowledge/devops/100-common-antipatterns.md`
- `knowledge/devops/98-production-checklist.md`
