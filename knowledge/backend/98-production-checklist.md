---
id: backend/98-production-checklist
topic: backend
slug: production-checklist
title: "Backend Production Checklist"
type: doc
order: 98
status: ready
tags: [backend, production-checklist]
related: [backend/27-production, backend/26-deployment, backend/22-observability, backend/21-security, backend/17-transactions]
when_to_use: "Read before shipping a backend service, endpoint, or job to production."
---
# Backend Production Checklist

## Purpose

This is the go/no-go checklist for putting backend code in front of real traffic. Every
item is a verifiable yes/no an agent can confirm by reading the code, config, or a
dashboard — not an aspiration. If an item cannot be answered "yes" or explicitly waived
with a reason, the change is not production-ready.

## Why It Matters

Production is where mistakes cost money, data, and trust, and where the feedback loop is
slow and public. The failures that cause outages are rarely novel — they are the same
missing timeout, unbounded query, or absent rollback plan every time. A checklist turns
that hard-won incident knowledge into a repeatable gate so the same outage is not
rediscovered service by service.

## Correctness and Data Safety

- [ ] All writes that a client or queue may retry are idempotent (unique key or upsert).
- [ ] Multi-step writes that must all-or-nothing run inside a single transaction.
- [ ] Database migrations are backward-compatible and safe to run before the new code
      deploys (expand/contract, no destructive change in the same release).
- [ ] There is a tested rollback or forward-fix path for both code and schema.
- [ ] No unbounded queries: every list endpoint and query is paginated or limited.
- [ ] Numeric money/quantity fields use integers or decimals, never floats.

## Reliability

- [ ] Every outbound network/DB call has an explicit timeout.
- [ ] Retries use exponential backoff with jitter and a maximum attempt cap.
- [ ] External dependencies are wrapped so one slow dependency cannot exhaust the pool
      (circuit breaker or bulkhead where a dependency is critical).
- [ ] Graceful shutdown drains in-flight requests and stops consuming new work on SIGTERM.
- [ ] Health (`/livez`) and readiness (`/readyz`) probes are distinct and accurate.
- [ ] Connection pools (DB, HTTP, queue) have sane max sizes and are not created per-request.

## Security

- [ ] All input is validated and authorization is enforced on every endpoint, not just the UI.
- [ ] Secrets come from a secrets manager or env, never from source or logs.
- [ ] TLS is enforced; internal service-to-service traffic is authenticated.
- [ ] Rate limiting protects login, write, and expensive endpoints. See [security](21-security.md).
- [ ] Dependencies are scanned for known CVEs and pinned to exact versions.

## Observability

- [ ] Structured logs carry a request/correlation id and never log secrets or PII.
- [ ] The four golden signals (latency, traffic, errors, saturation) are on a dashboard.
- [ ] Alerts fire on symptoms users feel (error rate, p99 latency), not just CPU.
- [ ] Traces span service boundaries so a slow request can be attributed. See [observability](22-observability.md).
- [ ] Every error branch increments a metric or logs at `error`/`warn` with context.

## Performance and Scale

- [ ] Load tested at expected peak plus headroom; p99 latency meets its SLO.
- [ ] No N+1 queries on hot paths; heavy reads are indexed or cached with a TTL.
- [ ] The service is horizontally scalable (stateless, or state externalized).
- [ ] Resource limits (CPU, memory) are set so one instance cannot starve the node.

## Operations

- [ ] Deployment is automated and repeatable (CI/CD), with a canary or rolling strategy.
- [ ] Configuration is environment-specific and injected, not baked into the image.
- [ ] Background jobs and cron have monitoring, retries, and a dead-letter path.
- [ ] A runbook documents the top failure modes and their first-response steps.
- [ ] On-call ownership and escalation for this service are defined.

## AI Review Checklist

- Does every network and DB call have a timeout and a bounded retry policy?
- Is every retryable write idempotent, and every multi-step write transactional?
- Are migrations backward-compatible with a rollback path?
- Are the four golden signals dashboarded and alerted on user-facing symptoms?
- Are secrets, authz, rate limiting, and input validation all enforced server-side?
- Is the service stateless and horizontally scalable with resource limits set?

## Related

- `knowledge/backend/27-production.md`
- `knowledge/backend/26-deployment.md`
- `knowledge/backend/22-observability.md`
- `knowledge/backend/21-security.md`
- `knowledge/backend/17-transactions.md`
