---
id: aws/18-ecs
topic: aws
slug: ecs
title: "ECS"
type: doc
order: 18
status: ready
tags: [aws, ecs, secrets, environment, DB_PASSWORD, "@sha", SIGTERM]
related: [aws/20-ecr, aws/19-eks, aws/12-lambda, aws/10-elastic-load-balancer, aws/11-auto-scaling]
when_to_use: "Read before defining an ECS task definition, service, or Fargate deployment."
---
# ECS

## Purpose

This document defines how to run containers on Amazon ECS (Elastic Container
Service) correctly: task definitions, services, launch types, networking, and
scaling. It is written so an agent can author a task definition and service that
run production traffic without leaking credentials, wasting capacity, or dropping
requests during deploys.

ECS orchestrates containers. A **task definition** is the immutable blueprint (image,
CPU/memory, IAM roles, logging); a **task** is a running instance of it; a **service**
keeps a desired number of tasks alive behind a load balancer. Prefer the **Fargate**
launch type unless you have a concrete reason to manage EC2 instances yourself.

## Why It Matters

ECS is where your container meets IAM, networking, and secrets. The failure modes are
expensive and quiet: an over-provisioned service burns money every hour, an
under-provisioned one throttles or OOM-kills tasks under load, and a task role that is
too broad turns one compromised container into account-wide access. Deploys are the
riskiest moment — get health checks or deployment settings wrong and you swap healthy
tasks for broken ones with no traffic left to serve. Because a task definition is
immutable and versioned, mistakes are auditable, but only if you never mutate config
out of band.

## Core Principles

- **Task definitions are immutable; roll forward, never edit in place.** Each change
  produces a new revision. Deploy by pointing the service at the new revision so you
  keep a clean rollback target.
- **Give each task its own least-privilege task role.** The task role grants the
  application its AWS permissions; the execution role only lets ECS pull images and
  fetch secrets. Never merge them or reuse one role across unrelated services.
- **Inject secrets, never bake them.** Reference Secrets Manager / SSM Parameter Store
  via the `secrets` block so values are resolved at launch and never sit in the image,
  the task definition JSON, or environment variables in plain text.
- **Right-size from measured usage.** Fargate bills for the CPU/memory you request, not
  what you use. Set values from real metrics, not guesses.
- **Health checks gate traffic.** The load balancer and container health checks decide
  when a task is "ready" — if they are wrong, deploys and autoscaling misbehave.

## Best Practices

- Use **Fargate** by default; reach for EC2 launch type only when you need GPUs, custom
  kernels, or per-instance cost tuning at scale. The cost is that you then own patching
  and capacity.
- Set `awslogs` (or `awsfirelens`) logging on every container so stdout/stderr reach
  CloudWatch. A container with no log driver is a black box in an incident.
- Use `awsvpc` network mode (the only mode on Fargate) so each task gets its own ENI
  and security group; scope that security group tightly.
- Configure the service deployment with `minimumHealthyPercent` and
  `maximumPercent` for rolling deploys, or use CodeDeploy blue/green for zero-downtime
  cutovers with automatic rollback.
- Enable **circuit breaker** (`deploymentCircuitBreaker` with `rollback: true`) so a
  failing deploy reverts automatically instead of leaving the service degraded.
- Set container `healthCheck` and a matching ALB target-group health check; align the
  `startPeriod` / deregistration delay with real startup and shutdown time.
- Scale services with **target-tracking** autoscaling on CPU, memory, or ALB
  request-count-per-target, not fixed task counts.
- Pin images by immutable digest or an immutable ECR tag — never deploy `:latest`, which
  makes the running version unknowable.

## Examples

**Good Example** — least-privilege roles, injected secrets, health-gated deploy

```json
{
  "family": "orders-api",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::111122223333:role/ecs-exec-orders",  // pulls image + secrets only
  "taskRoleArn": "arn:aws:iam::111122223333:role/orders-app",            // app's own least-privilege role
  "containerDefinitions": [{
    "name": "api",
    "image": "111122223333.dkr.ecr.eu-west-1.amazonaws.com/orders@sha256:9c4f...", // pinned by digest
    "secrets": [
      { "name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:eu-west-1:111122223333:secret:orders/db-AbCdEf" }
    ],
    "healthCheck": { "command": ["CMD-SHELL", "curl -f http://localhost:8080/healthz || exit 1"], "interval": 15, "startPeriod": 30 },
    "logConfiguration": { "logDriver": "awslogs", "options": { "awslogs-group": "/ecs/orders-api", "awslogs-region": "eu-west-1", "awslogs-stream-prefix": "api" } }
  }]
}
```

**Bad Example** — baked secret, mutable tag, no logs, no health check

```json
{
  "family": "orders-api",
  "containerDefinitions": [{
    "name": "api",
    "image": "111122223333.dkr.ecr.eu-west-1.amazonaws.com/orders:latest", // unknowable version
    "environment": [
      { "name": "DB_PASSWORD", "value": "s3cr3t-in-plaintext" }            // leaked in task def + console
    ]
    // no logConfiguration -> no logs in an incident
    // no healthCheck -> broken tasks receive traffic
  }]
}
```

## Common Mistakes

- Putting passwords or API keys in `environment` instead of `secrets` — they end up in
  the task definition, console, and CI logs in plaintext.
- Deploying `:latest`, so nobody can tell which build is actually running or roll back.
- Reusing one IAM role as both execution and task role, granting the app image-pull and
  secret-read powers it should not have.
- No deployment circuit breaker, so a crash-looping revision silently replaces a healthy
  one and stays broken.
- Health check `startPeriod` shorter than real startup time, causing the orchestrator to
  kill tasks in a restart loop.
- Requesting far more CPU/memory than measured, paying for idle Fargate capacity every
  hour.

## Production Tips

- Enable **ECS Exec** for debugging into running tasks over SSM instead of opening SSH;
  it is auditable and needs no bastion.
- Tag task definitions and services with owner, environment, and cost-center for
  billing and blast-radius analysis.
- Watch `RunningTaskCount` vs `DesiredCount` and CPU/memory utilization; alert when a
  service cannot reach desired count (usually capacity or image-pull failures).
- Set container `stopTimeout` and handle `SIGTERM` so in-flight requests drain before
  the task is killed during a deploy.

## AI Review Checklist

- Are secrets injected via the `secrets` block, never `environment` or the image?
- Are execution role and task role separate, each least-privilege?
- Is the image pinned by digest or an immutable tag, not `:latest`?
- Does every container have a log driver and a health check?
- Is the deployment circuit breaker (with rollback) or blue/green enabled?
- Is autoscaling target-tracking on a real signal, not a fixed count?
- Are CPU/memory sized from measured usage rather than guessed?

## Related

- `knowledge/aws/20-ecr.md`
- `knowledge/aws/19-eks.md`
- `knowledge/aws/12-lambda.md`
- `knowledge/aws/10-elastic-load-balancer.md`
- `knowledge/aws/11-auto-scaling.md`
