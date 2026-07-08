---
id: aws/30-engineering-principles
topic: aws
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [aws, engineering-principles]
related: [aws/29-well-architected-framework, aws/02-iam, aws/28-best-practices, aws/24-cost-optimization, aws/25-security]
when_to_use: "Read before designing any new AWS workload or making an architectural decision on AWS."
---
# Engineering Principles

## Purpose

This document defines the durable engineering principles for building on AWS: the
decisions that hold true across services and outlive any specific API. It is the mental
model an agent should apply *before* reaching for a service, so that the resulting
architecture is secure, cost-aware, and operable by default rather than by remediation.

These principles sit above the per-service docs (like [IAM](02-iam.md) or [S3](04-s3.md))
and beneath the formal [Well-Architected Framework](29-well-architected-framework.md).
Use them to make the many small choices no checklist will catch.

## Why It Matters

On AWS every resource is an API call, and every API call is billable, permissioned, and
logged. A design that ignores this produces the classic failure modes: a bill that grows
unbounded, an IAM role that owns the account, a single-AZ database that takes the app down
during routine maintenance. None of these break in a demo — they surface in production, at
scale, under load, or during an incident. The cost of a bad architectural default is paid
continuously and is expensive to unwind once data and traffic depend on it. Getting the
principles right up front is far cheaper than any migration later.

## Core Principles

- **Everything is a managed service until proven otherwise.** Prefer Lambda, Fargate, RDS,
  and SQS over self-managed EC2 equivalents. You are paying AWS to run the undifferentiated
  heavy lifting (patching, failover, backups); reclaiming it yourself adds risk, not value.
  The cost is less control — accept it unless you have a concrete reason not to.
- **Design for failure of any single component.** Assume every AZ, instance, and
  dependency will fail. Span at least two Availability Zones, make workloads stateless, and
  push state into managed, replicated stores. The blast radius of a design is whatever it
  shares a failure domain with.
- **Least privilege is the default, not a hardening step.** Every role, security group, and
  bucket policy starts closed and opens only for a proven need. Retrofitting least privilege
  onto a permissive system almost never happens; build it in from the first commit.
- **Infrastructure is code, and only code.** Provision through Terraform, CDK, or
  CloudFormation — never the console. Console changes are invisible, unreviewable, and
  undoable only by whoever remembers making them. The cost is upfront tooling; the payoff is
  reproducibility and audit.
- **Cost is a design constraint, not an afterthought.** Data transfer, idle capacity, and
  per-request pricing are architectural decisions. A choice that ignores them (cross-AZ
  chatter, over-provisioned instances) bills you forever.
- **Everything must be observable from day one.** If you cannot see it in
  [CloudWatch](14-cloudwatch.md) and trace it, you cannot operate it. Emit metrics, logs,
  and traces as part of the build, not after the first outage.

## Best Practices

- Choose the **highest-level service that fits**: managed → serverless → containers → EC2.
  Drop a level only when the one above genuinely cannot meet a hard requirement.
- Make compute **stateless**; store session, cache, and files in managed services
  (DynamoDB, ElastiCache, [S3](04-s3.md)) so any instance can serve any request.
- Assign **IAM roles to workloads**; never bake static access keys into an AMI, image, or
  environment file. See [IAM](02-iam.md).
- Encrypt at rest and in transit **by default** using KMS and TLS — it is free or near-free
  and removes a whole class of findings. See [Security](25-security.md).
- **Tag every resource** with owner, environment, and cost-center at creation. Untagged
  resources are un-attributable cost and orphaned risk.
- Right-size with data: start conservative, watch CloudWatch utilization, then adjust. Use
  Auto Scaling so capacity tracks demand instead of a guess. See
  [Cost Optimization](24-cost-optimization.md).
- Set **budgets and alarms** before deploying, so a runaway cost or error rate pages you
  instead of surprising you at month-end.

## Examples

**Good Example** — a stateless, role-based, multi-AZ Lambda in Terraform

```hcl
resource "aws_lambda_function" "api" {
  function_name = "orders-api"
  role          = aws_iam_role.orders_api.arn # scoped role, no static keys
  runtime       = "nodejs22.x"                 # current LTS, not a retired runtime
  handler       = "index.handler"
  memory_size   = 512
  timeout       = 10                           # bounded; no unbounded execution

  environment {
    variables = { TABLE = aws_dynamodb_table.orders.name } # state lives in a managed store
  }
  tracing_config { mode = "Active" } # X-Ray tracing on from day one
}
# DynamoDB is multi-AZ by design; the function holds no state, so any concurrent
# invocation is safe and failure of one execution environment is invisible.
```

**Bad Example** — a stateful, key-based, single-AZ EC2 box created by hand

```bash
# Launched from the console, in one AZ, with a long-lived access key baked in.
aws ec2 run-instances --image-id ami-0abc --instance-type m5.large \
  --subnet-id subnet-single-az        # one AZ: this instance IS the failure domain
# App writes user sessions to the local disk (state on compute) and reads
# credentials from ~/.aws/credentials (static keys that will leak).
# Nothing is in code, so no one can reproduce, review, or safely change it.
```

## Common Mistakes

- Running self-managed EC2 for something a managed service already does (databases, queues,
  load balancing), then owning all the patching and failover yourself.
- Keeping state (sessions, uploads, locks) on compute, which blocks scaling and loses data
  when an instance is replaced.
- Provisioning through the console "just this once", creating drift no code describes.
- Deploying into a single AZ and discovering it only during that AZ's next incident.
- Deferring cost, tagging, and observability to "after launch" — after launch they are a
  cleanup project no one funds.
- Over-provisioning "to be safe" instead of scaling to real demand, paying for idle
  capacity month after month.

## Production Tips

- Enforce IaC in CI: reject console drift by running `terraform plan` on a schedule and
  alerting on unexpected diffs.
- Codify guardrails with Service Control Policies and AWS Config rules so a mistake is
  blocked, not just documented.
- Keep a per-workload runbook and dashboard so on-call can act without tribal knowledge.
- Review architecture against the [Well-Architected Framework](29-well-architected-framework.md)
  pillars at each major milestone.

## AI Review Checklist

- Is the workload using the highest-level managed service that fits the requirement?
- Is compute stateless, with all state in a managed, replicated store?
- Does it span at least two Availability Zones for anything that must stay up?
- Are workloads using IAM roles and temporary credentials, never static keys?
- Is the whole stack defined in infrastructure-as-code, with no console-only changes?
- Are encryption, tagging, budgets, and observability present from the first deploy?
- Have cost implications (data transfer, idle capacity, per-request pricing) been reasoned about?

## Related

- `knowledge/aws/29-well-architected-framework.md`
- `knowledge/aws/02-iam.md`
- `knowledge/aws/28-best-practices.md`
- `knowledge/aws/24-cost-optimization.md`
- `knowledge/aws/25-security.md`
