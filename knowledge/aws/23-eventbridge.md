---
id: aws/23-eventbridge
topic: aws
slug: eventbridge
title: "EventBridge"
type: doc
order: 23
status: ready
tags: [aws, eventbridge, EventPattern, OrderShipped, detail]
related: [aws/22-sns, aws/21-sqs, aws/12-lambda, aws/15-cloudtrail, aws/02-iam]
when_to_use: "Read before defining an EventBridge bus, rule, schedule, or event-driven integration."
---
# EventBridge

## Purpose

This document defines how to use Amazon EventBridge correctly: event buses, rules and
pattern matching, targets, schemas, retries, and schedules. It is written so an agent can
build event-driven routing that decouples producers from consumers, delivers reliably,
and fails into a recoverable place rather than a black hole.

EventBridge is a serverless event router. Producers put **events** onto a **bus**;
**rules** match events by content-based **pattern** and forward them to **targets** (Lambda,
SQS, Step Functions, other buses, SaaS partners). Prefer it over [SNS](22-sns.md) when you
need content-based routing, event archiving/replay, or schema tooling; prefer SNS for
simple, high-throughput attribute fan-out.

## Why It Matters

EventBridge is the nervous system of an event-driven architecture — get its guarantees
wrong and events vanish or storm. Delivery is asynchronous with retries and can be
**duplicated**, so a target that assumes exactly-once will double-process. A rule with no
dead-letter queue drops events that repeatedly fail their target, with no record. An
overly broad event pattern silently matches events you never intended, fanning garbage to
expensive targets. And because rules route by the *content* of the event, a producer that
changes an event's shape can break every downstream consumer at once unless the schema is
treated as a contract.

## Core Principles

- **Targets must be idempotent.** EventBridge delivers at-least-once and may retry, so the
  same event can arrive more than once. Dedupe on an event id or business key.
- **Every rule/target needs a DLQ.** Configure a dead-letter queue on the target so events
  that exhaust retries are captured for inspection and replay, not lost silently.
- **Match tightly with event patterns.** A specific pattern (source, detail-type, and
  detail fields) routes only what you mean; a broad pattern floods targets and costs money.
- **The event is a contract.** Version event schemas and evolve them additively; a breaking
  change to an event's structure breaks consumers whose rules match on it.
- **Use a custom bus per domain.** Keep application events off the `default` bus (which also
  carries AWS service events) so permissions and rules stay scoped and legible.

## Best Practices

- Create a **custom event bus** per bounded context; grant `events:PutEvents` only to the
  producers that belong on it, scoped by resource ARN.
- Write **specific event patterns** — filter on `source`, `detail-type`, and `detail`
  fields — so a rule matches exactly the events it should. Test patterns before deploying.
- Attach a **DLQ** (SQS) to every target and set retry policy (`MaximumRetryAttempts`,
  `MaximumEventAgeInSeconds`) deliberately; alarm on DLQ depth.
- Register events in the **schema registry** and generate typed bindings so producers and
  consumers share one contract instead of ad-hoc JSON.
- Use **EventBridge Scheduler** (not legacy `rate()`/`cron()` rules) for scheduled
  invocations; it supports time zones, one-time schedules, and flexible windows, and scales
  to millions of schedules.
- Enable **archive and replay** on buses that carry important events so you can reprocess
  after a bug fix or a new consumer comes online.
- For high fan-out to many independent, durable consumers, route EventBridge → SQS per
  consumer so each buffers and retries on its own.
- Keep target IAM (the role EventBridge assumes) least-privilege and scoped to the specific
  target resource.

## Examples

**Good Example** — tight pattern, DLQ, retries, idempotent target

```json
// Rule: match only shipped orders over $500 from the orders service. Narrow by design.
{
  "EventBusName": "orders",
  "EventPattern": {
    "source": ["orders.api"],
    "detail-type": ["OrderShipped"],
    "detail": { "totalCents": [{ "numeric": [">", 50000] }] }
  },
  "Targets": [{
    "Id": "notify-fulfilment",
    "Arn": "arn:aws:lambda:eu-west-1:111122223333:function:fulfilment",
    "RetryPolicy": { "MaximumRetryAttempts": 4, "MaximumEventAgeInSeconds": 3600 },
    "DeadLetterConfig": { "Arn": "arn:aws:sqs:eu-west-1:111122223333:fulfilment-dlq" } // exhausted retries land here
  }]
}
```

```python
# The target dedupes on the event id because delivery is at-least-once.
def handler(event, _ctx):
    event_id = event["id"]              # unique per EventBridge event
    if seen(event_id):
        return                          # duplicate delivery -> no-op
    process(event["detail"])
    mark_seen(event_id)
```

**Bad Example** — catch-all pattern, no DLQ, non-idempotent

```json
{
  "EventBusName": "default",           // app events mixed with AWS service events
  "EventPattern": { "source": ["orders.api"] },  // matches EVERY orders event, floods the target
  "Targets": [{
    "Id": "notify",
    "Arn": "arn:aws:lambda:eu-west-1:111122223333:function:fulfilment"
    // no RetryPolicy, no DeadLetterConfig -> failed events are dropped with no trace
  }]
}
// Handler that reprocesses on every delivery double-ships on any retry.
```

## Common Mistakes

- Non-idempotent targets that double-process on at-least-once redelivery.
- No DLQ on targets, so events that fail all retries disappear without a record.
- Catch-all event patterns that match far more than intended and flood costly targets.
- Putting application events on the `default` bus, mixing them with AWS service events and
  muddying permissions.
- Treating event JSON as ad-hoc and making breaking shape changes that silently break
  consumers matching on those fields.
- Using legacy scheduled rules instead of EventBridge Scheduler, missing time-zone and
  scale features.
- Reaching for EventBridge when simple attribute fan-out would be cheaper and simpler with
  [SNS](22-sns.md).

## Production Tips

- Alarm on `FailedInvocations` and `DeadLetterInvocations` per rule; a rising DLQ means a
  target is broken.
- Enable archive + replay before you need it; you cannot replay events that were never
  archived.
- Use input transformers to reshape events per target instead of forcing every consumer to
  parse the full envelope.
- Record `PutEvents` and rule changes via CloudTrail so event flow and routing changes are
  auditable.

## AI Review Checklist

- Are targets idempotent against at-least-once, possibly duplicated, delivery?
- Does every rule target have a DLQ and an explicit retry policy, alarmed on depth?
- Is the event pattern specific (source, detail-type, detail), not a catch-all?
- Do application events use a custom bus rather than the `default` bus?
- Are event schemas versioned and evolved additively as a contract?
- Is EventBridge Scheduler used for scheduling instead of legacy rate/cron rules?
- Is the target-invocation IAM role least-privilege and scoped to the target?

## Related

- `knowledge/aws/22-sns.md`
- `knowledge/aws/21-sqs.md`
- `knowledge/aws/12-lambda.md`
- `knowledge/aws/15-cloudtrail.md`
- `knowledge/aws/02-iam.md`
