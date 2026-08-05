---
id: linux/05-permissions
topic: linux
slug: permissions
title: "Linux Permissions"
type: doc
order: 5
status: ready
tags: [linux, permissions]
related: [linux/04-users-and-groups, linux/01-filesystem, linux/00-overview, linux/03-bash, linux/02-shell]
when_to_use: "Read before setting a file mode, chowning a file, choosing a umask, or debugging a 'permission denied' error."
---
# Linux Permissions

## Purpose

This document defines the Linux access-control model that rides on every file: the
`rwx` permission bits for owner/group/other, ownership, `umask`, and the special bits
(setuid, setgid, sticky). It is written so an agent can grant exactly the access needed
and no more, and can fix a permission error correctly instead of with `chmod 777`.

Permissions build directly on [users and groups](04-users-and-groups.md): every file
carries an owning UID and GID, and the kernel checks the acting process's identity
against the file's bits.

## Why It Matters

Permissions are the last line of defense on data at rest. A private key readable by
"other" is a compromise waiting to happen — SSH will even refuse to use a key that is
too open. A world-writable script that runs as a privileged user is a direct path to
root. The classic bad fix — `chmod 777` to make an error go away — throws away this
defense entirely and usually masks the real problem, which is wrong *ownership*. Getting
the mode and owner right is cheap; a leaked secret is not.

## Core Principles

- **Three classes, three bits.** Every file has `rwx` for the owning **user**, the owning
  **group**, and **other**. `chmod` sets them; `ls -l` shows them.
- **On directories, the bits mean something different.** `x` means "may traverse into",
  `r` means "may list names", `w` (plus `x`) means "may create/delete entries". A
  readable-but-not-executable directory is nearly useless.
- **The kernel checks the first matching class only.** If you are the owner, only the
  owner bits apply — even if the group bits are more permissive. Ownership dominates.
- **`umask` subtracts default permissions at creation time.** A new file's mode is the
  requested mode minus the umask. It is a floor on privacy, not a grant.
- **Deny by default, grant by need.** Start closed (`0600`/`0700`) and open only the
  specific access some class actually requires.

## Best Practices

- Use octal modes deliberately: `0644` for readable config/data, `0600` for secrets,
  `0755` for executables and traversable dirs, `0700` for private dirs.
- Fix "permission denied" by correcting **ownership** (`chown user:group`) first; reach
  for `chmod` only when the mode is genuinely wrong. Never use `777`.
- Set secrets to `0600` owned by the service account. SSH private keys must be `0600`
  (or `0400`); more open and the client refuses them.
- Use the **setgid** bit on shared directories (`chmod 2775 dir`) so new files inherit
  the directory's group — this is how teams share a directory correctly.
- Use the **sticky** bit on world-writable shared dirs (`chmod 1777`, as on `/tmp`) so
  users can only delete their own files.
- Avoid **setuid** on your own binaries; a bug in a setuid-root program is a privilege
  escalation. Prefer capabilities or `sudo` with scoped rules.
- Apply modes recursively with intent: `find dir -type d -exec chmod 0755 {} +` and
  `-type f -exec chmod 0644 {} +` — never `chmod -R 0755`, which makes data files
  executable.

## Examples

**Good Example** — least privilege, correct owner, group sharing via setgid

```bash
# Secret: only the service account can read it; no group/other access at all.
install -o appuser -g appuser -m 0600 secrets.env /etc/myapp/secrets.env

# Shared drop directory for the "editors" group; setgid (2) makes new files
# inherit the "editors" group, and no "other" access keeps outsiders out.
install -d -o root -g editors -m 2770 /srv/shared

# Split recursive chmod so directories are traversable but files are NOT executable.
find /srv/shared -type d -exec chmod 2770 {} +
find /srv/shared -type f -exec chmod 0660 {} +
```

**Bad Example** — world-open, chmod hides an ownership bug, blanket recursion

```bash
chmod 777 /etc/myapp/secrets.env    # secret now readable AND writable by everyone
chmod 666 id_rsa                     # SSH will refuse this key; also world-readable
chmod -R 755 /srv/shared             # marks every data file executable; opens to "other"
# The real problem was that the dir was owned by root, not appuser — chmod hid it.
```

## Common Mistakes

- `chmod 777` (or `666` on secrets) to silence a permission error instead of fixing the
  owner — it removes the protection entirely and usually does not address the cause.
- Forgetting the `x` bit on a directory, so its contents are unreachable even though the
  files inside are readable.
- `chmod -R 0755 .` on a source tree, marking config and data files executable and
  world-readable.
- Leaving an SSH private key or `.env` more open than `0600`; the tool refuses it or the
  secret leaks.
- Not knowing the umask, so files land more open than intended (a `022` umask makes new
  files world-readable).
- Adding setuid to solve a "needs root" problem instead of scoped `sudo` or a capability.

## Production Tips

- Set a restrictive `umask` (`027` or `077`) for service accounts so anything they create
  is private by default, closing the gap before you remember to `chmod`.
- Prefer POSIX **ACLs** (`setfacl -m u:svc:rX path`) when you need to grant one extra user
  or group access without loosening the base mode for everyone.
- Audit for dangerous bits periodically: `find / -perm -4000` (setuid) and `find /
  -perm -0002` (world-writable) surface escalation and tampering risks.
- Let `install` set owner and mode atomically at copy time, so a secret never briefly
  exists world-readable between `cp` and `chmod`.

## AI Review Checklist

- Is every secret / private key `0600` (or `0400`) and owned by the right account?
- Is the mode the *least* that works — no world-writable files, no `777`?
- Was a permission error fixed by correcting ownership rather than widening the mode?
- Do directories have the `x` (traverse) bit, and shared dirs the setgid/sticky bit as
  appropriate?
- Does recursive `chmod` distinguish directories from files instead of a blanket `-R`?
- Is the service account's `umask` restrictive enough that new files are private?

## Related

- `knowledge/linux/04-users-and-groups.md`
- `knowledge/linux/01-filesystem.md`
- `knowledge/linux/00-overview.md`
- `knowledge/linux/03-bash.md`
- `knowledge/linux/02-shell.md`
