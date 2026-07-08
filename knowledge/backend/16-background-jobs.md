---
id: backend/16-background-jobs
topic: backend
slug: background-jobs
title: "Background Jobs"
type: doc
order: 16
status: ready
tags: [backend, background-jobs]
related: [backend/15-message-brokers, backend/14-events, backend/17-transactions, backend/22-observability, backend/12-error-handling]
when_to_use: "Read before moving work off the request path — emails, exports, webhooks, scheduled tasks, or long jobs."
---
# Background Jobs

## Purpose

This document defines how to run work outside the request/response cycle: queued jobs,
scheduled (cron) tasks, and long-running processes. It covers job design, idempotency,
retries, scheduling, concurrency, timeouts, and graceful shutdown. The goal is that an
agent can move slow or deferrable work off the hot path without losing jobs, running them
twice, or hanging a worker.

A background job is a *unit of deferred work* pulled from a queue and executed by a
worker. It often rides on a [message broker](15-message-brokers.md) or a queue library
(BullMQ, Sidekiq, Celery, a database-backed queue); the same delivery and idempotency
rules apply.

## Why It Matters

Anything slow, flaky, or bursty belongs off the request path: sending email, generating a
report, calling a third-party API, resizing an image. Moving it to a background job keeps
requests fast and lets the system absorb spikes. But a job runs *detached* from the user
who triggered it — there is no one watching it fail. If a job is lost, the email never
sends and no error ever surfaces; if it runs twice, the customer is charged twice; if it
hangs, a worker is tied up forever. Background work fails silently by nature, so its
reliability has to be engineered in, not assumed.

## Core Principles

- **Jobs are delivered at-least-once — make them idempotent.** A worker can crash after
  doing the work but before marking the job done, so it will run again. Running a job
  twice must equal running it once.
- **A job carries an id and inputs, never a live object.** Pass the order *id*, not the
  order object or a request context. The job reloads current state; a serialized snapshot
  goes stale and cannot be trusted.
- **Every job must have a timeout.** An unbounded job holds a worker forever and starves
  the queue. Bound it, and make it resumable or safely re-runnable if it is killed.
- **Retries are expected; make them safe and bounded.** Exponential backoff with jitter,
  a max attempt count, then a dead-letter/failed state with an alert. Infinite retries
  hide bugs and burn resources.
- **Workers must shut down gracefully.** On deploy/SIGTERM, stop taking new jobs, finish
  or re-queue in-flight ones, then exit. Killing a worker mid-job must not lose work.

## Best Practices

- **Enqueue after commit, not before.** Enqueue the job inside or after the database
  transaction that created the work (ideally via the [outbox](14-events.md)), so you never
  queue work for a row that rolled back.
- Make handlers **idempotent** via a unique job key or a processed-jobs record, so retries
  and duplicate enqueues are no-ops.
- Set an **explicit timeout and max-attempts** on every job type. Route exhausted jobs to
  a **dead-letter / failed queue** and alert — never drop them silently.
- Use **separate queues per workload** (fast vs. slow, critical vs. bulk) so a flood of
  low-priority jobs cannot starve time-sensitive ones.
- For **scheduled jobs**, guarantee single execution across instances with a distributed
  lock or a scheduler that leases; otherwise every replica runs the cron at once.
- **Break large jobs into smaller ones** (batch/fan-out) so a failure retries a small unit,
  not hours of work, and progress is checkpointed.
- Bound **concurrency and rate** when a job calls an external API, to respect its limits
  and avoid self-inflicted throttling.
- Emit **structured logs and metrics** per job (enqueue, start, success, failure,
  duration) with a correlation id; see [observability](22-observability.md).

## Examples

**Good Example** — id-based, idempotent, bounded, graceful

```ts
// Enqueue AFTER the row is committed; pass an id, not the object.
queue.add("sendReceipt", { orderId }, {
  jobId: `receipt:${orderId}`,   // stable id -> duplicate enqueue is deduped
  attempts: 5,
  backoff: { type: "exponential", delay: 2000 }, // + jitter from the queue lib
  timeout: 30_000,               // a hung SMTP call cannot pin a worker forever
});

async function sendReceipt(job: Job<{ orderId: string }>) {
  const order = await db.orders.findById(job.data.orderId); // reload fresh state
  if (!order || order.receiptSentAt) return;                // idempotent: already done
  await mailer.sendReceipt(order);
  await db.orders.markReceiptSent(order.id);                // record so a retry no-ops
}

// Worker lifecycle: drain in-flight jobs on shutdown instead of killing them.
process.on("SIGTERM", async () => { await worker.close(); process.exit(0); });
```

**Bad Example** — snapshot payload, no idempotency, no bounds

```ts
// Enqueues the whole object BEFORE commit: if the tx rolls back, job runs on ghost data.
queue.add("sendReceipt", { order }); // stale snapshot; no jobId, no attempts, no timeout

async function sendReceipt(job: Job<{ order: Order }>) {
  // Uses the serialized order — may be out of date (price changed, order cancelled).
  await mailer.sendReceipt(job.data.order);
  // No "already sent" check: at-least-once delivery emails the customer twice.
  // No timeout: a slow SMTP server holds this worker indefinitely.
}
```

## Common Mistakes

- Enqueuing before the transaction commits, running jobs for rolled-back data.
- Passing full objects/snapshots instead of ids, so jobs act on stale state.
- Non-idempotent handlers, duplicating emails/charges on retry or redelivery.
- No timeout, letting one hung job pin a worker and drain the pool.
- Unbounded retries, hiding a permanent failure as endless churn.
- One shared queue, so bulk jobs starve latency-critical ones.
- Cron jobs firing on every instance because there is no single-execution lock.
- Hard-killing workers on deploy, losing or corrupting in-flight jobs.

## Production Tips

- Monitor **queue depth, job latency, failure rate, and DLQ size**; a growing backlog is
  the earliest sign workers are undersized or stuck.
- Make the **failed queue replayable** so you can fix the cause and re-run, not lose work.
- Set **worker concurrency** from real CPU/IO profile, not a guess; too high thrashes,
  too low wastes capacity.
- Ensure jobs are **safe to run late** — a receipt processed an hour after the order must
  still be correct, because backlogs happen.

## AI Review Checklist

- Is every job idempotent and keyed so retries/duplicates are no-ops?
- Does the job carry ids and reload fresh state, rather than a serialized snapshot?
- Is the job enqueued after commit (or via outbox), never for uncommitted data?
- Does every job type have a timeout, bounded attempts, and a dead-letter path?
- Are critical and bulk workloads on separate queues to prevent starvation?
- Do scheduled jobs have single-execution protection across instances?
- Do workers drain in-flight jobs on graceful shutdown?

## Related

- `knowledge/backend/15-message-brokers.md`
- `knowledge/backend/14-events.md`
- `knowledge/backend/17-transactions.md`
- `knowledge/backend/22-observability.md`
- `knowledge/backend/12-error-handling.md`
