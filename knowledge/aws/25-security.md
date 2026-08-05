---
id: aws/25-security
topic: aws
slug: security
title: "AWS Security"
type: doc
order: 25
status: ready
tags: [aws, security]
related: [aws/02-iam, aws/06-vpc, aws/15-cloudtrail, aws/16-secrets-manager, aws/29-well-architected-framework]
when_to_use: "Read before granting permissions, opening a security group, storing a secret, or reviewing any AWS resource that touches data or the network."
---
# AWS Security

## Purpose

This document defines how to secure AWS workloads at the account, identity, network, and
data layers. It is written so an agent can provision resources or review infrastructure
code without leaving an open door: a public bucket, a wildcard IAM policy, an unencrypted
volume, or a hard-coded key.

AWS operates on a **shared responsibility model**: AWS secures the cloud (hardware,
hypervisor, managed-service internals); you secure everything *in* the cloud (identities,
configuration, data, network rules). Most breaches are customer misconfiguration, not an
AWS failure. This is the security pillar of the
[Well-Architected Framework](29-well-architected-framework.md).

## Why It Matters

A single over-broad IAM policy or a bucket set to public can expose an entire company's
data, and the mistake is invisible while it works — the app serves traffic exactly as
designed while an attacker exfiltrates data. Cloud misconfiguration has no compile error
and no crash; the only defenses are least privilege, encryption by default, and
continuous detection. Because AWS credentials grant programmatic control over the whole
account, a leaked key is not one compromised request — it is potential control of every
resource you own.

## Core Principles

- **Least privilege, always.** Grant the narrowest set of actions on the narrowest set of
  resources that the task requires. `Action: "*"` and `Resource: "*"` together are a
  standing invitation.
- **No long-lived credentials in code.** Use IAM **roles** (instance profiles, IRSA,
  Lambda execution roles) so AWS rotates short-lived credentials for you. Never commit an
  access key.
- **Encrypt everything, in transit and at rest.** TLS on every endpoint; KMS encryption on
  every volume, bucket, database, and queue. It is nearly free and default-on.
- **Private by default.** Resources live in private subnets with no public IP unless there
  is a specific, reviewed reason to expose them.
- **Assume breach; make it auditable and recoverable.** CloudTrail on everywhere, GuardDuty
  watching, and a tested path to rotate credentials and restore data.

## Best Practices

- Give humans federated SSO (**IAM Identity Center**) with MFA, not IAM users. Give
  workloads **roles**, not access keys. Reserve the root user for the handful of tasks
  that require it, with hardware MFA, and never use it day-to-day.
- Scope IAM policies to specific actions and resource ARNs; add `Condition` keys (source
  VPC, MFA present, IP range) to tighten further. Prefer AWS-managed job-function
  policies over inline wildcards.
- Store secrets in **Secrets Manager** or **Parameter Store (SecureString)**, fetched at
  runtime via the execution role — never in environment variables baked into an image or
  in the repo.
- Enable **encryption by default**: EBS default encryption on, S3 buckets with SSE-KMS and
  Block Public Access at the account level, RDS/DynamoDB/SQS encryption on.
- Security groups are **allow-only**; open the minimum ports to the minimum sources.
  Reference other security groups instead of `0.0.0.0/0`. Put admin access behind SSM
  Session Manager, not a public SSH port.
- Turn on the detection baseline in every account: **CloudTrail** (multi-region),
  **GuardDuty**, **AWS Config**, and **Security Hub**. Enforce guardrails org-wide with
  **Service Control Policies**.
- Use **KMS** customer-managed keys for sensitive data so you control key policy and can
  audit and revoke access independently of the resource.

## Examples

**Good Example** — scoped role, encryption, no static keys

```hcl
# Lambda assumes a role scoped to ONE bucket prefix and ONE action — least privilege.
data "aws_iam_policy_document" "reports_ro" {
  statement {
    actions   = ["s3:GetObject"]                       # only what the function needs
    resources = ["${aws_s3_bucket.reports.arn}/tenant-a/*"]  # exact prefix, not the bucket
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["true"]                              # deny any non-TLS request
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id
  rule { apply_server_side_encryption_by_default { sse_algorithm = "aws:kms" } }
}
# The function reads S3 via its execution role — no access key exists to leak.
```

**Bad Example** — wildcard policy, public bucket, hard-coded key

```hcl
resource "aws_iam_role_policy" "app" {
  role   = aws_iam_role.app.id
  policy = jsonencode({
    Statement = [{ Effect = "Allow", Action = "*", Resource = "*" }]  # admin to everything
  })
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = false   # bucket can be made world-readable by an ACL
  restrict_public_buckets = false
}

resource "aws_instance" "app" {
  user_data = "export AWS_ACCESS_KEY_ID=AKIA...; export AWS_SECRET_ACCESS_KEY=..."  # leaked key
}
```

## Common Mistakes

- `Action: "*"` / `Resource: "*"` policies — the number one cloud misconfiguration.
- Storing access keys in code, CI variables, AMIs, or environment variables.
- S3 buckets without account-level Block Public Access, or with public ACLs enabled.
- Security groups open to `0.0.0.0/0` on SSH (22), RDP (3389), or database ports.
- Using the root account or long-lived IAM users for automation instead of roles.
- Disabling or not centralizing CloudTrail, leaving no audit trail after an incident.
- Relying on unencrypted volumes/snapshots because "it is internal only."

## Production Tips

- Alert on IAM policy changes, root-account usage, and GuardDuty findings via EventBridge.
- Rotate secrets automatically with Secrets Manager rotation; test that consumers pick up
  the new value without a deploy.
- Run **IAM Access Analyzer** to find resources shared outside the account and unused
  permissions to trim.
- Keep an **incident runbook**: how to revoke a leaked key, quarantine an instance, and
  restore from immutable backups.

## AI Review Checklist

- Does every IAM policy scope actions and resource ARNs — no `*`/`*` grants?
- Do workloads use roles (instance profile / IRSA / execution role), never static keys?
- Is data encrypted at rest (KMS) and in transit (TLS enforced by policy/condition)?
- Is S3 Block Public Access on account-wide, and are resources in private subnets?
- Are secrets in Secrets Manager/Parameter Store, not in code or env vars?
- Are CloudTrail, GuardDuty, and Config enabled in every account/region?
- Are security groups allow-only, minimal, and free of `0.0.0.0/0` on admin ports?

## Related

- `knowledge/aws/02-iam.md`
- `knowledge/aws/06-vpc.md`
- `knowledge/aws/15-cloudtrail.md`
- `knowledge/aws/16-secrets-manager.md`
- `knowledge/aws/29-well-architected-framework.md`
