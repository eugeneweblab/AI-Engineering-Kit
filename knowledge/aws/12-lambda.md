---
id: aws/12-lambda
topic: aws
slug: lambda
title: "Lambda"
type: doc
order: 12
status: ready
tags: [aws, lambda]
related: [aws/13-api-gateway, aws/16-secrets-manager, aws/17-parameter-store, aws/14-cloudwatch, aws/02-iam]
when_to_use: "Read before writing, deploying, or reviewing any AWS Lambda function or its trigger wiring."
---
# Lambda

## Purpose

This document defines how to write and operate AWS Lambda functions that are correct
under concurrency, cheap to run, and safe to fail. It covers the execution model,
cold starts, idempotency, permissions, and configuration so an agent can build or
review a function without introducing a scaling, security, or reliability defect.

Lambda runs your code in response to events with no server to manage. That convenience
hides a strict contract: your handler runs in a reused container, may run thousands of
copies at once, and is billed per millisecond. Code that ignores this contract works in
a demo and fails in production.

## Why It Matters

A Lambda mistake does not stay local. A function that leaks a database connection per
invocation exhausts the database at scale. A non-idempotent handler double-charges a
customer when the event is redelivered. A function with a 15-minute timeout and no
concurrency limit can silently drain a downstream API or run up a large bill. Because
Lambda auto-scales, small correctness bugs are multiplied by concurrency you did not
choose, and the symptoms appear downstream, far from the code that caused them.

## Core Principles

- **The handler must be idempotent.** Every event source can deliver at least once.
  Processing the same event twice must not change the result. Deduplicate on a business
  key, not on hope.
- **Separate init from handling.** Code outside the handler runs once per container and
  is reused. Create clients, load config, and open pools there — never inside the handler.
- **Assume concurrency, not a single instance.** N events means up to N live containers.
  Never use module-level mutable state as a cache of request-specific data.
- **Least-privilege the execution role.** The function's IAM role is its identity. Grant
  only the specific actions and resources it uses; deny everything else by omission.
- **Fail fast and let the platform retry.** Throw on unrecoverable errors so the event
  source or a dead-letter queue handles them. Do not swallow errors to look healthy.

## Best Practices

- Set an explicit `timeout` slightly above the real p99, and set `memorySize` by
  measuring — more memory also means more CPU, so a bigger function is often cheaper.
- Set **reserved concurrency** on functions that call rate-limited or fragile
  downstreams, so a traffic spike cannot overwhelm them. The cost is capped throughput.
- Read secrets from [Secrets Manager](16-secrets-manager.md) or config from
  [Parameter Store](17-parameter-store.md) at init time; cache them in the container.
  Never bake secrets into environment variables in plaintext or into the deployment package.
- For async and stream sources (SQS, Kinesis, DynamoDB Streams, EventBridge), configure
  a **dead-letter queue** or on-failure destination so poison events are captured, not lost.
- Prefer **provisioned concurrency** only where cold-start latency is user-visible; it
  costs money while idle. For most async work, cold starts are acceptable.
- Keep the deployment package small and dependencies minimal — package size and cold
  start are linked. Use layers for shared, heavy dependencies.
- Emit structured JSON logs and metrics; wire distributed tracing (X-Ray or OTel) so a
  slow invocation can be traced across services.

## Examples

**Good Example** — init reuse, idempotency, least-privilege assumed

```python
import os, json, boto3

# Runs ONCE per container, reused across invocations — the pool survives warm starts.
_ddb = boto3.resource("dynamodb")
_table = _ddb.Table(os.environ["ORDERS_TABLE"])

def handler(event, context):
    for record in event["Records"]:
        order = json.loads(record["body"])
        # Conditional put makes reprocessing the same event a no-op (at-least-once safe).
        try:
            _table.put_item(
                Item=order,
                ConditionExpression="attribute_not_exists(order_id)",
            )
        except _ddb.meta.client.exceptions.ConditionalCheckFailedException:
            continue  # already processed — idempotent, not an error
    return {"processed": len(event["Records"])}
```

**Bad Example** — per-call client, non-idempotent, silent failure

```python
import json, boto3

def handler(event, context):
    ddb = boto3.resource("dynamodb")          # new client every call → wasted latency
    table = ddb.Table("orders")
    for record in event["Records"]:
        order = json.loads(record["body"])
        table.put_item(Item=order)            # redelivery re-inserts / overwrites → double effect
    try:
        charge(order)
    except Exception:
        return {"ok": True}                   # swallows failure → event lost, no retry, no DLQ
```

## Common Mistakes

- Creating SDK clients, DB connections, or reading secrets inside the handler instead of
  at init, adding latency and exhausting connection limits under load.
- Assuming exactly-once delivery; not deduplicating, so retries corrupt data.
- No reserved concurrency, letting a spike scale Lambda past what the database can handle.
- Storing secrets as plaintext environment variables visible to anyone with `GetFunction`.
- A wildcard (`Action: "*"` or `Resource: "*"`) execution-role policy.
- No dead-letter queue on async invocations, so failed events vanish.
- Catching and swallowing errors to keep metrics green, hiding real failures.

## Production Tips

- Alarm on `Throttles`, `Errors`, and `Duration` p99 in [CloudWatch](14-cloudwatch.md);
  a rising throttle count means you need more concurrency or a slower producer.
- Use aliases and versions for safe deploys; shift traffic gradually (canary) and roll
  back by moving the alias.
- Right-size memory by testing 128 MB steps against real payloads — the cheapest run is
  often not the smallest memory.
- Keep functions single-purpose; a function that does one thing is easier to scale,
  secure, and reason about than a monolith behind one handler.

## AI Review Checklist

- Are clients, pools, and secrets initialized outside the handler and reused?
- Is the handler idempotent against at-least-once redelivery?
- Does the execution role grant only the specific actions and resources used?
- Are secrets read from Secrets Manager / Parameter Store, not plaintext env vars?
- Is there a DLQ or on-failure destination for async/stream sources?
- Are timeout, memory, and reserved concurrency set deliberately, not left default?
- Are errors thrown (not swallowed) so retries and alarms work?

## Related

- `knowledge/aws/13-api-gateway.md`
- `knowledge/aws/16-secrets-manager.md`
- `knowledge/aws/17-parameter-store.md`
- `knowledge/aws/14-cloudwatch.md`
- `knowledge/aws/02-iam.md`
