---
id: aws/10-elastic-load-balancer
topic: aws
slug: elastic-load-balancer
title: "Elastic Load Balancer"
type: doc
order: 10
status: ready
tags: [aws, elastic-load-balancer, fast, interval]
related: [aws/06-vpc, aws/09-acm, aws/11-auto-scaling, aws/31-high-availability, aws/03-ec2]
when_to_use: "Read before putting a load balancer in front of a service — choosing ALB vs NLB, configuring listeners, health checks, or TLS termination."
---
# Elastic Load Balancer

## Purpose

This document defines how to run Elastic Load Balancing: choosing between Application
(ALB), Network (NLB), and Gateway load balancers; listeners and TLS termination; target
groups; and — most importantly — health checks and connection draining. It is written so
an agent can put a load balancer in front of a fleet that distributes traffic correctly
and removes bad instances *before* users hit them, rather than routing requests into a
black hole.

The load balancer is the point where availability is won or lost: a good health check is
the difference between a self-healing system and one that keeps serving errors.

## Why It Matters

The load balancer's health check is the system's immune response. Set it wrong and the
failure is silent and severe: too lax (checking `/` which returns 200 even when the DB is
down) and the LB keeps sending traffic to a broken instance; too strict or too slow
(long intervals, high thresholds) and a dead instance keeps taking requests for minutes
before it is pulled. Without connection draining, every deploy or scale-in **kills
in-flight requests**, showing users 5xx during routine operations. And picking the wrong
LB type (ALB for raw TCP, NLB when you need path routing) forces an expensive rebuild.
These are the defects that turn a "healthy" dashboard into an angry incident channel.

## Core Principles

- **Match the LB type to the protocol.** **ALB** for HTTP/HTTPS with path/host routing,
  WebSockets, and per-request features. **NLB** for TCP/UDP, extreme throughput, static
  IPs, or when you need to preserve the client IP at L4. Do not use an ALB for non-HTTP.
- **Health checks must test real health, not liveness.** Point the check at an endpoint
  that verifies critical dependencies (DB, cache), so an instance that cannot serve is
  marked unhealthy and removed.
- **Terminate TLS at the load balancer with an ACM cert.** Offload TLS at the edge, then
  re-encrypt to targets if the traffic is sensitive. Never hand-manage certs on each box.
- **Drain before you kill.** Enable deregistration delay (connection draining) so
  in-flight requests finish before a target is removed on deploy or scale-in.
- **Span multiple AZs with cross-zone balancing.** The LB must have a subnet in each AZ
  its targets live in, or that AZ gets no traffic.

## Best Practices

- Put the LB in **public subnets** and its targets in **private subnets**; the target
  security group allows traffic **only from the LB's security group**, not the internet.
- Configure health checks deliberately: a dedicated `/healthz` path, `interval` 10–30s,
  `healthy/unhealthy threshold` 2–3. Faster detection vs. flap-tolerance is the trade-off.
- Set **deregistration delay** to just above your longest normal request (e.g. 30s), so
  draining is quick but does not cut off real work.
- Redirect HTTP:80 to HTTPS:443 with a listener rule; attach a modern
  **security policy** (TLS 1.2+) to the HTTPS listener.
- Enable **access logs** to S3 and the LB's CloudWatch metrics (5xx count, target
  response time, unhealthy host count) with alarms.
- Enable **cross-zone load balancing** (default on for ALB; opt-in and sometimes charged
  for NLB) so load spreads evenly regardless of per-AZ target counts.

## Examples

**Good Example** — real health check, HTTPS termination, draining enabled

```hcl
resource "aws_lb_target_group" "app" {
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  # Checks a dependency-aware endpoint, and pulls a bad target fast (2 x 10s = 20s).
  health_check {
    path                = "/healthz"
    interval            = 10
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200"
  }

  # Let in-flight requests finish on deploy/scale-in instead of 5xx-ing users.
  deregistration_delay = 30
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.app.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate_validation.app.certificate_arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
```

**Bad Example** — liveness-only check, no draining, TLS not terminated

```hcl
resource "aws_lb_target_group" "app" {
  health_check {
    path     = "/"        # returns 200 even when the DB is down → broken targets stay in
    interval = 300        # 5-minute checks: a dead box serves errors for minutes
  }
  deregistration_delay = 0 # every deploy severs in-flight requests → user-visible 5xx
}
# Only an HTTP:80 listener — traffic is plaintext end to end.
```

## Common Mistakes

- Health-checking `/` or a static file that returns 200 regardless of real health, so
  broken instances keep receiving traffic.
- `deregistration_delay = 0`, cutting live connections on every deploy and scale-in.
- Long check intervals / high thresholds, leaving a dead instance in rotation for minutes.
- Using an ALB for raw TCP/UDP or when the app needs the true client IP at L4 (use NLB).
- Target security group open to `0.0.0.0/0` instead of only the LB's security group,
  letting clients bypass the LB.
- Only an HTTP listener, or a legacy TLS policy, so traffic is downgradeable.
- LB missing a subnet in an AZ where targets run, starving that AZ of traffic.

## Production Tips

- Alarm on `UnHealthyHostCount > 0` and `HTTPCode_ELB_5XX` — the LB sees failures the app
  logs may miss.
- Use **weighted target groups** or a second listener rule for blue/green and canary
  shifts instead of DNS changes.
- Enable **stickiness** only when the app truly needs session affinity; it undermines
  even load distribution.
- For NLB, remember health checks and preserved client IPs change how target security
  groups must be written (traffic arrives with the real client IP).

## AI Review Checklist

- Is the LB type correct for the protocol (ALB for HTTP, NLB for TCP/UDP/static IP)?
- Does the health check hit a dependency-aware endpoint, not `/`?
- Is `deregistration_delay` set so deploys and scale-in drain instead of dropping requests?
- Is TLS terminated with an ACM cert on an HTTPS listener with a TLS 1.2+ policy, and HTTP
  redirected to HTTPS?
- Does the target security group allow traffic only from the LB's security group?
- Does the LB span every AZ its targets run in, with cross-zone balancing on?

## Related

- `knowledge/aws/06-vpc.md`
- `knowledge/aws/09-acm.md`
- `knowledge/aws/11-auto-scaling.md`
- `knowledge/aws/31-high-availability.md`
- `knowledge/aws/03-ec2.md`
