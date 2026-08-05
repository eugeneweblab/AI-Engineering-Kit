---
id: nodejs/24-background-jobs
topic: nodejs
slug: background-jobs
title: "Node.js Background Jobs"
type: doc
order: 24
status: ready
tags: [nodejs, background-jobs, setTimeout, send, setInterval, alreadySent, Queue, Worker]
related: [nodejs/12-worker-threads, nodejs/16-error-handling, nodejs/17-logging, nodejs/25-microservices, nodejs/27-monitoring]
when_to_use: "Read before moving slow or unreliable work (email, image processing, webhooks, scheduled tasks) out of the request path."
---
# Node.js Background Jobs

## Purpose

This document defines how to run work outside the HTTP request/response cycle in
Node.js: queued jobs, workers, retries, and scheduling. It is written so an agent can
build a job system that survives crashes, deploys, and duplicate delivery without
losing or double-processing work.

A background job is any unit of work a request enqueues but does not wait for — sending
email, resizing an image, calling a slow third party, generating a report. The request
returns immediately; a separate worker process does the work later.

## Why It Matters

Doing slow or failure-prone work inside a request ties the user's latency (and your
event loop) to systems you do not control. A 30-second payment-provider call becomes a
30-second page load and a blocked worker. When the process restarts mid-work — every
deploy does this — in-memory "background" work vanishes with no record. A durable queue
turns "we lost 400 confirmation emails during the 2pm deploy" into "they were retried
after restart." The core risk is not throughput; it is *silent loss and silent
duplication*.

## Core Principles

- **Persist the job before you acknowledge the request.** A job that lives only in
  memory (`setTimeout`, an in-process array) is gone on restart. Write it to a durable
  store (Redis, Postgres, a broker) first.
- **Make handlers idempotent.** At-least-once delivery is the norm, not the exception.
  The same job *will* run twice; the second run must be a safe no-op.
- **Retry with backoff, then dead-letter.** Transient failures deserve retries;
  permanent failures must stop and be parked for inspection, not loop forever.
- **Keep the event loop free.** CPU-bound jobs still block the worker's event loop.
  Offload real computation to [worker threads](12-worker-threads.md) or child processes.
- **Separate the worker from the web process.** Scale, deploy, and crash them
  independently. A stuck job must not take down the API.

## Best Practices

- Use a battle-tested queue — **BullMQ** (Redis) for most apps, or a broker-backed queue
  (RabbitMQ, SQS) at [microservice](25-microservices.md) scale. Do not hand-roll a queue.
- Derive an idempotency key from the payload (`jobId = hash(userId + orderId)`) so
  enqueuing the same logical work twice collapses to one job.
- Configure bounded retries with exponential backoff and jitter; after the limit, route
  to a dead-letter queue and alert — never `attempts: Infinity`.
- Set a per-job timeout. A handler that hangs on a socket must be killed, not leaked.
- Make handlers pure of hidden global state and safe to run concurrently; assume N
  workers process the queue at once.
- For scheduled work, use the queue's repeatable/cron feature (one owner) rather than a
  `setInterval` in every replica, which fires N times.
- Log job start, success, failure, and retry with the job id and attempt number so a
  failed job is [traceable](27-monitoring.md), never a mystery.
- Store large payloads by reference (an S3 key, a row id), not inline — keep the queue
  message small.

## Examples

**Good Example** — durable queue, idempotent handler, bounded retries

```ts
import { Queue, Worker } from "bullmq";

const emails = new Queue("emails", { connection: redis });

// Enqueue with a deterministic jobId so a duplicate enqueue is dropped by the queue.
await emails.add(
  "welcome",
  { userId },
  { jobId: `welcome:${userId}`, attempts: 5, backoff: { type: "exponential", delay: 1000 } },
);

new Worker(
  "emails",
  async (job) => {
    // Idempotency: if we already recorded this send, return without re-sending.
    if (await alreadySent(job.data.userId, "welcome")) return;
    await mailer.send(job.data.userId, "welcome");
    await markSent(job.data.userId, "welcome"); // commit the effect atomically with the send
  },
  { connection: redis, concurrency: 10 }, // survives restart; failed jobs retry with backoff
);
```

**Bad Example** — in-memory "job", lost on restart, retried forever

```ts
app.post("/signup", async (req, res) => {
  createUser(req.body);
  res.json({ ok: true });

  // Not durable: a deploy or crash before this runs loses the email with no record.
  setTimeout(async () => {
    for (;;) {                        // unbounded retry — a bad address loops forever
      try { await mailer.send(req.body.email, "welcome"); break; }
      catch { /* no backoff, no dead-letter, no log */ }
    }
  }, 0);
});
```

## Common Mistakes

- Treating `setTimeout`/`process.nextTick`/an in-memory array as a job queue; it does
  not survive restart and cannot scale past one process.
- Non-idempotent handlers that charge a card or send an email twice on redelivery.
- Unbounded retries with no dead-letter queue, turning one poison message into an
  infinite loop that starves healthy jobs.
- Running CPU-heavy work directly in the handler, blocking the worker's event loop.
- A `setInterval` cron in every replica, so scheduled jobs fire once per instance.
- No per-job timeout, so a hung external call pins a worker slot indefinitely.
- Enqueuing giant payloads, bloating Redis/broker memory.

## Production Tips

- Monitor queue depth, wait time, and dead-letter count; a growing backlog is an early
  outage signal before users notice.
- Give the worker a graceful shutdown: stop pulling new jobs on `SIGTERM`, let in-flight
  jobs finish (up to a deadline), then exit — otherwise every deploy orphans work.
- Keep a dashboard or admin route to inspect, retry, and drain the dead-letter queue.
- Separate queues by priority/latency (transactional email vs. nightly report) so a slow
  bulk job cannot delay a time-sensitive one.

## AI Review Checklist

- Is the job persisted to a durable store before the request is acknowledged?
- Is the handler idempotent under at-least-once (duplicate) delivery?
- Are retries bounded with backoff, and do exhausted jobs go to a dead-letter queue?
- Does each job have a timeout, and does the worker shut down gracefully on `SIGTERM`?
- Is CPU-bound work offloaded to a [worker thread](12-worker-threads.md), not run inline?
- Are scheduled jobs owned by one runner, not duplicated across every replica?
- Is each job logged with an id and attempt number for [tracing](27-monitoring.md)?

## Related

- `knowledge/nodejs/12-worker-threads.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/17-logging.md`
- `knowledge/nodejs/25-microservices.md`
- `knowledge/nodejs/27-monitoring.md`
