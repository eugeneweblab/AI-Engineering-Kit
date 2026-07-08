---
id: linux/01-filesystem
topic: linux
slug: filesystem
title: "Filesystem"
type: doc
order: 1
status: ready
tags: [linux, filesystem]
related: [linux/00-overview, linux/05-permissions, linux/04-users-and-groups, linux/03-bash, linux/02-shell]
when_to_use: "Read before reading, writing, or deleting files by path, or deciding where an app's data, config, and logs belong."
---
# Filesystem

## Purpose

This document defines how the Linux filesystem is organized and how to address files
correctly: the single-rooted directory tree, the Filesystem Hierarchy Standard (FHS),
paths, mounts, inodes, and links. It is written so an agent can place data in the right
directory and manipulate paths without corrupting or losing files.

The filesystem is the substrate for every other Linux topic. Permissions, users, and
processes all act *on* files. Get the path model right first.

## Why It Matters

There is one tree, rooted at `/`, and every file has exactly one canonical place in it.
Put a database in `/tmp` and it vanishes on reboot; write logs to `/` and you fill the
root partition and crash the host; hardcode `/home/alice/config` and the script breaks
on every other machine. Path bugs are among the most common causes of "works on my
machine" failures and of accidental data loss, because a wrong path silently reads or
writes the wrong file rather than erroring.

## Core Principles

- **One tree, mounted from many devices.** `/` is the root; other disks and network
  shares are *mounted* onto directories within it. A path never names a drive letter.
- **The FHS assigns meaning to top-level directories.** `/etc` is config, `/var` is
  variable data, `/usr` is read-only programs, `/tmp` is scratch. Honor it.
- **A file is an inode; a name is a link to it.** Deleting a name (`unlink`) removes a
  link, not necessarily the data. Multiple names can point to one inode (hard links).
- **Absolute paths are unambiguous; relative paths depend on `cwd`.** In scripts and
  automation, prefer absolute paths or resolve relative ones explicitly.
- **Paths are bytes, not text.** A filename may contain spaces, newlines, or leading
  dashes. Never assume a path is a "safe" whitespace-free token.

## Best Practices

- Put config in `/etc/<app>`, persistent state in `/var/lib/<app>`, logs in
  `/var/log/<app>`, runtime sockets/PIDs in `/run/<app>`, and true scratch in a
  `mktemp -d` directory — not hand-picked names in `/tmp`.
- Create temp files atomically with `mktemp`, which avoids predictable-name races and
  guarantees a fresh path. Clean them up on exit.
- Prefer symbolic links over hard links for cross-directory references; hard links share
  an inode and cannot cross filesystems, which surprises people.
- Check free space and inodes (`df -h`, `df -i`) before large writes; running out of
  inodes fails writes even when `df -h` shows free space.
- Quote every path variable in shell (`"$path"`) and end option parsing with `--` before
  a path that may start with `-` (`rm -- "$file"`).
- Never parse `ls` output; use globs or `find -print0` piped to `xargs -0` for
  whitespace-safe iteration.

## Examples

**Good Example** — safe, portable temp handling and place-by-purpose

```bash
# mktemp gives a unique path with no name-collision race; trap guarantees cleanup
# even if the script exits early, so we never leak files into /tmp.
workdir="$(mktemp -d)"
trap 'rm -rf -- "$workdir"' EXIT

install -D -m 0644 app.conf /etc/myapp/app.conf   # config lives in /etc, mode 0644
install -d -m 0750 /var/lib/myapp                  # state dir, not world-readable
```

**Bad Example** — predictable paths, unquoted, wrong locations

```bash
tmp=/tmp/build            # predictable name: another process can pre-create/symlink it
mkdir $tmp                # unquoted; also fails silently if it already exists
cp app.conf /myapp.conf   # dumps config into / (root partition), ignores FHS
cp data.db /tmp/data.db   # "persistent" data in /tmp is wiped on reboot
```

## Common Mistakes

- Storing persistent data in `/tmp` or `/var/tmp` and losing it on reboot or cleanup.
- Hardcoding a user's home path or a distro-specific location instead of an FHS path.
- Writing logs or data under `/` and filling the root filesystem.
- Assuming a delete freed space when a running process still holds the file open — the
  inode persists until the last descriptor closes.
- Using a fixed temp filename, creating a symlink-attack or collision race.
- Iterating filenames with word-splitting (`for f in $(ls)`), which breaks on spaces.

## Production Tips

- Monitor `df -h` and `df -i` on `/`, `/var`, and any data mount; alert well before 90%.
- Mount `/tmp` and other volatile paths `noexec,nosuid,nodev` where policy allows, to
  reduce the attack surface.
- Use separate partitions/volumes for `/var/log` and application data so a runaway log
  cannot take down the root filesystem.
- Prefer `install` over `cp`+`chmod`+`chown`: it sets mode and owner atomically at copy
  time, avoiding a window where the file exists with wrong permissions.

## AI Review Checklist

- Does each file land in its FHS-correct directory (config → `/etc`, state → `/var/lib`,
  logs → `/var/log`, scratch → `mktemp`)?
- Are temp files created with `mktemp` and cleaned up via a `trap`?
- Is every path variable quoted, and are paths that may start with `-` guarded by `--`?
- Are absolute paths used in automation instead of `cwd`-relative ones?
- Is there a free-space/inode check before large or unbounded writes?
- Is filename iteration whitespace-safe (`find -print0` / globs, never parsing `ls`)?

## Related

- `knowledge/linux/00-overview.md`
- `knowledge/linux/05-permissions.md`
- `knowledge/linux/04-users-and-groups.md`
- `knowledge/linux/03-bash.md`
- `knowledge/linux/02-shell.md`
