---
id: cicd/10-deployment
topic: cicd
slug: deployment
title: "Deployment"
type: doc
order: 10
status: ready
tags: [cicd, deployment]
related: [cicd/07-artifacts, cicd/11-blue-green-deployment, cicd/14-rollbacks, cicd/16-environments]
when_to_use: "Read before building or reviewing any automated deployment to a live environment."
---
# Deployment

## Purpose

This document defines how to move an [artifact](07-artifacts.md) into a running
environment safely. It covers deployment strategies (rolling, recreate,
[blue-green](11-blue-green-deployment.md), [canary](12-canary-deployment.md)), the
prerequisites that make any strategy safe (health checks, idempotent migrations,
zero-downtime rollout), and the non-negotiable requirement that every deployment be
reversible.

Deployment is the last mile of CI/CD, where code meets real traffic. This is where latent
bugs become incidents, so it is held to the same higher bar as any code that runs against
production users.

## Why It Matters

A deploy is the single most common trigger of production incidents — not because the code
is wrong, but because the *transition* is mishandled: connections dropped mid-request, a
migration that locks a table, a bad build with no way back. The goal is to make deploys so
routine and safe that they are unremarkable, because that is what unlocks shipping often.
The two properties that get you there are **zero-downtime rollout** (users never see the
switch) and **fast rollback** (a bad deploy is undone in seconds, not debugged live).
Everything else in this document serves those two properties.

## Core Principles

- **Deploy the artifact you tested; never build in place.** Promote the exact bytes from
  staging. Rebuilding on the target reintroduces the "works in staging" gap.
- **Automated and repeatable.** A deploy is a pipeline step, not a person running commands
  over SSH. Manual deploys are unrepeatable and unauditable.
- **Zero downtime by default.** Roll out gradually with health checks and connection
  draining so no request is dropped. Recreate-all-at-once is only acceptable where an
  outage window is explicitly allowed.
- **Every deploy is reversible.** Know the rollback before you start. Prefer strategies
  where rollback is re-pointing traffic, not re-running a deploy.
- **Separate schema changes from code.** Make migrations backward-compatible and
  expand/contract, so old and new versions can run at once during rollout.

## Best Practices

- Gate deploys on readiness and liveness health checks; a new instance takes traffic only
  after it reports healthy, and the rollout halts if health regresses.
- Drain connections on shutdown: stop accepting new requests, finish in-flight ones, then
  exit. Otherwise every deploy drops live requests.
- Make deploys **idempotent**: re-running the same deploy yields the same state. Retries
  are then safe.
- Use **expand/contract** for database changes: (1) add the new column/table
  backward-compatibly, (2) deploy code that writes both, (3) backfill, (4) switch reads,
  (5) drop the old — never in one release. This keeps rollout and rollback safe.
- Choose the strategy by risk: **rolling** for stateless services, **blue-green** when you
  need instant rollback, **canary** when you want to validate on real traffic first.
- Automate rollback and make it a first-class pipeline action, not a manual scramble.
- Keep deploy config in the repo (GitOps / declarative manifests) so the deployed state is
  reviewable and reproducible.

## Examples

**Good Example** — rolling deploy of a tested artifact, health-gated, zero-downtime

```yaml
# Kubernetes: promote the exact digest, roll gradually, keep old pods until new are healthy
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 0, maxSurge: 1 } # never drop below capacity
  template:
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api@sha256:9f1c2ab...   # immutable digest, tested in staging
          readinessProbe:                              # no traffic until the pod is ready
            httpGet: { path: /healthz, port: 8080 }
          lifecycle:
            preStop:                                   # drain in-flight requests on shutdown
              exec: { command: ["sleep", "15"] }
# `kubectl rollout undo` reverts to the previous ReplicaSet in seconds.
```

**Bad Example** — build-in-place, restart-all, no health gate

```bash
ssh prod-box                       # manual, unauditable, unrepeatable
cd /app && git pull && npm ci && npm run build   # rebuilds — prod now differs from staging
pm2 restart api                    # kills all instances at once → every in-flight request drops
# No readiness check: traffic hits the process before it can serve → 502s during startup
# No migration ordering: if the pull included a schema change, old code is already gone
# Rollback plan: none. If the build is bad, the site is down until someone fixes it live.
```

## Common Mistakes

- Rebuilding on the target host instead of deploying the promoted artifact.
- Restarting all instances simultaneously, dropping in-flight requests.
- No readiness probe, so traffic hits instances before they can serve.
- Non-backward-compatible migrations shipped in the same release as the code that needs
  them, so rollback breaks the schema.
- No connection draining, so every deploy causes a burst of errors.
- Manual SSH deploys with no rollback path.
- Treating a failed deploy as "roll forward only" when a fast rollback was available.

## Production Tips

- Emit a deploy marker (version, digest, time) to your observability stack so dashboards
  and alerts can correlate incidents with the exact deploy that caused them.
- Set automated rollback triggers: if error rate or latency crosses a threshold within N
  minutes of a deploy, revert automatically.
- Rehearse rollback regularly; a rollback that is never tested fails when you need it.
- Keep deploys small and frequent — large deploys concentrate risk into rare, scary events.

## AI Review Checklist

- Does the deploy promote a pre-built, tested artifact rather than building in place?
- Is the rollout zero-downtime (gradual, health-gated, with connection draining)?
- Are readiness/liveness probes wired so traffic only reaches healthy instances?
- Are database migrations backward-compatible (expand/contract), separate from code?
- Is the deploy automated, idempotent, and defined declaratively in the repo?
- Is there a fast, rehearsed rollback path — ideally automated on health regression?
- Is the deployed version/digest recorded for incident correlation?

## Related

- `knowledge/cicd/07-artifacts.md`
- `knowledge/cicd/11-blue-green-deployment.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/16-environments.md`
