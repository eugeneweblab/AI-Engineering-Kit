---
id: kubernetes/99-ai-review-checklist
topic: kubernetes
slug: ai-review-checklist
title: "AI Review Checklist"
type: doc
order: 99
status: ready
tags: [kubernetes, ai-review-checklist]
related: [kubernetes/30-engineering-principles, kubernetes/100-common-antipatterns, kubernetes/22-security, kubernetes/18-rbac, kubernetes/19-resource-management]
when_to_use: "Read before reviewing any pull request that adds or changes Kubernetes manifests, Helm charts, or operators."
---
# AI Review Checklist

## Purpose

A focused checklist for an AI agent reviewing Kubernetes manifests in a pull request. Each item
is a yes/no check answerable from the diff alone. It catches the defects that pass `kubectl
apply` cleanly but fail in production: silent overcommit, probes that lie, over-broad RBAC, and
mutable images. Use it as the review gate; flag any "no" as a blocking comment with the fix.

## Why It Matters

A manifest that validates and deploys can still be wrong in ways the API server never checks —
missing resources, a `:latest` tag, a cluster-admin ServiceAccount. These pass CI and surface
only under failure. A reviewer who applies this list turns those latent bugs into review
comments instead of incidents.

## Images & Reproducibility

- [ ] Is every image pinned to a digest or immutable tag (never `:latest` or no tag)?
- [ ] Is `imagePullPolicy` consistent with the tag strategy (not `Always` on a digest)?
- [ ] Do images come from a trusted, scanned registry?

## Resources & Scheduling

- [ ] Does every container set CPU and memory `requests` and `limits`?
- [ ] Are the values justified by real usage, not copy-pasted placeholders?
- [ ] Are there ≥2 replicas and a `PodDisruptionBudget` for stateless services?
- [ ] Is there topology spread or anti-affinity so replicas do not share a failure domain?

## Health Probes

- [ ] Is there a `readinessProbe` that checks real serving ability, not just an open port?
- [ ] Is the `livenessProbe` distinct from readiness and safe from crash-looping under load?
- [ ] Do slow-starting containers use a `startupProbe` instead of a long liveness delay?
- [ ] Are probe timeouts and thresholds set (not left to defaults that mask hangs)?

## Security

- [ ] Does the `securityContext` set `runAsNonRoot: true` and a non-zero `runAsUser`?
- [ ] Are all capabilities dropped, with only the required ones added back?
- [ ] Is `readOnlyRootFilesystem: true` (or the write path documented)?
- [ ] Is `allowPrivilegeEscalation: false` and `privileged` unset?
- [ ] Does the workload use a dedicated, least-privilege ServiceAccount and RBAC Role?
- [ ] Is `automountServiceAccountToken: false` when the API is not needed?
- [ ] Is there a NetworkPolicy, and does the namespace default to deny?

## Configuration & Secrets

- [ ] Are secrets referenced from a Secret/secrets manager, never inline or in Git?
- [ ] Is config externalized to ConfigMaps rather than hardcoded in the manifest?
- [ ] Does a config change roll the Pods (checksum annotation), not silently persist stale values?

## State & Lifecycle

- [ ] Is persistent state on a PersistentVolume, not the Pod's ephemeral filesystem?
- [ ] Is `terminationGracePeriodSeconds` sufficient for graceful drain on `SIGTERM`?
- [ ] For StatefulSets, are volumeClaimTemplates and an ordered update strategy correct?

## Observability

- [ ] Are Prometheus scrape annotations / ServiceMonitor present for metrics?
- [ ] Do logs go to stdout/stderr in a structured format?

## Related

- `knowledge/kubernetes/30-engineering-principles.md`
- `knowledge/kubernetes/100-common-antipatterns.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/18-rbac.md`
- `knowledge/kubernetes/19-resource-management.md`
