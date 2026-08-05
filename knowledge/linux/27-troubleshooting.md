---
id: linux/27-troubleshooting
topic: linux
slug: troubleshooting
title: "Linux Troubleshooting"
type: doc
order: 27
status: ready
tags: [linux, troubleshooting]
related: [linux/19-debugging, linux/16-monitoring, linux/15-logging, linux/06-processes, linux/18-performance]
when_to_use: "Read when a Linux host or service is broken, slow, or behaving unexpectedly and you need a systematic way to find the cause."
---
# Linux Troubleshooting

## Purpose

This document defines a systematic method for diagnosing Linux problems:
form a hypothesis, check the layers from the outside in, read the evidence
before changing anything, and change one variable at a time. It is about the
*process*, not memorizing commands — the tools change, but the discipline of
narrowing a problem does not.

It complements [debugging](19-debugging.md) (finding faults in a specific
program) by focusing on host- and service-level failures: "the service is down,"
"the disk is full," "requests are slow." Use [monitoring](16-monitoring.md) and
[logging](15-logging.md) as the evidence sources this method reads from.

## Why It Matters

Under pressure the instinct is to *act* — restart the service, reboot the host,
clear a cache — before understanding anything. That often clears the evidence
while leaving the cause, so the outage returns an hour later with no clue left
behind. A restart that "fixes" an OOM loop hides a memory leak until it takes
down every replica at once. Disciplined troubleshooting is faster, not slower:
reading logs and metrics first turns a two-hour guessing game into a ten-minute
diagnosis, and it produces a root cause you can actually fix.

## Core Principles

- **Read before you touch.** Capture logs, metrics, and state *before* restarting
  or rebooting. A restart can destroy the only evidence of what went wrong.
- **Work the layers, outside in.** Is it DNS, the network, the process, the disk,
  or the app? Check each layer methodically instead of jumping to a favorite cause.
- **Change one thing at a time.** Multiple simultaneous changes make it impossible
  to know which one helped or hurt.
- **Correlate with time.** "What changed?" — a deploy, a cron job, a traffic spike.
  Line up the failure timestamp with recent events before theorizing.
- **Reproduce, then fix.** A fix you cannot verify against a reproduction is a guess.

## Best Practices

- Start with the four questions: is the process running (`systemctl status`,
  `ps`), can it reach the network (`ss`, `ping`, `curl`), is there disk/memory
  (`df -h`, `free -m`), and what do the logs say (`journalctl -u svc -e`)?
- Use `journalctl -u <svc> --since "10 min ago"` to scope logs to the incident
  window instead of scrolling the whole history.
- For "disk full," find the culprit with `du -xh --max-depth=1 / | sort -h`, and
  check for deleted-but-open files (`lsof +L1`) that `df` sees but `du` does not.
- For "slow," identify the bottleneck resource first with `top`/`htop`, `iostat`,
  and `ss -s` before optimizing code — see [performance](18-performance.md).
- Trace a specific process with `strace -p <pid>` or `ss -tanp` to see what it is
  actually blocked on, rather than guessing.
- Write findings down as you go — timestamps, commands, outputs — so the postmortem
  and the next responder have a trail.
- When you must restart to restore service, snapshot the evidence first
  (`journalctl > /tmp/incident.log`, `ps aux`, `dmesg`) so the cause survives.

## Examples

**Good Example** — evidence first, one layer at a time

```bash
# 1. Capture state BEFORE changing anything
systemctl status api.service --no-pager > /tmp/incident.txt
journalctl -u api.service --since "15 min ago" >> /tmp/incident.txt
dmesg | tail -50 >> /tmp/incident.txt      # OOM kills and disk errors show here

# 2. Check resources — is this a full disk or OOM, not an app bug?
df -h /                                     # disk full stops writes silently
free -m                                     # is the host swapping / out of memory?

# 3. Correlate: did a deploy or cron job line up with the failure time?
journalctl --since "20 min ago" | grep -Ei 'deploy|oom|error'
# Now form a hypothesis, change ONE thing, and verify.
```

**Bad Example** — act first, destroy the evidence

```bash
# service is down, so just restart it and hope
systemctl restart api.service      # clears logs from RAM, resets the OOM counter
reboot                             # nukes /tmp, dmesg ring buffer, process state
# problem "goes away"... then returns at peak traffic with no evidence left.
# nothing was written down, so the next responder starts from zero.
```

## Common Mistakes

- Restarting or rebooting before capturing logs, destroying the only evidence.
- Changing several things at once, so a fix cannot be attributed or reverted.
- Optimizing the app when the real cause is a full disk, DNS timeout, or OOM kill.
- Ignoring the timeline — missing that a deploy or cron job triggered the failure.
- Trusting `df` alone when a deleted-but-open file is holding space (`lsof +L1`).
- Declaring victory without reproducing the failure and confirming the fix.

## Production Tips

- Keep a lightweight incident log template so responders capture the same fields
  every time; consistent evidence makes patterns across incidents visible.
- Pre-stage diagnostic bundles (a script that dumps `journalctl`, `ps`, `ss`,
  `df`, `dmesg`) so evidence is captured in one command during a live outage.
- Feed every root cause back into [monitoring](16-monitoring.md) as an alert so the
  next occurrence is caught before users notice.

## AI Review Checklist

- Was host/service state captured before any restart or reboot?
- Did the diagnosis check layers (process, network, disk, memory, app) methodically?
- Was only one variable changed at a time, with each change verified?
- Was the failure timeline correlated with deploys, cron, or traffic changes?
- For disk issues, were deleted-but-open files checked, not just `df`?
- Was the failure reproduced and the fix confirmed, not assumed?

## Related

- `knowledge/linux/19-debugging.md`
- `knowledge/linux/16-monitoring.md`
- `knowledge/linux/15-logging.md`
- `knowledge/linux/06-processes.md`
- `knowledge/linux/18-performance.md`
