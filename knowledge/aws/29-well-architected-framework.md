---
id: aws/29-well-architected-framework
topic: aws
slug: well-architected-framework
title: "Well Architected Framework"
type: doc
order: 29
status: ready
tags: [aws, well-architected-framework, region]
related: [aws/24-cost-optimization, aws/25-security, aws/26-monitoring, aws/27-production, aws/28-best-practices]
when_to_use: "Read before an architecture review or major design decision, to evaluate a workload against AWS's six pillars and name the trade-offs you are making."
---
# Well Architected Framework

## Purpose

This document explains the AWS Well-Architected Framework — the six-pillar model AWS uses
to evaluate whether a cloud workload is sound — and how to apply it as a review lens. It is
written so an agent can assess a design, surface the trade-offs it makes, and recommend
concrete improvements grounded in the same vocabulary AWS Solutions Architects use.

The Framework is not a certification or a rulebook; it is a set of questions organized into
pillars. Its value is that it forces you to reason about the dimensions of a system that
are easy to ignore until they fail — and to make trade-offs *explicitly* rather than by
accident. The service-specific docs in this topic are the "how"; this doc is the "against
what do I judge the whole."

## Why It Matters

Most architectures optimize hard for the one dimension the author cares about — usually
"ship the feature" — and silently regress the other five. The system is fast but insecure,
or cheap but fragile, or reliable but unobservable. These trade-offs are always being made;
the only question is whether they are made deliberately and reviewed, or made by omission
and discovered during an incident. The Framework's job is to make every pillar a
first-class question so nothing important is skipped by default.

## Core Principles

The six pillars, each answering a distinct question about the workload:

- **Operational Excellence** — can you run, observe, and evolve it? Everything as code,
  small reversible changes, learn from failure. (See [monitoring](26-monitoring.md).)
- **Security** — is it protected at every layer? Least privilege, encryption everywhere,
  traceability, security in every phase. (See [security](25-security.md).)
- **Reliability** — does it recover from failure and meet demand? Auto-recovery, horizontal
  scale, tested backups, no single point of failure. (See [production](27-production.md).)
- **Performance Efficiency** — does it use the right resource for the job, and no more? Pick
  the right instance/service, measure, scale with demand.
- **Cost Optimization** — are you paying only for delivered value? Right-size, use the right
  pricing model, attribute and measure. (See [cost optimization](24-cost-optimization.md).)
- **Sustainability** — are you minimizing the environmental impact per unit of work? Right-
  size, choose efficient regions/hardware (Graviton), delete waste.

A seventh cross-cutting idea underlies all six: **trade-offs are inevitable — make them
explicit.** Improving one pillar often costs another (Multi-AZ raises reliability *and*
cost); the Framework asks you to name the trade, not hide it.

## Best Practices

- Run a **Well-Architected Review** on new and changing workloads using the console tool or
  the pillar question sets; record findings as risks (high/medium) with owners.
- Treat the pillars as a **checklist against every design**, not a one-time audit — a
  re-architecture can regress a pillar that was fine before.
- **State the trade-off** in the design doc/ADR: "we chose single-region to cut cost and
  latency, accepting a higher RTO if the region fails — reviewed and accepted."
- Apply **pillar-specific lenses** (Serverless, SaaS, Data Analytics, Machine Learning)
  when they match the workload; they add domain-specific questions.
- Convert review findings into **backlog items with severity**, and re-review after
  remediation. A review that produces no tracked actions changed nothing.
- Use it to **prioritize**: fix high-risk security and reliability gaps before polishing
  cost or performance.

## Examples

**Good Example** — a design decision recorded as an explicit pillar trade-off

```markdown
## ADR-014: Region strategy for checkout service
Decision: Single-region (us-east-1), Multi-AZ, PITR backups with cross-region copy.

Pillar trade-offs (explicit):
- Reliability: survives AZ loss automatically; region loss = manual restore, RTO ~2h.  # accepted
- Cost: Multi-AZ ~2x DB cost vs single-AZ; we accept it for the reliability gain.        # accepted
- Performance: single region keeps p99 latency low for our EU-concentrated users.        # benefit
- Security: unchanged; least-privilege roles + KMS apply regardless of region.
Revisit trigger: when >20% of revenue comes from outside EU, evaluate multi-region.
```

**Bad Example** — an implicit design that regresses pillars silently

```markdown
## Design: checkout service
"We'll run it on one big EC2 instance in one AZ to keep it simple and cheap."

# Reliability: single AZ, single instance — one failure is a full outage. (not mentioned)
# Operational Excellence: deployed by hand, no alarms — invisible when it breaks. (not mentioned)
# Security: default VPC, broad IAM copied from a sample. (not mentioned)
# The trade-offs were never named, so no one reviewed or accepted them.
```

## Common Mistakes

- Treating the review as a one-time launch gate instead of a recurring lens.
- Optimizing one pillar (usually speed-to-ship or cost) while silently regressing others.
- Producing a review with findings but no tracked, owned remediation items.
- Confusing the Framework with a compliance certificate — it is a reasoning tool.
- Ignoring Sustainability and the applicable lenses because they feel optional.
- Making major trade-offs (single-region, no backups) without recording *why*.

## Production Tips

- Schedule a **lightweight review each quarter** and a full one before major launches.
- Link each high-risk finding to a **runbook or backlog ticket** so it cannot be forgotten.
- Feed the pillar checklists into your [AI review](99-ai-review-checklist.md) and
  [production](98-production-checklist.md) checklists so they are enforced continuously.

## AI Review Checklist

- Has the design been evaluated against all six pillars, not just the author's priority?
- Are the trade-offs between pillars named and explicitly accepted (e.g., in an ADR)?
- Are high-risk security and reliability findings prioritized above cost/performance polish?
- Did the review produce tracked, owned remediation items — not just observations?
- Is the review repeated when the architecture changes, not only at launch?
- Were the relevant lenses (Serverless, Data, ML) applied where they fit?

## Related

- `knowledge/aws/24-cost-optimization.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/26-monitoring.md`
- `knowledge/aws/27-production.md`
- `knowledge/aws/28-best-practices.md`
