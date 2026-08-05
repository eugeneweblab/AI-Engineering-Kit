---
id: aws/24-cost-optimization
topic: aws
slug: cost-optimization
title: "Cost Optimization"
type: doc
order: 24
status: ready
tags: [aws, cost-optimization, arm64]
related: [aws/11-auto-scaling, aws/12-lambda, aws/14-cloudwatch, aws/28-best-practices, aws/29-well-architected-framework]
when_to_use: "Read before provisioning AWS resources, choosing instance types, or reviewing a bill that is growing faster than traffic."
---
# Cost Optimization

## Purpose

This document defines how to build AWS workloads that cost the minimum required to
meet their performance and reliability targets — and no more. It is written so an agent
can size resources, pick pricing models, and review infrastructure code without leaving
money on the table or, worse, hard-capping a system that needs to scale.

Cost is an architectural property, not an afterthought. The cheapest bill comes from
provisioning what the workload actually needs, turning off what it does not, and letting
AWS bill you per-use where the usage is spiky. Optimizing cost is the fifth pillar of the
[Well-Architected Framework](29-well-architected-framework.md).

## Why It Matters

AWS bills for provisioned capacity whether or not you use it. An idle `r6i.4xlarge`, a
forgotten NAT Gateway, or 40 TB of unqueried logs cost the same as a busy one. These
charges are silent — nothing breaks, no alert fires, the number just climbs. By the time
finance notices, months of waste are already spent. Unlike a code bug, over-spend has no
stack trace; the only way to catch it is to design for cost up front and measure
continuously. The inverse failure is just as real: aggressive cost-cutting that removes
Multi-AZ, backups, or headroom trades a predictable bill for an unpredictable outage.

## Core Principles

- **Pay for value, not for uptime.** Prefer serverless and managed services that bill
  per-request (Lambda, Fargate, S3, DynamoDB on-demand) for spiky or low-volume
  workloads. The cost is higher per unit but zero when idle.
- **Right-size from data, never from a guess.** Size instances and memory from observed
  CloudWatch utilization, not from a round number that "feels safe."
- **Commit to steady state, stay elastic for the peak.** Cover the always-on baseline
  with Savings Plans or Reserved Instances; absorb bursts with on-demand and Spot.
- **Delete is the cheapest optimization.** Unattached EBS volumes, idle load balancers,
  old snapshots, and orphaned Elastic IPs cost money for zero value.
- **Attribute every dollar.** Tag every resource so spend maps to a team, environment,
  and service. You cannot optimize what you cannot attribute.

## Best Practices

- Enable **Cost Explorer**, **AWS Budgets** with alert thresholds, and Cost Anomaly
  Detection on day one. A budget that emails at 80% of forecast catches runaway spend
  before the invoice does.
- Buy **Compute Savings Plans** for baseline EC2/Fargate/Lambda usage — up to ~66% off
  on-demand for a 1- or 3-year commit. They apply across instance families and regions,
  so they survive re-architecture that Reserved Instances do not.
- Run fault-tolerant, interruptible work (batch, CI, stateless web tiers behind an ASG)
  on **Spot** for up to 90% off; always mix Spot with on-demand in the capacity provider
  so a Spot reclamation cannot take the whole fleet.
- Move S3 data through **lifecycle policies**: Standard → Standard-IA after 30 days →
  Glacier/Deep Archive for cold data, and expire logs on a fixed schedule. Enable
  S3 Intelligent-Tiering when access patterns are unknown.
- Use current-generation Graviton (ARM) instances (`m7g`, `r7g`, Lambda `arm64`) — they
  are typically ~20% cheaper per unit of performance than x86 equivalents.
- Set **log retention** on every CloudWatch Log Group. The default is "never expire,"
  which turns logs into a permanent, growing line item.
- Delete the NAT Gateway if private subnets only need AWS APIs — use **VPC Gateway/
  Interface Endpoints** instead, which avoid per-GB data-processing charges.

## Examples

**Good Example** — a right-sized ASG with explicit retention and a mixed capacity policy

```hcl
# Baseline on Savings-Plan-covered on-demand, burst on Spot; instances sized from data.
resource "aws_autoscaling_group" "web" {
  min_size = 2                 # covers the measured baseline, not a guess
  max_size = 20                # real headroom so scaling is never capped by cost fear

  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 2   # steady state never runs on Spot
      on_demand_percentage_above_base_capacity = 20  # 80% of the burst is cheap Spot
    }
    launch_template {
      launch_template_specification { launch_template_id = aws_launch_template.web.id }
      override { instance_type = "m7g.large" }        # Graviton: ~20% cheaper per perf
      override { instance_type = "m7g.xlarge" }       # diversify so Spot pools stay deep
    }
  }
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/app/web"
  retention_in_days = 30       # logs expire; without this they bill forever
}
```

**Bad Example** — oversized, never-off, un-attributed

```hcl
resource "aws_instance" "web" {
  instance_type = "r6i.4xlarge"  # 128 GB RAM "to be safe" for a 2 GB app — 30x waste
  # no ASG: runs 24/7 even though traffic is 9-5, no Spot, no scale-to-zero
  # no tags: this cost can never be attributed to a team or shut off with confidence
}
# No Budget, no anomaly alert: the first signal of waste is next month's invoice.
```

## Common Mistakes

- Sizing instances by intuition instead of CloudWatch utilization, then never revisiting.
- Leaving CloudWatch Log Groups and CloudTrail with infinite retention.
- Running dev/staging 24/7 when it is only used during business hours (schedule stop/start).
- Forgetting NAT Gateway data-processing charges for high-egress private workloads.
- Buying Reserved Instances for a family you re-architect away from; Savings Plans flex.
- Orphaned resources: unattached EBS, idle ELBs, old snapshots, unassociated Elastic IPs.
- Treating cost-cutting as license to remove Multi-AZ or backups — that is a reliability
  cut disguised as a cost cut.

## Production Tips

- Put a **Budget alert** and Cost Anomaly Detection on every account; route to Slack/PagerDuty.
- Enforce a tagging policy with **AWS Config** or SCPs so untagged resources are flagged
  or blocked at creation, not audited later.
- Review the **Trusted Advisor** and **Compute Optimizer** recommendations monthly — they
  surface idle and over-provisioned resources automatically.
- Schedule non-production environments to stop nightly and on weekends; this alone often
  cuts a dev bill by 60-70%.

## AI Review Checklist

- Are instance sizes and Lambda memory justified by observed utilization, not guesses?
- Does every resource carry team/environment/service tags?
- Is the always-on baseline covered by a Savings Plan, and bursts by Spot/on-demand?
- Does every CloudWatch Log Group and log bucket have a finite retention/lifecycle policy?
- Are there Budgets and anomaly alerts wired to a human before the invoice arrives?
- Was any proposed cost cut checked against reliability (Multi-AZ, backups, headroom)?

## Related

- `knowledge/aws/11-auto-scaling.md`
- `knowledge/aws/12-lambda.md`
- `knowledge/aws/14-cloudwatch.md`
- `knowledge/aws/28-best-practices.md`
- `knowledge/aws/29-well-architected-framework.md`
