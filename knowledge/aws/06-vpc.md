---
id: aws/06-vpc
topic: aws
slug: vpc
title: "VPC"
type: doc
order: 6
status: ready
tags: [aws, vpc]
related: [aws/02-iam, aws/03-ec2, aws/10-elastic-load-balancer, aws/25-security, aws/28-best-practices]
when_to_use: "Read before creating or reviewing any network layout — subnets, routing, security groups, or internet/NAT egress."
---
# VPC

## Purpose

This document defines how to lay out an Amazon Virtual Private Cloud (VPC): the CIDR
plan, public/private subnet split, routing, gateways, and the packet-filtering layers
(security groups and network ACLs). It is written so an agent can build or review a
network without exposing a database to the internet or painting the account into a
CIDR corner that cannot grow.

The VPC is the boundary every other resource lives inside. Get it wrong and no amount
of application-layer hardening helps — the machine is simply reachable.

## Why It Matters

Networking mistakes fail in two opposite, expensive ways. An over-permissive layout
(public database, `0.0.0.0/0` on port 5432) is a breach waiting to happen and is
invisible until someone scans you. An over-restrictive or badly-planned layout
(overlapping CIDRs, subnets too small) blocks legitimate traffic or forces a full
rebuild — you cannot resize a VPC or subnet CIDR after creation, and you cannot peer
two VPCs whose ranges overlap. Because the CIDR plan is effectively permanent and the
security boundary is total, this is design-once, live-with-forever infrastructure.

## Core Principles

- **Plan the CIDR before you type it.** Pick a private RFC 1918 block big enough for
  years of growth, non-overlapping with every VPC you might peer or connect to a
  corporate network. `/16` for the VPC, `/24` per subnet is a safe default.
- **Public means "has a route to an Internet Gateway" — nothing else.** A subnet is
  public only because its route table sends `0.0.0.0/0` to an IGW. Put load balancers
  and NAT there; put everything else in private subnets.
- **Private compute reaches out through NAT, never in through an IGW.** Application
  servers and databases get no public IP. Outbound internet (package installs, API
  calls) goes via a NAT Gateway in a public subnet.
- **Security groups are stateful allow-lists; NACLs are stateless and subnet-wide.**
  Do primary filtering with security groups (return traffic is automatic). Use NACLs
  only for coarse subnet-level deny rules.
- **Span at least two Availability Zones.** One subnet per AZ per tier, so a single AZ
  failure does not take the whole system down.

## Best Practices

- Use a three-tier subnet pattern per AZ: **public** (ALB, NAT), **private-app**
  (compute), **private-data** (RDS, ElastiCache). Databases never touch a public subnet.
- Reference security groups *by ID*, not by CIDR, for internal traffic: allow the app
  SG as the source on the database SG. This survives IP changes and documents intent.
- One NAT Gateway **per AZ**. A single shared NAT is a single point of failure and
  forces cross-AZ data-transfer charges.
- Use **VPC Gateway Endpoints** for S3 and DynamoDB and **Interface Endpoints** for
  other AWS APIs so traffic stays on the AWS backbone and skips NAT cost.
- Enable **VPC Flow Logs** to CloudWatch or S3 from day one — you cannot investigate an
  incident with traffic you never recorded.
- Keep the default security group empty (no rules) and never attach it; create explicit,
  named groups instead.

## Examples

**Good Example** — private DB reachable only from the app tier, by SG reference

```hcl
resource "aws_security_group" "app" {
  name   = "app"
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group" "db" {
  name   = "db"
  vpc_id = aws_vpc.main.id
}

# DB accepts Postgres ONLY from the app security group — not a CIDR.
# Survives instance replacement and documents exactly who may connect.
resource "aws_vpc_security_group_ingress_rule" "db_from_app" {
  security_group_id            = aws_security_group.db.id
  referenced_security_group_id = aws_security_group.app.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
}
```

**Bad Example** — database open to the entire internet

```hcl
resource "aws_vpc_security_group_ingress_rule" "db_open" {
  security_group_id = aws_security_group.db.id
  cidr_ipv4         = "0.0.0.0/0" # every host on earth can reach Postgres
  ip_protocol       = "tcp"
  from_port         = 5432        # DB is presumably in a public subnet too — full exposure
  to_port           = 5432
}
```

## Common Mistakes

- Choosing a CIDR that overlaps another VPC or the corporate network, making future
  peering or VPN impossible — and it cannot be changed later.
- Placing databases in public subnets or giving them public IPs "to connect from my
  laptop." Use a bastion, SSM Session Manager, or VPN instead.
- Opening security groups to `0.0.0.0/0` on non-HTTP ports (22, 3389, 5432, 6379).
- A single NAT Gateway for all AZs — one AZ outage or NAT failure kills all egress.
- Relying on NACLs for fine-grained rules; their stateless nature means you must open
  ephemeral return ports, and people forget, causing silent one-way breakage.
- Forgetting Flow Logs, so a security investigation has zero network evidence.

## Production Tips

- Reserve extra CIDR space per AZ for future subnets (EKS pods, added tiers) — subnets
  cannot be resized.
- Add a secondary CIDR block to an existing VPC if you run out, rather than rebuilding.
- Tag subnets with their tier and AZ; automation (EKS, ALB target discovery) relies on
  consistent tags.
- Monitor NAT Gateway data-processing cost — a chatty service hitting a public API
  through NAT can quietly dominate the bill; move it behind a VPC endpoint.

## AI Review Checklist

- Is the VPC CIDR private, non-overlapping, and large enough to grow?
- Are databases and app servers in private subnets with no public IP?
- Do internal rules reference security groups by ID rather than broad CIDRs?
- Is there one NAT Gateway per AZ, and subnets spanning at least two AZs?
- Are ports 22/3389/5432/6379 closed to `0.0.0.0/0`?
- Are VPC Flow Logs enabled, and S3/DynamoDB access via gateway endpoints?

## Related

- `knowledge/aws/02-iam.md`
- `knowledge/aws/03-ec2.md`
- `knowledge/aws/10-elastic-load-balancer.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/28-best-practices.md`
