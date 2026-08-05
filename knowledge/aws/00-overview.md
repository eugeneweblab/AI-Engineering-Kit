---
id: aws/00-overview
topic: aws
slug: overview
title: "AWS Overview"
type: doc
order: 0
status: ready
tags: [aws, overview]
related: [aws/02-iam, aws/01-global-infrastructure, aws/29-well-architected-framework, aws/25-security, aws/100-common-antipatterns]
when_to_use: "Read first when starting any AWS work, to orient on which doc covers your task."
---
# AWS Overview

## Purpose

This document is the map for the `aws` topic. It orients an agent building or reviewing
infrastructure on Amazon Web Services: where each concept lives, how the docs connect, and
the non-negotiable rules that apply across every service. Read it first, then jump to the
specific service doc for the task at hand.

The goal of this topic is narrow and practical: help an agent provision AWS resources that
are **secure by default, least-privilege, cost-aware, and reproducible from code** — not
click-configured in the console.

## Why It Matters

AWS defaults optimize for "it works," not "it is safe." A resource created with the console
wizard or a copied snippet is frequently public, over-permissioned, unencrypted, or
un-tagged. Those mistakes do not fail loudly — the app runs fine while an S3 bucket leaks
data or an over-broad IAM role waits to be abused. Because a single misconfiguration can
expose every customer record at once, AWS work is held to the same bar as security code:
assume the default is wrong until you have verified otherwise.

## Core Principles

- **Everything is infrastructure-as-code.** Provision through Terraform, CDK, or
  CloudFormation, never by hand in the console. Console changes are invisible, unreviewable,
  and lost on the next deploy.
- **Least privilege, always.** Every identity, role, and security group grants the minimum
  it needs. `*` in an IAM action or resource is a red flag, not a shortcut.
- **Encrypt everywhere.** Data at rest and in transit is encrypted by default; there is no
  cost or latency reason left to skip it.
- **Tag and budget from day one.** Untagged resources cannot be attributed, secured, or
  cleaned up. Cost is a design constraint, not an afterthought.
- **Design for failure.** Single instances, single AZs, and single points of failure are
  outages waiting to happen. Spread across Availability Zones.

## How the Docs Fit Together

- **Foundations** — [Global Infrastructure](01-global-infrastructure.md) explains Regions
  and Availability Zones, the substrate every other service sits on.
- **Identity** — [IAM](02-iam.md) is the control plane for *who can do what*. Nearly every
  other doc depends on it; read it early.
- **Compute** — [EC2](03-ec2.md) for virtual machines,
  [Lambda](12-lambda.md) for functions, [ECS](18-ecs.md)/[EKS](19-eks.md) for containers,
  fronted by [Auto Scaling](11-auto-scaling.md) and
  [Elastic Load Balancer](10-elastic-load-balancer.md).
- **Storage & data** — [S3](04-s3.md) for objects, [RDS](05-rds.md) for relational
  databases.
- **Networking** — [VPC](06-vpc.md), [Route 53](07-route53.md),
  [CloudFront](08-cloudfront.md), and [ACM](09-acm.md) for certificates.
- **Operations** — [CloudWatch](14-cloudwatch.md) and [CloudTrail](15-cloudtrail.md) for
  observability and audit; [Secrets Manager](16-secrets-manager.md) and
  [Parameter Store](17-parameter-store.md) for configuration.
- **Cross-cutting guidance** — [Security](25-security.md),
  [Cost Optimization](24-cost-optimization.md),
  [Well-Architected Framework](29-well-architected-framework.md),
  [Best Practices](28-best-practices.md), and the
  [Common Anti-patterns](100-common-antipatterns.md) catalog.

## Best Practices

- Start any task by reading the relevant service doc *and* [IAM](02-iam.md); permissions are
  the most common source of both failures and vulnerabilities.
- Prefer managed services (RDS, Lambda, ECS Fargate) over self-managed equivalents on EC2
  unless there is a concrete reason; managed services remove patching and failover toil.
- Keep environments (dev/staging/prod) in separate accounts, wired together with AWS
  Organizations, so a mistake in one cannot reach another.
- Before merging any AWS change, run the [AI Review Checklist](99-ai-review-checklist.md).

## Common Mistakes

- Configuring resources in the console, then wondering why the next Terraform apply reverts
  them — the console is not the source of truth.
- Reaching for the AWS root account for daily work; it should be locked away with MFA and
  used almost never.
- Treating cost and tagging as "later" problems, then being unable to explain a bill.
- Deploying to a single Availability Zone because it is simpler, then taking an outage when
  that AZ degrades.

## AI Review Checklist

- Is the change expressed as infrastructure-as-code, not a console action?
- Does every new identity and network rule follow least privilege?
- Is data encrypted at rest and in transit?
- Are resources tagged with owner, environment, and cost center?
- Is the workload spread across at least two Availability Zones where it matters?
- Did you consult the specific service doc rather than guessing at API shapes?

## Related

- `knowledge/aws/02-iam.md`
- `knowledge/aws/01-global-infrastructure.md`
- `knowledge/aws/29-well-architected-framework.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/100-common-antipatterns.md`
