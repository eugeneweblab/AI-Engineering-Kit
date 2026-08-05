---
id: architecture/24-deployment
topic: architecture
slug: deployment
title: "Architecture Deployment"
type: doc
order: 24
status: ready
tags: [architecture, deployment]
related: [architecture/23-infrastructure, architecture/16-high-availability, architecture/18-observability, architecture/17-fault-tolerance, architecture/26-architecture-decision-records]
when_to_use: "Read before designing or reviewing how a service ships to production — pipelines, release strategy, rollout, and rollback."
---
# Architecture Deployment

## Purpose

This document defines how a change moves from a merged commit to running in production
safely. It covers the deployment pipeline, release strategies (rolling, blue-green,
canary), rollback, and the architectural properties a system needs to be deployable
without downtime. It is written so an agent can design or review a release path that is
automated, reversible, and boring.

Deployment is an architectural concern, not an afterthought. A system that cannot be
deployed frequently, safely, and independently is not production-grade regardless of how
clean its internals are.

## Why It Matters

Most production incidents happen *during* or *because of* a deployment. The moment code
changes is the moment risk is highest: new bugs, config drift, incompatible schema,
broken dependencies. If a deploy is manual, slow, or irreversible, teams deploy rarely
and in large batches — which makes each deploy riskier and the failure harder to
diagnose. The architecture that makes small, frequent, reversible deploys possible is the
same architecture that keeps the system stable. Deployability and reliability are the same
property viewed from two angles.

## Core Principles

- **Automate the entire path.** A human clicking through steps is a source of drift and
  error. The pipeline — build, test, deploy — must be reproducible from a commit.
- **One artifact, many environments.** Build once, promote the *same* immutable artifact
  through staging to production. Rebuilding per environment reintroduces variance.
- **Every deploy is reversible.** If you cannot roll back in minutes, you cannot deploy
  safely. Design forward, but always keep the exit.
- **Decouple deploy from release.** Shipping code to servers (deploy) and exposing a
  feature to users (release) are separate events. Feature flags let you deploy dark and
  release on your own schedule.
- **Backward-compatible changes only.** During a rollout, old and new versions run
  simultaneously. Both must work against the same database and API contracts.

## Best Practices

- Ship immutable, versioned artifacts (container images, signed bundles) tagged to a
  commit SHA. Never deploy from a mutable branch or a developer machine.
- Use a **rolling** deploy for stateless services with health checks; use **blue-green**
  when you need instant rollback and can afford double capacity; use **canary** when you
  want to limit blast radius by shifting a small percentage of traffic first.
- Gate rollout progression on real signals — health checks, error rate, latency — not on
  a fixed timer. Halt and roll back automatically when a signal degrades.
- Separate schema migrations from code deploys using **expand/contract**: add the new
  column, deploy code that writes both, backfill, then remove the old — never a
  destructive migration in the same release as the code that depends on it.
- Keep configuration and secrets out of the artifact; inject them per environment from a
  secrets manager. The same image must run in staging and production.
- Make deploys observable: emit a deploy marker (version, SHA, time) to your metrics and
  logs so you can correlate a regression with the release that caused it.
- Run smoke tests against the new version *before* it takes production traffic.

## Examples

**Good Example** — health-gated rolling update, backward-compatible

```yaml
# Kubernetes rolling deploy: old and new pods coexist, traffic only shifts to
# pods that pass readiness. maxUnavailable: 0 keeps full capacity during rollout.
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0   # never drop below desired capacity
  template:
    spec:
      containers:
        - name: api
          image: registry/api@sha256:9f3c...   # immutable, pinned to a digest
          readinessProbe:                       # no traffic until the app is truly ready
            httpGet: { path: /healthz/ready, port: 8080 }
            initialDelaySeconds: 5
```

**Bad Example** — mutable tag, destructive migration, no rollback

```yaml
spec:
  strategy:
    type: Recreate            # kills all old pods first → downtime window
  template:
    spec:
      containers:
        - name: api
          image: registry/api:latest   # "latest" is not reproducible; can't roll back
          # No readinessProbe: traffic hits pods before the app is up → 502s.
# Same release runs: ALTER TABLE users DROP COLUMN legacy_email;
# Old pods still reference legacy_email during rollout → runtime errors.
```

## Common Mistakes

- Deploying the `latest` tag or a branch name — you cannot reproduce or roll back to a
  known state.
- Coupling a destructive schema change to the deploy that removes the code — the
  in-flight old version breaks. Use expand/contract across two releases.
- No readiness probe, so traffic reaches instances before they can serve it.
- Rebuilding the artifact separately for staging and production, so what you tested is not
  what you shipped.
- Progressing a canary on a timer instead of on error-rate and latency signals.
- Storing secrets in the image or in the repo instead of injecting them at runtime.
- Treating rollback as a fresh forward deploy — too slow when production is on fire.

## Production Tips

- Keep the last known-good artifact one command away; rehearse rollback so it is muscle
  memory, not improvisation during an incident.
- Emit deploy markers and put them on your dashboards so on-call can instantly see "did a
  deploy cause this?".
- Deploy during low-traffic windows early on, but invest toward deploys being safe at any
  hour — that is the real goal.
- Record the *why* of non-obvious release choices (blue-green vs canary, migration
  strategy) as an [ADR](26-architecture-decision-records.md).

## AI Review Checklist

- Is the deployed artifact immutable and pinned to a commit SHA or image digest?
- Is the same artifact promoted across environments, with config injected per environment?
- Does the strategy keep old and new versions compatible during rollout (schema and API)?
- Are there readiness/health checks, and does rollout progression gate on real signals?
- Is rollback fast, tested, and to a known-good version?
- Are schema changes expand/contract rather than destructive-in-place?
- Is each deploy observable via a version/SHA marker in metrics and logs?

## Related

- `knowledge/architecture/23-infrastructure.md`
- `knowledge/architecture/16-high-availability.md`
- `knowledge/architecture/17-fault-tolerance.md`
- `knowledge/architecture/18-observability.md`
- `knowledge/architecture/26-architecture-decision-records.md`
