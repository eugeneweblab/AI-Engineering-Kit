---
id: mysql/12-security
topic: mysql
slug: security
title: "Security"
type: doc
order: 12
status: ready
tags: [mysql, security]
related: [mysql/13-users-and-roles, mysql/02-configuration, mysql/11-backups, mysql/15-monitoring]
when_to_use: "Read before exposing a MySQL server to any network, wiring an application to it, or reviewing DB connection and privilege code."
---
# Security

## Purpose

This document defines how to harden a MySQL server and its client connections:
network exposure, transport encryption, credential handling, data-at-rest
encryption, and injection-safe access. It is written so an agent can stand up or
review a MySQL deployment without leaving the database open to compromise.

Account and privilege design has its own document — see
[users and roles](13-users-and-roles.md). This file covers everything *around*
the accounts: the wire, the disk, the config, and the application boundary.

## Why It Matters

A database holds the crown jewels: every user record, every secret, in one place.
Unlike an application bug that leaks one request, a compromised MySQL instance
leaks the entire dataset at once, silently. The most common breaches are not
exotic — they are a `root` account with no password, port 3306 open to the
internet, plaintext connections on a shared network, or string-concatenated SQL.
These are cheap to prevent and catastrophic to miss, so MySQL security is held to
a strict, checklist-driven bar.

## Core Principles

- **Never reachable by default.** Bind to localhost or a private subnet; the
  database is not an internet-facing service. Expose it only through the app tier.
- **Least privilege, always.** Applications connect as a narrowly scoped account,
  never `root`. A privilege that is not granted cannot be abused.
- **Encrypt in transit and at rest.** TLS on every connection; TDE or filesystem
  encryption on the data files and backups. Assume the network and the disk are hostile.
- **Parameterize every query.** SQL injection is prevented at the driver boundary
  with bound parameters, never by escaping or concatenating strings.
- **Secrets live outside the code.** Credentials come from a secrets manager or
  environment, never from source, config committed to git, or query logs.

## Best Practices

- Run `mysql_secure_installation` (or its equivalent) on every new server: set a
  strong `root` password, remove anonymous accounts, drop the `test` database,
  and disable remote `root` login. These defaults are exploited within minutes.
- Set `bind-address` to `127.0.0.1` or a private IP, and restrict access with a
  host firewall / security group. Do not rely on MySQL account host-matching alone.
- Require TLS: set `require_secure_transport=ON` so cleartext connections are
  refused, and have clients verify the server certificate (`--ssl-mode=VERIFY_IDENTITY`).
- Encrypt data at rest with InnoDB tablespace encryption (`innodb_redo_log_encrypt`,
  `innodb_undo_log_encrypt`, and encrypted tablespaces) backed by a keyring plugin.
- Use `caching_sha2_password` (the 8.0+ default) over TLS; never `mysql_native_password`
  for new accounts and never store the old, weakly-hashed passwords.
- Grant privileges per-database and per-object; never `GRANT ALL ON *.*`. Reserve
  `SUPER`/`SYSTEM_*` dynamic privileges for operators, not applications.
- Disable `LOCAL INFILE` (`local_infile=OFF`) unless a specific loader needs it —
  it lets a malicious server read client-side files.
- Keep the server patched. MySQL CVEs are actively exploited; track the release
  notes and apply security updates promptly.

## Examples

**Good Example** — parameterized query, scoped account, TLS enforced

```sql
-- Server: refuse any cleartext connection.
SET PERSIST require_secure_transport = ON;

-- App account: only the rights the service actually uses, on one schema, over TLS.
CREATE USER 'orders_app'@'10.0.%'
  IDENTIFIED WITH caching_sha2_password BY '<from-secrets-manager>'
  REQUIRE SSL;
GRANT SELECT, INSERT, UPDATE, DELETE ON orders_db.* TO 'orders_app'@'10.0.%';
```

```python
# Client: bind parameters so user input can never become SQL, and verify the cert.
conn = mysql.connector.connect(
    host="db.internal", user="orders_app", password=os.environ["DB_PASSWORD"],
    database="orders_db", ssl_verify_identity=True,          # reject MITM certs
)
cur = conn.cursor()
cur.execute(
    "SELECT id, total FROM orders WHERE customer_id = %s",   # placeholder, not f-string
    (customer_id,),                                          # value passed separately
)
```

**Bad Example** — string-built SQL, superuser app account, cleartext

```python
# App connects as root over an unencrypted socket — full DB access on the wire.
conn = mysql.connector.connect(host="0.0.0.0", user="root", password="root")

# User input is concatenated straight into SQL: classic injection.
cur.execute(
    f"SELECT id, total FROM orders WHERE customer_id = {customer_id}"  # ' OR 1=1 --
)
```

## Common Mistakes

- Leaving `root` with no password, or reachable from any host (`root'@'%`).
- Binding to `0.0.0.0` and exposing port 3306 to the internet or a shared VLAN.
- Building SQL with string formatting or f-strings instead of bound parameters.
- Connecting the application as `root` or with `GRANT ALL ON *.*`.
- Allowing cleartext connections because `require_secure_transport` is off.
- Committing `my.cnf` or connection strings with real credentials to the repo.
- Leaving `local_infile` on, enabling client-file exfiltration by a rogue server.

## Production Tips

- Enable the audit log (or a proxy audit) to record connections, failed logins,
  and privilege changes; ship it off-box and alert on anomalies. See
  [monitoring](15-monitoring.md).
- Rotate application passwords on a schedule; MySQL 8 supports dual passwords so
  you can rotate without downtime (`ALTER USER ... RETAIN CURRENT PASSWORD`).
- Encrypt backups too — an unencrypted dump defeats at-rest encryption. See
  [backups](11-backups.md).
- Put the DB in a private subnet and reach it only through a bastion or the app tier.

## AI Review Checklist

- Is `bind-address` private and port 3306 firewalled off from the internet?
- Does every application query use bound parameters, never string concatenation?
- Does the app connect as a least-privilege account scoped to one schema, not `root`?
- Is TLS required (`require_secure_transport=ON`) and the server cert verified by clients?
- Is data-at-rest encryption enabled for tablespaces, redo/undo logs, and backups?
- Are credentials sourced from a secrets manager, absent from source and logs?
- Were default/anonymous accounts and the `test` database removed?

## Related

- `knowledge/mysql/13-users-and-roles.md`
- `knowledge/mysql/02-configuration.md`
- `knowledge/mysql/11-backups.md`
- `knowledge/mysql/15-monitoring.md`
