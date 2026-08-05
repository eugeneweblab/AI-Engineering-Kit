---
id: aws/22-sns
topic: aws
slug: sns
title: "SNS"
type: doc
order: 22
status: ready
tags: [aws, sns, RedrivePolicy, region]
related: [aws/21-sqs, aws/23-eventbridge, aws/12-lambda, aws/02-iam, aws/14-cloudwatch]
when_to_use: "Read before publishing to an SNS topic or subscribing a queue, Lambda, or endpoint."
---
# SNS

## Purpose

This document defines how to use Amazon SNS (Simple Notification Service) correctly: topic
types, subscriptions, fan-out, delivery reliability, and access control. It is written so
an agent can build a publish/subscribe flow that fans a message out to many consumers
without losing messages, leaking access, or coupling the publisher to its subscribers.

SNS is push-based pub/sub: a publisher sends a message to a **topic**, and SNS delivers a
copy to every **subscription** (SQS queues, Lambda, HTTP(S), email, SMS). The canonical
pattern is **SNS-to-SQS fan-out**: one publish, many durable queues, each consumed
independently.

## Why It Matters

SNS is how one event reaches many systems without the publisher knowing who is listening.
The failure modes are about durability and trust. SNS delivery to an HTTP or Lambda
endpoint is fire-and-forget with limited retries — if the endpoint is down past the retry
window and there is no dead-letter queue, the message is gone with no trace. Fanning out
directly to Lambda/HTTP instead of to SQS means a slow subscriber cannot buffer and drops
work. And an unrestricted topic policy lets any account publish to—or subscribe to—your
topic, turning a notification channel into an injection or exfiltration path.

## Core Principles

- **Fan out to SQS for durability.** SNS-to-SQS gives each consumer a durable buffer that
  survives consumer downtime and absorbs bursts. Direct SNS-to-Lambda/HTTP has no buffer —
  a down consumer loses messages unless a DLQ catches them.
- **Attach a redrive/DLQ to every subscription.** A subscription-level dead-letter queue
  captures messages SNS could not deliver after retries, so failures are recoverable, not
  silent.
- **The publisher must not know its subscribers.** That decoupling is the point of pub/sub;
  add or remove consumers by changing subscriptions, never by editing the publisher.
- **Filter at the subscription, not in the consumer.** A **filter policy** lets SNS deliver
  only matching messages to a subscription, so consumers do not receive-and-discard traffic
  they do not want.
- **Lock down who can publish and subscribe.** Topic access policies and IAM decide who can
  send to and receive from the topic; default-open topics are a security hole.

## Best Practices

- Prefer the **SNS-to-SQS fan-out** pattern for backend consumers so each gets an
  independent, durable, replayable queue. Reserve direct Lambda/HTTP subscriptions for
  cases where a lost message is acceptable or a DLQ is attached.
- Configure a **subscription DLQ** (`RedrivePolicy`) on every subscription that matters,
  and alarm on its depth.
- Use **message filter policies** to route by attribute (e.g. `eventType`, `region`) so
  subscribers receive only relevant messages, cutting cost and consumer load.
- Choose **FIFO topics** only when you need strict ordering and dedup end-to-end (they pair
  with FIFO queues); otherwise use standard topics for throughput.
- Encrypt topics with **SSE-KMS**, and scope the topic policy to specific publisher
  principals and the `sns:Publish` action — never allow `Principal: "*"` without conditions.
- **Verify signatures** on HTTP(S) subscriptions and confirm subscriptions deliberately;
  auto-confirming an unknown endpoint lets attackers hijack delivery.
- Enable **delivery status logging** so you can see delivery successes and failures per
  subscription instead of guessing.

## Examples

**Good Example** — durable fan-out with a filter policy and restricted policy

```json
// Topic policy: only the orders service may publish. No wildcard principals.
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "AWS": "arn:aws:iam::111122223333:role/orders-api" },
    "Action": "sns:Publish",
    "Resource": "arn:aws:sns:eu-west-1:111122223333:order-events"
  }]
}
```

```bash
# Subscribe an SQS queue with a filter policy so it only gets shipped-order events,
# plus a DLQ so undeliverable messages are captured, not lost.
aws sns subscribe \
  --topic-arn arn:aws:sns:eu-west-1:111122223333:order-events \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:eu-west-1:111122223333:fulfilment \
  --attributes '{
    "FilterPolicy": "{\"eventType\":[\"order.shipped\"]}",
    "RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:eu-west-1:111122223333:fulfilment-dlq\"}"
  }'
```

**Bad Example** — open topic, direct-to-Lambda with no buffer or DLQ

```json
// Anyone in any account can publish to (and inject into) this topic.
{
  "Effect": "Allow",
  "Principal": "*",                       // no principal restriction, no conditions
  "Action": "sns:Publish",
  "Resource": "arn:aws:sns:eu-west-1:111122223333:order-events"
}
// Subscribing Lambda directly with no DLQ: if the function fails past the retry
// window, the message is gone with no record and no way to replay it.
```

## Common Mistakes

- Fanning out directly to Lambda/HTTP with no DLQ, so a down consumer drops messages
  silently.
- Topic policy with `Principal: "*"` and no conditions, letting any account publish.
- Filtering unwanted messages inside the consumer instead of with a subscription filter
  policy, paying to deliver and discard.
- Auto-confirming HTTP subscriptions or skipping signature verification, allowing delivery
  hijack.
- Using SNS where you need durable, ordered, single-consumer processing — that is
  [SQS](21-sqs.md)'s job.
- Expecting SNS to store messages: it does not; an endpoint offline past the retry window
  loses the message unless a DLQ catches it.
- Coupling the publisher to subscriber identities instead of letting subscriptions vary.

## Production Tips

- Alarm on `NumberOfNotificationsFailed` per topic and on subscription DLQ depth.
- Use SNS-to-SQS as the backbone and let SQS handle retries, visibility, and its own DLQ —
  SNS delivers once to the queue, the queue makes consumption reliable.
- For cross-account fan-out, grant subscribe permission explicitly in the topic policy and
  confirm subscriptions from a trusted principal.
- Consider [EventBridge](23-eventbridge.md) instead when you need content-based routing,
  archiving/replay, or schema discovery beyond SNS's attribute filtering.

## AI Review Checklist

- Do durable consumers subscribe via SQS (fan-out) rather than direct Lambda/HTTP?
- Does every subscription that matters have a DLQ, alarmed on depth?
- Is the topic policy scoped to specific publisher principals, never open `*`?
- Are filter policies used so subscribers receive only relevant messages?
- Is the topic encrypted with SSE-KMS?
- Are HTTP(S) subscription signatures verified and confirmations deliberate?
- Is the publisher decoupled from specific subscriber identities?

## Related

- `knowledge/aws/21-sqs.md`
- `knowledge/aws/23-eventbridge.md`
- `knowledge/aws/12-lambda.md`
- `knowledge/aws/02-iam.md`
- `knowledge/aws/14-cloudwatch.md`
