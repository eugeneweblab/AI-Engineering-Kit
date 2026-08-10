---
id: aws/07-route53
topic: aws
slug: route53
title: "Route 53"
type: doc
order: 7
status: ready
tags: [aws, route53, example.com, evaluate_target_health, cloudfront, balancer, records]
related: [aws/08-cloudfront, aws/09-acm, aws/10-elastic-load-balancer, aws/31-high-availability]
when_to_use: "Read before creating DNS records, delegating a domain, or wiring a hostname to a load balancer, CloudFront, or S3."
---
# Route 53

## Purpose

This document defines how to run DNS on Amazon Route 53: hosted zones, record types,
alias vs. CNAME, health checks, routing policies, and failover. It is written so an
agent can point a domain at AWS resources correctly and safely, without breaking mail,
leaking internal names, or building a fragile failover that never actually fails over.

DNS is the first hop of every request. When it is wrong, the entire property is down —
and DNS caching means mistakes linger long after you "fix" them.

## Why It Matters

DNS errors are uniquely painful because of **TTL and propagation**. A wrong record is
cached by resolvers worldwide for its TTL; shortening the TTL only helps if you did it
*before* the change. A dangling record pointing at a released Elastic IP or deleted S3
bucket is a subdomain-takeover vector an attacker can claim. And DNS is a hard
dependency for TLS issuance, email deliverability, and service discovery — one deleted
`NS` or `MX` record cascades into outages far from where the change was made. The stakes
are total and the feedback loop is slow, so DNS changes demand review.

## Core Principles

- **Prefer alias records over CNAME for AWS targets.** Alias records resolve to the
  target's current IPs at the zone apex *and* subdomains, are free to query, and unlike
  CNAME can coexist with other records at the root (`example.com`).
- **TTL is a promise you must live with.** Set low TTLs (60s) on records you expect to
  change or fail over; use higher TTLs (3600s+) on stable records to cut query cost and
  latency. Lower the TTL *ahead* of a planned migration.
- **A health check does nothing unless a routing policy consults it.** Failover only
  works when records are Failover/Weighted/Latency policies *with* health checks
  attached. A single record with a health check just... has a health check.
- **Never leave dangling records.** Delete DNS records when you delete the resource they
  point to, or the name becomes hijackable.
- **The zone's `NS` records at the registrar must match Route 53's.** Delegation breaks
  silently if they drift.

## Best Practices

- Use **alias A/AAAA records** to point apex and subdomains at ALBs, CloudFront, S3
  website endpoints, and API Gateway.
- For active-passive failover, use two **Failover** records (PRIMARY/SECONDARY) each with
  a health check; for geo-distributed active-active use **Latency** or **Geolocation**
  routing.
- Set `evaluate_target_health = true` on alias records so Route 53 stops sending traffic
  to an unhealthy ALB target automatically.
- Keep DNS in version-controlled IaC (Terraform), not the console — DNS drift is
  invisible and dangerous. Review every change like code.
- Use a **private hosted zone** for internal-only names so internal topology is never
  published to the public internet.
- Configure health checks against a real, cheap health endpoint (`/healthz`) — not the
  homepage, which can be slow or cached.

## Examples

**Good Example** — apex alias to an ALB with target-health evaluation

```hcl
resource "aws_route53_record" "apex" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "example.com"
  type    = "A"

  alias {
    name    = aws_lb.app.dns_name
    zone_id = aws_lb.app.zone_id
    # Route 53 pulls the ALB out of DNS if its targets are unhealthy — free failover.
    evaluate_target_health = true
  }
}
```

**Bad Example** — CNAME at the apex, long TTL on a record you will move

```hcl
resource "aws_route53_record" "apex" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "example.com"
  type    = "CNAME"          # CNAME at the zone apex is invalid per RFC and breaks MX/NS
  ttl     = 86400            # 24h cache — a migration will be broken for a full day
  records = [aws_lb.app.dns_name]
}
```

## Common Mistakes

- Using a CNAME at the zone apex — it is not allowed and collides with `SOA`/`NS`/`MX`.
- High TTLs on records that fail over or migrate, so the change takes hours to propagate.
- Attaching a health check but keeping a `SIMPLE` routing policy, so nothing fails over.
- Deleting an ALB/S3 bucket but leaving its DNS record — subdomain takeover risk.
- Registrar `NS` records not matching the Route 53 hosted zone, breaking delegation
  (common after recreating a zone, which mints new name servers).
- Health-checking the homepage instead of a lightweight endpoint, causing flapping.

## Production Tips

- Enable **query logging** for public zones to investigate abuse and debug resolution.
- Use **DNSSEC** for zones where cache-poisoning is a real threat, but test it — a bad
  KSK rollover can take the zone offline.
- Alarm on health-check status changes; a silent failover you never noticed hides a
  broken primary.
- For blue/green, shift traffic with **Weighted** records (e.g. 90/10) rather than an
  all-at-once cutover.

## AI Review Checklist

- Are AWS targets referenced with alias records rather than CNAMEs (especially at apex)?
- Are TTLs low on records that migrate or fail over, and were they lowered beforehand?
- Does every failover/weighted record have a health check actually attached?
- Is `evaluate_target_health` set on alias records to load balancers?
- Are there any DNS records pointing at deleted or released resources?
- Do registrar `NS` records match the hosted zone's name servers?

## Related

- `knowledge/aws/08-cloudfront.md`
- `knowledge/aws/09-acm.md`
- `knowledge/aws/10-elastic-load-balancer.md`
- `knowledge/aws/31-high-availability.md`
