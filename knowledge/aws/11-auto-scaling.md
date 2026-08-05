---
id: aws/11-auto-scaling
topic: aws
slug: auto-scaling
title: "Auto Scaling"
type: doc
order: 11
status: ready
tags: [aws, auto-scaling, max_size, ELB]
related: [aws/03-ec2, aws/10-elastic-load-balancer, aws/31-high-availability, aws/14-cloudwatch, aws/24-cost-optimization]
when_to_use: "Read before configuring an Auto Scaling Group — launch templates, scaling policies, health checks, or capacity for a fleet behind a load balancer."
---
# Auto Scaling

## Purpose

This document defines how to run EC2 Auto Scaling Groups (ASGs): launch templates,
min/max/desired capacity, scaling policies, health checks, and safe instance refresh.
It is written so an agent can build a fleet that grows under load, shrinks when idle,
replaces dead instances automatically, and spreads across AZs — without thrashing,
without terminating healthy nodes mid-request, and without an unbounded bill.

Auto Scaling is what turns a load balancer plus a launch template into a self-healing,
elastic system. Done well it is invisible; done badly it amplifies every failure.

## Why It Matters

Auto Scaling is a control loop, and misconfigured control loops oscillate. Aggressive
thresholds with no cooldown cause **flapping** — scaling out, then in, then out — which
wastes money and destabilizes the fleet. If the ASG uses only EC2 status checks instead
of the load balancer's health check, it keeps instances that boot fine but cannot serve.
If `max_size` is unbounded, a traffic spike or a runaway metric scales you into a
four-figure surprise; if `min_size` is too low, a scale-in during a lull leaves no
headroom for the next spike. And a naive deploy that replaces all instances at once,
without draining, drops live traffic. These are the failure modes that make elasticity a
liability instead of a feature.

## Core Principles

- **Use a launch template, not a launch configuration.** Launch configurations are
  legacy and cannot express newer instance features. Templates are versioned and support
  mixed instances and Spot.
- **Let the load balancer decide health.** Set the ASG's health check type to `ELB` so an
  instance that passes EC2 status checks but fails the app health check is replaced.
- **Scale on the metric that reflects load, and add cooldowns.** Target-tracking on CPU or
  ALB request-count-per-target is usually right; a stabilization/cooldown window prevents
  flapping. React fast enough to matter, slow enough not to oscillate — that is the trade.
- **Bound capacity on both ends.** `min_size` guarantees baseline availability; `max_size`
  caps the blast radius of a runaway scale-out and the bill.
- **Spread across AZs.** Multiple subnets in different AZs so the ASG rebalances and a
  single AZ outage loses only a fraction of capacity.

## Best Practices

- Prefer **target-tracking** scaling (e.g. keep average CPU at 50%, or
  `ALBRequestCountPerTarget` at a set value) over hand-tuned step policies — it is
  self-adjusting and simpler to reason about.
- Set `min_size` to survive the loss of one AZ (e.g. `min_size >= 2` across 2+ AZs) and
  `max_size` to a real, affordable ceiling.
- Use **instance refresh** with a `min_healthy_percentage` and warm-up to roll out new
  launch-template versions gradually instead of replacing everything at once.
- Enable **scale-in protection** or lifecycle hooks for stateful or long-job instances so
  work drains before termination.
- Combine On-Demand and **Spot** via a mixed-instances policy for cost, keeping a
  guaranteed On-Demand base for stability.
- Attach the ASG to the ALB **target group** (not the classic LB) so registration,
  draining, and health flow through one place.

## Examples

**Good Example** — target tracking, ELB health, bounded and multi-AZ

```hcl
resource "aws_autoscaling_group" "app" {
  min_size            = 2                 # survives one AZ loss
  max_size            = 10                # hard ceiling on cost and blast radius
  desired_capacity    = 2
  vpc_zone_identifier = [aws_subnet.app_a.id, aws_subnet.app_b.id] # spread across AZs
  target_group_arns   = [aws_lb_target_group.app.arn]

  health_check_type         = "ELB"       # replace instances the app health check fails
  health_check_grace_period = 90          # give the app time to boot before judging it

  instance_refresh {
    strategy = "Rolling"
    preferences { min_healthy_percentage = 90 } # roll deploys without dropping capacity
  }
}

resource "aws_autoscaling_policy" "cpu" {
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    predefined_metric_specification { predefined_metric_type = "ASGAverageCPUUtilization" }
    target_value = 50.0                   # self-adjusting; no manual step thresholds to flap
  }
}
```

**Bad Example** — EC2-only health, no upper bound, twitchy step policy

```hcl
resource "aws_autoscaling_group" "app" {
  min_size          = 1
  max_size          = 1000              # a runaway metric scales into a huge bill
  health_check_type = "EC2"             # keeps instances that boot but can't serve requests
  # single subnet → no AZ resilience
  vpc_zone_identifier = [aws_subnet.app_a.id]
}

resource "aws_autoscaling_policy" "step" {
  autoscaling_group_name = aws_autoscaling_group.app.name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = 5
  cooldown               = 0            # no cooldown → scales out and in repeatedly (flapping)
}
```

## Common Mistakes

- Using `health_check_type = "EC2"`, so instances that pass status checks but fail the app
  health check stay in rotation forever.
- No `max_size` ceiling (or an absurd one), letting a spike or bad metric run up the bill.
- Zero cooldown / tight step thresholds, causing the group to flap in and out.
- A single-AZ `vpc_zone_identifier`, so the "auto-scaling, highly available" fleet dies
  with one AZ.
- Replacing all instances at once on deploy instead of using instance refresh with a
  healthy-percentage floor.
- No `health_check_grace_period`, so instances are killed before the app finishes booting.
- Using legacy launch configurations instead of launch templates.

## Production Tips

- Use **predictive scaling** or scheduled actions for known daily/weekly traffic shapes so
  you scale out *before* the spike, not during it.
- Add **lifecycle hooks** to drain connections, flush logs, or finish jobs before an
  instance terminates on scale-in.
- Alarm on `GroupInServiceInstances` vs `GroupDesiredCapacity` divergence — a persistent
  gap means launches or health checks are failing.
- Watch for scaling-activity failures (bad AMI, capacity errors) in the ASG activity log;
  a fleet stuck below desired is a silent degradation.

## AI Review Checklist

- Is the ASG using a launch template (not a launch configuration)?
- Is `health_check_type = "ELB"` with a sensible `health_check_grace_period`?
- Are `min_size` and `max_size` both set to sane, bounded values?
- Does `vpc_zone_identifier` span at least two AZs?
- Is scaling target-tracking (or step with cooldowns) so the group does not flap?
- Do deploys use instance refresh with a `min_healthy_percentage` floor?

## Related

- `knowledge/aws/03-ec2.md`
- `knowledge/aws/10-elastic-load-balancer.md`
- `knowledge/aws/31-high-availability.md`
- `knowledge/aws/14-cloudwatch.md`
- `knowledge/aws/24-cost-optimization.md`
