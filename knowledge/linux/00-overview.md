---
id: linux/00-overview
topic: linux
slug: overview
title: "Linux Overview"
type: doc
order: 0
status: ready
tags: [linux, overview]
related: [linux/01-filesystem, linux/02-shell, linux/03-bash, linux/04-users-and-groups, linux/05-permissions]
when_to_use: "Read before writing any Linux command, shell script, or server automation, to find the right topic doc."
---
# Linux Overview

## Purpose

This document maps the Linux knowledge base and tells you which doc to open for a
given task. It does not teach Linux itself — the sibling docs do that. Use it to
orient before writing a command, a shell script, or infrastructure automation that
runs on a Linux host.

The goal of this topic is that an AI agent operating a Linux system — building images,
writing deploy scripts, setting file modes, managing services — does so the way a
careful sysadmin would: predictably, reversibly, and without opening a security hole.

## Why It Matters

Linux is where almost all production software runs: containers, CI runners, cloud VMs,
and edge devices are Linux underneath. A shell command is executed literally and
immediately; there is no "are you sure?" and often no undo. A stray `rm -rf`, a
world-writable secret, or an unquoted variable in a script can destroy data or hand an
attacker a root shell. The blast radius is the whole machine. Getting these fundamentals
right is what separates a script that works on your laptop from one that is safe to run
on a fleet of servers.

## Core Principles

- **The command is the contract.** Linux does exactly what you typed, not what you
  meant. Precision beats cleverness.
- **Least privilege by default.** Run as an unprivileged user; reach for `root` only for
  the one operation that needs it, then drop back down.
- **Everything is a file.** Devices, sockets, and process state are files with owners and
  permission bits. Master files and you master the system.
- **Fail loud, fail early.** A script that ignores errors corrupts state silently. Make
  failures stop the run.
- **Reproducible over interactive.** A command captured in a script or config is
  reviewable and repeatable; a command typed once into a terminal is neither.

## How These Docs Fit Together

- **[Filesystem](01-filesystem.md)** — the directory hierarchy (FHS), paths, mounts,
  inodes, and links. Start here; every other topic manipulates files.
- **[Shell](02-shell.md)** — what a shell is, how it parses a command line, word
  splitting, globbing, quoting, redirection, and pipelines. The interactive layer.
- **[Bash](03-bash.md)** — writing correct, safe Bash *scripts*: `set -euo pipefail`,
  quoting, functions, and when to stop and use a real language instead.
- **[Users and Groups](04-users-and-groups.md)** — identity: UIDs, GIDs, `/etc/passwd`,
  service accounts, `sudo`, and privilege boundaries.
- **[Permissions](05-permissions.md)** — the access-control bits that ride on every file:
  `rwx`, ownership, `umask`, setuid, and ACLs. Depends on the two docs above.

Read them in order for a foundation, or jump straight to the one that matches your task.

## Best Practices

- Reach for the most specific doc: setting a file mode is [permissions](05-permissions.md),
  not [filesystem](01-filesystem.md); a `for` loop that breaks on spaces is
  [bash](03-bash.md), not [shell](02-shell.md).
- When a task spans docs (e.g. "a service account that owns `/var/lib/app`"), read the
  identity doc and the permissions doc together — ownership is the join between them.
- Prefer the POSIX-portable form shown in these docs unless a doc explicitly calls out a
  Bash-only feature; scripts move between distros and shells.

## Common Mistakes

- Treating "it worked in my terminal" as proof a script is correct — interactive shells
  forgive errors that scripts must catch. See [bash](03-bash.md).
- Editing system files as `root` when a normal user with `sudo` for one command would do.
  See [users and groups](04-users-and-groups.md).
- Fixing a "permission denied" with `chmod 777` instead of correcting ownership. See
  [permissions](05-permissions.md).
- Assuming path or tool locations (`/usr/bin/python`, GNU flags) that differ across
  distros. See [filesystem](01-filesystem.md).

## AI Review Checklist

- Did you route the task to the most specific sibling doc rather than guessing?
- For any command that writes or deletes, is the path absolute and quoted?
- Does the work run with the least privilege that completes it?
- Is the operation reversible or backed up before it runs?
- Are file modes and ownership set deliberately, not left to chance?

## Related

- `knowledge/linux/01-filesystem.md`
- `knowledge/linux/02-shell.md`
- `knowledge/linux/03-bash.md`
- `knowledge/linux/04-users-and-groups.md`
- `knowledge/linux/05-permissions.md`
