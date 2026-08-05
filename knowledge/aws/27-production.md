---
id: aws/27-production
topic: aws
slug: production
title: "AWS Production"
type: doc
order: 27
status: ready
tags: [aws, production]
related: [aws/25-security, aws/26-monitoring, aws/28-best-practices, aws/29-well-architected-framework, aws/98-production-checklist]
when_to_use: "Read before promoting any AWS workload to production or reviewing whether a system is actually ready to serve real users."
---
# AWS Production

## Purpose

This document defines what it takes for an AWS workload to be genuinely
**production-ready** — able to survive component failures, deploy safely, recover from
disaster, and be operated by a team that is not you. It is written so an agent can review
a system against the bar that real users and on-call engineers depend on, and refuse to
call something "done" when it is only "working on my laptop."

Production readiness is the union of the reliability, operational-excellence, and security
pillars applied to a specific workload. A demo that runs is not a production system; a
production system stays up when an Availability Zone fails, tells you when it is unhealthy,
and can be restored after a mistake.

## Why It Matters

The gap between "it works in the demo" and "it works at 2 a.m. during an AZ outage while
the author is on vacation" is where most incidents live. Single-AZ deployments, manual
deploys, missing backups, and no health checks all pass a happy-path test and then fail
catastrophically the first time reality diverges. Because AWS makes it trivial to launch a
single instance in a single subnet, the default path leads *away* from production
readiness — you have to deliberately design for failure. The cost of skipping this is not
paid at launch; it is paid, with interest, during the first outage.

## Core Principles

- **Design for failure.** Assume every instance, AZ, and dependency will fail. Run at least
  two AZs, use health checks and Auto Scaling to replace unhealthy nodes automatically, and
  make instances stateless so any one can die without data loss.
- **Automate every change.** All infrastructure is code (Terraform/CloudFormation/CDK) and
  every deploy runs through a pipeline. Manual console changes are unreproducible and
  invisible to review.
- **Deploy progressively, roll back instantly.** Use blue/green or canary releases with
  automated rollback on alarm. A deploy must never be an all-or-nothing bet.
- **Back up, and prove you can restore.** Backups you have never restored are a hypothesis,
  not a safety net. Define and test RPO (data loss tolerance) and RTO (downtime tolerance).
- **Make it operable by others.** Dashboards, alarms, runbooks, and least-privilege access
  so the on-call engineer who did not build it can still fix it.

## Best Practices

- Deploy across **≥2 Availability Zones** behind a load balancer; enable **Multi-AZ** on
  RDS and use regional/replicated services. Single-AZ is acceptable only for throwaway
  environments.
- Attach **health checks** at the load balancer and ASG so failing instances are drained
  and replaced without human action. Handle **SIGTERM** for graceful shutdown so
  in-flight requests finish during deploys and scale-in.
- Ship through a **CI/CD pipeline** with automated tests, then a **blue/green or canary**
  release (CodeDeploy) that shifts traffic gradually and auto-rolls-back on a CloudWatch
  alarm.
- Configure **backups with tested restores**: automated RDS snapshots, S3 versioning +
  cross-region replication for critical data, and AWS Backup with a documented restore
  runbook. Rehearse the restore on a schedule.
- Set **auto scaling** on target-tracking metrics so the system absorbs load; set
  connection draining/deregistration delay so scale-in does not drop live requests.
- Externalize **config and secrets** (Parameter Store/Secrets Manager) so the same
  immutable artifact is promoted from staging to production unchanged.
- Enforce the [monitoring](26-monitoring.md) and [security](25-security.md) baselines —
  a system with no alarms or open IAM is not production-ready regardless of uptime.

## Examples

**Good Example** — multi-AZ, self-healing, graceful

```hcl
resource "aws_autoscaling_group" "api" {
  min_size            = 2
  max_size            = 12
  vpc_zone_identifier = [aws_subnet.private_a.id, aws_subnet.private_b.id]  # 2 AZs
  health_check_type   = "ELB"     # replace instances the LB says are unhealthy
  health_check_grace_period = 60

  instance_refresh {              # rolling, health-checked deploys — not all-at-once
    strategy = "Rolling"
    preferences { min_healthy_percentage = 90 }
  }
}

resource "aws_db_instance" "app" {
  multi_az                = true  # automatic failover to the standby on AZ loss
  backup_retention_period = 14    # point-in-time restore for two weeks
  deletion_protection     = true  # a fat-fingered destroy cannot drop prod data
}
# App traps SIGTERM, stops taking new work, drains in-flight requests, then exits.
```

**Bad Example** — single point of failure, no recovery

```hcl
resource "aws_instance" "api" {
  subnet_id = aws_subnet.public_a.id  # one instance, one AZ, public — AZ loss = outage
  # no ASG, no health check: if it hangs, it stays in rotation serving errors
}

resource "aws_db_instance" "app" {
  multi_az                = false  # AZ failure takes the database down with no failover
  backup_retention_period = 0      # zero backups — a bad migration is unrecoverable
  # deployed by SSHing in and running git pull — nothing is reproducible or reviewable
}
```

## Common Mistakes

- Single-AZ (or single-instance) deployments with no automated failover.
- No health checks, so a hung process keeps receiving traffic and serving errors.
- Backups configured but never test-restored — discovered broken during a real incident.
- Manual console changes that drift from the IaC and vanish from review history.
- No graceful shutdown, so every deploy and scale-in drops in-flight requests.
- Big-bang deploys with no canary and no automated rollback.
- Hard-coded config/secrets per environment, so staging and prod artifacts differ.

## Production Tips

- Run a **game day**: kill an instance and an AZ in staging and confirm the system heals.
- Keep a per-service **runbook** covering deploy, rollback, restore, and common alarms.
- Set **deletion protection** and **termination protection** on stateful production resources.
- Define **RPO/RTO** per data store and validate them against the tested restore time.

## AI Review Checklist

- Does the workload run across at least two AZs with automated failover?
- Are instances stateless, health-checked, and replaced automatically when unhealthy?
- Is all infrastructure defined as code and deployed through a pipeline?
- Do releases use canary/blue-green with automated rollback on alarm?
- Are backups automated *and* restore-tested, with documented RPO/RTO?
- Does the app handle SIGTERM and drain connections on shutdown/scale-in?
- Are monitoring and security baselines in place before it is called "ready"?

## Related

- `knowledge/aws/25-security.md`
- `knowledge/aws/26-monitoring.md`
- `knowledge/aws/28-best-practices.md`
- `knowledge/aws/29-well-architected-framework.md`
- `knowledge/aws/98-production-checklist.md`
