---
id: linux/23-automation
topic: linux
slug: automation
title: "Linux Automation"
type: doc
order: 23
status: ready
tags: [linux, automation, useradd, rsync, cron, flock]
related: [linux/03-bash, linux/14-cron, linux/24-scripting, linux/20-backups, linux/25-production]
when_to_use: "Read before automating a Linux task — scheduled jobs, provisioning, or config management scripts."
---
# Linux Automation

## Purpose

This document defines how to automate operations on Linux reliably: scheduled jobs,
provisioning, and configuration changes that run without a human watching. It is written
so an agent writes automation that is safe to run repeatedly, fails loudly, and leaves the
system in a known state — not automation that silently corrupts hosts at 3 a.m.

Automation answers "how do I make this task run correctly every time, unattended?". The
hard part is not making it run once; it is making it safe to run a thousand times across a
fleet without supervision.

## Why It Matters

Automation multiplies whatever you give it — including mistakes. A manual command run
wrong breaks one host; the same command in a cron job or provisioning script breaks every
host, on schedule, until someone notices. And unattended jobs fail silently by default:
`cron` swallows output, exit codes go unchecked, and a job that stopped running produces no
error at all. Because automation runs when no one is looking, it must be built to assume
the worst — partial failure, concurrent runs, a half-applied change — and handle each
deliberately.

## Core Principles

- **Idempotent by design.** Running the automation twice must be safe and produce the same
  result. "Create the user if absent" — not "create the user", which fails or duplicates
  on the second run.
- **Fail loud, fail closed.** Exit non-zero and stop on the first error (`set -euo
  pipefail`). A job that hides its failure is worse than no job.
- **Automation is code.** Version it, review it, and test it. A script pasted onto a
  server is unreviewable and unreproducible.
- **Least privilege.** Run with the minimum rights the task needs, and scope credentials
  narrowly. Automated jobs are a prime target and run without a human to catch misuse.
- **Observable and alertable.** Every unattended job must report success AND absence. If
  nobody would notice it stopping, it is not production-ready.

## Best Practices

- Prefer declarative configuration management (Ansible, or systemd/cloud-init for
  provisioning) over imperative scripts; declaring desired state is inherently idempotent
  and reviewable.
- Guard scripts with `set -euo pipefail` and quote variables so an unset variable or a
  failed pipe stops the run instead of continuing on corrupt state.
- Make each step idempotent: check-then-act, use `install -D`, `mkdir -p`, `rsync`,
  `useradd ... || true` guards — never assume a clean starting state.
- Prevent overlapping runs with a lock (`flock`); a slow job that overruns its schedule
  must not stack a second copy on top of the first.
- Send failure output somewhere a human sees it: `MAILTO` for cron, or push job status to
  monitoring. Use a dead-man's-switch (heartbeat) to alert when a job stops running.
- Prefer systemd timers over cron for anything nontrivial: they log to the journal, track
  exit status, support dependencies, and survive missed runs (`Persistent=true`).
- Test automation in a scratch environment and run it twice to prove idempotency before
  it touches production.

## Examples

**Good Example** — strict mode, locked, idempotent, reports failure

```bash
#!/usr/bin/env bash
set -euo pipefail                      # stop on any error, unset var, or failed pipe

# flock prevents a second copy running if the previous run is still going.
exec 9>/var/run/sync-config.lock
flock -n 9 || { echo "already running" >&2; exit 1; }

dest=/etc/app/config.yml
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT               # clean up even on failure

fetch-config > "$tmp"                  # write to temp first...
if ! cmp -s "$tmp" "$dest"; then       # ...only act if something actually changed (idempotent)
  install -m 0640 "$tmp" "$dest"       # atomic replace; never leaves a half-written file
  systemctl reload app
fi
# Non-zero exit from any step above aborts the run and the timer records the failure.
```

**Bad Example** — no error handling, not idempotent, silent failure

```bash
#!/bin/bash
# No 'set -e': if fetch-config fails, the script writes an empty file and continues.
fetch-config > /etc/app/config.yml     # truncates the live config on any failure
useradd appuser                        # crashes on the second run (user exists) -> job fails forever
systemctl reload app
# Scheduled from crontab with output discarded, so when it breaks, nobody is told.
```

## Common Mistakes

- Non-idempotent steps (`useradd`, `mkdir`, append-to-file) that break or duplicate on a
  second run.
- Omitting `set -euo pipefail`, so a failed command mid-script leaves the system half
  configured while the job reports success.
- Redirecting a temp write directly over a live file, truncating it if the source fails.
- No locking, so a long run overlaps the next scheduled run and they corrupt shared state.
- Discarding job output (`>/dev/null 2>&1`) with no alerting, so failures are invisible.
- No heartbeat, so a job that silently stops running is discovered only when data is
  missing.
- Storing broad credentials in the script or its environment instead of scoped, injected
  secrets.

## Production Tips

- Drive fleet automation through a controller (Ansible, CI/CD) so every change is
  logged, reviewed, and reproducible, not typed on individual hosts.
- Use a dead-man's-switch service so a job that stops firing raises an alert on its own.
- Make destructive automation dry-run first (`--check`, `rsync -n`) and require an
  explicit flag to actually apply.
- Keep automation runs and their exit status in the journal (systemd timers) so you can
  audit what ran, when, and whether it succeeded.

## AI Review Checklist

- Is the automation idempotent — safe and consistent when run twice?
- Does it use `set -euo pipefail` (or a declarative tool) so errors stop the run?
- Are writes atomic (temp file + move), never truncating live files on failure?
- Is concurrent execution prevented with a lock where overlap would corrupt state?
- Does failure reach a human (MAILTO, monitoring), and does a stopped job alert?
- Is it run with least privilege and scoped credentials, not broad standing secrets?
- Is the automation versioned and reviewable, not pasted onto the host?

## Related

- `knowledge/linux/03-bash.md`
- `knowledge/linux/14-cron.md`
- `knowledge/linux/24-scripting.md`
- `knowledge/linux/20-backups.md`
- `knowledge/linux/25-production.md`
