---
id: mysql/13-users-and-roles
topic: mysql
slug: users-and-roles
title: "Users And Roles"
type: doc
order: 13
status: ready
tags: [mysql, users-and-roles, migrator, SUPER, app_readwrite, app_readonly, REVOKE, ALL]
related: [mysql/12-security, mysql/02-configuration, mysql/16-migrations, mysql/15-monitoring]
when_to_use: "Read before creating a MySQL account, granting privileges, or reviewing who can do what in the database."
---
# Users And Roles

## Purpose

This document defines how to model identity and access inside MySQL: creating
accounts, granting the minimum privileges, and packaging those privileges into
roles. It is written so an agent can provision database access without handing an
application — or an attacker who steals its credentials — more power than the task
requires.

This is the account layer. Network, transport, and injection defenses live in
[security](12-security.md); read that too, because a perfectly scoped account is
still lost if it travels over a cleartext wire.

## Why It Matters

MySQL privileges are the last enforcement point before your data. Get them wrong
and every other control is decoration: an app account with `GRANT ALL ON *.*` can,
once its password leaks, read every schema, drop every table, and create new
backdoor accounts. Because privileges accumulate quietly — a temporary grant that
was never revoked, a role that grew over years — access sprawl is the normal
failure mode. Designing least privilege up front, and packaging it in roles, is
far cheaper than auditing a tangle of ad-hoc grants after an incident.

## Core Principles

- **Least privilege by default.** Grant only the statements and objects the
  account actually uses. Start from nothing and add, never start from `ALL` and trim.
- **One identity per purpose.** Separate accounts for each application, each
  environment, and each human operator. Shared accounts destroy accountability.
- **Bundle privileges into roles.** Assign privileges to a role, assign the role to
  users. This makes access reviewable and revocable in one place.
- **Scope by host.** An account is `user@host`; restrict the host to the network
  the client actually connects from, never `@'%'` for privileged accounts.
- **Applications are not operators.** Schema changes, user management, and `SUPER`-class
  privileges belong to migration/ops credentials, not the runtime app account.

## Best Practices

- Create accounts with an explicit authentication plugin and TLS requirement:
  `CREATE USER ... IDENTIFIED WITH caching_sha2_password ... REQUIRE SSL`.
- Grant on the narrowest object that works: prefer `db.table` over `db.*`, and
  `db.*` over `*.*`. Column-level grants exist for sensitive fields.
- Define roles per function (`app_readwrite`, `app_readonly`, `reporting`,
  `migrator`) and grant roles to users; use `SET DEFAULT ROLE` so the privileges
  are active on connect.
- Give read-only consumers (dashboards, analytics) a `SELECT`-only role. A reporting
  tool never needs `INSERT`.
- Set resource limits on shared or exposed accounts (`WITH MAX_USER_CONNECTIONS`,
  `MAX_QUERIES_PER_HOUR`) to blunt runaway or abusive clients.
- Use `REQUIRE SSL` (or `REQUIRE X509`) per account so credentials cannot be used
  over cleartext even if the server default were relaxed.
- Prune relentlessly: `SHOW GRANTS`, drop unused accounts, `REVOKE` on offboarding,
  and never leave `WITH GRANT OPTION` on an application account.
- Apply `PASSWORD EXPIRE` policy and MySQL 8 dual passwords to rotate without downtime.

## Examples

**Good Example** — role-based least privilege, host-scoped

```sql
-- One role captures exactly what the runtime service needs: CRUD on its schema.
CREATE ROLE 'app_readwrite';
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.* TO 'app_readwrite';

-- The app account is host-scoped to the app subnet, requires TLS, and holds no
-- DDL or user-admin rights. If its password leaks, blast radius is one schema's rows.
CREATE USER 'shop_app'@'10.0.%'
  IDENTIFIED WITH caching_sha2_password BY '<from-secrets-manager>'
  REQUIRE SSL;
GRANT 'app_readwrite' TO 'shop_app'@'10.0.%';
SET DEFAULT ROLE 'app_readwrite' TO 'shop_app'@'10.0.%';  -- role active on connect
```

**Bad Example** — superuser app account, wide-open host

```sql
-- Reachable from anywhere, every privilege on every schema, and it can mint
-- new accounts. One leaked password = total database compromise.
CREATE USER 'app'@'%' IDENTIFIED BY 'app';
GRANT ALL PRIVILEGES ON *.* TO 'app'@'%' WITH GRANT OPTION;
```

## Common Mistakes

- Using one `root`/`admin` account for the app, migrations, and human logins alike.
- `GRANT ALL ON *.*` "to get unblocked", then never narrowing it.
- Creating accounts as `user@'%'`, allowing connections from any host on earth.
- Granting privileges directly to each user instead of through roles, so a policy
  change means editing dozens of accounts.
- Leaving `WITH GRANT OPTION` on service accounts, letting a compromise self-escalate.
- Forgetting `SET DEFAULT ROLE`, so granted roles are inactive and the app "mysteriously"
  gets access-denied errors.
- Never revoking access when a service is retired or a person leaves.

## Production Tips

- Keep account and grant definitions in version-controlled migrations, not hand-typed
  in production, so access is reviewable and reproducible. See [migrations](16-migrations.md).
- Audit periodically: query `information_schema.user_privileges` and diff against the
  intended policy; alert on new `*.*` grants.
- Maintain distinct `migrator` credentials with DDL rights, used only by the deploy
  pipeline and disabled between deploys where possible.

## AI Review Checklist

- Does each application, environment, and human have its own distinct account?
- Are privileges granted through roles rather than directly to each user?
- Is every grant scoped to the narrowest object (table/db) the account truly needs?
- Are privileged accounts host-restricted, not `@'%'`?
- Is the runtime app account free of DDL, user-admin, `SUPER`, and `GRANT OPTION`?
- Do read-only consumers hold a `SELECT`-only role?
- Are account and grant changes captured in version-controlled migrations?

## Related

- `knowledge/mysql/12-security.md`
- `knowledge/mysql/02-configuration.md`
- `knowledge/mysql/16-migrations.md`
- `knowledge/mysql/15-monitoring.md`
