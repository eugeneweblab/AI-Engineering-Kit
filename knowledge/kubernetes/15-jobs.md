---
id: kubernetes/15-jobs
topic: kubernetes
slug: jobs
title: "Jobs"
type: doc
order: 15
status: ready
tags: [kubernetes, jobs, backoffLimit, ttlSecondsAfterFinished, activeDeadlineSeconds, OnFailure, Always, resources.requests]
related: [kubernetes/16-cronjobs, kubernetes/05-deployments, kubernetes/19-resource-management, kubernetes/04-pods, kubernetes/24-debugging]
when_to_use: "Read before running a batch task, migration, or one-off script that must run to completion rather than run forever."
---
# Jobs

## Purpose

This document defines how to run a workload that **runs to completion** and then stops — a
data migration, a batch import, a report generation, a backfill — using a **Job**. A
[Deployment](05-deployments.md) keeps pods running forever and restarts them when they
exit; a Job does the opposite: it runs its pods until a target number succeed, then
considers itself done. For workloads that repeat on a schedule, wrap the Job in a
[CronJob](16-cronjobs.md).

Use a Job whenever "success" means the process exits `0`, not "the process stays up."

## Why It Matters

Batch work is where at-least-once and exactly-once semantics collide with reality. A Job
*will* retry a failed pod, and a pod can be killed and restarted for reasons unrelated to
your code (node drain, spot reclaim, OOM). If the task is not idempotent — it charges a
card, sends an email, or appends rows without a dedupe key — a retry does the work *twice*.
The most expensive Kubernetes incidents are not crashes; they are Jobs that quietly ran a
non-idempotent migration three times because `backoffLimit` did exactly what it promised.
A correct Job is idempotent, bounded, and observable. An incorrect one is a silent
double-billing engine.

## Core Principles

- **Completion is the success condition.** A Job finishes when `completions` pods exit `0`.
  Retries (`backoffLimit`) and parallelism (`parallelism`) are how it gets there.
- **Retries mean at-least-once — design for it.** Any Job pod may run more than once. The
  task must be idempotent or guarded by an external dedupe key. Kubernetes gives no
  exactly-once guarantee.
- **Jobs do not clean up after themselves by default.** Completed Jobs and their pods
  linger until you delete them or set `ttlSecondsAfterFinished`.
- **Bound everything.** Without `backoffLimit` and `activeDeadlineSeconds`, a broken Job
  retries and burns resources indefinitely.
- **Parallelism is explicit.** `parallelism` sets concurrent pods; `completions` sets how
  many must succeed. Indexed completion (`completionMode: Indexed`) gives each pod a fixed
  index for partitioned work.

## Best Practices

- Make the task **idempotent** — use a unique job key, upsert instead of insert, or check
  "already done" before acting. Assume every step can run twice.
- Set `backoffLimit` deliberately (e.g. `4`). It caps retries; the default is `6`. A
  non-idempotent Job with a high backoff limit multiplies side effects.
- Set `activeDeadlineSeconds` so a hung Job is killed rather than running forever.
- Set `ttlSecondsAfterFinished` (e.g. `3600`) so finished Jobs and pods are auto-garbage-
  collected instead of accumulating.
- Set `restartPolicy: Never` (or `OnFailure`) on the pod template — a Job pod may not use
  `Always`. Prefer `Never` so each attempt is a fresh, inspectable pod.
- Set explicit `resources.requests`/`limits`; a batch job competing unbounded with services
  can degrade the whole cluster.
- For parallel partitioned work, use `completionMode: Indexed` and shard by
  `JOB_COMPLETION_INDEX` so pods don't process the same partition.
- Enable `podFailurePolicy` (stable since 1.31) to fail fast on non-retryable exit codes
  and avoid wasting the whole `backoffLimit` on a permanent error.

## Examples

**Good Example** — idempotent, bounded, self-cleaning

```yaml
apiVersion: batch/v1
kind: Job
metadata: { name: migrate-2026-07 }
spec:
  backoffLimit: 4                 # cap retries; task must tolerate re-runs
  activeDeadlineSeconds: 1800     # kill if it hangs past 30m
  ttlSecondsAfterFinished: 3600   # auto-delete Job + pods 1h after finish
  template:
    spec:
      restartPolicy: Never        # fresh pod per attempt, easy to inspect
      containers:
        - name: migrate
          image: myapp/migrator:1.8.0   # pinned tag, reproducible
          args: ["--idempotent", "--migration-id=2026-07"]  # dedupe key → safe to retry
          resources:
            requests: { cpu: 250m, memory: 256Mi }
            limits:   { cpu: 500m, memory: 512Mi }
```

**Bad Example** — non-idempotent, unbounded, leaks pods

```yaml
apiVersion: batch/v1
kind: Job
metadata: { name: charge-customers }
spec:
  backoffLimit: 20                # BUG: up to 20 retries of a payment step
  # No activeDeadlineSeconds → a hang runs forever.
  # No ttlSecondsAfterFinished → completed pods pile up until manual cleanup.
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: charge
          image: billing:latest   # unpinned
          # Inserts a charge row with no idempotency key:
          # a retried pod charges every customer AGAIN.
          command: ["./charge-all-customers.sh"]
```

## Common Mistakes

- Assuming a Job runs exactly once and writing non-idempotent side effects.
- No `activeDeadlineSeconds`, so a stuck Job runs indefinitely.
- No `ttlSecondsAfterFinished`, leaving completed Jobs/pods to accumulate and clutter the namespace.
- Setting `restartPolicy: Always` (rejected) or misunderstanding that `OnFailure` restarts
  the container in place, hiding failures across attempts.
- Using a Job for a long-running service (it will "complete" and stop) — use a Deployment.
- High `backoffLimit` on a non-idempotent task, multiplying side effects on every retry.
- Overlapping runs of the same Job via CronJob without a concurrency guard (see
  [CronJobs](16-cronjobs.md)).

## Production Tips

- Emit a structured "job started/finished/id" log and alert on Jobs that exceed their
  expected duration or exhaust `backoffLimit`.
- Store a durable idempotency record (a row keyed by migration id) so re-runs are no-ops.
- Keep a small pod-history window via TTL, but ship logs to your log backend before the
  pods are garbage-collected.
- For fan-out work, prefer `Indexed` completion over hand-partitioning with environment math.

## AI Review Checklist

- Is the task idempotent or guarded by an external dedupe key, given retries are at-least-once?
- Are `backoffLimit` and `activeDeadlineSeconds` both set to bound retries and runtime?
- Is `ttlSecondsAfterFinished` set so finished Jobs and pods are cleaned up?
- Is `restartPolicy` `Never` or `OnFailure` (never `Always`)?
- Are `resources.requests`/`limits` set so the batch job can't starve services?
- For a long-running process, is a [Deployment](05-deployments.md) used instead of a Job?

## Related

- `knowledge/kubernetes/16-cronjobs.md`
- `knowledge/kubernetes/05-deployments.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/24-debugging.md`
