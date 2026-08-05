---
id: aws/05-rds
topic: aws
slug: rds
title: "RDS"
type: doc
order: 5
status: ready
tags: [aws, rds]
related: [aws/02-iam, aws/06-vpc, aws/16-secrets-manager, aws/01-global-infrastructure, aws/14-cloudwatch]
when_to_use: "Read before provisioning, securing, or scaling a managed relational database on AWS."
---
# RDS

## Purpose

This document defines how to run a managed relational database on **Amazon RDS** (and
**Aurora**) correctly: network isolation, encryption, credentials, high availability,
backups, and scaling. It exists so an agent provisions a database that is private,
recoverable, and highly available rather than a publicly reachable single point of failure
holding the most valuable data in the system.

An RDS instance is *regional*; its high availability comes from placing standby and replica
nodes in different Availability Zones.

## Why It Matters

The database usually holds the crown jewels — customer records, credentials, financial data.
Two failure modes dominate. First, exposure: an RDS instance with a public endpoint and an
open security group is directly attackable, and the breach is total. Second, data loss: a
single-AZ instance with no tested backups turns a routine hardware failure or a bad
migration into permanent loss. Both are configuration choices made at creation time, so the
cost of getting them wrong is paid long after the decision is forgotten.

## Core Principles

- **Never public.** Place RDS in **private subnets** with `publicly_accessible = false`, and
  a security group that allows only the application tier's security group on the DB port.
  The database must not be reachable from the internet.
- **Multi-AZ for production.** Run a standby (or Aurora replicas) in another AZ so a node or
  AZ failure triggers automatic failover instead of an outage.
- **Encrypt at rest and in transit.** Enable storage encryption (KMS) at creation — it
  cannot be added to an existing unencrypted instance without a snapshot/restore — and force
  TLS connections.
- **Credentials belong in a secrets store.** Use RDS-managed master-password rotation in
  Secrets Manager, or IAM database authentication. Never hardcode DB passwords.
- **Backups are only real if restore is tested.** Automated backups and snapshots are
  worthless until you have proven a restore works and know your RTO/RPO.

## Best Practices

- Enable **automated backups** with a retention window that meets your RPO (7–35 days), and
  take manual snapshots before risky migrations.
- Use **Multi-AZ DB clusters or Aurora** for production; reserve Single-AZ for dev/test only.
- Offload reads to **read replicas** rather than oversizing the primary; scale writes
  vertically or with Aurora, which separates storage from compute.
- Turn on **Performance Insights** and **Enhanced Monitoring** to catch slow queries and
  saturation before they cause incidents.
- Set **deletion protection** on production instances and require a final snapshot on
  delete, so a stray `terraform destroy` cannot vaporize the data.
- Apply minor version upgrades in a maintenance window; test major version upgrades against
  a restored snapshot first.

## Examples

**Good Example** — private, encrypted, Multi-AZ, managed credentials (Terraform)

```hcl
resource "aws_db_instance" "app" {
  engine            = "postgres"
  instance_class    = "db.r7g.large"       # Graviton: better price/perf
  allocated_storage = 100
  storage_encrypted = true                 # KMS at rest; must be set at creation

  db_subnet_group_name   = aws_db_subnet_group.private.name # private subnets only
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false           # no internet endpoint

  multi_az                = true            # standby in another AZ -> auto failover
  manage_master_user_password = true       # password stored + rotated in Secrets Manager

  backup_retention_period = 14             # meets RPO; enables point-in-time restore
  deletion_protection     = true           # block accidental destroy
  final_snapshot_identifier = "app-final"
}
```

**Bad Example** — public, unencrypted, single-AZ, hardcoded password

```hcl
resource "aws_db_instance" "app" {
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  publicly_accessible = true               # reachable from the internet
  username            = "admin"
  password            = "P@ssw0rd123"      # secret committed to source control
  # storage_encrypted defaults off; multi_az off; no backups configured.
  skip_final_snapshot = true               # destroy -> data gone forever
}
```

## Common Mistakes

- Setting `publicly_accessible = true`, exposing the database directly to the internet.
- Hardcoding the master password in Terraform or app config instead of using Secrets Manager
  or IAM auth.
- Running Single-AZ in production, so any node failure is a full outage.
- Forgetting to enable encryption at creation, then discovering it requires a
  snapshot/restore migration to fix.
- Trusting backups that have never been restore-tested, or setting `skip_final_snapshot` on
  a production instance.
- Scaling the primary ever larger for read-heavy traffic instead of adding read replicas.

## Production Tips

- Rehearse restores: periodically restore the latest snapshot into a scratch instance and
  verify the data and RTO. An untested backup is a hope, not a plan.
- Use RDS Proxy for serverless or spiky workloads to pool connections and survive failovers
  without exhausting database connections.
- Alarm on CPU, freeable memory, free storage, and replica lag in CloudWatch; storage
  exhaustion is a silent, hard-stop outage.
- Keep the DB security group referencing the app security group by ID, not a CIDR range, so
  access tracks the fleet automatically.

## AI Review Checklist

- Is the instance in private subnets with `publicly_accessible = false`?
- Does the DB security group allow only the app tier's security group on the DB port?
- Is storage encryption enabled (set at creation) and TLS enforced for connections?
- Is Multi-AZ (or Aurora) used for production, not Single-AZ?
- Are credentials managed via Secrets Manager or IAM auth, never hardcoded?
- Are automated backups enabled, deletion protection on, and restore tested?
- Are read replicas used for read scaling instead of oversizing the primary?

## Related

- `knowledge/aws/02-iam.md`
- `knowledge/aws/06-vpc.md`
- `knowledge/aws/16-secrets-manager.md`
- `knowledge/aws/01-global-infrastructure.md`
- `knowledge/aws/14-cloudwatch.md`
