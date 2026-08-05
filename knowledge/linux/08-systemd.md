---
id: linux/08-systemd
topic: linux
slug: systemd
title: "Systemd"
type: doc
order: 8
status: ready
tags: [linux, systemd, PrivateTmp, enable, ProtectSystem, NoNewPrivileges, ExecStart, StartLimitBurst]
related: [linux/07-services, linux/06-processes, linux/14-cron, linux/15-logging, linux/25-production]
when_to_use: "Read before writing, editing, or debugging a systemd unit, timer, or journal query."
---
# Systemd

## Purpose

This document defines how to use systemd — the init system and service manager on
essentially every current Linux distribution — to run, supervise, sandbox, and observe
services. It is the concrete mechanics behind the concepts in [services](07-services.md):
unit files, `systemctl`, `journalctl`, timers, and the hardening directives you should
almost always set.

If [processes](06-processes.md) are the raw material and [services](07-services.md) are the
policy, systemd is the tool that enforces the policy. An agent editing units must know the
directives that change behavior silently and the commands that make changes take effect.

## Why It Matters

Systemd is PID 1: it reaps zombies, forwards signals, orders boot, and restarts failures.
Its behavior is controlled by declarative unit files where a single wrong directive changes
everything — `Type=forking` on a foreground binary makes systemd wait forever; a missing
`daemon-reload` means your edit silently does nothing; `Restart=always` without limits
recreates the crash loop. Because units are terse and their defaults are non-obvious,
mistakes are easy to write and hard to spot in review. Knowing the handful of load-bearing
directives is what separates a robust unit from one that "worked on my machine".

## Core Principles

- **`Type=` must match how the program actually runs.** `Type=simple` (default) for a
  foreground process, `Type=notify` for one that signals readiness, `Type=forking` *only*
  for a program that truly double-forks. A mismatch corrupts systemd's idea of "started".
- **Editing a unit is not enough — reload.** `systemctl daemon-reload` after any unit
  change, or systemd keeps running the old definition.
- **`enable` and `start` are different verbs.** `enable` sets boot behavior; `start` acts
  now. `enable --now` does both. Confusing them means "works until reboot" or the reverse.
- **The journal is the log.** `journalctl -u <unit>` is the source of truth. Do not bolt on
  a separate log file when the journal already captures, timestamps, and rotates output.
- **Hardening is opt-in but cheap.** `NoNewPrivileges`, `ProtectSystem`, `PrivateTmp` and
  friends sandbox a service with a few lines. Omitting them leaves the whole host exposed.

## Best Practices

- Put local units in `/etc/systemd/system/`; never edit vendor units in `/usr/lib/...`
  directly — use `systemctl edit` to create a drop-in override so package updates don't
  clobber your change.
- Always run `systemctl daemon-reload` after writing or editing a unit, then
  `systemctl restart` (or `enable --now`) to apply it.
- Set restart control: `Restart=on-failure`, `RestartSec=`, and `StartLimitIntervalSec` /
  `StartLimitBurst` so a broken service stops instead of looping.
- Add sandboxing by default: `NoNewPrivileges=yes`, `ProtectSystem=strict`,
  `ProtectHome=yes`, `PrivateTmp=yes`, and a `User=` that is not root. Each line shrinks the
  blast radius at near-zero cost.
- Prefer a **systemd timer** over cron for scheduled work you already run under systemd:
  timers get journald logging, dependency ordering, and `Persistent=true` catch-up. See
  [cron](14-cron.md) for the trade-off.
- Order with `After=`/`Requires=`/`Wants=` and use `network-online.target` (with its
  `Wants=`) when the service genuinely needs the network up.

## Examples

**Good Example** — a hardened service plus its timer

```ini
# /etc/systemd/system/report.service
[Unit]
Description=Nightly report generator

[Service]
Type=oneshot                 # runs to completion; correct for a batch job
User=report                  # non-root
ExecStart=/usr/local/bin/report
NoNewPrivileges=yes          # process can never gain privileges
ProtectSystem=strict         # / is read-only except explicitly allowed paths
PrivateTmp=yes               # isolated /tmp, cleaned up on exit
# logs land in the journal automatically: journalctl -u report

# /etc/systemd/system/report.timer
[Unit]
Description=Run report nightly

[Timer]
OnCalendar=*-*-* 02:30:00    # 02:30 every day
Persistent=true              # if the box was off at 02:30, run at next boot

[Install]
WantedBy=timers.target
# apply: systemctl daemon-reload && systemctl enable --now report.timer
```

**Bad Example** — wrong type, no reload discipline, no hardening

```ini
[Service]
Type=forking                 # but the binary runs in the FOREGROUND ->
                             # systemd waits for a fork that never happens and
                             # eventually marks the start as failed / times out
ExecStart=/usr/local/bin/api
Restart=always               # no RestartSec, no StartLimit -> crash loop
# runs as root by default, no sandboxing, self-logging to a file
# and the author edited this file but forgot `systemctl daemon-reload`,
# so systemd is still running the previous version anyway
```

## Common Mistakes

- Editing a unit and forgetting `daemon-reload`, so the change has no effect.
- `Type=forking` (or the wrong `Type`) for a foreground process, breaking start detection.
- Confusing `start` with `enable`, so the service does not come back after reboot.
- Editing vendor units in `/usr/lib/systemd` instead of a drop-in, losing changes on update.
- Shipping units with no sandboxing directives and running them as root.
- Reinventing log rotation instead of querying and configuring the journal.

## Production Tips

- Debug with `systemctl status <unit>`, `journalctl -u <unit> -e`, and
  `systemd-analyze verify <unit>` to catch syntax and dependency errors before deploy.
- `systemctl show <unit>` prints the *effective* config with all defaults resolved — use it
  when a directive "isn't working" to see what systemd actually applied.
- Cap resources with `MemoryMax=` / `CPUQuota=` (cgroup-backed) instead of external tools.

## AI Review Checklist

- Does `Type=` match how the program actually runs (simple/notify/oneshot/forking)?
- Is there a `daemon-reload` step after any unit edit in the workflow?
- Are restart limits set so a failing service cannot crash-loop forever?
- Is the service sandboxed (`NoNewPrivileges`, `ProtectSystem`, `PrivateTmp`, non-root `User`)?
- Are local changes drop-in overrides, not edits to vendor units?
- Is scheduled work a systemd timer (with journald logging) where appropriate?

## Related

- `knowledge/linux/07-services.md`
- `knowledge/linux/06-processes.md`
- `knowledge/linux/14-cron.md`
- `knowledge/linux/15-logging.md`
- `knowledge/linux/25-production.md`
