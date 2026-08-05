---
id: aws/01-global-infrastructure
topic: aws
slug: global-infrastructure
title: "Global Infrastructure"
type: doc
order: 1
status: ready
tags: [aws, global-infrastructure]
related: [aws/00-overview, aws/06-vpc, aws/11-auto-scaling, aws/05-rds, aws/31-high-availability, aws/08-cloudfront]
when_to_use: "Read before choosing a Region, laying out subnets, or designing for high availability."
---
# Global Infrastructure

## Purpose

This document defines the physical and logical layout of AWS — **Regions**, **Availability
Zones (AZs)**, **edge locations**, and the difference between *global*, *regional*, and
*zonal* services. It exists so an agent places resources in the right scope and does not
accidentally build a single point of failure into the foundation of a system.

Every other AWS decision inherits from this one. Where you put data determines its latency,
its legal residency, and whether an entire outage takes you down with it.

## Why It Matters

The single most common availability bug in AWS is not a code error — it is deploying an
entire workload into one Availability Zone. It works perfectly in testing, then a routine
AZ degradation takes the whole system offline. AZ and Region choices also carry
irreversible consequences: data residency is a legal obligation in many jurisdictions, and
inter-Region data transfer is billed and adds real latency. Getting the topology right up
front is far cheaper than migrating later.

## Core Principles

- **A Region is an isolated geographic area** (e.g. `us-east-1`, `eu-west-1`) containing
  multiple AZs. Regions are independent by design — an outage in one does not cascade to
  another, and most services do not replicate across Regions unless you configure it.
- **An Availability Zone is one or more discrete data centers** within a Region, with
  independent power, cooling, and networking. AZs in a Region are close enough for
  low-latency sync replication but far enough to fail independently.
- **Span at least two AZs for anything that must stay up.** Single-AZ is acceptable only for
  disposable or dev workloads.
- **Services have a scope.** IAM, Route 53, CloudFront, and WAF are *global*. Most services
  (EC2, RDS, S3, VPC) are *regional*. Subnets, EBS volumes, and single EC2 instances are
  *zonal*. Know the scope before you reason about failure.
- **Region choice is nearly permanent.** Migrating a running system between Regions is a
  project, not a config change. Choose deliberately.

## Best Practices

- Pick a Region by: data-residency and compliance requirements first, proximity to users
  second, service availability third, and price fourth. Not every service exists in every
  Region.
- Distribute subnets across **three AZs** where the Region offers them; three tolerates one
  AZ loss with capacity to spare, and quorum-based systems (RDS Multi-AZ, etcd) need an odd
  number.
- Reference AZs by their AZ ID (e.g. `use1-az1`), not their name (`us-east-1a`), when
  consistency across accounts matters — the name-to-physical-AZ mapping differs per account.
- Keep latency-sensitive traffic within one Region; use CloudFront edge locations to serve
  users far from your Region rather than deploying full stacks everywhere.
- Only build multi-Region active-active when an explicit RTO/RPO requirement justifies its
  cost and complexity; it roughly doubles operational surface area.

## Examples

**Good Example** — subnets spread across three AZs (Terraform)

```hcl
# Query the AZs actually available in this Region instead of hardcoding names,
# so the same module works in any Region.
data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_subnet" "private" {
  count             = 3 # one subnet per AZ -> survives a single-AZ outage
  vpc_id            = aws_vpc.main.id
  availability_zone = data.aws_availability_zones.available.names[count.index]
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 4, count.index)
}
```

**Bad Example** — the whole workload pinned to one AZ

```hcl
resource "aws_subnet" "app" {
  vpc_id            = aws_vpc.main.id
  availability_zone = "us-east-1a" # hardcoded single AZ = single point of failure
  cidr_block        = "10.0.1.0/24"
}
# Every instance, RDS node, and load-balancer target lands here.
# When us-east-1a degrades, the entire system is down with no fallback.
```

## Common Mistakes

- Deploying all resources into one AZ because it is fewer lines of config.
- Hardcoding `us-east-1a`-style names, which map to different physical AZs in different
  accounts and break portability.
- Assuming S3 or RDS data is replicated across Regions automatically — it is not, unless you
  enable Cross-Region Replication or a read replica.
- Choosing `us-east-1` by habit for a European user base, adding latency and violating data
  residency.
- Treating edge locations (CloudFront) as compute Regions — they cache and route, they do
  not run your application.

## AI Review Checklist

- Are subnets and compute spread across at least two (ideally three) AZs?
- Is the Region choice justified by residency, latency, and service availability — not habit?
- Are AZs selected dynamically (data source) rather than hardcoded?
- Is any cross-Region replication explicitly configured where the requirement demands it?
- Is each resource's scope (global/regional/zonal) understood in the failure analysis?

## Related

- `knowledge/aws/00-overview.md`
- `knowledge/aws/06-vpc.md`
- `knowledge/aws/11-auto-scaling.md`
- `knowledge/aws/05-rds.md`
- `knowledge/aws/31-high-availability.md`
- `knowledge/aws/08-cloudfront.md`
