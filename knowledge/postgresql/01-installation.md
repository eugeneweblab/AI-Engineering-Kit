---
id: postgresql/01-installation
topic: postgresql
slug: installation
title: "Installation"
type: doc
order: 1
status: ready
tags: [postgresql, installation]
related: [postgresql/02-configuration, postgresql/18-security, postgresql/19-roles-and-permissions, postgresql/26-production]
when_to_use: "Read before installing PostgreSQL for a new project, environment, or CI pipeline."
---
# Installation

## Purpose

This document defines how to install PostgreSQL so that the resulting instance is
reproducible, version-pinned, and secure by default. It covers choosing a version,
installing on Linux and in containers, initializing the data directory, and the
first steps that turn a fresh install into a usable database. Production hardening
of settings lives in [configuration](02-configuration.md); this doc gets you a
correct starting point.

## Why It Matters

An install decision is sticky. The major version you pick constrains features and
determines your upgrade path for years, and a fresh `initdb` bakes in the locale,
encoding, and checksum settings that you cannot change later without a full dump
and reload. A default install also ships with permissive local access and a stock
config tuned for a laptop — fine for a demo, a liability in production. Getting the
install right the first time avoids painful, downtime-heavy corrections later.

## Core Principles

- **Pin the major version explicitly.** "Latest" drifts and breaks reproducibility.
  Choose a supported major (PostgreSQL follows a 5-year support window) and pin it.
- **Prefer the official PGDG packages or official images.** Distro packages lag and
  the official `postgres` Docker image and PGDG apt/yum repos track releases closely.
- **`initdb` choices are permanent.** Encoding (`UTF8`), locale, and data checksums
  are fixed at cluster creation. Set them right the first time.
- **Never expose a fresh install.** Default `listen_addresses`, `pg_hba.conf`, and
  the empty `postgres` password must be locked down before the port is reachable.
- **Reproducible over manual.** Installs belong in a Dockerfile, image, or config
  management, not in shell history.

## Best Practices

- Enable **data checksums** at `initdb` (`--data-checksums`); they catch silent disk
  corruption and cannot be turned on later without a rebuild. The CPU cost is small.
- Initialize with `--encoding=UTF8` and an explicit locale; avoid `SQL_ASCII`.
- Put the data directory (`PGDATA`) on a fast, dedicated volume, not the OS root disk.
- Match client and server major versions for `pg_dump`/`pg_restore` compatibility.
- In containers, mount `PGDATA` as a named volume so data survives container replacement.
- Set a strong `postgres` superuser password and restrict `pg_hba.conf` before first exposure.
- Verify with `SELECT version();` and check `data_checksums` via `SHOW data_checksums;`.

## Examples

**Good Example** — pinned image, checksums, secrets injected, data persisted

```yaml
# docker-compose.yml — reproducible, version-pinned, data survives restarts
services:
  db:
    image: postgres:17.2          # pin exact version, not "latest" or "postgres"
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/pg_pw   # secret, not inline plaintext
      POSTGRES_DB: app
      POSTGRES_INITDB_ARGS: "--data-checksums --encoding=UTF8"  # permanent, set now
    volumes:
      - pgdata:/var/lib/postgresql/data            # named volume => data persists
    ports:
      - "127.0.0.1:5432:5432"      # bind to loopback, not 0.0.0.0
    secrets: [pg_pw]
volumes: { pgdata: {} }
secrets: { pg_pw: { file: ./secrets/pg_pw.txt } }
```

**Bad Example** — floating tag, plaintext secret, exposed, ephemeral, no checksums

```yaml
services:
  db:
    image: postgres:latest         # non-reproducible: rebuilds pull a different major
    environment:
      POSTGRES_PASSWORD: postgres  # weak, plaintext, committed to the repo
    ports:
      - "5432:5432"                # 0.0.0.0 => reachable from the whole network
    # no volume => `docker compose down` deletes all data
    # no --data-checksums => silent corruption goes undetected forever
```

## Common Mistakes

- Using the `:latest` tag, so a rebuild silently jumps a major version and breaks.
- Forgetting `--data-checksums`, then wanting them after data exists (requires a rebuild).
- Choosing `SQL_ASCII` or a mismatched locale, causing collation and sorting surprises.
- Leaving `POSTGRES_PASSWORD` empty or trivial while the port is publicly reachable.
- Storing `PGDATA` in the container's writable layer, losing data on container replacement.
- Mixing client tool versions so `pg_dump` output cannot restore on the server.

## Production Tips

- Keep the PGDG repo pinned and apply minor-version patches promptly; they are
  binary-compatible and fix data-loss and security bugs.
- Plan major upgrades with `pg_upgrade` (in-place, fast) or logical replication
  (near-zero downtime); never rely on `pg_dump` for large clusters under load.
- Record the exact version, locale, and `initdb` flags in your infra repo so any
  environment can be recreated identically.

## AI Review Checklist

- Is the PostgreSQL major version pinned to an exact, supported release?
- Were `--data-checksums` and `--encoding=UTF8` set at `initdb`?
- Is `PGDATA` on a persistent, dedicated volume?
- Is the port bound to loopback/private network, not `0.0.0.0`, on a fresh install?
- Is the superuser password strong and injected as a secret, not inline?
- Do client tool versions match the server major version?

## Related

- `knowledge/postgresql/02-configuration.md`
- `knowledge/postgresql/18-security.md`
- `knowledge/postgresql/19-roles-and-permissions.md`
- `knowledge/postgresql/26-production.md`
