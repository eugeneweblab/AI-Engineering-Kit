---
id: linux/19-debugging
topic: linux
slug: debugging
title: "Debugging"
type: doc
order: 19
status: ready
tags: [linux, debugging]
related: [linux/06-processes, linux/15-logging, linux/16-monitoring, linux/18-performance, linux/27-troubleshooting]
when_to_use: "Read before investigating a crashed, hung, or misbehaving process on a Linux host."
---
# Debugging

## Purpose

This document defines how to debug a running or crashed process on Linux: reading its
state, tracing its system calls, capturing core dumps, and following the evidence to a
root cause. It is written so an agent investigates methodically instead of restarting the
service and hoping.

Debugging answers "what is this process actually doing, and where did it go wrong?". It is
the discipline of forming a hypothesis, testing it against observable state, and narrowing
until the cause is proven — not guessed.

## Why It Matters

The instinct under pressure is to restart the service and move on. That destroys the
evidence and guarantees the bug returns, usually at a worse time. A process that hangs,
leaks, or crashes is leaving a trail — in `/proc`, in its file descriptors, in its
syscalls, in a core dump — and that trail expires the moment you kill it. Because the
failure is often intermittent, the one crash in front of you may be the only chance to
capture what you need. Preserving and reading that evidence is the whole job.

## Core Principles

- **Reproduce or capture first.** Before restarting anything, capture the state: stack,
  open files, logs, a core dump. A restarted process tells you nothing.
- **Observe, do not assume.** The bug is rarely where you think. Trust `strace`, `/proc`,
  and logs over your mental model of the code.
- **Follow one hypothesis at a time.** State it ("it is blocked on a lock"), find the one
  observation that confirms or kills it, then move on.
- **Narrow the search space.** Each observation should cut the possible causes roughly in
  half — which process, which thread, which syscall, which resource.
- **Read the errno.** Linux syscalls fail with a specific error (`EACCES`, `ENOENT`,
  `EAGAIN`). The errno usually names the root cause directly.

## Best Practices

- Inspect a stuck process before touching it: `cat /proc/<pid>/status` (state, threads),
  `cat /proc/<pid>/wchan` (kernel function it is blocked in), `ls -l /proc/<pid>/fd`
  (open files and sockets).
- Trace syscalls with `strace -f -T -tt -p <pid>` to see exactly what a process asks the
  kernel and how long each call takes; a process stuck in `read()` or `futex()` tells you
  where it is hung.
- For a CPU-spinning process, use `perf top -p <pid>` or repeated `gdb` backtraces to find
  the hot loop; `strace` shows nothing because it is not making syscalls.
- Enable core dumps (`ulimit -c unlimited`, a real `kernel.core_pattern`) so crashes leave
  an analyzable artifact; open it with `gdb <binary> <core>` and run `bt`.
- Debug dynamic-library problems with `ldd`, `LD_DEBUG=libs`, and `ldconfig -p` rather than
  guessing which `.so` was picked.
- Use `journalctl -u <service> --since "10 min ago"` and correlate timestamps across logs;
  the cause is often an event just before the visible symptom.
- Change one thing per attempt and keep a written log of what you tried and what you saw.

## Examples

**Good Example** — capture evidence before recovering

```bash
# A service is hung. Preserve state FIRST, then recover.
pid=$(pgrep -f my-service)

cat /proc/$pid/status | grep -E 'State|Threads'   # is it sleeping (D/S) or running (R)?
cat /proc/$pid/stack 2>/dev/null                  # kernel stack: what is it blocked on?
ls -l /proc/$pid/fd                               # stuck on a file/socket? which one?
timeout 5 strace -f -tt -p $pid                   # snapshot of live syscalls

gcore $pid                                        # dump memory for offline analysis
# Only now restart the service — the evidence is safely captured.
systemctl restart my-service
```

**Bad Example** — destroy the evidence, learn nothing

```bash
# Service is hung. Reflexively wipe the one crime scene we had.
systemctl restart my-service   # process gone; /proc, fds, stack all vanished
# It hangs again tomorrow. With no captured state, we are exactly where we started,
# and no strace/core dump exists to explain either occurrence.
```

## Common Mistakes

- Restarting the process before capturing its state, permanently losing the evidence.
- Running `strace` on a busy-looping process and concluding "nothing is happening" — it is
  burning CPU in userspace, not in syscalls.
- Ignoring the errno and treating every failure as generic, missing that `ENOSPC` or
  `EACCES` names the cause outright.
- Debugging on a different kernel, glibc, or architecture than production, so the repro
  does not match.
- Attaching a debugger to production and pausing a process holding a critical lock,
  turning one incident into an outage.
- Changing several things at once, so when it "works" nobody knows why.

## Production Tips

- Ship debug symbols (or `debuginfod`) so core dumps and `perf` output are readable in
  production, not full of `??`.
- Configure `core_pattern` to write dumps to a dedicated, size-limited location so a crash
  loop cannot fill the disk.
- Prefer `gcore`/`perf`/`bpftrace` (low overhead) over interactive `gdb` stepping on a
  live production process.
- Keep a runbook of the first five commands to run for a hang, so responders capture state
  reflexively instead of restarting.

## AI Review Checklist

- Is process state captured (`/proc`, fds, stack, core dump) before any restart?
- Is the tool matched to the symptom — `strace` for syscall blocks, `perf` for CPU spins?
- Is the failing syscall's errno identified and used to name the cause?
- Is only one hypothesis tested per step, with a concrete confirming observation?
- Are core dumps enabled and routed somewhere that cannot fill the disk?
- Does the debug environment match production (kernel, libc, symbols)?

## Related

- `knowledge/linux/06-processes.md`
- `knowledge/linux/15-logging.md`
- `knowledge/linux/16-monitoring.md`
- `knowledge/linux/18-performance.md`
- `knowledge/linux/27-troubleshooting.md`
