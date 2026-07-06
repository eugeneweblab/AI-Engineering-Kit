# Observability

## Purpose

This document defines the engineering standards for implementing observability in NestJS applications.

The objective is to make every production system measurable, traceable, and debuggable by collecting meaningful telemetry.

Observability answers one question:

> What is happening inside the system?

Every production service should provide enough information to diagnose problems without reproducing them locally.

---

# Core Principle

If a system cannot be observed, it cannot be reliably operated.

Observability is a production requirement.

Not a debugging tool.

---

# Goals

Every application should provide:

- structured logging;
- distributed tracing;
- metrics;
- health monitoring;
- alerting;
- auditability.

These capabilities should work together.

---

# Three Pillars

Observability consists of three complementary pillars.

## Logs

Describe discrete events.

Examples:

- HTTP request;
- authentication;
- exception;
- deployment;
- background job.

---

## Metrics

Measure numerical values over time.

Examples:

- request rate;
- latency;
- memory usage;
- CPU utilization;
- queue depth.

---

## Traces

Show how requests travel across the system.

Example:

```
Client

↓

API Gateway

↓

Orders Service

↓

Payment Service

↓

Database

↓

Response
```

Tracing identifies bottlenecks across distributed systems.

---

# Structured Logging

Logs should always be structured.

Include:

- timestamp;
- log level;
- service name;
- correlation ID;
- request ID;
- user ID (when available);
- message.

Avoid free-form logging.

---

# Log Levels

Use consistent levels.

```
TRACE

DEBUG

INFO

WARN

ERROR

FATAL
```

Choose the lowest level that accurately represents the event.

---

# Correlation IDs

Every request should receive a correlation ID.

Propagate it through:

- HTTP;
- queues;
- events;
- background jobs;
- scheduled tasks.

A single business operation should be traceable end-to-end.

---

# Distributed Tracing

Trace every significant operation.

Typical spans:

- HTTP request;
- SQL query;
- cache lookup;
- external API;
- queue publish;
- queue processing.

Every span should have meaningful names.

---

# Metrics

Collect metrics for:

- request count;
- error rate;
- response time;
- throughput;
- queue size;
- retry count;
- cache hit ratio.

Measure trends rather than isolated values.

---

# Health Checks

Health endpoints should report:

- application status;
- database connectivity;
- cache availability;
- queue availability;
- external dependencies.

Separate:

- liveness;
- readiness.

---

# Audit Logs

Audit logs record security-sensitive actions.

Examples:

- login;
- permission changes;
- financial operations;
- user deletion;
- administrative actions.

Audit logs should be immutable.

---

# Error Tracking

Capture:

- exceptions;
- stack traces;
- request metadata;
- affected user;
- release version.

Every production exception should be traceable.

---

# OpenTelemetry

Prefer OpenTelemetry as the standard telemetry framework.

Benefits:

- vendor-neutral;
- standardized instrumentation;
- broad ecosystem support.

Application code should remain independent of monitoring vendors.

---

# Dashboards

Dashboards should expose:

- service health;
- latency;
- error rate;
- infrastructure usage;
- queue status;
- deployment history.

Dashboards should support rapid diagnosis.

---

# Alerting

Alert on:

- elevated error rates;
- service unavailability;
- failed background jobs;
- excessive latency;
- resource exhaustion.

Avoid alert fatigue.

Alerts should be actionable.

---

# Performance

Observability introduces overhead.

Review:

- log volume;
- metric cardinality;
- trace sampling;
- storage costs.

Collect useful telemetry.

Avoid unnecessary telemetry.

---

# Security

Never log:

- passwords;
- JWT tokens;
- API keys;
- encryption keys;
- payment information.

Review log content regularly.

---

# Privacy

Protect personal information.

Follow applicable privacy regulations.

Log only what is operationally necessary.

---

# Testing

Verify:

- logs generated;
- traces propagated;
- metrics collected;
- health endpoints;
- alert rules.

Observability should be continuously validated.

---

# AI Decision Matrix

Always observe:

✓ HTTP requests

✓ Background jobs

✓ External API calls

✓ Database queries

✓ Cache operations

✓ Security events

Do **not** log:

✗ Passwords

✗ Tokens

✗ Secrets

✗ Sensitive personal data

---

# AI Execution Checklist

## Investigation

☐ Identify critical workflows.

☐ Review telemetry requirements.

☐ Review compliance requirements.

☐ Review operational needs.

---

## Planning

☐ Add structured logging.

☐ Add metrics.

☐ Add tracing.

☐ Configure health checks.

---

## Verification

☐ Correlation IDs propagated.

☐ Logs structured.

☐ Metrics collected.

☐ Traces complete.

☐ Sensitive data excluded.

☐ Dashboards available.

---

# Common Mistakes

Avoid:

Logging secrets.

Using inconsistent log formats.

Ignoring distributed tracing.

Missing correlation IDs.

Creating excessive metric cardinality.

Logging every debug event in production.

Treating observability as optional.

---

# Completion Criteria

Observability is complete when:

- structured logs are available;
- metrics cover critical services;
- distributed tracing is implemented;
- health checks reflect application readiness;
- alerts detect operational failures;
- production incidents can be investigated without code changes.

---

# Summary

Observability provides visibility into the runtime behavior of an application.

By combining structured logging, metrics, distributed tracing, health monitoring, and actionable alerts, engineering teams can operate production systems with confidence, detect failures early, and diagnose incidents efficiently.