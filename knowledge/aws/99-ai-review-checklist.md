---
id: aws/99-ai-review-checklist
topic: aws
slug: ai-review-checklist
title: "AWS AI Review Checklist"
type: doc
order: 99
status: ready
tags: [aws, ai-review-checklist, "aws:PrincipalOrgID", Condition, timeout]
related: [aws/98-production-checklist, aws/02-iam, aws/25-security, aws/100-common-antipatterns, aws/30-engineering-principles]
when_to_use: "Read when reviewing AWS infrastructure code (Terraform/CDK/CloudFormation) or a proposed AWS change."
---
# AWS AI Review Checklist

## Purpose

This is the checklist an AI agent runs when **reviewing** AWS infrastructure code or a
proposed change — a pull request, a Terraform plan, a CDK diff. Each item is a concrete
thing to look for in the diff and flag if wrong. Where the [production checklist](98-production-checklist.md)
gates a launch, this gates a *change*: it is what to grep for and reason about on every
review, so defects are caught before merge.

## Why It Matters

AWS defects are cheap to write and expensive to run. A single `"Resource": "*"`, a
public S3 bucket, or a security group open to `0.0.0.0/0` passes every functional test and
merges without complaint — the app works, the pipeline is green. The damage is latent and
total: it surfaces as a breach, a leaked dataset, or a runaway bill weeks later. Review is
the last automated point where these are still cheap to fix. Assume the author optimized
for "it works", and check for the failure modes that "working" hides.

## Identity & Permissions

**Rules:** [IAM](02-iam.md)

- [ ] No policy uses `"Action": "*"` or `"Resource": "*"`; each statement is scoped to the minimum.
- [ ] No `*FullAccess` AWS-managed policies are attached where a scoped policy would do.
- [ ] No static access keys or `aws_access_key_id` literals appear in the diff; workloads use roles.
- [ ] Trust policies (`AssumeRole`) name specific principals, not `"AWS": "*"`.
- [ ] New cross-account access is intentional and constrained by `Condition` (e.g. `aws:PrincipalOrgID`).

## Secrets & Configuration

**Rules:** [Secrets Manager](16-secrets-manager.md) · [Parameter Store](17-parameter-store.md)

- [ ] No hardcoded secrets, tokens, passwords, or connection strings — values come from Secrets Manager / SSM.
- [ ] `.tfstate`, `.env`, and credential files are not committed and are gitignored.
- [ ] KMS keys have scoped key policies, not account-wide `kms:*`.
- [ ] Environment-specific values are parameterized, not copy-pasted per environment.

## Network Exposure

**Rules:** [VPC](06-vpc.md) · [Security](25-security.md)

- [ ] No security-group rule opens SSH (22), RDP (3389), or a database port to `0.0.0.0/0`.
- [ ] New resources default to **private** subnets unless public exposure is justified in the change.
- [ ] Load balancers and CloudFront enforce HTTPS; no plaintext listeners are added.
- [ ] S3 buckets keep **Block Public Access** on; any public grant is explicit and reviewed.

## Data Protection

**Rules:** [S3](04-s3.md) · [Security](25-security.md)

- [ ] Encryption at rest is set on new RDS, EBS, S3, and DynamoDB resources (no `encrypted = false`).
- [ ] New stateful resources have backups / point-in-time recovery configured.
- [ ] `deletion_protection` (or equivalent) is on for production databases.
- [ ] No `prevent_destroy = false` or `--force` that could silently drop a stateful resource.

## Resilience & Correctness

**Rules:** [High Availability](31-high-availability.md) · [Auto Scaling](11-auto-scaling.md)

- [ ] Multi-AZ / multi-subnet is preserved; the change does not collapse a workload into one AZ.
- [ ] Lambda functions set a bounded `timeout` and use a current, non-retired runtime.
- [ ] Auto Scaling min/max bounds are sane; nothing is pinned to a single fixed instance where HA is required.
- [ ] Health checks and connection draining are configured for anything behind a load balancer.

## Observability & Cost

**Rules:** [Monitoring](26-monitoring.md) · [Cost Optimization](24-cost-optimization.md)

- [ ] New components emit metrics/logs/traces; alarms exist for the paths they add.
- [ ] Log retention is set (not unbounded), and CloudTrail coverage is not weakened.
- [ ] Instance/function sizing is justified; no obvious over-provisioning.
- [ ] The change does not introduce avoidable cross-AZ or cross-Region data transfer.
- [ ] Every new resource is tagged (owner, environment, cost-center).

## Change Hygiene

**Rules:** [Production](27-production.md) · [Best Practices](28-best-practices.md)

- [ ] The change is in infrastructure-as-code, not a described console action.
- [ ] The `terraform plan` / CDK diff shows only intended changes — no surprise replacements of stateful resources.
- [ ] Destructive actions (replace/delete of data stores) are called out and confirmed intentional.

## Related

- `knowledge/aws/98-production-checklist.md`
- `knowledge/aws/02-iam.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/100-common-antipatterns.md`
- `knowledge/aws/30-engineering-principles.md`
