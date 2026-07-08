---
id: linux/07-services
topic: linux
slug: services
title: "Services"
type: doc
order: 7
status: ready
tags: [linux, services]
related: [linux/06-processes, linux/08-systemd, linux/15-logging, linux/16-monitoring, linux/25-production]
when_to_use: "Read before turning a program into a long-running, self-restarting Linux service."
---
# Services

## Purpose

This document defines what it means to run a program *as a service* on Linux: a
long-lived process that starts on boot, restarts on failure, logs somewhere durable,
and shuts down cleanly. It is written so an agent can decide how a workload should be
supervised and can configure that supervision correctly.

A "service" is a policy layer on top of a [process](06-processes.md): the process is the
thing that runs; the service is the promise that it *keeps* running. On modern Linux that
policy is almost always enforced by [systemd](08-systemd.md); this document is the
concepts, and the systemd doc is the mechanics.

## Why It Matters

The difference between "I ran the binary" and "the binary is a service" is the difference
between a demo and production. Without a supervisor, a crash at 3 a.m. is an outage until a
human notices; with one, it is a restart nobody sees. But supervision done wrong is worse
than none: a tight restart loop on a mis-configured service masks the real error, burns CPU,
and fills logs, while a service that starts before its database is reachable fails on every
boot. Choosing the right restart policy, dependency order, and health signal is what makes a
service actually reliable rather than merely "started".

## Core Principles

- **A service is defined by its restart policy, not just its command.** Decide up front:
  restart always, only on failure, or never — and with what backoff. No backoff means a
  crash loop.
- **Run in the foreground; let the supervisor own the lifecycle.** A service that
  daemonizes itself hides its PID and its crashes from the supervisor. Stay attached.
- **Log to stdout/stderr, not to a self-managed file.** The supervisor captures and rotates
  it. Self-rotated logs drift, fill disks, and get lost.
- **Declare dependencies; do not sleep-and-hope.** "Start after the network is up" is a
  dependency to express, not a `sleep 30` to guess.
- **Run with the least privilege that works.** A service rarely needs root; a dedicated
  unprivileged user limits the blast radius of a compromise.

## Best Practices

- Set a restart policy with backoff and a failure ceiling, so a genuinely broken service
  stops flapping and surfaces the error instead of hiding it in a loop.
- Run as a dedicated non-root user with only the files and ports it needs. The trade-off is
  a little setup for a large reduction in compromise impact.
- Emit logs to stdout/stderr in a structured, timestamped format and let the platform
  handle rotation and retention.
- Expose a health signal (a readiness endpoint, or systemd `Type=notify`) so the supervisor
  restarts on *hangs*, not just on exits.
- Make start and stop idempotent and bounded: starting twice is a no-op; stopping always
  finishes within a known timeout.
- Externalize configuration (environment or a config file), never bake secrets or hostnames
  into the unit. It lets the same artifact run in every environment.

## Examples

**Good Example** — a supervised, unprivileged, foreground service (systemd unit)

```ini
[Unit]
Description=Orders API
After=network-online.target postgresql.service   # declared dependency, not a sleep
Wants=network-online.target

[Service]
User=orders                    # dedicated non-root user, least privilege
ExecStart=/usr/local/bin/orders-api   # runs in foreground; systemd owns the PID
Restart=on-failure             # restart on crash, not on clean exit
RestartSec=2                   # backoff so a crash loop cannot spin the CPU
StartLimitBurst=5              # give up after 5 fast failures -> error surfaces
# stdout/stderr go to the journal automatically; no self-managed log file

[Install]
WantedBy=multi-user.target
```

**Bad Example** — self-daemonizing, root, crash-looping

```ini
[Service]
User=root                      # runs everything as root: full-host blast radius
ExecStart=/usr/local/bin/orders-api --daemonize --pidfile /run/o.pid
                               # forks into background -> systemd loses the real PID
                               # and thinks the service "started" the instant fork returns
Restart=always                 # restarts even on config errors...
# ...with no RestartSec and no StartLimit -> a broken build spins in a tight loop,
# pegging CPU and burying the actual error in a flood of restarts
StandardOutput=append:/var/log/orders.log   # self-managed file, never rotated -> fills disk
```

## Common Mistakes

- No restart backoff, so a startup error becomes a CPU-pegging crash loop.
- `Restart=always` on a service that has valid clean-exit paths, masking real failures.
- Letting the service daemonize itself, hiding its PID and crashes from the supervisor.
- Running as root out of convenience when a dedicated user would do.
- Guessing readiness with `sleep` instead of declaring a dependency or a health check.
- Writing and rotating its own log file, which eventually fills the disk.

## Production Tips

- Distinguish *started* from *ready*: a service can be up but not serving. Wire a real
  readiness signal so dependents wait for readiness, not for the process to exist.
- Alert on restart count, not just "is it running" — a service restarting every minute is
  technically "up" and actually broken.
- Keep the unit/artifact identical across environments; vary only injected configuration.

## AI Review Checklist

- Is there an explicit restart policy with backoff and a failure ceiling?
- Does the service run in the foreground under the supervisor, not self-daemonize?
- Does it run as a dedicated non-root user with least privilege?
- Do logs go to stdout/stderr for the platform to capture and rotate?
- Are dependencies declared rather than approximated with `sleep`?
- Is there a readiness/health signal so hangs (not just exits) trigger a restart?

## Related

- `knowledge/linux/06-processes.md`
- `knowledge/linux/08-systemd.md`
- `knowledge/linux/15-logging.md`
- `knowledge/linux/16-monitoring.md`
- `knowledge/linux/25-production.md`
