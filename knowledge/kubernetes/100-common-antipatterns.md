---
id: kubernetes/100-common-antipatterns
topic: kubernetes
slug: common-antipatterns
title: "Kubernetes Common Antipatterns"
type: doc
order: 100
status: ready
tags: [kubernetes, common-antipatterns]
related: [kubernetes/30-engineering-principles, kubernetes/99-ai-review-checklist, kubernetes/19-resource-management, kubernetes/22-security, kubernetes/04-pods]
when_to_use: "Read before writing Kubernetes manifests, and when a workload behaves badly under load, rollout, or node failure."
---
# Kubernetes Common Antipatterns

## Purpose

A catalog of the Kubernetes mistakes that recur across teams. Each entry names the anti-pattern,
explains *why it is wrong* in terms of how the control plane actually behaves, and gives *the
fix*. An agent should recognize these on sight and refuse to generate them.

## Why It Matters

These patterns pass validation and deploy without error, so they survive review and reach
production. They fail later — under load, during a rollout, or when a node dies — and the symptom
is far from the cause. Learning to spot them at authoring time is the cheapest place to fix them.

## Anti-patterns

### 1. Using the `:latest` tag (or no tag)

- **Why it is wrong:** the tag is mutable, so two Pods of the same Deployment can run different
  builds, and a rollback has no defined target. Nodes may pull a newer image on restart, changing
  behavior with no manifest change.
- **The fix:** pin to an immutable digest (`image@sha256:...`) or a unique, never-reused tag per
  build. Set `imagePullPolicy: IfNotPresent` with digests.

### 2. No resource requests or limits

- **Why it is wrong:** the scheduler treats a request-less container as needing 0, so it packs
  nodes past capacity. Under pressure the kernel OOM-kills Pods — often the wrong ones — and CPU
  throttling starves everything. Missing limits let one Pod consume a whole node.
- **The fix:** set `requests` and `limits` for CPU and memory on every container; match memory
  request to limit for latency-sensitive work to get `Guaranteed` QoS.

### 3. Readiness probe that only checks the port

- **Why it is wrong:** a `tcpSocket` or bare process check passes the instant the process binds,
  before the app can serve. The Service adds the Pod to endpoints and traffic hits an app that is
  still warming up its cache or connecting to the database — users get 502s during every rollout.
- **The fix:** use an `httpGet` readiness probe against an endpoint that verifies critical
  dependencies and returns 200 only when the Pod can actually serve requests.

### 4. Liveness probe that restarts under load

- **Why it is wrong:** an aggressive liveness probe (short timeout, tight threshold) fails when the
  app is merely slow under load, so the kubelet kills a healthy-but-busy Pod. That removes
  capacity, increasing load on the rest — a self-inflicted cascading outage.
- **The fix:** make liveness detect only true deadlocks, with generous timeouts. Gate traffic with
  readiness, not liveness. Use a `startupProbe` for slow boots.

### 5. Storing state on the Pod filesystem

- **Why it is wrong:** Pods are disposable — evicted, preempted, or rescheduled at any time. Data
  written to the container filesystem or an `emptyDir` is gone on the next reschedule.
- **The fix:** put durable state in a PersistentVolume, database, or object store. For per-replica
  stable storage and identity, use a StatefulSet with `volumeClaimTemplates`.

### 6. Single replica with no PodDisruptionBudget

- **Why it is wrong:** a routine node drain (upgrade, autoscale-down) evicts the only Pod and the
  service goes down — a *voluntary* disruption becomes an outage.
- **The fix:** run ≥2 replicas, add a `PodDisruptionBudget` (`minAvailable`), and spread replicas
  across nodes/zones with `topologySpreadConstraints`.

### 7. Over-privileged ServiceAccount

- **Why it is wrong:** binding a workload to `cluster-admin` (or the default SA with broad RBAC)
  means any container compromise becomes full cluster takeover. The mounted token is a ready-made
  lateral-movement credential.
- **The fix:** give each workload a dedicated ServiceAccount with a least-privilege Role, and set
  `automountServiceAccountToken: false` when the app never calls the API.

### 8. Running as root with a writable, privileged container

- **Why it is wrong:** root inside the container plus `privileged` or extra capabilities means an
  RCE can escape to the node. A writable rootfs lets an attacker persist and tamper with binaries.
- **The fix:** `runAsNonRoot: true`, drop `ALL` capabilities, `allowPrivilegeEscalation: false`,
  and `readOnlyRootFilesystem: true`.

### 9. Secrets in plain text

- **Why it is wrong:** secrets committed to Git, baked into images, or passed as literal env values
  in a manifest leak through source history, image layers, and `kubectl describe`. Base64 is not
  encryption.
- **The fix:** store secrets in an encrypted backend (KMS-encrypted etcd, External Secrets, Vault),
  enable etcd encryption at rest, and reference them via `secretKeyRef`.

### 10. Ignoring SIGTERM

- **Why it is wrong:** on rollout or scale-down Kubernetes sends `SIGTERM`, then removes the Pod
  from Service endpoints. An app that exits immediately drops in-flight requests; every deploy
  causes errors.
- **The fix:** trap `SIGTERM`, stop accepting new work, drain in-flight requests, then exit within
  `terminationGracePeriodSeconds`. Add a `preStop` hook if the app cannot handle the signal itself.

### 11. Fixing production with `kubectl edit`

- **Why it is wrong:** an in-place edit is invisible to Git, undocumented, and overwritten by the
  next `apply` or GitOps sync — so the fix silently disappears and the incident recurs.
- **The fix:** change the manifest in version control and apply it through the normal pipeline.
  Treat the cluster as a projection of Git, never the source of truth.

### 12. One giant namespace for everything

- **Why it is wrong:** without namespace boundaries there is no `ResourceQuota`, no isolation, and
  no blast-radius control — one team's runaway workload starves everyone, and RBAC cannot be scoped.
- **The fix:** partition by team/environment into namespaces with `ResourceQuota`, `LimitRange`,
  and scoped RBAC.

## AI Review Checklist

- Is any image using `:latest` or an untagged reference?
- Is any container missing `requests`/`limits`?
- Does any readiness probe check only a port instead of real serving ability?
- Could a liveness probe restart healthy Pods under load?
- Is durable state written to the Pod filesystem instead of a PersistentVolume?
- Does any service run a single replica or lack a PodDisruptionBudget?
- Does any workload use an over-privileged or default ServiceAccount?
- Is any container root, privileged, or writable without justification?
- Are any secrets in plain text, in Git, or baked into an image?

## Related

- `knowledge/kubernetes/30-engineering-principles.md`
- `knowledge/kubernetes/99-ai-review-checklist.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/04-pods.md`
