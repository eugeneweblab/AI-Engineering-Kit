---
id: aws/31-high-availability
topic: aws
slug: high-availability
title: "AWS High Availability"
type: doc
order: 31
status: ready
tags: [aws, high-availability]
related: [aws/01-global-infrastructure, aws/05-rds, aws/06-vpc, aws/07-route53, aws/10-elastic-load-balancer, aws/11-auto-scaling, aws/29-well-architected-framework]
when_to_use: "Read before designing a workload to survive an Availability Zone or Region failure — Multi-AZ layout, failover behavior, health checks, and the RTO/RPO the design actually delivers."
---
# AWS High Availability

## Purpose

This document defines how to build AWS workloads that survive infrastructure failure:
spreading across Availability Zones, choosing a failover mechanism for each layer,
setting health checks that detect real failure, and picking a disaster-recovery strategy
that matches the recovery objectives the business will pay for.

It is written so an agent can lay out a workload that keeps serving when an AZ goes dark —
without pretending that a second subnet alone makes a system highly available.

## Why It Matters

Most "highly available" AWS architectures fail their first real test for reasons that were
visible in the configuration all along. A fleet spans two AZs but each AZ runs at 100%
capacity, so losing one leaves the survivors overloaded and the outage becomes total. A
database is Multi-AZ but the application caches its endpoint IP, so failover completes and
traffic still goes nowhere. A health check returns `200` from a static route while the
dependency behind it is dead, so the load balancer keeps sending traffic to an instance
that cannot serve. Or the failover path itself needs a control-plane call — launching
instances, provisioning capacity — precisely when the control plane is the thing that is
degraded.

Availability is a property of the whole request path, not of any one resource. Every
single-AZ hop in that path — one NAT gateway, one primary node, one subnet — caps the
availability of everything behind it.

## Core Principles

- **An AZ is the unit of failure.** Availability Zones are physically separate facilities
  with independent power and cooling, connected by low-latency links. Designing for
  "a server dies" is not the same as designing for "an AZ is unreachable."
- **Redundancy without spare capacity is theater.** If N AZs each run at full utilization,
  losing one loses the service. Size so that the remaining AZs absorb the load: with two
  AZs that means roughly 50% headroom, with three roughly 33%.
- **Prefer static stability.** A failover that depends on provisioning new resources
  depends on the control plane being healthy during an event where it may not be.
  Pre-provisioned standby capacity fails over more reliably than capacity you must create.
- **Health checks must exercise the real dependency path.** A check that only proves the
  process is running will happily keep a broken instance in rotation.
- **State is the hard part.** Stateless tiers scale and fail over trivially; databases,
  sessions, and file storage need an explicit replication and failover decision.
- **Know the objectives before choosing the mechanism.** RTO (how long recovery may take)
  and RPO (how much data may be lost) determine the strategy — and the cost.

## Multi-AZ Building Blocks

| Layer | Mechanism | Failover behavior |
|---|---|---|
| DNS | Route 53 health checks + failover routing | Records swap after checks fail; clients still honor TTL |
| Load balancing | ALB/NLB across ≥2 subnets in different AZs | Unhealthy targets removed from rotation automatically |
| Compute | Auto Scaling Group spanning AZ subnets | Failed instances replaced; capacity rebalanced across AZs |
| Relational data | RDS Multi-AZ (synchronous standby) | Automatic failover, DNS endpoint repointed; typically 60–120s |
| Object storage | S3 Standard | Redundant across ≥3 AZs by design; no action required |
| Outbound network | One NAT gateway per AZ | A single shared NAT gateway is a single-AZ dependency |

Two details worth internalizing, because both are silent defaults:

- **Cross-zone load balancing** is always on for ALB. For NLB it is **off by default**, so
  each node distributes only to targets in its own AZ — uneven target counts per AZ then
  produce uneven load.
- **RDS read replicas are not a HA mechanism.** They replicate asynchronously and do not
  fail over automatically. Multi-AZ is the availability feature; read replicas are a
  read-scaling feature. They solve different problems and are often confused.

## Best Practices

- Place every tier in **at least two AZs**, and use **three** for quorum-based systems
  (etcd, ZooKeeper, Aurora, and anything electing a leader) so a single AZ loss still
  leaves a majority.
- Give each AZ its **own NAT gateway** and route table. A shared NAT gateway means an AZ
  failure takes out egress for AZs that are otherwise healthy.
- Make the ASG's health check type `ELB`, so the load balancer's view of health — not just
  the EC2 status check — drives instance replacement.
- Point applications at the **RDS endpoint name**, never a resolved address, and keep JVM
  or driver-level DNS caching short so a failover is actually followed.
- Use **Route 53 alias records with `evaluate_target_health`** for ELB and CloudFront
  targets rather than health-checking them separately.
- Keep DNS **TTLs low (60s or less)** on records used for failover; a 3600s TTL turns a
  30-second failover into an hour-long outage for cached clients.
- Handle **AZ-scoped storage** explicitly: an EBS volume lives in one AZ and cannot be
  attached across AZs. Shared state belongs in EFS, S3, or a managed database.
- Test failover deliberately — reboot RDS with failover, drain an AZ's targets — rather
  than discovering the behavior during an incident.

## Examples

**Good Example** — every layer spans AZs, including egress

```hcl
# One private subnet, one NAT gateway, and one route table per AZ.
# A shared NAT gateway would make AZ-b's egress depend on AZ-a staying up.
resource "aws_nat_gateway" "per_az" {
  for_each      = aws_subnet.public          # keyed by AZ
  allocation_id = aws_eip.nat[each.key].id
  subnet_id     = each.value.id
}

resource "aws_lb" "app" {
  load_balancer_type = "application"
  subnets            = [for s in aws_subnet.public : s.id]  # ≥2 AZs
}

resource "aws_lb_target_group" "app" {
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/healthz"   # checks the DB and cache it needs, not just liveness
    interval            = 10
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2            # removes a bad target within ~20s
  }

  deregistration_delay = 30            # drain in-flight requests before removing a target
}

resource "aws_db_instance" "app" {
  identifier           = "app-prod"
  multi_az             = true          # synchronous standby in a second AZ
  backup_retention_period = 7          # PITR window; Multi-AZ is not a backup
  deletion_protection  = true
}

# Capacity sized so one AZ can be lost without overload:
# 4 instances across 2 AZs, steady-state load fits in 2.
resource "aws_autoscaling_group" "app" {
  min_size            = 4
  max_size            = 12
  vpc_zone_identifier = [for s in aws_subnet.private : s.id]
  target_group_arns   = [aws_lb_target_group.app.arn]
  health_check_type   = "ELB"
}
```

**Bad Example** — Multi-AZ on paper, single-AZ in practice

```hcl
resource "aws_lb" "app" {
  load_balancer_type = "application"
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]  # looks redundant
}

# ...but everything behind it depends on AZ-a:
resource "aws_nat_gateway" "single" {
  subnet_id = aws_subnet.public_a.id   # AZ-a dies → AZ-b instances lose all egress
}

resource "aws_db_instance" "app" {
  multi_az = false                     # a single instance; recovery means restoring a snapshot
}

resource "aws_lb_target_group" "app" {
  health_check {
    path     = "/"                     # static page: returns 200 while the DB is unreachable
    interval = 30
    unhealthy_threshold = 5            # 150s of traffic into a dead target before removal
  }
}

resource "aws_autoscaling_group" "app" {
  min_size = 2                         # one instance per AZ, both at 90% CPU
  max_size = 2                         # losing one AZ halves capacity with no room to recover
}
```

The second configuration passes a review that only asks "is it in two AZs?" It fails the
question that matters: *what still works when AZ-a is gone?*

## Disaster Recovery Strategies

Multi-AZ protects against losing a facility. Region-level events, accidental deletion, and
data corruption need a DR strategy, and AWS classifies them by cost and recovery speed:

| Strategy | RTO / RPO | What runs in the second Region | Cost |
|---|---|---|---|
| Backup & Restore | Hours / hours | Nothing; restore from backups | Lowest |
| Pilot Light | Tens of minutes / minutes | Data replicated, servers off | Low |
| Warm Standby | Minutes / seconds | Scaled-down but live copy | Medium |
| Multi-Site Active/Active | Near zero / near zero | Full capacity serving traffic | Highest |

Choose by the objectives the business will fund, not by ambition. Multi-Region
active/active also imposes real design constraints — cross-Region write conflicts,
replication lag, and doubled operational surface — so it is the right answer far less often
than it is proposed. For most workloads Multi-AZ plus tested backups is the correct
stopping point.

For managed cross-Region replication, the usual building blocks are Aurora Global Database
(sub-second replication with a promotable secondary), DynamoDB Global Tables (multi-Region
multi-active), and S3 Cross-Region Replication.

## Common Mistakes

- Counting subnets instead of counting **surviving capacity** — redundant AZs each running
  at full utilization fail together.
- A **single NAT gateway**, single bastion, or single-AZ cache silently pinning the whole
  workload to one AZ.
- Treating **read replicas as failover**. They are asynchronous and require manual
  promotion; data written since the last replication is gone.
- **Shallow health checks** (`/` returning a static `200`) that keep broken instances in
  rotation, or **deep checks** so strict that one slow dependency ejects the entire fleet.
- **High DNS TTLs** on failover records, so clients keep resolving to the failed endpoint
  long after the swap.
- Assuming **Multi-AZ is a backup**. It replicates corruption and deletions synchronously;
  only snapshots and point-in-time recovery protect against bad data.
- Failover paths that were **never tested**, so the first execution is during an incident.
- Storing state on **instance storage or a single EBS volume** and calling the tier
  stateless.

## Production Tips

- Run a **game day**: force an RDS failover, deregister an AZ's targets, and confirm the
  system degrades the way the design claims. Measure the actual RTO rather than quoting the
  documented one.
- Alarm on **per-AZ health**: unhealthy host count per AZ, and target count divergence
  between AZs — these surface a degrading AZ before it fails outright.
- Verify that **capacity math survives the loss**: `desired_capacity` must leave enough
  headroom that N-1 AZs carry peak load, not average load.
- Watch **replication lag** on any asynchronous replica; lag is your real RPO, and it grows
  quietly under write pressure.
- Keep the failover path **free of control-plane dependencies** where possible —
  pre-provisioned standby capacity beats "launch new instances during the outage."
- Confirm backups are **restorable**, not merely present. An untested restore is a
  hypothesis, not a recovery plan.

## AI Review Checklist

- Does every tier — including NAT, cache, and bastion — span at least two AZs?
- Is there enough spare capacity that losing one AZ does not overload the survivors?
- Is the database Multi-AZ, and does the application connect via the endpoint name rather
  than a cached address?
- Do health checks exercise the dependencies the request path actually needs?
- Are DNS TTLs on failover records low enough for the intended RTO?
- Are read replicas being relied on for availability when Multi-AZ is what is required?
- Are RTO and RPO written down, and does the chosen DR strategy match them?
- Has the failover been tested, with the measured recovery time recorded?

## Related

- `knowledge/aws/01-global-infrastructure.md`
- `knowledge/aws/06-vpc.md`
- `knowledge/aws/07-route53.md`
- `knowledge/aws/10-elastic-load-balancer.md`
- `knowledge/aws/11-auto-scaling.md`
- `knowledge/aws/05-rds.md`
- `knowledge/aws/29-well-architected-framework.md`
