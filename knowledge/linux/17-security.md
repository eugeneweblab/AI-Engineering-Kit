---
id: linux/17-security
topic: linux
slug: security
title: "Security"
type: doc
order: 17
status: ready
tags: [linux, security]
related: [linux/05-permissions, linux/10-ssh, linux/21-firewall, linux/04-users-and-groups]
when_to_use: "Read before hardening a Linux host, granting privileges, or reviewing anything that runs as root."
---
# Security

## Purpose

This document defines how to harden a Linux host: least-privilege user and service
accounts, safe use of `sudo`, file permissions, network exposure, and keeping the system
patched. It is written so an agent can provision or review a host without leaving it open
to trivial compromise. It complements the topic-specific docs on
[permissions](05-permissions.md), [SSH](10-ssh.md), and the [firewall](21-firewall.md).

## Why It Matters

A Linux host is a multi-tenant, network-attached target. A single weak spot — a service
running as root, a world-writable file, an open port, an unpatched CVE — can be enough
for full compromise, and the attacker's first move is usually to erase the evidence.
Security failures are silent until they are catastrophic, and by then the blast radius is
the whole machine and everything it can reach. Because the cost of a breach is total,
hardening is not optional polish; it is part of "does this run correctly".

## Core Principles

- **Least privilege, always.** Every process and person gets the minimum access needed,
  and nothing more. A service that only reads one directory should not run as root.
- **Never run application code as root.** Give each service its own unprivileged system
  account. If it is compromised, the damage is bounded to that account.
- **Reduce attack surface.** Fewer packages, fewer open ports, fewer running services —
  each removed component is one you cannot be exploited through.
- **Deny by default.** Firewalls, permissions, and access rules should start closed and
  open only what is required.
- **Patch is a security control.** An unpatched known CVE is an open door; keeping the
  system current is as important as any config.

## Best Practices

- Run each service under a dedicated non-login system user (`useradd --system
  --no-create-home --shell /usr/sbin/nologin`); never `root`, never a shared account.
- Grant `sudo` narrowly: specific commands via `/etc/sudoers.d/`, validated with
  `visudo`, not blanket `ALL=(ALL) NOPASSWD: ALL`.
- Harden `systemd` units with sandboxing: `NoNewPrivileges=true`, `ProtectSystem=strict`,
  `PrivateTmp=true`, `ProtectHome=true`, and a minimal `CapabilityBoundingSet`.
- Keep the firewall default-deny for inbound; open only the ports a service actually
  serves (see [firewall](21-firewall.md)).
- Enforce correct file modes: no world-writable files, secrets at `0600`/`0640` owned by
  the service user, `umask 027` for service processes.
- Disable password SSH auth and root login; use keys only (see [SSH](10-ssh.md)).
- Apply security updates automatically (`unattended-upgrades`/`dnf-automatic`) and reboot
  for kernel/glibc changes.
- Keep SELinux/AppArmor in enforcing mode instead of disabling it at the first denial;
  write a policy exception instead.

## Examples

**Good Example** — dedicated user, sandboxed unit, least privilege

```ini
# myapp.service — runs unprivileged and sandboxed, so a compromise is contained.
[Service]
User=myapp
Group=myapp
ExecStart=/usr/local/bin/myapp
NoNewPrivileges=true      # process can never gain new privileges via setuid
ProtectSystem=strict      # entire filesystem read-only except explicit paths
ProtectHome=true          # /home, /root invisible to the service
PrivateTmp=true           # isolated /tmp, cannot be used to attack other services
ReadWritePaths=/var/lib/myapp   # the one place it is actually allowed to write
```

```bash
# Narrow sudo grant, edited safely with visudo (syntax-checked).
# Lets the deploy user restart ONLY this service — not a root shell.
echo 'deploy ALL=(root) NOPASSWD: /bin/systemctl restart myapp' \
  | sudo EDITOR='tee' visudo -f /etc/sudoers.d/deploy
```

**Bad Example** — root service, blanket sudo, world-writable secret

```ini
[Service]
User=root                 # a bug in the app is now a root compromise
ExecStart=/usr/local/bin/myapp
# no sandboxing: full access to the filesystem, /tmp, and all capabilities
```

```bash
chmod 777 /etc/myapp/secret.env          # any local user can read the secret
echo 'deploy ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers   # deploy user == root, no audit
```

## Common Mistakes

- Running services as `root` because it "just works", removing every containment boundary.
- Granting blanket `NOPASSWD: ALL` sudo, which is functionally a root account with no
  audit trail.
- World-writable or world-readable secret files (`chmod 777`, `0644` on a credentials
  file).
- Disabling SELinux/AppArmor or the firewall to make an error go away, instead of adding a
  scoped rule.
- Leaving password-based and root SSH login enabled, inviting brute force.
- Never patching, so a public CVE stays exploitable for months.
- Editing `/etc/sudoers` directly instead of `visudo`, risking a syntax error that locks
  out sudo entirely.

## Production Tips

- Enable auditing (`auditd`) for privileged actions and ship the logs off-host so an
  attacker cannot erase them locally.
- Run a periodic vulnerability/benchmark scan (`lynis`, CIS benchmarks, `trivy` for
  images) and track findings.
- Use a secrets manager or `systemd` `LoadCredential=` instead of environment variables
  for sensitive values.
- Enforce MFA and key-only access on all administrative entry points; rotate keys on
  offboarding.

## AI Review Checklist

- Does each service run as a dedicated non-root, non-login system user?
- Is `sudo` scoped to specific commands via `sudoers.d`, edited with `visudo`?
- Are `systemd` units sandboxed (`NoNewPrivileges`, `ProtectSystem`, `PrivateTmp`)?
- Is the inbound firewall default-deny with only required ports open?
- Are secret files `0600`/`0640` and owned by the service user, with nothing
  world-writable?
- Is SSH key-only with root login and password auth disabled?
- Are security updates automated, and is SELinux/AppArmor in enforcing mode?

## Related

- `knowledge/linux/05-permissions.md`
- `knowledge/linux/10-ssh.md`
- `knowledge/linux/21-firewall.md`
- `knowledge/linux/04-users-and-groups.md`
