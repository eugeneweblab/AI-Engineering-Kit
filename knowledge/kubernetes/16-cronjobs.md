---
id: kubernetes/16-cronjobs
topic: kubernetes
slug: cronjobs
title: "Cronjobs"
type: doc
order: 16
status: ready
tags: [kubernetes, cronjobs, backoffLimit, activeDeadlineSeconds, ttlSecondsAfterFinished, Allow, OnFailure]
related: [kubernetes/15-jobs, kubernetes/19-resource-management, kubernetes/21-observability, kubernetes/24-debugging, kubernetes/26-production]
when_to_use: "Read before scheduling any recurring task — backups, report generation, cleanup, or periodic sync — on a cron schedule."
---
# Cronjobs

## Purpose

This document defines how to run a [Job](15-jobs.md) on a repeating schedule using a
**CronJob**. A CronJob is a Job factory: on each schedule tick it creates a new Job, which
runs to completion. Use it for backups, nightly reports, cache warming, cleanup, and
periodic syncs — anything that should happen "every N minutes/hours/days" rather than
continuously.

Everything true of Jobs (idempotency, retries, bounding) is true of the Jobs a CronJob
creates. This document adds what is unique to *scheduling*: cron syntax, time zones,
missed runs, and overlap.

## Why It Matters

Scheduled work fails in ways that are invisible until the day you need its output. A backup
CronJob that silently stopped running three weeks ago looks identical to a healthy one in
`kubectl get cronjob` — until a restore is needed and there is nothing there. Two failure
modes dominate: **overlap**, where a slow run is still going when the next tick fires and
two copies corrupt each other; and **schedule drift**, where a misread cron expression or a
UTC-vs-local timezone confusion runs the job at 4am instead of 4pm. Because the output is
consumed asynchronously (often by humans, days later), nobody notices the failure at the
time. A correct CronJob is idempotent, non-overlapping, timezone-explicit, and *monitored
for absence*, not just for errors.

## Core Principles

- **A CronJob only creates Jobs.** All Job semantics apply to each run; the CronJob itself
  just decides *when*. Configure the run under `jobTemplate`.
- **Concurrency must be chosen, not defaulted.** `concurrencyPolicy` decides what happens
  when a run is still active at the next tick: `Allow` (default, overlaps), `Forbid` (skip),
  or `Replace` (kill the old, start the new).
- **Schedules are wall-clock and timezone-sensitive.** As of the stable `timeZone` field,
  set it explicitly; without it the controller uses the kube-controller-manager's zone
  (usually UTC), which is rarely what you meant.
- **Missed ticks have a deadline.** `startingDeadlineSeconds` bounds how late a run may
  start after its scheduled time; miss it and the run is skipped, not queued forever.
- **History is bounded and must be harvested.** `successfulJobsHistoryLimit` /
  `failedJobsHistoryLimit` keep only the last few Jobs; ship logs before they roll off.

## Best Practices

- Set `concurrencyPolicy: Forbid` for jobs that must not overlap (backups, migrations,
  anything writing shared state). Use `Replace` only when the newest run supersedes the old.
- Set `timeZone` explicitly (e.g. `"America/New_York"`) so the schedule means what a human
  reads, and does not shift with DST assumptions.
- Set `startingDeadlineSeconds` (e.g. `120`) so a briefly unavailable controller does not
  fire a flood of missed runs at once, but a slightly late run still executes.
- Keep the underlying Job **idempotent and bounded** — set `backoffLimit`,
  `activeDeadlineSeconds`, and `ttlSecondsAfterFinished` on the `jobTemplate` exactly as for
  a standalone Job.
- Tune `successfulJobsHistoryLimit`/`failedJobsHistoryLimit` low (e.g. 3/3) to avoid pod
  buildup, but ship logs/metrics out first.
- Use `suspend: true` to pause a schedule (maintenance, incident) instead of deleting and
  recreating the object and losing its history.
- Validate the cron expression — five fields, minute-hour-dom-month-dow. `0 4 * * *` is
  4am; `4 * * * *` is every hour at minute 4. They are easy to swap.

## Examples

**Good Example** — non-overlapping, timezone-explicit, bounded

```yaml
apiVersion: batch/v1
kind: CronJob
metadata: { name: nightly-backup }
spec:
  schedule: "0 2 * * *"          # 02:00 daily, in the timeZone below
  timeZone: "America/New_York"   # explicit; not the controller's UTC default
  concurrencyPolicy: Forbid      # never run two backups at once
  startingDeadlineSeconds: 300   # if the tick is missed by <5m, still run; else skip
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 3600      # kill a backup that hangs past 1h
      ttlSecondsAfterFinished: 86400   # auto-clean finished Jobs after a day
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: backup
              image: myapp/backup:2.3.0   # pinned
              args: ["--dedupe-key=$(date +%F)"]  # idempotent per day
```

**Bad Example** — overlaps, ambiguous time, unbounded

```yaml
apiVersion: batch/v1
kind: CronJob
metadata: { name: sync }
spec:
  schedule: "* * * * *"          # BUG: every minute — a 90s run overlaps the next tick
  # No timeZone → runs in UTC, not the operator's local time they assumed.
  # concurrencyPolicy defaults to Allow → overlapping runs corrupt shared state.
  jobTemplate:
    spec:
      # No backoffLimit/activeDeadlineSeconds/ttl → failures pile up, pods accumulate.
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: sync
              image: sync:latest   # unpinned
```

## Common Mistakes

- Leaving `concurrencyPolicy` at the default `Allow`, so a slow run overlaps the next tick.
- Not setting `timeZone`, then being surprised the job runs on UTC, not local time.
- Misreading cron fields (swapping minute and hour) and running at the wrong time.
- Treating the CronJob as the unit of correctness and forgetting each run is a full Job that
  needs `backoffLimit`, `activeDeadlineSeconds`, and idempotency.
- Monitoring only for errors, not for *absence* — a schedule that stopped firing looks fine.
- Deleting a CronJob to pause it (and losing history) instead of `suspend: true`.

## Production Tips

- Add a **dead-man's-switch**: have each run ping a heartbeat/monitoring endpoint on success,
  and alert when the ping is missing — this catches "the schedule silently stopped."
- Verify backups by periodically restoring them; a green CronJob is not a tested backup.
- Stagger many CronJobs off the top of the hour (`7 * * * *`, not `0 * * * *`) to avoid a
  thundering herd of Jobs and pod scheduling spikes.
- Record run duration as a metric and alert when it trends toward the schedule interval —
  the early warning before overlap begins.

## AI Review Checklist

- Is `concurrencyPolicy` set (`Forbid`/`Replace`) for jobs that must not overlap?
- Is `timeZone` set explicitly so the schedule matches human intent?
- Is `startingDeadlineSeconds` set to bound missed-run behavior?
- Does the `jobTemplate` carry `backoffLimit`, `activeDeadlineSeconds`, and
  `ttlSecondsAfterFinished`, and is the task idempotent (see [Jobs](15-jobs.md))?
- Are history limits set so completed pods don't accumulate?
- Is there monitoring for *missed* runs, not just failed ones?

## Related

- `knowledge/kubernetes/15-jobs.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/21-observability.md`
- `knowledge/kubernetes/24-debugging.md`
- `knowledge/kubernetes/26-production.md`
