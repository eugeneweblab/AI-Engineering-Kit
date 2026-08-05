---
id: linux/15-logging
topic: linux
slug: logging
title: "Linux Logging"
type: doc
order: 15
status: ready
tags: [linux, logging, logrotate, DATABASE_URL, vector, systemd-timesyncd, systemd, level]
related: [linux/16-monitoring, linux/08-systemd, linux/19-debugging, linux/25-production]
when_to_use: "Read before adding logging to a service, configuring journald/syslog, or setting up log rotation and shipping."
---
# Linux Logging

## Purpose

This document defines how to produce, store, and rotate logs on Linux — application
output, `journald`, `syslog`, and log rotation. It is written so an agent can make a
service observable without filling a disk, leaking secrets, or losing the one line that
explains an outage.

## Why It Matters

Logs are the primary record of what a system actually did, and the first thing you reach
for during an incident. But logging done wrong causes its own outages: unrotated logs
fill the disk and take the service down with them; secrets written to logs turn a log
store into a credential dump; unstructured output makes the critical line unsearchable at
3am. Because logs are written on the hot path, bad logging also costs latency. Good
logging is deliberate about *what*, *where*, and *how much*.

## Core Principles

- **Log to stdout/stderr; let the platform handle transport.** A service under `systemd`
  or in a container should write to stdout and let `journald`/the runtime collect it.
  Do not have the app manage its own files and rotation.
- **Structure logs for machines, format for humans only at the edge.** JSON lines with
  stable field names are searchable and aggregatable; ad-hoc prose is not.
- **Never log secrets or full PII.** Credentials, tokens, card numbers, and session IDs
  must be redacted at the logging boundary, because logs are copied, shipped, and kept.
- **Every log has a level, and levels mean something.** `ERROR` is actionable, `WARN` is
  suspicious, `INFO` is milestones, `DEBUG` is off in production. Do not log everything at
  `INFO`.
- **Logs must rotate.** Unbounded logs are a disk-exhaustion outage waiting to happen.

## Best Practices

- Emit one event per line as JSON with consistent keys (`ts`, `level`, `msg`, `request_id`,
  `service`). One structured line beats ten `printf`s.
- Include a correlation/request ID so a single request can be traced across log lines and
  services.
- Configure rotation with `logrotate` (or rely on `journald`'s `SystemMaxUse=`): cap by
  size and age, compress old files, and keep a bounded number.
- Set `journald` limits (`SystemMaxUse`, `MaxRetentionSec`) so the journal cannot grow
  without bound; make the journal persistent (`Storage=persistent`) if you need history
  across reboots.
- Redact secrets before they reach the log call — a filter at the sink is too late if the
  string was already built and buffered.
- Log to stderr for errors and stdout for normal output, so severity is separable by the
  collector.
- Ship logs off the host (`journald` → `vector`/`fluent-bit` → central store) so a dead
  host does not take its logs with it.

## Examples

**Good Example** — structured, rotated, secret-free, to stdout

```bash
#!/usr/bin/env bash
set -euo pipefail

log() {  # one JSON line per event: searchable, level-tagged, no secrets
  printf '{"ts":"%s","level":"%s","msg":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2"
}

log INFO "backup started"
# Log the outcome and the (non-secret) target — never the credentials used.
if pg_dump "$DATABASE_URL" > /backups/db.sql; then
  log INFO "backup complete host=db-01"
else
  log ERROR "backup failed host=db-01"   # ERROR is reserved for actionable failures
  exit 1
fi
```

```
# /etc/logrotate.d/myapp — bound size and age so logs never fill the disk
/var/log/myapp/*.log {
    daily
    rotate 14          # keep two weeks
    maxsize 100M       # rotate early if it grows fast
    compress
    missingok
    copytruncate       # do not require the app to reopen the file
}
```

**Bad Example** — unrotated file, leaks a secret, unsearchable

```bash
# Writes forever to one file with no rotation → fills the disk, kills the host.
# Prints the connection string, including the password → secret in the log store.
# Free-form text with no level → cannot filter errors from noise.
echo "connecting to $DATABASE_URL and starting backup" >> /var/log/backup.log
```

## Common Mistakes

- No rotation, so a chatty service fills `/var` and takes the host down.
- Logging credentials, tokens, or full request bodies, turning logs into a breach.
- Logging everything at `INFO` (or leaving `DEBUG` on in production), drowning the signal
  and inflating cost.
- Managing log files inside the app instead of writing to stdout and letting the platform
  collect — this breaks under containers and complicates rotation.
- Free-form messages with no stable fields, so you cannot query or aggregate them.
- Using `logrotate` with `create` on a file the app holds open, silently writing to the
  now-rotated inode until restart (use `copytruncate` or signal the app).

## Production Tips

- Centralize logs and set retention there; keep host-local logs short-lived. Investigate
  in the aggregator, not by SSHing to boxes.
- Alert on log *patterns* (spike in `ERROR`, a specific stack trace), not just on the
  absence of logs.
- Sample high-volume `DEBUG`/access logs rather than dropping observability entirely.
- Keep the clock synced (`chrony`/`systemd-timesyncd`) so timestamps across hosts are
  comparable during an incident.

## AI Review Checklist

- Does the service log to stdout/stderr and let the platform collect, rather than manage
  its own files?
- Are logs structured (JSON) with stable, queryable field names?
- Is rotation configured (`logrotate` or `journald` limits) so logs cannot fill the disk?
- Are secrets and full PII redacted before the log call?
- Are levels used meaningfully, with `DEBUG` off in production?
- Is there a correlation/request ID to trace a request across lines?
- Are logs shipped off-host so a dead node does not lose its history?

## Related

- `knowledge/linux/16-monitoring.md`
- `knowledge/linux/08-systemd.md`
- `knowledge/linux/19-debugging.md`
- `knowledge/linux/25-production.md`
