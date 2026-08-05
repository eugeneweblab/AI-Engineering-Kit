---
id: cicd/22-kubernetes-integration
topic: cicd
slug: kubernetes-integration
title: "Kubernetes Integration"
type: doc
order: 22
status: ready
tags: [cicd, kubernetes-integration, readinessProbe, cluster-admin, RollingUpdate, requests, limits, livenessProbe]
related: [cicd/10-deployment, cicd/14-rollbacks, cicd/16-environments, cicd/21-docker-integration]
when_to_use: "Read before deploying to Kubernetes from a pipeline or reviewing a rollout config."
---
# Kubernetes Integration

## Purpose

This document defines how to deploy to Kubernetes from a pipeline safely. It covers
declarative apply vs `kubectl` scripting, GitOps (pull) vs push deploys, image-digest
pinning, health probes and rollout strategy, RBAC-scoped deploy credentials, and automated
rollback. The goal is an agent that can ship to a cluster without causing a silent
partial-outage or handing the pipeline cluster-admin.

This builds on [deployment](10-deployment.md) and [Docker integration](21-docker-integration.md);
here we cover the Kubernetes-specific mechanics of getting a new version live and rolled
back safely.

## Why It Matters

Kubernetes will happily roll out a broken image: without readiness probes it routes traffic
to pods that are not ready, and with `imagePullPolicy` on a mutable tag it may run a
different image than you tested. The deploy credential is the other hazard — a pipeline with
a cluster-admin `kubeconfig` is a single stolen token away from total compromise. Rollouts
are also the moment things break for users, so the difference between a declarative,
health-gated, auto-rolling-back deploy and an imperative `kubectl` script is the difference
between a 30-second blip and a paged incident.

## Core Principles

- **Declarative apply, not imperative commands.** `kubectl apply`/GitOps reconciles the
  cluster to a versioned desired state; `kubectl edit`/`set image` drifts it invisibly. The
  cost of declarative is writing manifests; the payoff is that the repo *is* the cluster.
- **Deploy images by digest.** Reference `myapp@sha256:...`, not `myapp:latest`. A tag can
  be re-pushed; a digest is the exact image you scanned and tested.
- **No readiness probe, no safe rollout.** Kubernetes uses `readinessProbe` to decide when
  a pod can receive traffic and to gate a rolling update. Without it, a rollout "succeeds"
  while sending users to dead pods.
- **Least-privilege deploy credentials.** The pipeline's ServiceAccount gets a namespaced
  Role scoped to the resources it deploys — never `cluster-admin`. A leaked token should
  compromise one namespace, not the cluster.
- **Every deploy must be reversible.** Use a Deployment with `RollingUpdate` and record the
  revision so `rollout undo` (or GitOps revert) restores the last-good state in one step.

## Best Practices

- Prefer **GitOps** (Argo CD, Flux): the pipeline commits a manifest change, and an
  in-cluster controller pulls and applies it. This removes cluster credentials from CI
  entirely — the cluster reaches out, not the other way around.
- If pushing directly, authenticate with a **short-lived OIDC token** and a namespaced
  RBAC Role; never store a long-lived cluster-admin kubeconfig as a CI secret.
- Set both `readinessProbe` and `livenessProbe`, and configure `RollingUpdate` with
  `maxUnavailable: 0` so capacity never drops during a deploy.
- Use `kubectl rollout status --timeout=...` (or Argo health checks) to *wait* for the
  rollout and fail the job if pods do not become ready — then trigger [rollback](14-rollbacks.md).
- Set resource `requests`/`limits` on every container so the scheduler can place pods and
  one workload cannot starve the node.
- Verify image signatures at admission (cosign + policy controller) so only pipeline-built,
  signed images run.
- Keep environment differences in overlays (Kustomize/Helm values), not divergent
  hand-edited manifests — see [environments](16-environments.md).

## Examples

**Good Example** — digest-pinned, probes, waited rollout, scoped deploy

```yaml
# deployment.yaml — reconciled by GitOps or `kubectl apply`
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 0, maxSurge: 1 }  # never drop capacity mid-deploy
  template:
    spec:
      containers:
        - name: app
          image: registry.example.com/myapp@sha256:<digest>  # exact tested image
          readinessProbe:                    # gates traffic + the rollout itself
            httpGet: { path: /healthz, port: 8080 }
            initialDelaySeconds: 5
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits:   { cpu: 500m, memory: 256Mi }
```

```bash
# CI deploy step: apply, then WAIT and fail loudly if the rollout is unhealthy
kubectl apply -f deployment.yaml
kubectl rollout status deployment/myapp --timeout=120s \
  || kubectl rollout undo deployment/myapp    # auto-revert to last-good on failure
```

**Bad Example** — mutable tag, imperative, no probe, no wait, cluster-admin

```bash
# kubeconfig in CI is cluster-admin → a leaked token owns the whole cluster
kubectl set image deployment/myapp app=myapp:latest   # mutable tag; drifts from what was tested
# no readinessProbe on the pod → traffic hits pods that never became ready
# no `rollout status` → the job goes green while the app is down
```

## Common Mistakes

- Deploying by mutable tag (`latest`) instead of an immutable digest.
- Missing `readinessProbe`, so a broken rollout still reports success while users get errors.
- Not waiting on `rollout status`, so the pipeline is green while pods crash-loop.
- Giving the pipeline a `cluster-admin` kubeconfig instead of a namespaced RBAC Role.
- Imperative `kubectl set image`/`edit` that drifts the cluster away from the repo.
- No resource `requests`/`limits`, causing unschedulable pods or noisy-neighbor outages.
- No automated rollback path, so recovery is a manual scramble under pressure.

## Production Tips

- Adopt **GitOps** so the deploy credential lives in the cluster, not in CI, and every
  change is an auditable, revertible git commit.
- For risk-sensitive services, layer a progressive rollout (Argo Rollouts / Flagger) on top
  of the Deployment to get [canary](12-canary-deployment.md) or blue-green with automatic
  analysis-based rollback.
- Alert on `Deployment` `Progressing`/`Available` conditions and on crash-loop restarts;
  a stuck rollout should page before users notice.
- Keep manifests and their image digests in git so "what is running in prod?" is answered
  by a commit, not a live `kubectl get`.

## AI Review Checklist

- Is the image referenced by digest, not a mutable tag?
- Does every pod define a `readinessProbe` (and ideally a `livenessProbe`)?
- Does the deploy step wait on `rollout status` and fail if pods do not become ready?
- Is there an automatic rollback (`rollout undo` / GitOps revert) on failure?
- Is the pipeline's RBAC scoped to a namespace, never `cluster-admin`?
- Are deploys declarative (apply/GitOps) rather than imperative `set image`/`edit`?
- Are resource `requests`/`limits` set on every container?

## Related

- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/16-environments.md`
- `knowledge/cicd/21-docker-integration.md`
