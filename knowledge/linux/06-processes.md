---
id: linux/06-processes
topic: linux
slug: processes
title: "Processes"
type: doc
order: 6
status: ready
tags: [linux, processes, SIGTERM, SIGKILL, SIGINT, tini, pgrep, nohup]
related: [linux/07-services, linux/08-systemd, linux/16-monitoring, linux/18-performance, linux/19-debugging]
when_to_use: "Read before starting, supervising, signalling, or debugging any long-running Linux process."
---
# Processes

## Purpose

This document defines how a Linux process behaves — how it starts, forks, receives
signals, exits, and is reaped — so an agent can launch, supervise, and terminate
processes correctly. It covers the mechanics you must respect whether you run a
command by hand, spawn a child from code, or hand the lifecycle to a supervisor.

A process is a running program with its own PID, memory, file descriptors, and exit
status. Getting the lifecycle wrong produces zombies, orphaned children, leaked file
descriptors, and services that ignore shutdown signals and get killed mid-write.

## Why It Matters

Processes are how work actually runs on Linux; everything above them (services, jobs,
containers) is a supervision policy on top. The failure modes are quiet and expensive:
a process that ignores `SIGTERM` corrupts data when it is finally `SIGKILL`ed; an
unreaped child accumulates as a zombie until the PID table is exhausted; a background
job that inherits the shell's session dies the moment the terminal closes. These bugs
do not show up in a quick test — they show up under load, on deploy, and at shutdown,
which is exactly when they cost the most.

## Core Principles

- **Every process has a parent, and the parent must reap it.** A child that exits but is
  not `wait()`ed becomes a zombie holding its exit status. In containers, PID 1 must reap
  or zombies pile up forever.
- **Signals are the shutdown contract.** `SIGTERM` means "clean up and exit"; `SIGKILL`
  (`-9`) cannot be caught and gives the process no chance to flush. Always try `SIGTERM`
  first, then escalate.
- **Exit codes are the interface.** `0` is success; non-zero is failure. `128 + N` means
  the process was terminated by signal `N` (137 = SIGKILL, 143 = SIGTERM).
- **The PID is not a stable identity.** PIDs are reused. Never signal a PID you read
  seconds ago without re-verifying it, or you may kill an unrelated process.
- **Foreground processes die with their terminal.** Anything meant to outlive the session
  must be detached (a supervisor, `systemd-run`, or `nohup`/`setsid`), not just `&`.

## Best Practices

- Prefer a supervisor (systemd, a container runtime) over ad-hoc backgrounding for
  anything that must stay running. It handles restart, logging, and reaping for you.
- Send `SIGTERM`, wait a bounded grace period, then `SIGKILL` only if the process has not
  exited. Never lead with `kill -9`.
- Handle `SIGTERM` and `SIGINT` in long-running code: stop accepting work, flush, close
  connections, exit `0`. The cost of skipping this is data loss on every restart.
- Check exit status explicitly (`$?`, `wait`, or your language's API). Do not assume a
  command succeeded because it returned.
- Identify a target by matching command line (`pgrep -f`) or a pidfile you control, not by
  eyeballing `ps`. Guessing PIDs kills the wrong thing.
- Cap resources (`ulimit`, cgroups) on untrusted or memory-hungry work so a runaway
  process cannot take the host down.

## Examples

**Good Example** — graceful shutdown with a bounded escalation

```bash
#!/usr/bin/env bash
set -euo pipefail

start_worker() {
  ./worker &                 # spawn child, record its PID immediately
  echo $! > /run/worker.pid  # pidfile is the stable handle, not a re-scanned ps
}

stop_worker() {
  local pid; pid=$(cat /run/worker.pid)
  kill -TERM "$pid"          # ask politely: let the worker flush and exit 0
  for _ in $(seq 1 10); do   # bounded grace period, ~10s
    kill -0 "$pid" 2>/dev/null || return 0  # gone? we are done
    sleep 1
  done
  kill -KILL "$pid"          # only escalate after the process refused to leave
}
```

**Bad Example** — leads with SIGKILL and races on a stale PID

```bash
#!/usr/bin/env bash
./worker &
WORKER_PID=$!

# ...minutes later, PID may have been reused by an unrelated process...
kill -9 "$WORKER_PID"   # -9 gives worker no chance to flush -> corrupted state
                        # and if the PID was recycled, this kills a bystander
# no wait/reap -> if worker exits on its own it lingers as a zombie
```

## Common Mistakes

- Using `kill -9` as the default, so processes never get to flush buffers or release locks.
- Spawning children and never `wait()`ing them, creating zombies (fatal for PID 1).
- Backgrounding with `&` and expecting survival past terminal close — it will not.
- Signalling a PID read earlier without re-checking it still refers to your process.
- Ignoring exit codes and treating any completion as success.
- Parsing `ps` output with fragile column math instead of `pgrep`/`pidof`.

## Production Tips

- In a container, make PID 1 a real init (`tini`, `--init`, or an exec'd app that reaps),
  or zombies and unforwarded signals will bite on shutdown.
- `exec` the final binary in wrapper scripts so signals reach the app, not the shell.
- Watch for processes stuck in `D` (uninterruptible sleep) — they cannot be killed and
  usually mean blocked I/O or a hung mount.

## AI Review Checklist

- Is shutdown `SIGTERM`-first with a bounded grace period before `SIGKILL`?
- Does long-running code install a `SIGTERM`/`SIGINT` handler that flushes and exits `0`?
- Are child processes reaped (`wait`), especially when the code runs as PID 1?
- Is every process identified by pidfile or `pgrep -f`, never a stale PID?
- Are exit codes checked rather than assumed?
- Is anything meant to outlive the shell run under a supervisor, not just `&`?

## Related

- `knowledge/linux/07-services.md`
- `knowledge/linux/08-systemd.md`
- `knowledge/linux/16-monitoring.md`
- `knowledge/linux/18-performance.md`
- `knowledge/linux/19-debugging.md`
