---
id: linux/21-firewall
topic: linux
slug: firewall
title: "Firewall"
type: doc
order: 21
status: ready
tags: [linux, firewall]
related: [linux/09-networking, linux/10-ssh, linux/17-security, linux/22-containers, linux/25-production]
when_to_use: "Read before configuring or reviewing packet filtering, port exposure, or network access rules on a Linux host."
---
# Firewall

## Purpose

This document defines how to configure a host firewall on Linux: controlling which network
traffic is allowed in and out, with a default-deny posture. It is written so an agent can
write firewall rules that reduce the attack surface without locking themselves — or the
service — out.

A firewall answers "which packets may cross this boundary?". The correct default answer is
"none, unless explicitly allowed". Everything else is exceptions to that rule.

## Why It Matters

Every open port is a door an attacker can knock on. A host with a permissive firewall
exposes services that were never meant to face the network — a database bound to
`0.0.0.0`, a debug endpoint, an admin panel. These get found by automated scanners within
minutes of going live. The firewall is the cheapest, broadest control you have: it stops
whole classes of attack before they reach the application. But it is also the easiest place
to lock yourself out or, worse, believe you are protected when a misordered rule silently
allows everything.

## Core Principles

- **Default deny.** Set the default inbound policy to DROP, then explicitly allow only what
  is needed. An allowlist fails safe; a blocklist forgets a port and fails open.
- **Least exposure.** Open the minimum ports, to the minimum sources. A database should
  accept connections only from the app hosts, never the whole internet.
- **Rule order is logic.** Firewalls evaluate top-to-bottom and stop at the first match. A
  broad ALLOW above a specific DENY makes the DENY dead code.
- **Never lock yourself out.** Always permit your management path (SSH) before applying a
  default-deny, and apply changes so a mistake auto-reverts.
- **The firewall is a layer, not the whole defense.** It complements — never replaces —
  authentication, TLS, and binding services to the right interface.

## Best Practices

- Use the distro's front-end (`ufw` on Debian/Ubuntu, `firewalld` on RHEL/Fedora) over
  raw `nftables`/`iptables` for host rules; they manage ordering and persistence for you.
- Explicitly allow SSH (or your admin path) *before* enabling default-deny, so you keep
  access. Verify with a second session before closing the first.
- Scope rules to source and interface, not just port: allow Postgres `5432` only from the
  app subnet, not from anywhere.
- Persist rules so they survive reboot (`ufw enable`, `firewalld` permanent zones); a
  runtime-only ruleset silently disappears on restart.
- Prefer binding services to `127.0.0.1` or a private interface over relying on the
  firewall alone — defense in depth, and it survives a firewall flush.
- Understand that Docker manipulates `iptables` directly and can bypass `ufw`; publish
  container ports deliberately and check the actual ruleset (see [containers](22-containers.md)).
- Log dropped packets at a sampled rate to spot scans and misconfigurations without
  flooding the log.

## Examples

**Good Example** — default deny, SSH kept, scoped source, reversible

```bash
# Allow the management path FIRST so enabling deny cannot lock us out.
ufw allow 22/tcp comment 'ssh admin'

# Expose only what the public needs, scoped where possible.
ufw allow 443/tcp comment 'https'
ufw allow from 10.0.1.0/24 to any port 5432 proto tcp comment 'postgres: app subnet only'

ufw default deny incoming     # everything not explicitly allowed is dropped
ufw default allow outgoing
ufw enable                    # rules persist across reboot

ufw status verbose            # verify BEFORE closing the current SSH session
```

**Bad Example** — permissive, wrong order, exposes the database

```bash
iptables -P INPUT ACCEPT                       # default-open: forgets one port -> exposed
iptables -A INPUT -p tcp --dport 5432 -j ACCEPT # Postgres open to the entire internet
iptables -A INPUT -s 10.0.1.0/24 -j DROP        # dead rule: ACCEPT above already matched
# Nothing is persisted, so a reboot drops every rule and the host reverts to fully open.
```

## Common Mistakes

- Leaving the default policy as ACCEPT, so any forgotten or future service is exposed.
- Ordering a broad ALLOW above a specific DENY, making the DENY unreachable.
- Enabling default-deny without first allowing SSH, locking yourself out of a remote host.
- Opening a port to `0.0.0.0/0` when only a specific subnet or host needs it.
- Editing runtime rules but not persisting them, so a reboot wipes the configuration.
- Assuming `ufw` governs container traffic when Docker has inserted its own `iptables`
  rules ahead of it.
- Treating the firewall as the only control, leaving services bound to all interfaces.

## Production Tips

- Apply firewall changes through configuration management (Ansible, etc.) so the ruleset
  is versioned, reviewable, and reproducible — not typed live and forgotten.
- On cloud hosts, layer a network-level security group in front of the host firewall;
  two independent default-deny layers are far harder to misconfigure into open.
- Wrap risky remote changes so they auto-revert (e.g. a scheduled `ufw reset` you cancel
  once you confirm you still have access).
- Periodically scan your own public IPs (`nmap`) from outside to see what is actually
  reachable, not what you believe is reachable.

## AI Review Checklist

- Is the default inbound policy DROP/deny, with services added as explicit exceptions?
- Is SSH (or the admin path) allowed before default-deny is enabled?
- Are exposed ports scoped to the minimum source addresses, not `0.0.0.0/0`?
- Is rule order correct — specific rules before broad ones, no dead rules?
- Are rules persisted so they survive a reboot?
- Are container/Docker rules accounted for rather than assumed covered by `ufw`?
- Are sensitive services also bound to a private interface, not just firewalled?

## Related

- `knowledge/linux/09-networking.md`
- `knowledge/linux/10-ssh.md`
- `knowledge/linux/17-security.md`
- `knowledge/linux/22-containers.md`
- `knowledge/linux/25-production.md`
