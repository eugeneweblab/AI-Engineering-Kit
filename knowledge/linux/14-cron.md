---
id: linux/14-cron
topic: linux
slug: cron
title: "Cron"
type: doc
order: 14
status: ready
tags: [linux, cron]
related: [linux/08-systemd, linux/15-logging, linux/23-automation, linux/13-environment]
when_to_use: "Read before scheduling a recurring job, or debugging a cron/timer that runs by hand but not on schedule."
---
# Cron

## Purpose

This document defines how to schedule recurring work on Linux with `cron` and, where it
fits better, `systemd` timers. It covers crontab syntax, the minimal environment cron
provides, overlap and failure handling, and logging. It is written so an agent can add a
scheduled job that runs reliably, does not overlap itself, and does not fail silently.

## Why It Matters

Scheduled jobs run unattended, so their failures are invisible until something downstream
is already broken — a backup that has not run for a week, a queue that quietly stopped
draining. Cron's execution environment is deliberately minimal and differs from your
login shell, which is why "it works when I run it by hand" is the single most common cron
bug. And a job that overruns its interval can pile up copies that exhaust the machine.
Reliable scheduling is mostly about making these silent failures loud.

## Core Principles

- **Cron's environment is minimal, not yours.** Cron runs with a bare `PATH`
  (often `/usr/bin:/bin`), no `~/.bashrc`, and `HOME` set from the crontab owner. Never
  assume the environment of your interactive shell.
- **Use absolute paths for everything.** The binary, the script, and every file it
  touches — cron's working directory and `PATH` are not what you expect.
- **A silent job is a broken job.** Capture output, exit codes, and failures; route them
  somewhere a human or alert will see.
- **Prevent overlap explicitly.** If a run can outlast its interval, guard it with a lock
  so two copies never run at once.
- **Pick the right scheduler.** `systemd` timers give you logging, dependencies,
  `Persistent=` catch-up, and resource limits that plain cron lacks.

## Best Practices

- Set `PATH` and `SHELL` at the top of the crontab, or call binaries by absolute path.
- Redirect output: send stdout/stderr to a log or to `logger` so it reaches the journal.
  A cron job with no redirection mails root — which nobody reads on modern hosts.
- Wrap the command in `flock` to prevent overlapping runs of a long job.
- Make the job idempotent where possible, so a missed or repeated run does not corrupt
  state.
- For anything that must survive downtime or needs dependencies/limits, use a `systemd`
  timer with `Persistent=true` instead of cron.
- Use `run-parts` directories (`/etc/cron.daily` etc.) for system-wide jobs; keep
  per-user jobs in that user's crontab, not root's.
- Never edit `/etc/crontab` by hand for user jobs; use `crontab -e` so syntax is checked.

## Examples

**Good Example** — absolute paths, no overlap, failures are visible

```cron
# Explicit environment — cron does not source your shell config.
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# m h dom mon dow  command
# flock: skip this run if the previous one is still going (no pile-up).
# logger: send output to the journal so failures are searchable/alertable.
*/5 * * * *  flock -n /run/lock/sync.lock /usr/local/bin/sync.sh 2>&1 | logger -t sync
```

**Bad Example** — relies on login environment, hides every failure

```cron
# No PATH: `sync.sh` and the tools it calls may not be found.
# Relative path: depends on a working directory cron does not guarantee.
# No redirection: errors vanish (or mail root, which no one reads).
# No lock: a slow run at :00 overlaps the next at :05, doubling load.
*/5 * * * *  sync.sh
```

## Common Mistakes

- Using relative paths or assuming a rich `PATH`, so the job fails with "command not
  found" only under cron.
- Discarding output (or letting it mail root), so failures are never seen.
- Percent signs (`%`) in the command — cron treats them as newlines unless escaped
  (`\%`); this silently breaks `date +%Y-%m-%d` in a crontab.
- No overlap guard on a job that can run longer than its interval.
- Scheduling in the wrong timezone; cron uses the system/user timezone, which may not be
  UTC — DST transitions can skip or repeat a run.
- Putting jobs that must survive reboots in cron instead of a `Persistent=` timer.

## Production Tips

- Prefer `systemd` timers for production: you get `journalctl -u job.timer`,
  `OnCalendar=` scheduling, `Persistent=true` to catch up missed runs, and
  `RuntimeMaxSec=` to kill runaways.
- Emit a heartbeat to a dead-man's-switch (e.g. a healthcheck ping) on success, and alert
  when the heartbeat is missing — this catches jobs that never ran at all, which no
  failure log can.
- Set explicit resource limits (`nice`, `ionice`, or timer `CPUQuota=`) so batch jobs do
  not starve interactive services.

## AI Review Checklist

- Does the job use absolute paths for the binary, script, and data files?
- Is `PATH` set in the crontab, or every command called by absolute path?
- Is output captured to a log/`logger`, not discarded or mailed to root?
- Is a long-running job guarded with `flock` against overlap?
- Are `%` characters escaped in the crontab command?
- For jobs that must survive downtime, is a `systemd` timer with `Persistent=` used?
- Is there an alert when the job fails *or* does not run at all?

## Related

- `knowledge/linux/08-systemd.md`
- `knowledge/linux/15-logging.md`
- `knowledge/linux/23-automation.md`
- `knowledge/linux/13-environment.md`
