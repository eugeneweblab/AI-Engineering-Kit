---
id: postgresql/18-security
topic: postgresql
slug: security
title: "PostgreSQL Security"
type: doc
order: 18
status: ready
tags: [postgresql, security, pg_hba.conf, trust, scram-sha-256, listen_addresses, postgres]
related: [postgresql/19-roles-and-permissions, postgresql/12-replication, postgresql/14-backups, postgresql/17-monitoring, postgresql/26-production]
when_to_use: "Read before exposing a PostgreSQL instance to any network, wiring an app's database credentials, or reviewing connection, encryption, or data-access controls."
---
# PostgreSQL Security

## Purpose

This document defines how to secure a PostgreSQL deployment at the layers the database
itself controls: network exposure, connection authentication (`pg_hba.conf`), transport
encryption (TLS), encryption at rest, row-level access, and the handling of secrets and
sensitive columns. It is written so an agent can stand up or review a deployment without
leaving the database reachable, unauthenticated, or unencrypted.

Access control *inside* the database — who owns what and who may do what — lives in
[roles and permissions](19-roles-and-permissions.md). This document is the perimeter:
getting a connection to the server at all, and protecting the bytes in transit and at rest.

## Why It Matters

A database holds the crown jewels: every user's data in one place. Unlike application bugs
that leak one record, a database misconfiguration exposes the whole dataset at once, and
often silently — the server answers attackers exactly as it answers the app. The classic
breaches are not exotic exploits: a Postgres port open to `0.0.0.0/0`, a `trust` line in
`pg_hba.conf`, a `postgres` superuser with a default password, or `sslmode=disable` on a
link crossing the public internet. Each is a one-line mistake with total blast radius.

## Core Principles

- **Deny by network first.** The database should be unreachable from anywhere it does not
  need to serve. Firewalls and `listen_addresses` are the first control, not TLS.
- **Authenticate every connection with a strong method.** `pg_hba.conf` is evaluated
  top-to-bottom, first match wins. Never use `trust` off localhost; prefer `scram-sha-256`.
- **Encrypt in transit, always, and verify the peer.** TLS without certificate
  verification stops passive sniffing but not an active man-in-the-middle.
- **Least privilege at the connection.** The app connects as a bounded role, never as a
  superuser or the object owner. Superuser is for migrations and admin only.
- **Secrets live in a secrets manager, not in code, config repos, or connection URLs in
  logs.** Rotate them; assume any credential in a repo is already compromised.
- **Sensitive columns get extra protection** — encryption, masking, or row-level security —
  because a single over-broad `SELECT` should not spill PII.

## Best Practices

- Set `listen_addresses` to the specific interfaces the app uses; never leave the port open
  to the internet. Put the database in a private subnet and reach it over the VPC only.
- Require `scram-sha-256` for password auth (`password_encryption = scram-sha-256`).
  Never `md5` (crackable) and never `trust` for non-local, non-socket connections.
- Set `ssl = on`, provide a real certificate chain, and make clients connect with
  `sslmode=verify-full` so the hostname and CA are checked — not merely `require`.
- Give the application a dedicated login role with only the privileges it needs. Reserve
  superuser for schema migrations and operations, run from a separate credential.
- Store credentials in a secrets manager (AWS Secrets Manager, Vault). Inject at runtime;
  never commit them. Enable automatic rotation where the platform supports it.
- Encrypt at rest with volume/disk encryption (or a managed instance that does). This
  protects backups and snapshots, which are as sensitive as the live data.
- Use Row-Level Security (RLS) for multi-tenant tables so a tenant can never read another's
  rows even through a shared connection. Encrypt or hash secrets stored in columns.
- Keep the server patched — subscribe to the PostgreSQL security announcements and apply
  minor releases promptly; they carry CVE fixes.

## Examples

**Good Example** — locked-down `pg_hba.conf` and a verified TLS DSN

```conf
# pg_hba.conf — first match wins, so order from most specific to least.
# TYPE  DATABASE  USER      ADDRESS         METHOD
local   all       all                       peer            # OS-user maps to db-user
hostssl app_db    app_user  10.0.0.0/16     scram-sha-256   # app: TLS + hashed password
hostssl all       postgres  10.0.10.5/32    scram-sha-256   # admin from bastion only
# No trailing "host all all 0.0.0.0/0 trust" — anything unmatched is rejected.
```

```bash
# App connects with full verification: CA-signed cert AND hostname must match.
export DATABASE_URL="postgresql://app_user:$PG_PASS@db.internal:5432/app_db?sslmode=verify-full&sslrootcert=/etc/ssl/rds-ca.pem"
# $PG_PASS is injected from the secrets manager at boot — never baked into the image.
```

**Bad Example** — open, unauthenticated, unencrypted

```conf
# pg_hba.conf
host  all  all  0.0.0.0/0  trust   # anyone who can reach the port is a superuser
```

```bash
# Credentials in the repo, TLS disabled → sniffable password + full data on the wire.
export DATABASE_URL="postgresql://postgres:postgres@db:5432/app?sslmode=disable"
```

## Common Mistakes

- Binding `listen_addresses = '*'` and opening the security group to `0.0.0.0/0`.
- A `trust` line matching remote hosts, or `md5` instead of `scram-sha-256`.
- `sslmode=require` (or `disable`) instead of `verify-full`, so an MITM goes undetected.
- The application connecting as `postgres`/superuser or as the table owner.
- Connection strings with passwords committed to git or printed in application logs.
- Assuming the managed provider encrypts backups — verify snapshot and backup encryption.
- Forgetting that `PUBLIC` has `CONNECT` and schema `USAGE` by default; revoke it.

## Production Tips

- Log connection attempts (`log_connections = on`, `log_disconnections = on`) and alert on
  auth failures — credential-stuffing shows up here first.
- Run authenticated vulnerability scans and periodically audit `pg_hba.conf` in CI by
  diffing it against a known-good policy.
- Terminate idle sessions with `idle_session_timeout` to shrink the window a leaked
  connection stays useful.

## AI Review Checklist

- Is the port closed to the public internet, with `listen_addresses` scoped to the app?
- Does every non-local `pg_hba.conf` line use `scram-sha-256` (never `trust`/`md5`)?
- Is `ssl = on` and does the client DSN use `sslmode=verify-full` with a CA path?
- Does the application connect as a least-privilege role, not superuser or owner?
- Are credentials sourced from a secrets manager, absent from code and logs?
- Is data at rest (including backups and snapshots) encrypted?
- Are sensitive/multi-tenant tables protected by RLS or column encryption?

## Related

- `knowledge/postgresql/19-roles-and-permissions.md`
- `knowledge/postgresql/12-replication.md`
- `knowledge/postgresql/14-backups.md`
- `knowledge/postgresql/17-monitoring.md`
- `knowledge/postgresql/26-production.md`
