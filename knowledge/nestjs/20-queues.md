---
id: nestjs/20-queues
topic: nestjs
slug: queues
title: "NestJS Queues"
type: doc
order: 20
status: ready
tags: [nestjs, queues]
related: [nestjs/21-events, nestjs/23-distributed-systems, backend/16-background-jobs, redis/16-message-queues]
when_to_use: "Read before building or reviewing background jobs, queues, or asynchronous work moved outside the request lifecycle."
---
# NestJS Queues

## Purpose

This document defines the engineering standards for implementing asynchronous job processing using queues in NestJS applications.

The objective is to move long-running, resource-intensive, and retryable work outside the synchronous request lifecycle while maintaining reliability, observability, and scalability.

Queues execute background work.

They should not replace synchronous business logic unnecessarily.

---

## Core Principle

Respond quickly.

Process expensive work asynchronously.

---

## Queue Goals

Every queue system should provide:

- reliability;
- scalability;
- fault tolerance;
- retry support;
- observability;
- predictable execution.

Background processing should never compromise business consistency.

---

## Responsibilities

Queues are responsible for:

- asynchronous processing;
- workload distribution;
- retrying transient failures;
- scheduling delayed work;
- smoothing traffic spikes.

Queues should not:

- replace transactions;
- implement authorization;
- become permanent storage;
- execute request validation.

---

## Processing Flow

```
HTTP Request

↓

Business Service

↓

Persist Business State

↓

Enqueue Job

↓

Worker

↓

Execute Background Task

↓

Complete
```

Business state should be committed before background processing begins.

---

## Typical Use Cases

Queues are appropriate for:

- sending emails;
- generating reports;
- image processing;
- video transcoding;
- webhook delivery;
- data synchronization;
- notifications;
- scheduled jobs.

Avoid queues for operations that must complete before responding to the client.

---

## Queue Technologies

Common implementations include:

- BullMQ;
- RabbitMQ;
- Kafka;
- Amazon SQS;
- Google Pub/Sub;
- Azure Service Bus.

Application architecture should remain independent of the queue provider.

---

## Job Design

Every job should have:

- unique identifier;
- payload;
- creation timestamp;
- retry metadata;
- execution status.

Jobs should contain only the data required for execution.

The idiomatic NestJS integration is `@nestjs/bullmq` (BullMQ over Redis). Register the connection once, declare each queue, and set safe default job options — retries, exponential backoff, and retention — in one place so producers stay simple.

```ts
// email.module.ts
import { Module } from '@nestjs/common';
import { BullModule } from '@nestjs/bullmq';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { EmailService } from './email.service';
import { EmailProcessor } from './email.processor';

@Module({
  imports: [
    // Register the Redis connection once for the whole application.
    BullModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        connection: {
          host: config.getOrThrow<string>('REDIS_HOST'),
          port: config.getOrThrow<number>('REDIS_PORT'),
        },
      }),
    }),
    // Declare the queues this module produces to and consumes from.
    BullModule.registerQueue(
      {
        name: 'email',
        defaultJobOptions: {
          attempts: 5,
          backoff: { type: 'exponential', delay: 5000 },
          removeOnComplete: 1000,
          removeOnFail: false, // keep failed jobs for inspection and DLQ routing
        },
      },
      { name: 'email-dlq' },
    ),
  ],
  providers: [EmailService, EmailProcessor],
})
export class EmailModule {}
```

The producer enqueues **after** the business state is committed, and uses a
stable `jobId` so re-enqueueing the same unit of work is a no-op:

```ts
// email.service.ts
import { Injectable } from '@nestjs/common';
import { InjectQueue } from '@nestjs/bullmq';
import { Queue } from 'bullmq';

export interface WelcomeEmailJob {
  userId: string;
  email: string;
  correlationId: string;
}

@Injectable()
export class EmailService {
  constructor(
    @InjectQueue('email') private readonly emailQueue: Queue<WelcomeEmailJob>,
  ) {}

  async enqueueWelcomeEmail(job: WelcomeEmailJob): Promise<void> {
    // Call this only once the user has been persisted and committed.
    await this.emailQueue.add('send-welcome', job, {
      // A stable jobId makes enqueueing idempotent: a second add with the
      // same id is ignored while that job is still in the queue.
      jobId: `welcome:${job.userId}`,
    });
  }
}
```

---

## Idempotency

Workers should be idempotent.

Running the same job multiple times should not produce duplicate business effects.

Examples:

- sending duplicate invoices → avoid;
- charging the same payment twice → avoid;
- creating duplicate records → avoid.

Idempotency is essential for reliable distributed systems.

---

## Retry Strategy

Retry only transient failures.

Examples:

- temporary network errors;
- unavailable external APIs;
- temporary database connectivity issues.

Do not retry:

- validation failures;
- authorization failures;
- permanent business rule violations.

In BullMQ, a processor that throws a normal error is retried until `attempts`
is exhausted. Throw `UnrecoverableError` to fail a job **immediately** with no
further retries — use it for permanent failures.

```ts
// Bad — every failure consumes all 5 attempts, including permanent ones.
// A malformed payload burns retries and delays reaching the DLQ.
async process(job: Job<WelcomeEmailJob>): Promise<void> {
  const dto = await this.validate(job.data); // throws on invalid data
  await this.mailer.sendWelcome(dto);        // throws on network error
}
```

```ts
// Good — classify failures. Transient errors bubble up so BullMQ retries
// with backoff; permanent errors throw UnrecoverableError to fail at once.
import { UnrecoverableError } from 'bullmq';

async process(job: Job<WelcomeEmailJob>): Promise<void> {
  let dto: WelcomeEmailJob;
  try {
    dto = await this.validate(job.data);
  } catch {
    // Validation never succeeds on retry — do not waste attempts.
    throw new UnrecoverableError('Invalid email job payload');
  }

  // Network/SMTP errors are transient — let them bubble up to be retried.
  await this.mailer.sendWelcome(dto);
}
```

---

## Backoff Strategy

Prefer exponential backoff.

Example:

```
Retry 1 → 5 seconds

Retry 2 → 15 seconds

Retry 3 → 45 seconds

Retry 4 → 2 minutes
```

Avoid aggressive retry loops.

---

## Dead Letter Queue (DLQ)

Failed jobs exceeding retry limits should move to a Dead Letter Queue.

```
Job

↓

Retries Exhausted

↓

Dead Letter Queue

↓

Manual Investigation
```

Never silently discard failed jobs.

---

## Poison Messages

A poison message consistently fails processing.

Detect:

- repeated failures;
- malformed payloads;
- incompatible schemas.

Move poison messages to the DLQ.

---

## Delayed Jobs

Use delayed execution for:

- reminders;
- scheduled notifications;
- retry scheduling;
- deferred processing.

Scheduling should remain predictable.

---

## Job Priorities

Support priorities when required.

Example:

High:

- payment processing;
- security events.

Medium:

- notifications.

Low:

- analytics;
- report generation.

Priorities should reflect business value.

---

## Worker Design

Workers should:

- perform one responsibility;
- remain stateless;
- be horizontally scalable;
- produce structured logs.

Avoid large, multi-purpose workers.

A NestJS worker is a `@Processor` class extending `WorkerHost`. The single
`process` method handles one job type; concurrency is configured on the
decorator, and `@OnWorkerEvent` hooks handle lifecycle events. Even though the
payload came from our own queue, it is untrusted input and is validated before
use. The `failed` handler routes exhausted or unrecoverable jobs to the DLQ —
BullMQ has no native dead-letter queue, so this is done explicitly.

```ts
// email.processor.ts
import {
  Processor,
  WorkerHost,
  OnWorkerEvent,
  InjectQueue,
} from '@nestjs/bullmq';
import { Logger } from '@nestjs/common';
import { Job, Queue, UnrecoverableError } from 'bullmq';
import { plainToInstance } from 'class-transformer';
import { validateOrReject, IsEmail, IsString } from 'class-validator';
// Your application's own mail sender (declared as a Nest provider).
import { MailerService } from './mailer.service';

class WelcomeEmailPayload {
  @IsString() userId!: string;
  @IsEmail() email!: string;
  @IsString() correlationId!: string;
}

@Processor('email', { concurrency: 5 })
export class EmailProcessor extends WorkerHost {
  private readonly logger = new Logger(EmailProcessor.name);

  constructor(
    private readonly mailer: MailerService,
    @InjectQueue('email-dlq') private readonly dlq: Queue,
  ) {
    super();
  }

  async process(job: Job<unknown>): Promise<void> {
    const payload = plainToInstance(WelcomeEmailPayload, job.data);
    try {
      await validateOrReject(payload);
    } catch {
      // Schema violations are permanent — fail fast, do not retry.
      throw new UnrecoverableError('Invalid email job payload');
    }

    // Idempotency guard: sending the same welcome email twice is a business
    // bug, so short-circuit if delivery was already recorded.
    if (await this.mailer.alreadySent(payload.userId)) {
      this.logger.log(`Skipping duplicate welcome email for ${payload.userId}`);
      return;
    }

    // Transient SMTP/network errors bubble up and are retried with backoff.
    await this.mailer.sendWelcome(payload);
  }

  @OnWorkerEvent('failed')
  async onFailed(job: Job, err: Error): Promise<void> {
    this.logger.error(
      `Job ${job.id} failed on attempt ${job.attemptsMade}: ${err.message}`,
    );

    const exhausted = job.attemptsMade >= (job.opts.attempts ?? 1);
    if (exhausted || err instanceof UnrecoverableError) {
      await this.dlq.add('dead-letter', {
        originalName: job.name,
        data: job.data,
        reason: err.message,
      });
    }
  }
}
```

`WorkerHost` closes its BullMQ worker on application shutdown, so enable Nest's
shutdown hooks in `main.ts` (`app.enableShutdownHooks()`) to let in-flight jobs
finish before the process exits.

---

## Concurrency

Configure worker concurrency carefully.

Consider:

- CPU usage;
- database capacity;
- external API limits;
- memory consumption.

Higher concurrency is not always better.

---

## Ordering

Do not assume global ordering.

If ordering matters:

- partition work;
- serialize processing for affected entities.

Explicitly document ordering guarantees.

---

## Queue Monitoring

Monitor:

- queue length;
- processing rate;
- retry count;
- failed jobs;
- worker utilization;
- processing latency.

Healthy queues require continuous monitoring.

---

## Graceful Shutdown

Workers should:

- stop accepting new jobs;
- finish active jobs;
- acknowledge completed work;
- exit cleanly.

Avoid terminating active processing abruptly.

---

## Observability

Every job should include:

- correlation ID;
- execution duration;
- retry count;
- worker identifier;
- failure reason.

Background execution should be traceable.

---

## Security

Validate all job payloads.

Never trust queued data simply because it originated internally.

Protect:

- API keys;
- tokens;
- personal data.

Sensitive information should be minimized.

---

## Performance

Optimize:

- batch processing;
- payload size;
- worker concurrency;
- retry frequency.

Avoid oversized job payloads.

---

## Testing

Verify:

- successful execution;
- retries;
- dead-letter handling;
- idempotency;
- delayed jobs;
- graceful shutdown.

Queue behavior should remain deterministic.

---

## AI Decision Matrix

Use queues for:

✓ Email delivery

✓ Image processing

✓ Report generation

✓ Notifications

✓ External integrations

Do **not** use queues for:

✗ Authentication

✗ Authorization

✗ Request validation

✗ Immediate user responses

---

## AI Execution Checklist

## Investigation

☐ Identify asynchronous work.

☐ Review retry requirements.

☐ Review failure scenarios.

☐ Review scalability needs.

---

## Planning

☐ Design idempotent jobs.

☐ Configure retries.

☐ Configure DLQ.

☐ Plan observability.

---

## Verification

☐ Jobs idempotent.

☐ Retries appropriate.

☐ DLQ configured.

☐ Correlation IDs propagated.

☐ Graceful shutdown supported.

☐ Queue independently testable.

---

## Examples

**Good Example** — idempotent job, bounded retries, permanent failures sent to the DLQ

```ts
@Injectable()
export class OrdersService {
  constructor(@InjectQueue('emails') private readonly emails: Queue) {}

  async place(command: PlaceOrder): Promise<Order> {
    const order = await this.orders.create(command);

    await this.emails.add(
      'order-confirmation',
      { orderId: order.id },              // an id, not the whole object
      {
        jobId: `order-confirmation:${order.id}`,   // deduplicates retries of the caller
        attempts: 5,
        backoff: { type: 'exponential', delay: 1_000 },
        removeOnComplete: 1_000,
        removeOnFail: false,              // keep failures for inspection
      },
    );

    return order;
  }
}
```

```ts
@Processor('emails')
export class EmailProcessor extends WorkerHost {
  async process(job: Job<{ orderId: string }>): Promise<void> {
    const order = await this.orders.findById(job.data.orderId);

    // A malformed or obsolete job must not consume all five attempts.
    if (!order) {
      throw new UnrecoverableError(`Order ${job.data.orderId} no longer exists`);
    }

    // Idempotency: the worker may run twice for the same job after a crash.
    if (order.confirmationSentAt) {
      return;
    }

    await this.mailer.sendConfirmation(order);
    await this.orders.markConfirmationSent(order.id);
  }
}
```

**Bad Example** — the payload is the state, and every failure retries forever

```ts
// The whole entity is serialised into the job. By the time it runs, the order
// has changed — and the worker acts on a snapshot that is minutes old.
await this.emails.add('order-confirmation', { order }, { attempts: Number.MAX_SAFE_INTEGER });

@Processor('emails')
export class EmailProcessor extends WorkerHost {
  async process(job: Job<{ order: OrderEntity }>): Promise<void> {
    // No idempotency check: a redelivery sends the customer a second email.
    await this.mailer.sendConfirmation(job.data.order);

    // A validation failure is permanent, but it is thrown as a generic error,
    // so it retries forever and the queue never drains.
    if (!job.data.order.email) {
      throw new Error('missing email');
    }
  }
}
```

---

## Common Mistakes

Avoid:

Performing synchronous work inside request handlers.

Retrying permanent failures.

Ignoring duplicate job execution.

Creating oversized job payloads.

Dropping failed jobs.

Ignoring monitoring.

Blocking workers with long-running synchronous code.

---

## Completion Criteria

Queue implementation is complete when:

- asynchronous work is isolated from request processing;
- jobs are idempotent;
- retries and backoff are configured;
- failed jobs are recoverable through a Dead Letter Queue;
- observability is implemented;
- workers can scale horizontally.

---

## Summary

Queues enable reliable asynchronous processing in NestJS applications.

By designing idempotent jobs, configuring intelligent retry strategies, using Dead Letter Queues, monitoring worker health, and treating background processing as a first-class architectural component, applications become more scalable, resilient, and production-ready.

## Related

- `knowledge/nestjs/21-events.md`
- `knowledge/nestjs/23-distributed-systems.md`
- `knowledge/backend/16-background-jobs.md`
- `knowledge/redis/16-message-queues.md`
