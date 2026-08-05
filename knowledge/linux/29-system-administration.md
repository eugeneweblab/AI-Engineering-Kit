---
id: linux/29-system-administration
topic: linux
slug: system-administration
title: "System Administration"
type: doc
order: 29
status: ready
tags: [linux, system-administration, sudo, visudo, unattended-upgrades]
related: [linux/04-users-and-groups, linux/12-package-management, linux/08-systemd, linux/23-automation, linux/17-security]
when_to_use: "Read before performing or reviewing host administration — user management, packages, updates, and configuration changes across servers."
---
# System Administration

## Purpose

This document defines how to administer Linux hosts responsibly: managing users,
packages, updates, and system configuration in a way that is repeatable,
auditable, and recoverable. The central idea is that administration is *code* —
declared in version control and applied by automation — not a sequence of
commands typed into a terminal and forgotten.

It draws together [users and groups](04-users-and-groups.md),
[package management](12-package-management.md), [systemd](08-systemd.md), and
[automation](23-automation.md) into an operating discipline for fleets, not
single pets.

## Why It Matters

Manual administration does not scale and does not survive. A change typed onto
one host is invisible on the other forty, undocumented for the next admin, and
lost when the machine is rebuilt. This "configuration drift" is why two servers
that should be identical behave differently, and why "works on server A, breaks
on server B" is so common. It is also a security and compliance problem: without
config as code you cannot answer "who has access?" or "is this patched?" across
the fleet. Treating administration as version-controlled, automated code makes
hosts reproducible, changes reviewable, and access auditable.

## Core Principles

- **Configuration as code.** Users, packages, and settings are declared in
  version control (Ansible, cloud-init, Nix) and applied by tooling — never
  hand-edited on a live host.
- **Reproducible, not pets.** Any host must be rebuildable from code to the same
  state. If a rebuild loses configuration, that configuration was not managed.
- **Least privilege and auditability.** Access is granted through groups and
  `sudo` rules in code; every privileged action is attributable to a person.
- **Patch deliberately.** Security updates are applied on a known cadence and
  tested, not "whenever someone remembers" and not blindly auto-applied to
  everything at once.
- **Change safely.** Roll out to a canary, verify, then the fleet. Keep changes
  small, reversible, and reviewed.

## Best Practices

- Manage users and groups through automation, keyed on SSH keys, not shared
  passwords. Disable password SSH and root login — see [ssh](10-ssh.md).
- Grant privilege via `sudo` rules in `/etc/sudoers.d/` (validated with `visudo`),
  scoped to the commands a role needs, rather than blanket `ALL=(ALL)`.
- Pin package versions and use the distro's package manager; avoid `curl | sudo bash`
  installers that bypass the package database and cannot be audited or removed cleanly.
- Apply security updates on a cadence: `unattended-upgrades` for security patches on
  most hosts, staged manual updates for critical ones. Reboot for kernel updates
  (or use livepatch) — a patched-but-unrebooted kernel is still vulnerable.
- Keep `/etc` under version control or configuration management so every change is
  diffable and revertible; never edit config on a host with no record of the change.
- Roll changes fleet-wide through a canary: apply to one host, verify health, then
  expand. A bad change applied everywhere at once is a fleet-wide outage.
- Back up state and test restores; document the rebuild path so a lost host is a
  reprovision, not an archaeology project — see [backups](20-backups.md).

## Examples

**Good Example** — declarative, auditable, scoped

```yaml
# Ansible: users, packages, and sudo declared in version control
- hosts: web
  become: true
  tasks:
    - name: Deploy user with key-based auth only
      ansible.builtin.user:
        name: deploy
        groups: web           # privilege via group membership, not per-host tweaks
    - name: Install SSH key                     # no shared passwords
      ansible.posix.authorized_key:
        user: deploy
        key: "{{ deploy_ssh_key }}"
    - name: Pin the package version             # reproducible across the fleet
      ansible.builtin.apt:
        name: nginx=1.26.*
        state: present
    - name: Scoped sudo rule, validated on write
      ansible.builtin.copy:
        dest: /etc/sudoers.d/deploy
        content: "deploy ALL=(root) NOPASSWD: /bin/systemctl restart nginx\n"
        validate: 'visudo -cf %s'               # reject a broken sudoers file
```

**Bad Example** — manual, drifting, unauditable

```bash
# typed directly onto one production host, recorded nowhere
adduser deploy && passwd deploy          # shared password, no key auth
usermod -aG sudo deploy                  # full sudo, far more than the role needs
curl -fsSL https://get.example.com | sudo bash   # unaudited, unremovable install
apt-get install -y nginx                 # unpinned: every host gets a different version
# the other 39 hosts never got these changes -> configuration drift
# rebuild this host and all of it is gone
```

## Common Mistakes

- Making changes directly on hosts with no record, causing configuration drift
  across a fleet that should be identical.
- Shared passwords or root SSH login instead of per-user keys, so actions cannot be
  attributed and access cannot be revoked cleanly.
- `curl | sudo bash` installers that bypass the package manager and cannot be
  audited, pinned, or uninstalled.
- Granting blanket `sudo ALL=(ALL)` instead of scoping to the commands a role needs.
- Never patching, or blindly auto-patching every host at once with no canary.
- Treating servers as pets — hand-tuned and irreplaceable — instead of reproducible
  from code.

## Production Tips

- Keep an inventory and run configuration management on a schedule so drift is
  detected and corrected, not just applied once.
- Separate "what a host is" (role in code) from "what a host runs" (data), so you can
  rebuild the host without losing state.
- Maintain a per-role runbook and a tested rebuild procedure; the measure of good
  administration is how fast a lost host is replaced — see [automation](23-automation.md).

## AI Review Checklist

- Are users, packages, and sudo rules declared in version control, not typed on hosts?
- Can the host be rebuilt from code to the same state?
- Is access key-based and per-user, with root/password SSH disabled?
- Are `sudo` grants scoped to a role's commands and validated with `visudo`?
- Are packages installed via the package manager with pinned versions, not `curl | bash`?
- Is there a patch cadence and a canary rollout for fleet-wide changes?

## Related

- `knowledge/linux/04-users-and-groups.md`
- `knowledge/linux/12-package-management.md`
- `knowledge/linux/08-systemd.md`
- `knowledge/linux/23-automation.md`
- `knowledge/linux/17-security.md`
