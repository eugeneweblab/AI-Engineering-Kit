---
id: linux/04-users-and-groups
topic: linux
slug: users-and-groups
title: "Users And Groups"
type: doc
order: 4
status: ready
tags: [linux, users-and-groups]
related: [linux/05-permissions, linux/01-filesystem, linux/00-overview, linux/03-bash, linux/02-shell]
when_to_use: "Read before creating accounts, running a process as a user, configuring sudo, or setting file ownership."
---
# Users And Groups

## Purpose

This document defines Linux identity: user accounts (UIDs), groups (GIDs), the account
databases (`/etc/passwd`, `/etc/shadow`, `/etc/group`), privilege boundaries, `sudo`,
and service accounts. It is written so an agent can run software under the right identity
and grant privilege without handing out `root`.

Identity is the foundation of [permissions](05-permissions.md): every file is owned by a
UID and a GID, and every process runs as some user. This doc is about *who*; permissions
is about *what they may do*.

## Why It Matters

The user a process runs as *is* its security boundary. A web app running as `root` that
gets compromised gives the attacker the whole machine; the same app running as an
unprivileged service account limits the damage to that app's own files. Most real-world
container and server breaches escalate precisely because something ran as `root` that had
no need to. Identity mistakes are also silent — a process runs fine as `root`, so nobody
notices the missing boundary until it is exploited.

## Core Principles

- **The kernel sees numbers, not names.** Access checks use UID and GID; the names in
  `/etc/passwd` are a convenience mapping. UID `0` is `root` and bypasses permission
  checks entirely.
- **Least privilege is the default.** A process should run as the least-privileged
  identity that can do its job, and drop privileges as soon as it can.
- **`root` is a scalpel, not a chair.** Use it for the single operation that requires it
  (via `sudo`), not as the identity you live in.
- **Service accounts are not people.** Daemons run as dedicated, non-login system accounts
  with no shell and no password, so a compromise cannot log in interactively.
- **Group membership is how you share, not `777`.** Put users who need shared access in a
  common group and grant the group access, rather than opening files to the world.

## Best Practices

- Create daemons as system accounts: `useradd --system --no-create-home --shell
  /usr/sbin/nologin appuser`. No login shell, no home, no password.
- Grant privilege narrowly with `sudo`: scope specific commands to specific users in
  `/etc/sudoers.d/`, and validate with `visudo` (never edit `/etc/sudoers` directly, a
  syntax error can lock everyone out).
- Prefer running a service as a non-root user and granting only the capability it needs
  (e.g. `CAP_NET_BIND_SERVICE` to bind port 80) over running the whole process as `root`.
- Use `usermod -aG group user` — the `-a` (append) is mandatory; `usermod -G` *replaces*
  a user's supplementary groups and can remove them from `sudo`.
- Never store passwords in `/etc/passwd`; hashes live in `/etc/shadow`, which is
  root-only. Do not `chmod` `/etc/shadow` readable.
- In containers, add a `USER` instruction so the image does not run as `root`; a running
  container inherits the host kernel, so `root` in the container is nearly `root` on host.
- Log privileged actions; `sudo` already logs to the system journal — keep that intact.

## Examples

**Good Example** — dedicated service account, scoped sudo, drop privilege

```bash
# System account: no home, no login shell, no password — cannot be logged into.
useradd --system --no-create-home --shell /usr/sbin/nologin appuser

# Scope sudo to exactly one command for one user, validated by visudo syntax.
# %deploy may restart only this unit — not a blanket root grant.
cat >/etc/sudoers.d/deploy <<'EOF'
%deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart myapp.service
EOF
visudo -cf /etc/sudoers.d/deploy    # verify before it takes effect

install -d -o appuser -g appuser -m 0750 /var/lib/myapp   # owned by the service acct
```

**Bad Example** — everything as root, replaced groups, world-open

```bash
# Runs the app as root: any RCE bug is an instant full-host compromise.
useradd appuser
usermod -G docker appuser        # -G without -a REPLACES groups: drops appuser's others
echo "appuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers   # blanket root, edited unsafely
chmod 777 /var/lib/myapp         # world-writable to "fix" a permission error
```

## Common Mistakes

- Running a daemon or container as `root` when an unprivileged account would work.
- `usermod -G` without `-a`, silently stripping a user's other group memberships.
- Editing `/etc/sudoers` with a normal editor and introducing a syntax error that breaks
  `sudo` for everyone (always use `visudo`).
- Granting `NOPASSWD: ALL` instead of scoping `sudo` to specific commands.
- Giving a service account a login shell and password "just in case".
- Confusing the primary group (one, in `/etc/passwd`) with supplementary groups (many,
  in `/etc/group`) when reasoning about access.

## Production Tips

- Prefer central identity (LDAP/SSSD) or configuration management over hand-created
  accounts so UIDs stay consistent across a fleet — mismatched UIDs corrupt shared and
  NFS-mounted file ownership.
- Reserve stable UIDs/GIDs for service accounts in infra-as-code so backups restore with
  correct ownership.
- Audit `sudo` rules and group membership in review; privilege tends to accrete and never
  gets removed.
- In containers, run rootless and set a numeric `USER` (e.g. `USER 10001`) so the
  identity is meaningful even without an `/etc/passwd` entry.

## AI Review Checklist

- Does the process run as the least-privileged identity that works, not `root`?
- Are daemons dedicated system accounts with `nologin` and no password?
- Is `sudo` scoped to specific commands in `/etc/sudoers.d/` and validated with `visudo`?
- Does every `usermod -G` include `-a`, so existing groups are preserved?
- Do containers set a non-root `USER`?
- Is shared access granted via a group rather than world (`o+w` / `777`)?

## Related

- `knowledge/linux/05-permissions.md`
- `knowledge/linux/01-filesystem.md`
- `knowledge/linux/00-overview.md`
- `knowledge/linux/03-bash.md`
- `knowledge/linux/02-shell.md`
