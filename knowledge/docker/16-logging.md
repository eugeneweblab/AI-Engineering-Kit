---
id: docker/16-logging
topic: docker
slug: logging
title: "Docker Logging"
type: doc
order: 16
status: ready
tags: [docker, logging, toISOString, Date, Authorization, containerized, logs, ships]
related: [docker/15-healthchecks, docker/24-monitoring, docker/17-resource-limits, docker/22-production, docker/14-secrets]
when_to_use: "Read before deciding where a containerized app writes logs or how a host retains and ships them."
---
# Docker Logging

## Purpose

This document defines how a containerized application should emit logs and how the
host should collect, rotate, and ship them. It is written so an agent can set up
logging that is discoverable with standard tooling, survives restarts, does not fill
the disk, and does not leak secrets.

Containers are ephemeral; their filesystems vanish on removal. Logging is how the
system's behavior outlives the container that produced it. Getting it right is the
difference between a debuggable production incident and a black box.

## Why It Matters

When something breaks at 3 a.m., logs are often the only evidence of what happened.
If the app logged to a file inside the container, that evidence died with the
container. If the daemon's default `json-file` driver ran without rotation, the log
quietly grew until it filled the host disk and took down *every* container on the
box — a common and self-inflicted outage. And if the app logged a request body
containing a password, that secret is now replicated across every log aggregator and
backup. Logging decisions made casually have host-wide and security-wide consequences.

## Core Principles

- **Log to stdout/stderr, not to files.** The container writes to standard streams;
  the platform decides where they go. This is the twelve-factor contract and lets
  `docker logs`, drivers, and aggregators all work uniformly.
- **One event per line, structured.** Emit single-line JSON so logs are machine-
  parseable and a stack trace does not fragment into dozens of "events".
- **Rotation is not optional.** Unbounded logs fill the disk and crash the host.
  Every driver that stores locally must cap size and file count.
- **Never log secrets or full PII.** Credentials, tokens, and sensitive personal data
  must be redacted before they reach a stream that is stored and copied everywhere.
- **Logs are ephemeral by default.** To retain them, ship them off the host; do not
  rely on the container's local log surviving.

## Best Practices

- Write application logs to stdout (normal) and stderr (errors); let Docker capture
  them. Do not have the app manage log files or rotation itself.
- Emit structured JSON with a level, timestamp, and message so downstream tooling can
  filter and index without fragile regex parsing.
- Configure the `json-file` driver with `max-size` and `max-file` (globally in
  `/etc/docker/daemon.json`, or per-service in compose) so logs rotate and cannot
  exhaust the disk.
- For centralized logging, use a shipping driver or a sidecar/agent (Fluent Bit,
  Vector) rather than the app writing directly to a remote sink — keep the app simple.
- Be aware the `json-file` and `local` drivers support `docker logs`; some remote
  drivers do not, which hampers quick local debugging.
- Redact secrets and sensitive fields at the logging boundary; never log full request
  bodies, `Authorization` headers, or credentials.
- Include correlation IDs (request/trace IDs) so a single request can be followed
  across services.

## Examples

**Good Example** — structured logs to stdout, rotation capped on the driver

```yaml
# compose.yaml — app logs to stdout; driver caps size so disk cannot fill
services:
  app:
    image: myorg/app:1.4.2
    logging:
      driver: json-file
      options:
        max-size: "10m"   # rotate each file at 10 MB
        max-file: "3"      # keep 3 files → hard cap of ~30 MB per container
```

```ts
// App writes one structured line per event to stdout — no local log file
logger.info({
  level: "info",
  ts: new Date().toISOString(),
  msg: "payment.captured",
  requestId: ctx.requestId,        // correlation id to trace across services
  amount: order.total,
  // note: no card number, no auth token — sensitive fields are omitted
});
```

**Bad Example** — file logging, no rotation, secret leaked

```ts
// Logs to a file INSIDE the container → lost when the container is removed,
// invisible to `docker logs`, and never shipped anywhere.
fs.appendFileSync("/var/log/app.log", line);

// Default json-file driver with NO max-size → grows until the host disk is full,
// taking down every container on the box.

logger.info(`login for ${email} with password ${password}`); // secret in every sink
```

## Common Mistakes

- Logging to files inside the container, so logs die with the container and are
  invisible to `docker logs` and aggregators.
- Leaving the default `json-file` driver uncapped, letting logs fill the disk and
  crash the host.
- Emitting unstructured multi-line text, so a stack trace becomes many mangled
  "events" that are hard to search.
- Logging secrets, tokens, or full request bodies, replicating sensitive data across
  every downstream store.
- Assuming logs are durable — without shipping, they are cleared on container removal.
- Having the app push logs directly to a remote service, coupling app code to the
  logging backend.

## Production Tips

- Set `max-size`/`max-file` defaults globally in `/etc/docker/daemon.json` so every
  new container is capped by default, not just the ones someone remembered to tune.
- Ship logs to a central store (Loki, Elasticsearch, CloudWatch) with an agent so
  they survive host loss and are searchable across the fleet.
- Give each request a trace ID at the edge and propagate it so cross-service logs
  join up (pairs with [monitoring](24-monitoring.md)).
- Add a redaction filter in the log pipeline as a backstop, so a stray secret is
  scrubbed even if application code forgets.

## AI Review Checklist

- Does the app log to stdout/stderr rather than to files inside the container?
- Are logs single-line structured (JSON) with level, timestamp, and correlation id?
- Is the log driver configured with `max-size` and `max-file` to enforce rotation?
- Are secrets, tokens, and full request bodies kept out of the logs?
- Are logs shipped off-host if they need to be retained beyond the container's life?
- Is the app decoupled from the logging backend (driver/agent, not direct writes)?

## Related

- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/24-monitoring.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/22-production.md`
- `knowledge/docker/14-secrets.md`
