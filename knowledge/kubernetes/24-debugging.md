---
id: kubernetes/24-debugging
topic: kubernetes
slug: debugging
title: "Debugging"
type: doc
order: 24
status: ready
tags: [kubernetes, debugging]
related: [kubernetes/04-pods, kubernetes/21-observability, kubernetes/23-monitoring, kubernetes/19-resource-management, kubernetes/07-services]
when_to_use: "Read before diagnosing a CrashLoopBackOff, Pending pod, failing probe, or unreachable Service."
---
# Debugging

## Purpose

This document defines how to diagnose a broken workload on Kubernetes: pods that will
not start, containers that crash-loop, probes that fail, and traffic that never
arrives. It is written so an agent can go from a symptom to a root cause using a
repeatable order of investigation, not guesswork.

Debugging on Kubernetes means reading the *reconciliation trail* — the events, states,
and logs the control plane leaves behind — rather than SSHing into a box. Almost every
answer is already in `kubectl describe`, the pod's events, or the last container's
logs.

## Why It Matters

A cluster is a distributed system with many moving controllers, so a single symptom
("my app is down") can originate from scheduling, image pull, config, networking,
storage, or the app itself. Guessing wastes an outage's worth of time and often makes
things worse (deleting the wrong pod, editing live state). A disciplined top-down
sequence — is it scheduled? did it pull? did it start? did it pass probes? can it be
reached? — narrows the fault domain in minutes and produces evidence you can attach to
an incident. The cost of skipping it is a longer outage and a change you cannot explain.

## Core Principles

- **Read state before you change it.** `kubectl describe` and `kubectl get -o yaml`
  first; mutations destroy the evidence you need.
- **Follow the pod lifecycle in order.** Pending -> ContainerCreating -> Running ->
  Ready. Diagnose the *first* stage that fails; later symptoms are downstream noise.
- **Events expire.** The `Events:` section is the fastest signal but is retained ~1
  hour by default. Capture it early.
- **Logs are per-container and per-restart.** Use `-c` for the right container and
  `--previous` to read the crashed instance, not the fresh one.
- **Reproduce inside the cluster.** Network and DNS problems only show up from a pod in
  the same namespace; `curl` from your laptop proves nothing.

## Best Practices

- Start with `kubectl describe pod <name>` and read `Events:` bottom-up — the reason is
  usually the last message (`ImagePullBackOff`, `FailedScheduling`, `OOMKilled`).
- For a crash loop, read the *previous* container's logs: `kubectl logs <pod> --previous`.
  The current logs are from the retry and often empty.
- Check `State`/`Last State` and the exit code in `describe`. Exit 137 = OOMKilled or
  SIGKILL; exit 1 = app error; `Error` with reason `OOMKilled` means raise the memory
  limit or fix the leak (see [resource-management](19-resource-management.md)).
- For `Pending`, read the scheduler's message: insufficient CPU/memory, unschedulable
  taints, or an unbound PVC. Fix the constraint, do not force-schedule.
- Use `kubectl debug` with an ephemeral container to attach a shell/toolbox to a
  distroless pod without rebuilding the image.
- Verify Services with `kubectl get endpoints <svc>` — no endpoints means the selector
  matches no ready pods, the most common "Service is down" cause.
- Prefer a debug sidecar or ephemeral container over `kubectl exec` into the app
  container; keep the app image minimal (see [security](22-security.md)).

## Examples

**Good Example** — top-down triage that isolates the failing stage

```bash
# 1. What state is the pod in and WHY? Read events bottom-up.
kubectl describe pod api-7d9f -n prod        # -> Events: OOMKilled, exit 137

# 2. Read the CRASHED container, not the restarted one.
kubectl logs api-7d9f -n prod --previous -c api

# 3. Confirm the resource envelope before changing anything.
kubectl get pod api-7d9f -n prod -o jsonpath='{.spec.containers[0].resources}'

# 4. If Service traffic fails, check endpoints — not the pod.
kubectl get endpoints api -n prod            # empty => selector/readiness problem
```

**Bad Example** — mutating live state and reading the wrong logs

```bash
# Deletes the evidence: the crashed pod (and its events) is gone forever.
kubectl delete pod api-7d9f -n prod

# Reads the FRESH retry container, which just started and logged nothing,
# so you conclude "no errors" and miss the real stack trace.
kubectl logs api-7d9f -n prod

# "Fixes" it by editing the live object by hand, so the change is not in Git
# and vanishes on the next reconcile/redeploy.
kubectl edit deployment api -n prod
```

## Common Mistakes

- Reading current logs instead of `--previous` on a crash-looping pod, seeing nothing,
  and declaring the app healthy.
- Deleting the failing pod before capturing `describe`/events, destroying the evidence.
- Treating a `Pending` pod as an app bug when the scheduler already explained the
  resource or taint constraint.
- Blaming the Service when `kubectl get endpoints` shows zero ready backends (a
  readiness-probe or selector-label mismatch).
- Debugging DNS/connectivity from your laptop instead of from a pod inside the cluster.
- Ignoring exit code 137 / `OOMKilled` and adding restarts instead of memory.

## Production Tips

- Ship logs and events to a central store (see [observability](21-observability.md)) so
  post-mortem data survives pod deletion and the 1-hour event TTL.
- Keep a small `netshoot`/`busybox` debug pod manifest handy for on-call DNS and
  connectivity checks in a locked-down cluster.
- Add `kubectl debug node/<node>` to inspect a NotReady node's kubelet and container
  runtime without SSH.

## AI Review Checklist

- Does the diagnosis start from `describe`/events before any mutation?
- Is the *first* failing lifecycle stage identified, not a downstream symptom?
- Are crash-loop logs read with `--previous` and the correct `-c` container?
- Are exit codes / `OOMKilled` interpreted, not just restarted away?
- Is a "Service down" report checked against `kubectl get endpoints`?
- Is connectivity tested from inside the cluster, not the operator's machine?

## Related

- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/21-observability.md`
- `knowledge/kubernetes/23-monitoring.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/07-services.md`
