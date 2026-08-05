---
id: linux/25-production
topic: linux
slug: production
title: "Linux Production"
type: doc
order: 25
status: ready
tags: [linux, production, MemoryMax, RestartSec, LimitNOFILE, ProtectSystem, NoNewPrivileges]
related: [linux/08-systemd, linux/16-monitoring, linux/15-logging, linux/17-security, linux/98-production-checklist]
when_to_use: "Read before promoting a Linux host or service to production, or reviewing a deployment for operational readiness."
---
# Linux Production

## Purpose

This document defines what makes a Linux host or service *production-grade*:
supervised by an init system, resource-bounded, observable, secured, and
recoverable. It is the bridge between "it runs on my machine" and "it survives
a reboot, a traffic spike, and a 3 a.m. failure without a human."

Production is not a single technique — it is the sum of the operational
disciplines covered across this topic: [systemd](08-systemd.md),
[monitoring](16-monitoring.md), [logging](15-logging.md),
[security](17-security.md), and [backups](20-backups.md). This doc ties them
into a readiness bar.

## Why It Matters

Code that works in development has been tested against exactly one condition:
the happy path, once, with you watching. Production is the opposite — it runs
unattended, under load, through reboots and kernel upgrades, while being
probed by the internet. A process started with `nohup ./app &` has no restart,
no log rotation, no memory limit, and no health check; the first OOM event or
reboot ends it silently. The gap between "starts" and "stays up" is where
outages live. Closing it deliberately, before launch, is far cheaper than
debugging it during an incident.

## Core Principles

- **Nothing runs bare.** Every long-lived process is supervised by an init
  system (systemd) that restarts it, bounds its resources, and captures its logs.
- **Fail into a known state.** Services restart with backoff, health checks gate
  traffic, and a bad deploy rolls back — no manual `ssh` and pray.
- **Bound every resource.** Memory, file descriptors, and disk are capped so one
  runaway process cannot take down the host.
- **If it is not observed, it is not in production.** Logs, metrics, and alerts
  exist *before* launch, not after the first outage.
- **Least privilege by default.** Services run as a dedicated non-root user with
  the narrowest filesystem and capability grants that still work.

## Best Practices

- Run services as systemd units with `Restart=on-failure`, `RestartSec`, and a
  dedicated `User=`. Never `nohup`, `screen`, or a bare `&` for production processes.
- Set resource limits: `MemoryMax=`, `LimitNOFILE=`, `TasksMax=` in the unit, plus
  cgroup accounting. An unbounded process is a latent host-wide outage.
- Add a real health check (`ExecStartPost`/readiness probe) and wire it to your
  load balancer so traffic only reaches healthy instances.
- Rotate and ship logs via the journal or a shipper; never let a service write an
  unbounded file that fills the disk — see [logging](15-logging.md).
- Harden the unit: `NoNewPrivileges=yes`, `ProtectSystem=strict`,
  `ProtectHome=yes`, `PrivateTmp=yes`. These cost nothing and shrink the blast radius.
- Deploy immutably where possible: build an artifact once, promote the same
  artifact through environments, and keep config in the environment, not the image.
- Rehearse recovery: reboot the host, kill the process, and fill the disk in
  staging. If the service does not come back on its own, it is not production-ready.

## Examples

**Good Example** — supervised, bounded, hardened systemd unit

```ini
# /etc/systemd/system/api.service
[Unit]
Description=API service
After=network-online.target
Wants=network-online.target

[Service]
User=api                     # dedicated non-root user, least privilege
ExecStart=/opt/api/bin/api
Restart=on-failure           # auto-recover from crashes
RestartSec=2                 # backoff so a crash loop does not spin the CPU
MemoryMax=512M               # OOM this service, not the whole host
LimitNOFILE=65536            # explicit fd cap sized for real connections
NoNewPrivileges=yes          # cannot escalate via setuid binaries
ProtectSystem=strict         # filesystem is read-only except declared paths
PrivateTmp=yes               # isolated /tmp, no cross-service leakage

[Install]
WantedBy=multi-user.target
```

**Bad Example** — unsupervised, unbounded, unobservable

```bash
# deploy.sh on the production host
cd /opt/api
nohup ./api > /var/log/api.log 2>&1 &   # no restart on crash or reboot
# no memory limit: one leak OOM-kills random processes host-wide
# log grows forever until the disk fills and everything stops
# runs as root: a bug is now a host compromise
echo $! > /var/run/api.pid               # PID file goes stale on crash
```

## Common Mistakes

- Launching services with `nohup &`, `screen`, or `tmux` instead of an init system,
  so nothing restarts them after a crash or reboot.
- No resource limits, letting a single memory leak OOM-kill unrelated processes.
- Logging to an unrotated file that eventually fills the disk and halts the host.
- Running as `root` because it "just works," turning any bug into a full compromise.
- Shipping to production without health checks, so the load balancer sends traffic
  to a broken instance.
- Never rehearsing reboot or failure, discovering only during an incident that the
  service does not come back on its own.

## Production Tips

- Enable `systemd-oomd` or a `MemoryMax` on every unit so the kernel OOM killer is
  a last resort, not the first line of defense.
- Keep a runbook per service: how to restart, where the logs are, what the alerts
  mean. The person on call at 3 a.m. is not the person who wrote it.
- Track the four golden signals — latency, traffic, errors, saturation — per
  [monitoring](16-monitoring.md), and alert on symptoms users feel, not raw CPU.

## AI Review Checklist

- Is every long-lived process supervised by systemd with `Restart=` set?
- Does each service run as a dedicated non-root `User=`?
- Are `MemoryMax`, `LimitNOFILE`, and `TasksMax` set to bound resources?
- Are unit hardening options (`NoNewPrivileges`, `ProtectSystem`) enabled?
- Is there a health check gating traffic, and are logs rotated?
- Has reboot and failure recovery been rehearsed in staging?
- Do monitoring and alerts exist before launch, not after the first outage?

## Related

- `knowledge/linux/08-systemd.md`
- `knowledge/linux/16-monitoring.md`
- `knowledge/linux/15-logging.md`
- `knowledge/linux/17-security.md`
- `knowledge/linux/98-production-checklist.md`
