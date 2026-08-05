---
id: linux/11-storage
topic: linux
slug: storage
title: "Storage"
type: doc
order: 11
status: ready
tags: [linux, storage, mkfs, disk, partition]
related: [linux/01-filesystem, linux/20-backups, linux/16-monitoring, linux/19-debugging, linux/25-production]
when_to_use: "Read before partitioning, mounting, resizing, or diagnosing disk and filesystem issues on Linux."
---
# Storage

## Purpose

This document defines how block storage works on Linux — disks, partitions, filesystems,
mounts, and free space — so an agent can add capacity, mount volumes durably, and diagnose
a full or failing disk without losing data. It covers the layers (`block device` ->
`partition`/`LVM` -> `filesystem` -> `mount`) and the operations that are safe versus the
ones that destroy data.

It builds on the [filesystem](01-filesystem.md) doc (paths, layout, ownership); here the
concern is the physical and logical storage underneath those paths, and how to change it
without an outage.

## Why It Matters

Storage failures are among the few that take a whole host down hard and, unlike most bugs,
can be irreversible. A disk that hits 100% full stops writes everywhere at once — databases
corrupt, logs stop, services crash — and the symptoms rarely name the cause. Partitioning
and filesystem commands operate on raw devices, so a single wrong `mkfs` or `dd` erases data
with no undo. And a volume mounted by hand vanishes on reboot, turning a working server into
a broken one after the next restart. Because the blast radius is the whole machine and some
mistakes are unrecoverable, storage operations demand verification before every destructive
step.

## Core Principles

- **Identify devices by UUID or label, never by kernel name.** `/dev/sdb` can become
  `/dev/sdc` after a reboot or a disk swap. Mount and reference storage by `UUID=` so it
  stays correct.
- **Destructive commands have no undo.** `mkfs`, `dd`, `wipefs`, `parted`, and repartitioning
  overwrite data immediately. Confirm the target device *twice* before running them.
- **Free space has two dimensions: bytes and inodes.** A disk can be "full" with space left
  if it is out of inodes (millions of tiny files). Check both `df -h` and `df -i`.
- **A mount is not persistent until it is in `/etc/fstab` (or a mount unit).** A live `mount`
  command is gone on reboot; only a persisted entry survives.
- **Deleting a file does not free space if a process still holds it open.** Space returns
  when the last file descriptor closes, not when `rm` runs.

## Best Practices

- Reference volumes in `/etc/fstab` by `UUID=` (from `blkid`/`lsblk -f`), not `/dev/sdX`, so
  a device rename does not mount the wrong disk or fail to boot.
- After editing `/etc/fstab`, validate with `mount -a` (and `findmnt --verify`) *before*
  rebooting — a bad fstab line can drop the machine into emergency mode.
- Add `nofail` (and consider `x-systemd.device-timeout=`) to non-critical fstab entries so a
  missing disk does not block boot.
- Prefer LVM (or a cloud volume manager) for anything that may need to grow: it lets you
  extend a filesystem online (`lvextend` + `resize2fs`/`xfs_growfs`) instead of repartitioning.
- When space runs low, diagnose before deleting: `du -xhd1 /path | sort -h` to find the
  offenders, `df -i` for inode exhaustion, and `lsof +L1` for deleted-but-open files.
- Choose the filesystem deliberately: ext4 as a safe default, XFS for large files and
  parallel I/O. Set the right mount options (`noatime` to cut write amplification where
  access times don't matter).

## Examples

**Good Example** — add a disk, mount it durably by UUID

```bash
lsblk -f                       # inspect devices; confirm the NEW disk (e.g. /dev/sdb is empty)
sudo mkfs.ext4 /dev/sdb        # destructive: only after confirming sdb is the right, empty disk
UUID=$(sudo blkid -s UUID -o value /dev/sdb)   # stable identifier, survives renames

echo "UUID=$UUID /data ext4 defaults,noatime,nofail 0 2" | sudo tee -a /etc/fstab
sudo mkdir -p /data
sudo mount -a                  # validates fstab NOW; catches typos before a reboot does
findmnt /data                  # confirm it actually mounted from the fstab entry
```

**Bad Example** — device-name mount, no validation, blind wipe

```bash
sudo mkfs.ext4 /dev/sdb        # ran mkfs without checking sdb — it held the data disk. Gone.

# mount by kernel name, only for this boot:
sudo mount /dev/sdb /data      # /dev/sdb may be /dev/sdc after the next reboot -> mounts
                               # the wrong disk, or nothing, and /data silently goes empty
# never added to /etc/fstab -> the mount disappears on reboot
# never ran `df -i`, so "disk full" with free bytes stays a mystery
```

## Common Mistakes

- Mounting by `/dev/sdX` instead of `UUID=`, so a device rename breaks the mount or boot.
- Running `mkfs`/`dd`/`parted` on the wrong device because the target was not re-verified.
- Editing `/etc/fstab` and rebooting without `mount -a`, dropping the host into emergency mode.
- Diagnosing "disk full" by bytes only, missing inode exhaustion (`df -i`).
- Deleting a large log and seeing no space return because a process still holds it open.
- Growing storage by repartitioning in place instead of using LVM/online resize.

## Production Tips

- Monitor and alert on disk usage *before* it hits 100% (e.g. warn at 80%): a full root
  filesystem cascades into failures across every service on the box.
- For deleted-but-held space, truncate the open file (`: > /path/logfile`) or restart the
  holding process rather than deleting again.
- Snapshot (LVM/cloud) before any risky storage change so an irreversible mistake becomes a
  restore. See [backups](20-backups.md).

## AI Review Checklist

- Are volumes referenced by `UUID=`/label in `/etc/fstab`, never by `/dev/sdX`?
- Is every destructive command (`mkfs`, `dd`, `parted`, `wipefs`) run against a re-verified target?
- Is `/etc/fstab` validated with `mount -a` before any reboot, and do non-critical entries use `nofail`?
- Does capacity diagnosis check both bytes (`df -h`) and inodes (`df -i`)?
- Is deleted-but-open space considered before re-deleting to reclaim disk?
- Is growable storage on LVM / a volume manager for online resize?

## Related

- `knowledge/linux/01-filesystem.md`
- `knowledge/linux/20-backups.md`
- `knowledge/linux/16-monitoring.md`
- `knowledge/linux/19-debugging.md`
- `knowledge/linux/25-production.md`
