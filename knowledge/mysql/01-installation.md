---
id: mysql/01-installation
topic: mysql
slug: installation
title: "MySQL Installation"
type: doc
order: 1
status: ready
tags: [mysql, installation]
related: [mysql/00-overview, mysql/02-configuration, mysql/12-security, mysql/20-production, mysql/13-users-and-roles]
when_to_use: "Read before installing, upgrading, or pinning a MySQL server version in any environment."
---
# MySQL Installation

## Purpose

This document defines how to install MySQL reproducibly across development, CI, and
production: which version to pick, how to run it, and how to make the very first server
secure. The goal is that the same MySQL behaves identically everywhere, so a query that
works locally works in production.

## Why It Matters

MySQL's behavior changes between versions — default collation, authentication plugin,
SQL modes, and optimizer heuristics all shifted in 8.0 and again in 8.4. If dev runs
8.0 and production runs 8.4, or a laptop runs Homebrew's "latest" while CI runs a pinned
image, you get bugs that reproduce in one place and not another. Installation is also the
moment the database is most exposed: a fresh server with a blank root password and an open
port is compromised within minutes on a public network. Pin the version and lock it down
before anything else touches it.

## Core Principles

- **Pin an exact version.** Use a fully qualified tag like `mysql:8.4.3`, never `mysql:latest`
  or `mysql:8`. Floating tags make your database a moving target.
- **Prefer a container or managed service over a hand-installed daemon.** Reproducibility
  beats convenience; a `docker-compose` service or RDS instance is declarative and disposable.
- **Secure on first boot, not later.** Set a strong root password, remove anonymous users and
  the test database, and bind to a known interface before the server accepts real traffic.
- **Separate the engine from the data.** Store the data directory on a named volume so an
  engine upgrade never risks the data.

## Best Practices

- Choose an LTS line for production: **MySQL 8.4 LTS** (supported into 2032) or **8.0**
  (maintenance through 2026). Match the same minor version across all environments.
- In Docker, mount `/var/lib/mysql` to a named volume and pass secrets via
  `MYSQL_ROOT_PASSWORD_FILE` or Docker secrets, never as a plaintext env var in the compose file.
- After a fresh install, run the equivalent of `mysql_secure_installation`: remove anonymous
  accounts, disallow remote root login, drop the `test` schema.
- Set the connection charset and collation at install time (`utf8mb4` / `utf8mb4_0900_ai_ci`)
  so you never inherit a legacy `latin1` default.
- Create a dedicated least-privilege application user; never let the app connect as `root`.
- Verify the install: connect and run `SELECT VERSION();` in CI to assert the pinned version.

## Examples

**Good Example** — pinned, containerized, secured

```yaml
# docker-compose.yml — reproducible across dev, CI, and staging
services:
  db:
    image: mysql:8.4.3                 # exact tag: identical engine everywhere
    command:
      - --character-set-server=utf8mb4 # correct charset from first boot
      - --collation-server=utf8mb4_0900_ai_ci
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root   # secret, not inline plaintext
      MYSQL_DATABASE: app
      MYSQL_USER: app                  # least-privilege app user, not root
      MYSQL_PASSWORD_FILE: /run/secrets/db_app
    volumes:
      - db_data:/var/lib/mysql         # data survives engine upgrades
    secrets: [db_root, db_app]
volumes: { db_data: {} }
secrets:
  db_root: { file: ./secrets/db_root.txt }
  db_app:  { file: ./secrets/db_app.txt }
```

**Bad Example** — floating tag, plaintext root, no volume

```yaml
services:
  db:
    image: mysql:latest                # "latest" changes under you between pulls
    environment:
      MYSQL_ROOT_PASSWORD: password     # weak, plaintext, and app connects as root
    # no volume: docker-compose down -v silently destroys all data
    # no charset flags: may default to a legacy collation
```

## Common Mistakes

- Using `mysql:latest` or `mysql:8`, so a rebuild silently upgrades the engine.
- Leaving the data directory unmounted, so `docker-compose down -v` wipes the database.
- Shipping `MYSQL_ROOT_PASSWORD` as a plaintext compose env var visible in `docker inspect`.
- Skipping `mysql_secure_installation`, leaving anonymous users and the `test` schema in place.
- Connecting the application as `root` because it "just works" — one SQL injection becomes total.
- Different minor versions in dev vs production, producing bugs that only reproduce in one place.

## Production Tips

- Prefer a managed service (RDS, Cloud SQL, Aurora MySQL) in production; it handles patching,
  backups, and failover you would otherwise build by hand. Still pin the engine version.
- Restrict network access with a firewall or security group; MySQL should never listen on a
  public IP. Bind to the private interface and require TLS for connections.
- Automate the upgrade path: test the target version in staging, take a backup, then upgrade —
  never let a `latest` tag upgrade production implicitly.

## AI Review Checklist

- Is the MySQL image pinned to an exact version (e.g. `8.4.3`), not `latest` or `8`?
- Is the same minor version used in dev, CI, and production?
- Is the data directory on a named volume so upgrades don't risk data?
- Is the root password strong and supplied via a secret, not inline plaintext?
- Were anonymous users and the `test` schema removed after install?
- Does the application connect as a least-privilege user, not `root`?
- Is the server charset `utf8mb4` from first boot?

## Related

- `knowledge/mysql/00-overview.md`
- `knowledge/mysql/02-configuration.md`
- `knowledge/mysql/12-security.md`
- `knowledge/mysql/20-production.md`
- `knowledge/mysql/13-users-and-roles.md`
