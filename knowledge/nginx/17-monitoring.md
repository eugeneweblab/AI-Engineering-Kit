---
id: nginx/17-monitoring
topic: nginx
slug: monitoring
title: "Nginx Monitoring"
type: doc
order: 17
status: ready
tags: [nginx, monitoring, stub_status, request_time, worker_connections, tier, edge, observability]
related: [nginx/16-logging, nginx/14-rate-limiting, nginx/25-production, nginx/27-high-availability]
when_to_use: "Read before wiring nginx metrics, health checks, or alerts, or reviewing observability for the edge tier."
---
# Nginx Monitoring

## Purpose

This document defines how to observe a running nginx: exposing metrics, defining health
checks, and choosing what to alert on. It is written so an agent instruments the edge so
that failures are detected from signals, not from user complaints.

Monitoring answers "is the edge healthy, and if not, where does it hurt?" nginx sits on
the request path for everything, so its metrics — status codes, latency, upstream health,
connection counts — are the earliest and broadest signal that something is wrong.

## Why It Matters

The edge is where a problem first becomes visible and where its scope is widest: a slow
upstream, a saturated worker, or a spike in 5xx shows up in nginx before any single
service's own dashboard. Without metrics you learn about outages from users, minutes or
hours late. But instrumentation done carelessly is its own hazard: an unauthenticated
`stub_status` or metrics endpoint leaks internals to the internet, and alerting on the
wrong signal (raw request count instead of error rate) trains the team to ignore pages.
Good monitoring is specific, secured, and actionable — otherwise it is noise or a leak.

## Core Principles

- **Measure the golden signals.** Traffic, error rate, latency (percentiles, not
  averages), and saturation tell you what users experience — track these first.
- **Metrics over log-scraping for real time.** Export counters/gauges for dashboards and
  alerts; use logs for the detailed forensics behind an alert.
- **Health checks must be honest.** A check that only proves nginx is up, not that the
  upstream can serve, is worse than none — it hides the outage.
- **Secure every observability surface.** `stub_status`, Prometheus exporters, and status
  pages are internal-only: bind to localhost or require auth.
- **Alert on symptoms, page on impact.** Page on user-facing pain (error rate, latency
  SLO breach); leave capacity trends to dashboards, not the pager.

## Best Practices

- Expose `stub_status` (or the Prometheus exporter / NGINX Plus API) on an
  **internal-only** location for basic connection and request metrics.
- Derive rate/error/latency from the structured access log (see [logging](16-logging.md))
  via an exporter; alert on **p95/p99 `request_time`** and **5xx ratio**, not averages.
- Distinguish nginx 5xx from upstream 5xx (`$status` vs `$upstream_status`) so you know
  whether the edge or the app is failing.
- Provide a lightweight `/healthz` for the load balancer that reflects real readiness,
  and monitor upstream health separately.
- Track saturation: active connections, worker CPU, and `worker_connections` headroom —
  a full connection table drops traffic silently.
- Monitor certificate expiry and config-reload success as first-class metrics.
- Set alert thresholds against an SLO (e.g. "5xx > 1% for 5m"), not an arbitrary number.

## Examples

**Good Example** — secured metrics, honest health, symptom-based signals

```nginx
server {
    listen 127.0.0.1:8080;                       # metrics bound to localhost only
    location = /stub_status {
        stub_status;                             # active conns, requests, handled
        allow 127.0.0.1; deny all;               # scraper is local; nothing external
    }
}

server {
    listen 443 ssl;
    # Health check the LB can poll; cheap and does not touch a failing upstream needlessly.
    location = /healthz { access_log off; return 200 "ok\n"; }

    location / {
        proxy_pass http://app;
        # Record upstream status separately so a 502 from the app is not mistaken
        # for an nginx fault when alerting. (Consumed by the log-based exporter.)
        proxy_next_upstream error timeout http_502 http_503;
    }
}
# Alert (in your metrics system): 5xx ratio > 1% for 5m, or p99 request_time > 1s.
```

**Bad Example** — exposed metrics, dishonest health, useless alert

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    location = /status {
        stub_status;                             # reachable from the internet: leaks
        # No allow/deny → anyone can read connection and request internals.
    }

    # "Healthy" as long as nginx is up, even if EVERY upstream is down → hides outages.
    location = /healthz { return 200; }
}
# Alert configured on total request count dropping — fires on normal nightly troughs,
# so the team mutes it and misses the real 5xx spike.
```

## Common Mistakes

- Exposing `stub_status` or a metrics exporter to the internet, leaking internal state.
- A health check that returns 200 while every upstream is down, masking the outage.
- Alerting on averages, which hide the tail; users feel p99, not the mean.
- Not separating nginx 5xx from upstream 5xx, so alerts point at the wrong layer.
- Alerting on raw traffic volume, which pages on normal daily cycles and trains muting.
- Ignoring saturation (connection table, worker CPU) until nginx silently drops requests.
- No monitoring of cert expiry or reload success — both cause sudden, total outages.

## Production Tips

- Build one dashboard around the golden signals per service, with the nginx edge view
  on top so you triage "edge vs. app" in seconds.
- Tie alert thresholds to a written SLO and review them after every incident; an alert
  that never fires or always fires is broken.
- Scrape metrics on a short interval but keep long retention for capacity planning.
- Test the alert path itself (synthetic 5xx, expired-cert canary) so you know it pages.

## AI Review Checklist

- Are `stub_status`/exporter endpoints bound to localhost or auth-protected (never public)?
- Does the health check reflect real upstream readiness, not just that nginx is running?
- Are alerts based on error rate and p95/p99 latency against an SLO, not averages or raw counts?
- Is nginx 5xx distinguished from upstream 5xx in metrics?
- Are saturation signals (connections, worker CPU, connection headroom) tracked?
- Are certificate expiry and reload success monitored?
- Do metrics come from exported counters/gauges, with logs reserved for forensics?

## Related

- `knowledge/nginx/16-logging.md`
- `knowledge/nginx/14-rate-limiting.md`
- `knowledge/nginx/25-production.md`
- `knowledge/nginx/27-high-availability.md`
