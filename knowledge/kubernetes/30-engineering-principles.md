---
id: kubernetes/30-engineering-principles
topic: kubernetes
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [kubernetes, engineering-principles]
related: [kubernetes/19-resource-management, kubernetes/27-best-practices, kubernetes/22-security, kubernetes/21-observability, kubernetes/26-production]
when_to_use: "Read before designing or reviewing any workload manifest, Helm chart, or controller that runs on Kubernetes."
---
# Engineering Principles

## Purpose

This document defines the engineering mindset for building on Kubernetes: how to write
manifests, controllers, and deployment tooling that behave predictably when nodes die,
traffic spikes, and the scheduler moves your Pods without asking. It is written so an
agent can author or review Kubernetes workloads without shipping a config that only works
on a quiet cluster.

Kubernetes is a *declarative, self-healing control loop*, not a deployment script. You
describe desired state; controllers converge toward it continuously. Every principle here
follows from that fact — code that fights the control loop will lose.

## Why It Matters

A Kubernetes manifest is not application code you run once — it is a contract the cluster
enforces forever, across every rescheduling, rollout, and node failure. A missing
`resources.requests` or a wrong `readinessProbe` does not fail loudly at commit time; it
fails at 3 a.m. under load, when the scheduler overcommits a node or routes traffic to a
Pod that is not ready. The blast radius is the whole service, and the symptom (cascading
evictions, silent request drops) rarely points back to the one-line cause. Because the
cost lands in production and the failure is delayed, Kubernetes config is held to a higher
bar than the app it wraps. Assume every Pod will be killed and rescheduled at any moment.

## Core Principles

- **Declare desired state; never imperatively mutate the cluster.** Manage everything
  through version-controlled manifests applied via GitOps or `kubectl apply`. Never fix
  production with `kubectl edit` — the change is invisible and the next apply reverts it.
- **Design every Pod to be disposable.** A Pod can be evicted, preempted, or killed at any
  instant. State lives in PersistentVolumes, databases, or object storage — never on the
  Pod's local disk or in memory that cannot be rebuilt.
- **Make readiness honest.** A Pod that reports ready receives traffic. Its readiness probe
  must check that it can actually serve, not merely that the process started.
- **Set requests and limits on every container.** The scheduler places Pods by `requests`;
  the kernel enforces `limits`. Omitting either lets one Pod starve a node.
- **Fail closed on identity and network.** Default RBAC and NetworkPolicy to deny; grant the
  minimum each workload needs. An unscoped ServiceAccount is a lateral-movement path.
- **Converge idempotently.** Applying the same manifest twice must produce the same result.
  This is what makes rollouts, retries, and disaster recovery safe.

## Best Practices

- Pin container images to an immutable digest (`image@sha256:...`) or a specific tag, never
  `:latest` — otherwise rollbacks and reproducibility break silently.
- Define `readinessProbe`, `livenessProbe`, and `startupProbe` deliberately. Readiness gates
  traffic; liveness restarts a hung process; startup protects slow-booting apps from being
  killed before they finish initializing.
- Set `resources.requests` and `resources.limits` for CPU and memory on every container.
  Match memory request to limit for predictable QoS (`Guaranteed`) on latency-sensitive work.
- Run more than one replica and set a `PodDisruptionBudget` so voluntary disruptions (node
  drains, upgrades) cannot take the whole service down.
- Use `topologySpreadConstraints` or anti-affinity to spread replicas across nodes and zones.
- Configure `terminationGracePeriodSeconds` and handle `SIGTERM` — drain in-flight requests
  before exit, or rollouts will drop connections.
- Store configuration in ConfigMaps and secrets in Secrets (encrypted at rest / external
  secrets manager); never bake either into the image.
- Drop all Linux capabilities, run as non-root, and set `readOnlyRootFilesystem: true` unless
  a specific need is documented.

## Examples

**Good Example** — disposable Pod with honest probes and bounded resources

```yaml
# A container that the scheduler can place safely and the kubelet can gate correctly.
containers:
  - name: api
    image: registry.example.com/api@sha256:9f2a...   # immutable digest, reproducible
    resources:
      requests: { cpu: "250m", memory: "256Mi" }      # scheduler reserves this
      limits:   { cpu: "500m", memory: "256Mi" }      # mem limit == request → Guaranteed QoS
    readinessProbe:                                    # gates traffic, not just liveness
      httpGet: { path: /healthz/ready, port: 8080 }    # checks DB/deps, returns 200 only when serving
      periodSeconds: 5
    securityContext:
      runAsNonRoot: true
      readOnlyRootFilesystem: true
      capabilities: { drop: ["ALL"] }
```

**Bad Example** — mutable image, no resources, probe that lies

```yaml
containers:
  - name: api
    image: api:latest              # tag moves → rollback is undefined, nodes pull different builds
    # no resources → scheduler assumes 0, overcommits the node, OOM-kills neighbors
    readinessProbe:
      tcpSocket: { port: 8080 }     # port is open the instant the process starts,
                                    # so traffic arrives before the app can serve → 502s
    # runs as root, writable rootfs → any RCE owns the container
```

## Common Mistakes

- Using `:latest` (or no tag), making rollouts and rollbacks non-reproducible.
- Omitting `resources.requests`, so the scheduler overcommits nodes and triggers evictions.
- A `readinessProbe` that only checks TCP or process liveness, sending traffic to a Pod that
  cannot yet serve.
- Storing state on the Pod filesystem or in memory, lost on every reschedule.
- Running a single replica with no PodDisruptionBudget — a routine node drain is an outage.
- Ignoring `SIGTERM`, dropping in-flight requests on every rollout.
- Editing live objects with `kubectl edit`, creating drift that the next GitOps sync erases.

## Production Tips

- Enforce these rules in CI with a policy engine (Kyverno, OPA Gatekeeper) so a manifest
  missing probes, resources, or a non-root context is rejected before merge.
- Adopt GitOps (Argo CD, Flux) so the cluster state always matches Git and drift is detected.
- Load-test rollouts with `maxUnavailable`/`maxSurge` tuned so a deploy never drops below
  capacity.
- Alert on `Pending` Pods and OOMKilled restarts — both usually mean a resources bug.

## AI Review Checklist

- Is every image pinned to a digest or specific tag, never `:latest`?
- Does every container declare CPU and memory `requests` and `limits`?
- Does the readiness probe verify the app can actually serve, not just that it started?
- Is all state external to the Pod, so any Pod can be killed and rescheduled safely?
- Are there multiple replicas plus a PodDisruptionBudget and topology spread?
- Does the container run as non-root with dropped capabilities and a read-only rootfs?
- Is the workload managed declaratively (GitOps / `kubectl apply`), with no manual drift?

## Related

- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/27-best-practices.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/21-observability.md`
- `knowledge/kubernetes/26-production.md`
