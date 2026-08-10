---
id: aws/98-production-checklist
topic: aws
slug: production-checklist
title: "AWS Production Checklist"
type: checklist
order: 98
status: ready
tags: [aws, production-checklist, Resource, Action, go-live, signing, off]
related: [aws/27-production, aws/29-well-architected-framework, aws/25-security, aws/26-monitoring, aws/24-cost-optimization]
when_to_use: "Read before promoting any AWS workload to production or signing off a go-live."
---
# AWS Production Checklist

## Purpose

This is a verifiable, pre-launch checklist for AWS workloads. Every item is a yes/no
question an agent can confirm against real infrastructure — not advice to consider. If an
item is unchecked, the workload is not production-ready. It complements the
[Production](27-production.md) and [Well-Architected](29-well-architected-framework.md)
docs by turning their guidance into a gate.

## Why It Matters

The gap between "works in staging" and "survives production" is a specific set of controls
that are easy to skip because their absence is invisible until the worst moment: no
backups until data is lost, no multi-AZ until an AZ fails, no budget alarm until the bill
arrives. A checklist forces each control to be confirmed *before* it is needed, when fixing
it is cheap. Treat an unchecked box as a launch blocker, not a follow-up ticket.

## Identity & Access

**Rules:** [IAM](02-iam.md)

- [ ] Every workload uses an **IAM role**; there are no static access keys in AMIs, images, or env files.
- [ ] Policies are scoped to specific actions and resource ARNs — no bare `"*"` on `Action` or `Resource`.
- [ ] The **root account** has MFA, no active access keys, and is not used for daily work.
- [ ] MFA is enforced for all human principals (via IAM Identity Center / SSO).
- [ ] Service Control Policies and permission boundaries cap what accounts and delegated admins can do.

## Network & Perimeter

**Rules:** [VPC](06-vpc.md) · [Elastic Load Balancer](10-elastic-load-balancer.md)

- [ ] Resources live in **private subnets**; only load balancers and bastions sit in public subnets.
- [ ] Security groups allow only required ports from required sources — no `0.0.0.0/0` on SSH/RDP/databases.
- [ ] TLS terminates at the ALB/CloudFront with a valid [ACM](09-acm.md) certificate; HTTP redirects to HTTPS.
- [ ] WAF and/or Shield protect internet-facing endpoints against common and volumetric attacks.
- [ ] VPC Flow Logs are enabled for network-level audit and incident forensics.

## Data & Encryption

**Rules:** [S3](04-s3.md) · [ACM](09-acm.md)

- [ ] Encryption at rest is on (KMS) for RDS, EBS, [S3](04-s3.md), and any snapshots/backups.
- [ ] Encryption in transit (TLS) is enforced end to end, including between services.
- [ ] S3 buckets **block public access** at the account and bucket level unless public is a deliberate requirement.
- [ ] Automated **backups** are configured with a tested restore, and retention meets the RPO.
- [ ] Point-in-time recovery / snapshots exist for every stateful store, and restore has been rehearsed.

## Resilience & Scaling

**Rules:** [High Availability](31-high-availability.md) · [Auto Scaling](11-auto-scaling.md)

- [ ] The workload spans **at least two Availability Zones**; no single-AZ point of failure.
- [ ] Databases run **Multi-AZ**; read scaling uses replicas, not the primary.
- [ ] Auto Scaling (or serverless concurrency) tracks demand, with sane min/max bounds.
- [ ] Health checks and load-balancer target draining are configured for zero-downtime deploys.
- [ ] Service quotas (Lambda concurrency, EIPs, ENIs) are checked against expected peak load.

## Observability

**Rules:** [CloudWatch](14-cloudwatch.md) · [Monitoring](26-monitoring.md)

- [ ] Metrics, logs, and traces flow to [CloudWatch](14-cloudwatch.md) / X-Ray from every component.
- [ ] Alarms exist for error rate, latency, saturation, and health, and they page a real owner.
- [ ] Dashboards cover the golden signals so on-call can triage without spelunking.
- [ ] [CloudTrail](15-cloudtrail.md) is enabled org-wide, log-file validation on, and cannot be disabled by a workload role.
- [ ] Log retention and a sink (S3/OpenSearch) are set; logs are not defaulting to indefinite CloudWatch cost.

## Deployment & Operations

**Rules:** [Production](27-production.md) · [ECS](18-ecs.md)

- [ ] All infrastructure is defined in **code** (Terraform/CDK/CloudFormation) with no console drift.
- [ ] Deploys run through CI/CD with rollback (or blue-green / canary) and no manual prod changes.
- [ ] Secrets come from [Secrets Manager](16-secrets-manager.md) or Parameter Store — none in code or env vars.
- [ ] Every resource is **tagged** with owner, environment, and cost-center.
- [ ] A runbook exists for the top failure modes, and on-call knows where it is.

## Cost

**Rules:** [Cost Optimization](24-cost-optimization.md)

- [ ] AWS Budgets and cost-anomaly alarms are configured before launch.
- [ ] Instances/functions are right-sized against measured utilization, not guessed.
- [ ] Committed-use discounts (Savings Plans / Reserved) are evaluated for steady-state load.
- [ ] Data-transfer paths (cross-AZ, NAT, cross-Region) are reviewed for avoidable egress cost.
- [ ] Non-production environments have a shutdown or scale-to-zero schedule.

## AI Review Checklist

- [ ] Is every box above either checked or explicitly waived with a documented reason?
- [ ] Do the Identity, Network, and Data sections all pass, given they are the highest-blast-radius controls?
- [ ] Has a backup restore actually been tested end to end, not just configured?
- [ ] Is the workload multi-AZ, and does an AZ-loss game-day confirm it?
- [ ] Are alarms proven to page a real on-call human, not a dead inbox?

## Related

- `knowledge/aws/27-production.md`
- `knowledge/aws/29-well-architected-framework.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/26-monitoring.md`
- `knowledge/aws/24-cost-optimization.md`
