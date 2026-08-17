---
id: kubernetes/98-production-checklist
topic: kubernetes
slug: production-checklist
title: "Kubernetes Production Checklist"
type: checklist
order: 98
status: ready
tags: [kubernetes, production-checklist, SIGTERM, readinessProbe, livenessProbe, LimitRange, ResourceQuota, Guaranteed, go-live, signing, "off"]
related: [kubernetes/26-production, kubernetes/19-resource-management, kubernetes/22-security, kubernetes/28-disaster-recovery, kubernetes/21-observability]
when_to_use: "Read before promoting any Kubernetes workload to production or signing off a go-live review."
---
# Kubernetes Production Checklist

## Purpose

A verifiable, grouped checklist for taking a Kubernetes workload to production. Each item is
a yes/no question an agent or reviewer can confirm against the manifests, cluster config, and
runbooks. If any box is unchecked, the workload is not production-ready — resolve it or record
an explicit, signed-off exception.

## Why It Matters

Most Kubernetes outages trace back to a small set of omitted settings — no resource requests,
no PodDisruptionBudget, an unbounded liveness probe, a Secret in plain text. Each is trivial to
add and expensive to discover in an incident. This list turns that tribal knowledge into a gate
you run before, not after, the pager goes off.

## Workload & Scheduling

**Rules:** [Deployments](05-deployments.md) · [Resource Management](19-resource-management.md)

- [ ] Every container has CPU and memory `requests` and `limits` set.
- [ ] Latency-sensitive workloads use `Guaranteed` QoS (limit == request for memory).
- [ ] At least 2 replicas run for every stateless service.
- [ ] A `PodDisruptionBudget` protects the service during node drains and upgrades.
- [ ] `topologySpreadConstraints` or anti-affinity spread replicas across nodes and zones.
- [ ] Rollout strategy (`maxSurge`/`maxUnavailable`) keeps capacity above minimum during deploys.
- [ ] `terminationGracePeriodSeconds` is long enough for the app to drain on `SIGTERM`.

## Health & Reliability

**Rules:** [Pods](04-pods.md) · [Autoscaling](20-autoscaling.md)

- [ ] `readinessProbe` reflects true ability to serve (checks critical dependencies).
- [ ] `livenessProbe` restarts only on genuine hangs and cannot cause a crash loop under load.
- [ ] `startupProbe` protects slow-starting apps from premature liveness kills.
- [ ] Container images are pinned to a digest or immutable tag, never `:latest`.
- [ ] The app handles `SIGTERM` and stops accepting new work before exiting.

## Configuration & Secrets

**Rules:** [Configmaps](09-configmaps.md) · [Secrets](10-secrets.md)

- [ ] No secrets are committed to Git or baked into images.
- [ ] Secrets come from an encrypted store (KMS-backed etcd, External Secrets, Vault).
- [ ] etcd encryption at rest is enabled for the cluster.
- [ ] Config is in ConfigMaps/Secrets and mounted or injected, not hardcoded.
- [ ] A rollout is triggered (checksum annotation or new object) when config changes.

## Security

**Rules:** [Security](22-security.md) · [Network Policies](17-network-policies.md)

- [ ] Containers run as non-root with `runAsNonRoot: true`.
- [ ] All Linux capabilities are dropped; only required ones are added back.
- [ ] `readOnlyRootFilesystem: true` unless a documented write path requires otherwise.
- [ ] Each workload has a dedicated ServiceAccount with least-privilege RBAC.
- [ ] `automountServiceAccountToken: false` where the API is not needed.
- [ ] A default-deny NetworkPolicy is in place; ingress/egress is explicitly allowed.
- [ ] Images are scanned for CVEs in CI and admission is blocked on critical findings.

## Observability

**Rules:** [Observability](21-observability.md) · [Monitoring](23-monitoring.md)

- [ ] Metrics are exported (Prometheus/OpenMetrics) and scraped.
- [ ] Structured logs go to stdout/stderr and are shipped to a central store.
- [ ] Alerts exist for CrashLoopBackOff, OOMKilled, Pending Pods, and probe failures.
- [ ] Dashboards cover request rate, error rate, latency, and saturation (RED/USE).
- [ ] Distributed tracing is wired for multi-service request paths.

## Resilience & Recovery

**Rules:** [Disaster Recovery](28-disaster-recovery.md) · [Upgrades](25-upgrades.md)

- [ ] etcd and PersistentVolumes are backed up on a schedule and restores are tested.
- [ ] Autoscaling (HPA/VPA/Cluster Autoscaler) is configured and load-tested.
- [ ] `ResourceQuota` and `LimitRange` bound each namespace's consumption.
- [ ] A documented, rehearsed rollback path exists for every deployment.
- [ ] Node and control-plane upgrade procedures are documented and drained safely.
- [ ] A disaster-recovery runbook with RTO/RPO targets exists and has been exercised.

## Sign-off

- [ ] A staging environment mirrors production config and has passed the same checks.
- [ ] Policy engine (Kyverno/Gatekeeper) enforces these rules in CI, not just review.
- [ ] An on-call owner and runbook are assigned for the workload.

## Related

- `knowledge/kubernetes/26-production.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/28-disaster-recovery.md`
- `knowledge/kubernetes/21-observability.md`
