---
id: aws/21-sqs
topic: aws
slug: sqs
title: "SQS"
type: doc
order: 21
status: ready
tags: [aws, sqs]
related: [aws/22-sns, aws/23-eventbridge, aws/12-lambda, aws/14-cloudwatch, aws/02-iam]
when_to_use: "Read before producing to or consuming from an SQS queue, or wiring a dead-letter queue."
---
# SQS

## Purpose

This document defines how to use Amazon SQS (Simple Queue Service) correctly: queue
types, message visibility, idempotency, dead-letter queues, and consumer behavior. It is
written so an agent can build a producer/consumer that survives duplicates, retries, and
poison messages without losing or double-processing work.

SQS is a durable, pull-based queue that decouples producers from consumers. A consumer
*receives* a message (which hides it for a **visibility timeout**), processes it, then
*deletes* it. Understanding that receive-process-delete cycle is the whole game — most
SQS bugs are a misunderstanding of it.

## Why It Matters

Queues are where "it worked in the demo" meets reality: retries, duplicates, slow
consumers, and messages that can never succeed. SQS **Standard** guarantees at-least-once
delivery, which means duplicates *will* happen — a consumer that assumes exactly-once
will double-charge a card or double-ship an order. A message deleted before processing
finishes is lost; a message never deleted is redelivered forever. Without a dead-letter
queue, one poison message can wedge a consumer in an infinite retry loop, starving every
healthy message behind it. These are correctness bugs, not performance tuning.

## Core Principles

- **Design consumers to be idempotent.** At-least-once delivery means the same message
  can arrive twice. Dedupe on a business key or a `MessageId` you record, so reprocessing
  is a no-op — never assume exactly-once on Standard queues.
- **Delete only after successful processing.** The visibility timeout hides a message
  during work; delete it only when the work is durably done. Delete-then-crash loses the
  message.
- **Size the visibility timeout to the work.** It must exceed your worst-case processing
  time, or SQS redelivers a message you are still handling, causing concurrent duplicate
  processing.
- **Every production queue needs a dead-letter queue.** A `RedrivePolicy` with a
  `maxReceiveCount` moves poison messages aside after N failures so they stop blocking the
  queue and can be inspected.
- **Choose the queue type deliberately.** Standard = high throughput, at-least-once,
  best-effort ordering. FIFO = exactly-once processing and strict ordering per message
  group, at lower throughput. Pick FIFO only when you truly need ordering or dedup.

## Best Practices

- Attach a **DLQ** to every queue with a sensible `maxReceiveCount` (e.g. 5). Alarm on
  DLQ depth > 0 — messages there mean something is broken.
- Use **long polling** (`WaitTimeSeconds` up to 20) to cut empty receives, reduce cost,
  and lower latency. Short polling wastes API calls.
- Set the visibility timeout from measured processing time plus headroom; for variable
  work, extend it with `ChangeMessageVisibility` while processing rather than setting a
  huge default.
- Encrypt queues with **SSE-KMS**, and scope producer/consumer IAM to specific queue ARNs
  and actions (`sqs:SendMessage` vs `sqs:ReceiveMessage`/`DeleteMessage`), never `sqs:*`.
- For FIFO queues, set a meaningful `MessageGroupId` (ordering scope) and either a
  content-based or explicit `MessageDeduplicationId`.
- When triggering **Lambda** from SQS, report partial failures with
  `ReportBatchItemFailures` so only failed messages are retried, not the whole batch.
- Batch sends/deletes (`SendMessageBatch`, up to 10) to cut request cost under load.

## Examples

**Good Example** — idempotent consumer, delete after success, DLQ configured

```python
import boto3

sqs = boto3.client("sqs")

def poll(queue_url: str) -> None:
    resp = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20,        # long polling: fewer empty receives, lower cost
        VisibilityTimeout=60,      # must exceed worst-case processing time
    )
    for msg in resp.get("Messages", []):
        key = msg["MessageAttributes"]["orderId"]["StringValue"]
        if already_processed(key):     # idempotency: at-least-once means duplicates happen
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])
            continue
        process(msg)                    # durable side effect
        mark_processed(key)
        # Delete ONLY after success — a crash before here safely redelivers the message.
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])
    # A poison message that never succeeds hits maxReceiveCount and lands in the DLQ.
```

**Bad Example** — delete before processing, assumes exactly-once, no DLQ

```python
def poll(queue_url: str) -> None:
    resp = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)  # short poll
    for msg in resp.get("Messages", []):
        # Deleting first means a crash in process() loses the message forever.
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])
        process(msg)   # no idempotency -> duplicate delivery double-processes
    # No DLQ: a message that always fails is redelivered until it expires, blocking work.
```

## Common Mistakes

- Deleting a message before processing completes, losing it on any failure.
- Assuming exactly-once on a Standard queue and double-charging or double-shipping.
- Visibility timeout shorter than processing time, causing concurrent redelivery of
  in-flight messages.
- No dead-letter queue, so a poison message loops forever and starves the queue.
- Using SQS as a pub/sub fan-out to many consumers — a message is consumed once; use
  [SNS](22-sns.md) or [EventBridge](23-eventbridge.md) to fan out.
- Short polling everywhere, inflating request cost and latency.
- Ignoring the 256 KB message size limit instead of storing large payloads in S3 and
  passing a pointer.

## Production Tips

- Alarm on `ApproximateNumberOfMessagesVisible` (backlog growing = consumers falling
  behind) and on `ApproximateAgeOfOldestMessage` (work is stalling).
- Alarm on DLQ depth and build a redrive path to replay fixed messages back to the main
  queue after a bug fix.
- For large payloads, use the S3 extended-client pattern: body in S3, reference in the
  message, so you stay under the size limit.
- Prefer FIFO high-throughput mode when you need ordering without the classic FIFO
  throughput ceiling.

## AI Review Checklist

- Is the consumer idempotent, tolerating at-least-once duplicate delivery?
- Is the message deleted only after processing durably succeeds?
- Does the visibility timeout exceed worst-case processing time?
- Is a dead-letter queue configured with a `maxReceiveCount`, and alarmed on depth?
- Is long polling enabled to avoid wasteful empty receives?
- Is IAM scoped to specific queue ARNs and send/receive actions, and is SSE-KMS on?
- If ordering/dedup is required, is a FIFO queue used with correct group/dedup IDs?

## Related

- `knowledge/aws/22-sns.md`
- `knowledge/aws/23-eventbridge.md`
- `knowledge/aws/12-lambda.md`
- `knowledge/aws/14-cloudwatch.md`
- `knowledge/aws/02-iam.md`
