---
id: docker/24-monitoring
topic: docker
slug: monitoring
title: "Docker Monitoring"
type: doc
order: 24
status: ready
tags: [docker, monitoring]
related: [docker/16-logging, docker/15-healthchecks, docker/17-resource-limits, docker/22-production, docker/23-orchestration]
when_to_use: "Read before shipping a container to production or when you cannot see why a running container is unhealthy."
---
# Docker Monitoring

## Purpose

This document defines how to observe containers in production: what to collect
(metrics, health, events), how to collect it without coupling your app to a
specific backend, and how to turn signals into alerts. It is written so an agent
can instrument a container stack that is debuggable at 3 a.m., not just green on a
dashboard during business hours.

Monitoring answers "is this container healthy, and if not, why?". It builds on
[logging](16-logging.md) (what happened) and [healthchecks](15-healthchecks.md)
(is it alive) and feeds [resource limits](17-resource-limits.md) tuning.

## Why It Matters

A container is a black box: the process is isolated, the filesystem is ephemeral,
and when it dies the evidence usually dies with it. Without external observation
you learn about failures from users, not systems. Container workloads also fail in
ways bare processes do not — OOM kills, restart loops, throttled CPU, exhausted
file descriptors — and each of these is invisible unless you are watching the
runtime, not just the application. The cost of skipping this is measured in mean
time to recovery: an unmonitored outage is one you debug blind.

## Core Principles

- **Instrument the runtime and the app.** Container-level stats (CPU, memory,
  restarts) and app-level metrics (latency, error rate) answer different
  questions. You need both.
- **Push signals out of the container.** Storage inside a container is ephemeral;
  metrics and logs must leave the container before it dies to be useful.
- **Expose, do not embed.** Emit metrics on an endpoint or via the runtime; let a
  scraper collect them. Do not hard-wire your app to one monitoring vendor.
- **Alert on symptoms, not causes.** Page on user-visible SLO breaches (error
  rate, latency); use resource metrics for diagnosis, not paging.
- **Every alert must be actionable.** An alert nobody can act on is noise that
  trains people to ignore the real one.

## Best Practices

- Expose application metrics in Prometheus format on a dedicated port/path
  (`/metrics`), separate from your traffic port, so scraping cannot be reached by
  public users.
- Collect container runtime metrics with cAdvisor (or the orchestrator's built-in
  metrics) and node metrics with node-exporter. `docker stats` is for humans, not
  automation — it has no history and no alerting.
- Track the four golden signals — latency, traffic, errors, saturation — plus
  container-specific ones: restart count, OOM kills, and CPU throttling
  (`container_cpu_cfs_throttled_seconds_total`).
- Define a [healthcheck](15-healthchecks.md) so the orchestrator knows liveness;
  monitoring reports on it but does not replace it.
- Set alert thresholds against your [resource limits](17-resource-limits.md): alert
  when memory approaches the limit, because crossing it is an instant OOM kill.
- Keep the metrics endpoint cheap. A `/metrics` scrape that runs expensive queries
  becomes a self-inflicted load source at scrape frequency.
- Retain metrics long enough to see trends (weeks), not just incidents (minutes),
  so you can spot slow leaks and plan capacity.

## Examples

**Good Example** — app exposes metrics on an internal port; scraper collects them

```yaml
# compose.yaml — app emits Prometheus metrics; Prometheus scrapes them.
services:
  api:
    image: myorg/api:1.4.2
    ports:
      - "8080:8080"        # public traffic
    expose:
      - "9090"             # metrics: reachable only inside the compose network
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 3s
      retries: 3

  prometheus:
    image: prom/prometheus:v3.1.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro  # scrape config as code
    # Prometheus pulls from api:9090/metrics — the app stays vendor-neutral.
```

**Bad Example** — no runtime visibility, metrics trapped inside the container

```yaml
services:
  api:
    image: myorg/api:latest        # unpinned: can't correlate a metric with a build
    # no healthcheck: orchestrator can't tell "running" from "hung"
    # metrics written to /var/log/metrics.log inside the container —
    # ephemeral, unscraped, and gone the instant the container is replaced
    logging:
      driver: json-file            # default, unbounded → disk fills, no export
```

## Common Mistakes

- Relying on `docker stats` or `docker logs` as a monitoring strategy — no history,
  no alerts, no aggregation across replicas.
- Not distinguishing "container running" from "app healthy"; a hung process still
  shows as `Up`.
- Exposing `/metrics` on the public traffic port, leaking internal cardinality and
  timing data to anyone.
- High-cardinality labels (user id, request id) that explode Prometheus memory.
- Alerting on CPU/memory alone, which pages on normal load spikes instead of
  actual user impact.
- Assuming the orchestrator monitors for you — it restarts containers but does not
  tell you *why* they keep dying.

## Production Tips

- Wire OOM-kill and restart-count alerts first; they are the earliest signal of a
  misconfigured limit or a memory leak.
- Correlate metrics with image tags/digests via a label so a regression points to a
  specific build, not a vague time window.
- Ship metrics and traces through the OpenTelemetry Collector so switching backends
  is a config change, not an app rewrite.
- Test the alert path in staging: force an OOM, confirm the page fires and links to
  a runbook.

## AI Review Checklist

- Are both runtime metrics (CPU, memory, restarts, OOM) and app metrics collected?
- Is the `/metrics` endpoint on an internal port, not the public one?
- Do alerts page on user-visible symptoms and use resource metrics for diagnosis?
- Are metric labels bounded (no per-request cardinality)?
- Is a [healthcheck](15-healthchecks.md) defined so liveness is distinct from
  "process running"?
- Do metrics and logs leave the container before it is replaced?
- Is every alert tied to an action or runbook?

## Related

- `knowledge/docker/16-logging.md`
- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/22-production.md`
- `knowledge/docker/23-orchestration.md`
