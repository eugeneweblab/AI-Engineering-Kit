---
id: architecture/22-cloud-architecture
topic: architecture
slug: cloud-architecture
title: "Cloud Architecture"
type: doc
order: 22
status: ready
tags: [architecture, cloud-architecture]
related: [architecture/23-infrastructure, architecture/16-high-availability, architecture/13-scalability, architecture/15-security, architecture/24-deployment]
when_to_use: "Read before choosing cloud services for a workload, or when designing for scale, cost, resilience, or multi-region on a cloud provider."
---
# Cloud Architecture

## Purpose

This document defines how to design systems that run on cloud platforms: choosing managed
services, designing for elasticity and failure, and controlling cost. It is written so an agent
can make cloud design decisions that are resilient and economical rather than merely functional.

The cloud is not "someone else's computer" — it is a set of building blocks with different
reliability, scaling, and pricing characteristics than a datacenter. Designing well means
matching each workload to the right primitive and treating the provider's own failure domains
(zones, regions, quotas) as first-class inputs, not afterthoughts.

## Why It Matters

In the cloud, architecture decisions have a direct, metered price and a direct blast radius.
Pin everything to one availability zone and a routine zone outage takes you down; spread across
zones needlessly and you pay for cross-zone traffic you did not need. An unbounded autoscaler
plus a retry storm can turn a traffic spike into a five-figure bill overnight. The platform
gives you elasticity and managed resilience, but only if you design for them — the defaults
optimize for getting started, not for production. Getting the failure domains and the cost model
right is as much a part of correctness here as the code.

## Core Principles

- **Design for failure; the cloud will fail parts of itself.** Instances are cattle, not pets.
  Assume any single instance, and occasionally a whole zone, disappears. Spread across
  availability zones and make instances stateless and replaceable.
- **Prefer managed services over self-hosting undifferentiated infrastructure.** Let the
  provider run the database, queue, and load balancer unless you have a concrete reason not to.
  The reason is operational leverage, and the cost is some lock-in — weigh it deliberately.
- **Cost is an architectural constraint.** Egress, cross-zone traffic, idle provisioned
  capacity, and per-request pricing shape the design. A choice that is 10x slower to code but
  10x cheaper to run is often the right one.
- **Scale horizontally and statelessly.** Push session and state to a shared store so any node
  can serve any request and autoscaling can add or remove nodes freely.
- **Right-size the elasticity.** Match the compute model — serverless, containers, or VMs — to
  the load shape (spiky, steady, or batch). The wrong model overpays or falls over.

## Best Practices

- Deploy across at least **three availability zones** for anything that must stay up, behind a
  load balancer with health checks. Reserve multi-*region* for true DR/latency needs — it
  multiplies cost and complexity.
- Keep compute **stateless**; store state in managed, replicated services (object storage,
  managed DB, distributed cache). Never store durable data on an instance's local disk.
- Set **autoscaling with an upper bound** and pair it with per-dependency rate limits, so a
  spike (or a retry storm) cannot scale into a runaway bill or overwhelm the database.
- Use IAM with **least privilege**: scoped roles per service, no long-lived static keys, secrets
  in a managed secrets store. Over-broad roles are the most common cloud breach vector.
- Provision everything as **infrastructure as code** (Terraform/Pulumi/CDK). Click-ops
  environments are unreproducible and drift; see infrastructure for the discipline.
- Tag resources by owner, environment, and cost center, and set budgets and alerts. Untagged,
  unmonitored resources are how cloud bills surprise teams.
- Choose the compute model by workload: serverless for spiky/event-driven, containers for
  steady services, managed batch for jobs. Do not run a 24/7 service on per-invocation pricing.

## Examples

**Good Example** — multi-AZ, stateless, bounded, least-privilege (Terraform sketch)

```hcl
# Stateless app across 3 AZs; state lives in a managed, replicated DB, not on disk.
resource "aws_autoscaling_group" "app" {
  min_size            = 3
  max_size            = 12                      # bounded: a spike can't scale into a runaway bill
  vpc_zone_identifier = var.private_subnet_ids  # one subnet per AZ -> survives a zone outage
  health_check_type   = "ELB"                   # LB evicts unhealthy instances automatically
}

resource "aws_iam_role_policy" "app" {
  # Least privilege: read one bucket, nothing else. No wildcard "*".
  policy = jsonencode({ Statement = [{
    Effect = "Allow", Action = ["s3:GetObject"], Resource = "${var.assets_bucket_arn}/*"
  }]})
}
```

**Bad Example** — single AZ, stateful, unbounded, over-privileged

```hcl
resource "aws_instance" "app" {
  availability_zone = "us-east-1a"     # single AZ -> one zone outage = full outage
  # app writes user uploads to the local disk -> data lost when the instance is replaced
}

resource "aws_iam_role_policy" "app" {
  policy = jsonencode({ Statement = [{
    Effect = "Allow", Action = "*", Resource = "*"   # god-mode role: one leak = full breach
  }]})
}
# autoscaling with no max_size -> a retry storm scales to a five-figure bill overnight
```

## Common Mistakes

- Pinning a service to a single availability zone, so a routine zone failure is a full outage.
- Storing durable state on instance local disk, losing it when the instance is replaced.
- Autoscaling with no upper bound, letting a spike or retry storm run up the bill.
- Over-broad IAM roles and long-lived static access keys instead of scoped, short-lived credentials.
- Ignoring data egress and cross-zone transfer costs until the invoice arrives.
- Running steady 24/7 workloads on per-invocation serverless pricing (or spiky ones on always-on VMs).
- Manually clicking infrastructure into existence, producing environments no one can reproduce.

## Production Tips

- Set cost budgets with alerts *before* launch, and review the bill by tag weekly; cost is a
  reliability signal — a sudden jump often means a bug (a retry loop, a leak).
- Test zone failure in a game day: terminate a zone's instances and confirm the system holds.
- Use reserved/committed capacity for the steady baseline and on-demand/spot for the peak.
- Track service quotas; hitting an account limit mid-incident blocks the very scaling you need.

## AI Review Checklist

- Is the workload spread across multiple availability zones behind health-checked load balancing?
- Is compute stateless, with all durable state in managed, replicated services?
- Does autoscaling have an upper bound and per-dependency rate limits?
- Are IAM roles least-privilege and short-lived, with no wildcard actions or static keys?
- Is the compute model (serverless/containers/VMs) matched to the load shape and cost?
- Is all infrastructure defined as code, tagged, and covered by budget alerts?
- Are egress and cross-zone costs accounted for in the design?

## Related

- `knowledge/architecture/23-infrastructure.md`
- `knowledge/architecture/16-high-availability.md`
- `knowledge/architecture/13-scalability.md`
- `knowledge/architecture/15-security.md`
- `knowledge/architecture/24-deployment.md`
