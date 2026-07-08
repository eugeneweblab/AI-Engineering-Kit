---
id: architecture/12-integration-patterns
topic: architecture
slug: integration-patterns
title: "Integration Patterns"
type: doc
order: 12
status: ready
tags: [architecture, integration-patterns]
related: [architecture/08-event-driven-architecture, architecture/11-api-first, architecture/20-message-brokers, architecture/17-fault-tolerance, architecture/09-microservices]
when_to_use: "Read before connecting two services, calling a third-party API, or choosing between synchronous calls and messaging."
---
# Integration Patterns

## Purpose

This document defines how two independently deployed components talk to each
other: request/response calls, asynchronous messaging, shared data, and the
adapters that keep one system's model from leaking into another. It is written so
an agent can choose an integration style and implement it without creating hidden
coupling or silent data loss.

Integration is where distributed systems actually fail. The code inside one
service can be perfect and the system still breaks at the seams between services.
Pick the coupling you want *on purpose* rather than inheriting it by accident.

## Why It Matters

Every integration point is a place where the network can be slow, partition, or
lie. A synchronous call chain means one slow dependency stalls everything upstream;
an unvalidated payload means a partner's bug becomes your outage. Integrations also
outlive the code around them — a message contract or webhook shape is a public
promise that other teams build on, so a careless change breaks consumers you cannot
see. Getting the pattern right is cheaper than migrating a bad one later, because a
bad integration spreads coupling through every caller before you notice.

## Core Principles

- **Choose sync or async deliberately.** Synchronous (HTTP/gRPC) when the caller
  needs the result *now* to continue; asynchronous (events/queues) when the caller
  only needs the work to *eventually* happen. Defaulting everything to sync creates
  fragile call chains.
- **Integrate through contracts, not internals.** Never share a database table or
  reach into another service's schema. Expose an explicit API or event; the internal
  model stays private and free to change.
- **Assume the other side will fail.** Every remote call needs a timeout, a retry
  policy, and a defined behavior when it exhausts them. No unbounded waits.
- **Make retries safe.** Any operation that can be retried must be idempotent, keyed
  by a caller-supplied idempotency key, so a duplicate delivery does not double-charge.
- **Translate at the boundary.** Put an adapter (anti-corruption layer) between your
  domain and an external model so their concepts never bleed into your core.

## Best Practices

- Set an explicit connect and read timeout on every outbound call. A missing timeout
  defaults to "wait forever," which is how one dependency takes down the whole system.
- Wrap remote dependencies in a **circuit breaker** so repeated failures fail fast
  instead of piling up threads (see [fault-tolerance](17-fault-tolerance.md)).
- For async, prefer **publish/subscribe with a broker** over point-to-point calls so
  producers and consumers scale and deploy independently (see [message-brokers](20-message-brokers.md)).
- Guarantee at-least-once delivery and design consumers to be idempotent; exactly-once
  across a network is a myth you should not build on.
- Use the **transactional outbox** pattern to publish events atomically with the DB
  write — never write to the DB and the broker in two separate steps that can half-fail.
- Version your contracts and evolve them additively (add optional fields; never
  repurpose or remove one) so old consumers keep working (see [api-first](11-api-first.md)).
- Validate every inbound payload at the edge against a schema; treat partner data as
  hostile until proven well-formed.

## Examples

**Good Example** — bounded, idempotent, translated at the boundary

```python
# Synchronous call with an explicit timeout, retry budget, and idempotency key.
# WHY: the timeout bounds the blast radius of a slow partner; the key makes a
# retried request safe to process twice.
def charge(order_id: str, amount_cents: int) -> Payment:
    resp = payments_client.post(
        "/charges",
        json={"amount": amount_cents},
        headers={"Idempotency-Key": order_id},  # dedupes on the provider side
        timeout=Timeout(connect=2.0, read=5.0),  # never wait forever
        retries=Retry(total=3, backoff=0.5, retry_on=[502, 503, 504]),
    )
    # Adapter: map the provider's model into OUR domain type, so their field
    # names and enums never leak past this function.
    return to_domain_payment(resp.json())
```

**Bad Example** — unbounded, non-idempotent, coupled to their schema

```python
def charge(order_id, amount_cents):
    # No timeout: one slow response stalls this worker indefinitely.
    resp = requests.post("https://pay.example/charges",
                         json={"amount": amount_cents})
    # No idempotency key: a client retry double-charges the customer.
    # Returns the provider's raw dict, so their JSON shape spreads through
    # every caller — a rename on their side becomes a bug on ours.
    return resp.json()
```

## Common Mistakes

- No timeout on outbound calls, so one slow dependency exhausts the caller's threads.
- Building long synchronous chains (A calls B calls C calls D) where any hop failing
  fails the whole request and latency compounds.
- Sharing a database between services instead of integrating through an API — the
  worst coupling, because a schema change silently breaks a service you forgot about.
- Retrying non-idempotent operations, causing duplicate orders, charges, or emails.
- Writing to the database and publishing an event as two steps, so a crash between
  them leaves the system inconsistent (fix: transactional outbox).
- Passing an external partner's data model straight into your domain with no adapter.
- Assuming "exactly-once" delivery and skipping consumer-side deduplication.

## Production Tips

- Emit metrics per integration: success rate, p99 latency, timeout count, retry count,
  and circuit-breaker state. These are your early warning of a failing partner.
- Keep a dead-letter queue for messages a consumer cannot process, with alerting —
  never drop or infinitely re-queue a poison message.
- Record correlation/trace IDs across every hop so a request can be followed end to end
  (see [observability](18-observability.md)).
- Contract-test integrations in CI (consumer-driven contracts) so a producer change
  that breaks a consumer fails the build, not production.

## AI Review Checklist

- Does every outbound remote call have an explicit timeout and a bounded retry policy?
- Are retryable operations idempotent (idempotency key or natural dedupe)?
- Is the integration async where the caller does not need the result synchronously?
- Do services integrate through explicit contracts, never a shared database?
- Is external data translated by an adapter before entering the domain?
- Are events published atomically with the state change (outbox), not in two steps?
- Is there a dead-letter path for messages that cannot be processed?

## Related

- `knowledge/architecture/08-event-driven-architecture.md`
- `knowledge/architecture/11-api-first.md`
- `knowledge/architecture/20-message-brokers.md`
- `knowledge/architecture/17-fault-tolerance.md`
- `knowledge/architecture/09-microservices.md`
