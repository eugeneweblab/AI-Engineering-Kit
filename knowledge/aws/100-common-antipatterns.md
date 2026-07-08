---
id: aws/100-common-antipatterns
topic: aws
slug: common-antipatterns
title: "Common Antipatterns"
type: doc
order: 100
status: ready
tags: [aws, common-antipatterns]
related: [aws/02-iam, aws/04-s3, aws/25-security, aws/24-cost-optimization, aws/30-engineering-principles]
when_to_use: "Read when designing or reviewing AWS infrastructure to recognize and avoid the recurring failure modes."
---
# Common Antipatterns

## Purpose

This document catalogs the AWS mistakes that recur across almost every account. Each entry
names the anti-pattern, explains **why it is wrong** (the concrete failure it causes), and
gives **the fix**. It is a lookup for agents: when you see one of these in a design or diff,
you know the failure mode and the correct alternative without re-deriving it.

## Why It Matters

These anti-patterns share one trait: they all *work*. The app runs, tests pass, and the
demo succeeds — which is exactly why they survive into production. Their cost is paid later
and elsewhere: a breach from an over-permissioned role, a data-loss incident from a
single-AZ database, a five-figure bill from cross-AZ chatter. Recognizing the pattern early
is the cheapest possible fix; every day it lives in production, unwinding it gets harder.

## Anti-Patterns

### 1. The wildcard IAM policy

- **Why it is wrong:** `"Action": "*"` on `"Resource": "*"` grants the whole account. If the
  role is ever assumed by an attacker, a leaked key, or a compromised dependency, it is a
  full takeover — and it passes every test, so nothing flags it. See [IAM](02-iam.md).
- **The fix:** Start from zero and add only the specific actions on specific resource ARNs
  the workload has been observed to need. Use IAM Access Analyzer to generate a
  least-privilege policy from CloudTrail history.

### 2. Long-lived access keys on compute

- **Why it is wrong:** Static keys baked into an AMI, container image, or `~/.aws/credentials`
  are the most-leaked secret in existence; they do not rotate and outlive the person who
  created them.
- **The fix:** Attach an IAM role to the EC2 instance, Lambda, ECS task, or CI job. The
  workload receives short-lived, auto-rotated STS credentials with no secret to leak.

### 3. Security group open to `0.0.0.0/0`

- **Why it is wrong:** SSH (22), RDP (3389), or a database port exposed to the entire
  internet is scanned and brute-forced within minutes of launch.
- **The fix:** Restrict ingress to a known CIDR or another security group. Reach instances
  through SSM Session Manager or a bastion, and keep databases in private subnets with no
  public route.

### 4. Public S3 bucket by accident

- **Why it is wrong:** A bucket with public access is the classic data-leak headline —
  customer data indexed by search engines. It usually happens by copying a permissive policy,
  not by intent. See [S3](04-s3.md).
- **The fix:** Leave **Block Public Access** on at the account and bucket level. Serve public
  content through CloudFront with an Origin Access Control, keeping the bucket private.

### 5. Single-AZ everything

- **Why it is wrong:** One Availability Zone is one failure domain. A single-AZ database or
  instance means routine AWS maintenance or an AZ incident is a full outage — and data loss
  if it is your only copy.
- **The fix:** Span at least two AZs. Run databases Multi-AZ, put instances behind a
  load balancer across subnets in different AZs, and store durable data in S3 (multi-AZ by
  design).

### 6. State on compute

- **Why it is wrong:** Writing sessions, uploads, or locks to an instance's local disk means
  no instance is replaceable — scaling out breaks correctness and replacing an instance
  loses data.
- **The fix:** Keep compute stateless. Push session and cache to ElastiCache/DynamoDB, files
  to S3, and data to a managed database. Any instance can then serve any request.

### 7. Console-driven infrastructure ("ClickOps")

- **Why it is wrong:** Changes made in the console are invisible, unreviewable, and
  reproducible only by whoever remembers them. Drift accumulates until no code describes
  reality and disaster recovery is impossible.
- **The fix:** Define everything in Terraform, CDK, or CloudFormation. Gate changes through
  CI with `plan`/diff review. Detect drift on a schedule and treat it as a defect.

### 8. Secrets in code or environment variables

- **Why it is wrong:** Credentials in source control leak the moment the repo is shared or
  the image layer is pulled; plaintext env vars appear in logs and process listings.
- **The fix:** Store secrets in [Secrets Manager](16-secrets-manager.md) or SSM Parameter
  Store (SecureString) and fetch them at runtime via the workload's IAM role. Rotate them.

### 9. No cost guardrails

- **Why it is wrong:** Without budgets and anomaly alarms, a runaway Lambda loop, a
  forgotten NAT gateway, or an over-provisioned fleet is discovered only on the monthly
  invoice. See [Cost Optimization](24-cost-optimization.md).
- **The fix:** Set AWS Budgets and cost-anomaly detection *before* launch, right-size from
  measured CloudWatch utilization, and use Savings Plans for steady-state load.

### 10. Cross-AZ / NAT data-transfer sprawl

- **Why it is wrong:** Chatty services placed across AZs, or all egress funneled through a
  single NAT gateway, bill per-GB continuously — a large, silent line item no feature
  justifies.
- **The fix:** Co-locate tightly coupled services, use VPC Gateway/Interface Endpoints to
  reach S3/DynamoDB without NAT, and measure data-transfer paths during design.

### 11. Logging and audit turned off (or disable-able)

- **Why it is wrong:** Without CloudTrail and VPC Flow Logs you cannot investigate an
  incident; if a workload role can disable them, a compromise can go dark before you notice.
- **The fix:** Enable CloudTrail org-wide with log-file validation, and use an SCP that
  denies disabling CloudTrail, GuardDuty, and Config for everyone. See [Security](25-security.md).

### 12. Over-provisioning "to be safe"

- **Why it is wrong:** Fixed, oversized instances pay for idle capacity every hour and still
  fail to absorb a spike beyond their fixed ceiling — you get the worst of both.
- **The fix:** Right-size to measured load and let Auto Scaling (or serverless concurrency)
  track demand, so capacity follows traffic instead of a guess.

## AI Review Checklist

- Does any IAM policy, trust policy, or KMS key policy use a bare `"*"`?
- Are there static access keys anywhere a role could be used instead?
- Is any security group or S3 bucket exposed to the public without explicit justification?
- Is every stateful workload multi-AZ with backups, and is compute stateless?
- Is the change in infrastructure-as-code, with secrets externalized and cost guardrails in place?
- Can audit logging be disabled by a workload, and are budget/anomaly alarms configured?

## Related

- `knowledge/aws/02-iam.md`
- `knowledge/aws/04-s3.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/24-cost-optimization.md`
- `knowledge/aws/30-engineering-principles.md`
