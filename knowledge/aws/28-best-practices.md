---
id: aws/28-best-practices
topic: aws
slug: best-practices
title: "AWS Best Practices"
type: doc
order: 28
status: ready
tags: [aws, best-practices]
related: [aws/24-cost-optimization, aws/25-security, aws/26-monitoring, aws/27-production, aws/29-well-architected-framework]
when_to_use: "Read before designing an AWS solution or reviewing infrastructure code, as a cross-cutting checklist of the habits that separate durable systems from demos."
---
# AWS Best Practices

## Purpose

This document collects the cross-cutting habits that apply to nearly every AWS workload,
regardless of which service you reach for. It is the general-practice companion to the
service-specific docs and to the [Well-Architected Framework](29-well-architected-framework.md):
where those go deep on one topic, this gives an agent the short list of defaults to apply
everywhere and the trade-off behind each one.

These are opinionated defaults, not laws. Each one exists because the alternative causes a
recurring, expensive class of failure. Deviate deliberately and with a stated reason —
never by accident.

## Why It Matters

AWS gives you thousands of knobs and almost no guardrails; the console will happily let
you build something insecure, unobservable, un-reproducible, and expensive. The defaults
optimize for "get one thing running," not "run a fleet for five years." Best practices are
the accumulated scar tissue that keeps a system operable as it grows from one service to
fifty and from one engineer to a team. Skipping them is invisible at first and then
suddenly not — the day of the outage, the audit, or the bill review.

## Core Principles

- **Everything is code.** Infrastructure, policies, and pipelines live in version control
  (Terraform/CloudFormation/CDK). If it was clicked in the console, it does not exist to
  review, reproduce, or roll back.
- **Least privilege and private by default.** Start from zero access and open only what is
  needed; keep resources off the public internet unless there is a reviewed reason.
- **Managed over self-hosted.** Prefer the managed service (RDS, SQS, Fargate) over
  running it yourself on EC2 — you buy back patching, HA, and backups. The cost is less
  control; accept it unless you truly need the control.
- **Multi-account isolation.** Separate prod, staging, dev, and security into distinct
  accounts under Organizations. A blast radius that stops at an account boundary is a
  feature.
- **Automate the toil.** Scaling, deploys, patching, backups, and remediation should be
  automatic. Humans are for decisions, not for repetitive, error-prone steps.

## Best Practices

- **Tag everything** with owner, environment, service, and cost-center at creation, and
  enforce it with AWS Config or SCPs. Tags drive cost attribution, automation, and access.
- **Isolate by account and VPC.** Use AWS Organizations with separate accounts per
  environment and SCP guardrails; keep workloads in private subnets behind load balancers
  and endpoints.
- **Pin and version everything**: IaC provider versions, container image digests (not
  `:latest`), and Lambda runtime versions, so a rebuild is deterministic.
- **Right-size and set retention** on every resource: instance/memory from utilization,
  log groups with expiry, S3 lifecycle rules. (See [cost optimization](24-cost-optimization.md).)
- **Encrypt by default and rotate secrets**: KMS at rest, TLS in transit, Secrets Manager
  with rotation. (See [security](25-security.md).)
- **Build for failure and observe it**: ≥2 AZs, health checks, auto scaling, golden-signal
  alarms with runbooks. (See [production](27-production.md) and [monitoring](26-monitoring.md).)
- **Deploy through a pipeline** with automated tests, progressive rollout, and automated
  rollback — never `terraform apply` or a console change straight to prod by hand.

## Examples

**Good Example** — reproducible, tagged, pinned, least-privilege module

```hcl
terraform {
  required_version = "~> 1.9"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.60" } }  # pinned
}

# One place applies mandatory tags to every resource in the stack — cost + ownership.
provider "aws" {
  default_tags {
    tags = { Service = "checkout", Environment = "prod", Owner = "payments", CostCenter = "cc-42" }
  }
}

resource "aws_ecs_service" "checkout" {
  task_definition = aws_ecs_task_definition.checkout.arn  # image referenced by digest, not :latest
  desired_count   = 2                                     # multi-AZ, self-healing
  # execution role scoped to this service's secrets + logs only — least privilege
}
```

**Bad Example** — clicked together, untagged, unpinned, shared account

```hcl
# Provider unpinned: a future `init` silently upgrades and changes behavior.
provider "aws" {}   # no default tags: nothing here can be attributed or governed

resource "aws_ecs_service" "checkout" {
  # runs in the single shared account alongside dev and prod — no blast-radius boundary
  # task uses image tag ":latest" — a rebuild is non-deterministic and un-rollback-able
  desired_count = 1  # single task, single AZ
}
# The load balancer and DNS for this were created by hand in the console — invisible to review.
```

## Common Mistakes

- Console-clicked ("ClickOps") infrastructure that drifts from and outlives the IaC.
- Untagged resources, making cost attribution and automated governance impossible.
- One AWS account for everything, so a dev mistake can take down prod.
- Using `:latest` image tags and unpinned provider versions — non-reproducible builds.
- Reinventing managed services (self-hosting a database on EC2) without a real need.
- Copy-pasting an over-broad IAM policy from a tutorial instead of scoping it.
- Treating best practices as optional for "internal" or "temporary" systems that then persist.

## Production Tips

- Adopt a **landing zone** (Control Tower) so new accounts start with guardrails, logging,
  and SSO already wired.
- Run **policy-as-code** (OPA/Conftest, cfn-guard, `tflint`) in CI to reject non-compliant
  infrastructure before it merges.
- Keep a shared **module library** so teams inherit the good defaults instead of
  re-deriving them per project.

## AI Review Checklist

- Is all infrastructure in version-controlled IaC, with nothing created by hand?
- Does every resource carry owner/environment/service/cost tags?
- Are provider versions and image digests pinned for reproducible builds?
- Are prod/staging/dev isolated by account with SCP guardrails?
- Are the security, cost, monitoring, and production baselines all applied?
- Is a managed service used where one exists, unless a documented reason says otherwise?

## Related

- `knowledge/aws/24-cost-optimization.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/26-monitoring.md`
- `knowledge/aws/27-production.md`
- `knowledge/aws/29-well-architected-framework.md`
