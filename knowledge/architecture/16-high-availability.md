---
id: architecture/16-high-availability
topic: architecture
slug: high-availability
title: "High Availability"
type: doc
order: 16
status: ready
tags: [architecture, high-availability]
related: [architecture/17-fault-tolerance, architecture/13-scalability, architecture/21-distributed-systems, architecture/22-cloud-architecture, architecture/24-deployment]
when_to_use: "Read when a system has an uptime target and must survive the loss of a node, zone, or dependency."
---
# High Availability

## Purpose

This document defines how a system keeps serving requests despite failures of its
parts: eliminating single points of failure, redundancy, health checking, failover,
and the deployment practices that avoid self-inflicted downtime. It is written so an
agent can design or review a system against a concrete uptime target.

High availability (HA) is about *staying up* — the system as a whole keeps answering
even when a component dies. It overlaps with but is not the same as
[fault-tolerance](17-fault-tolerance.md), which is about how individual requests
survive partial failure. HA is the architecture; fault tolerance is the request-level
behavior that makes it real.

## Why It Matters

Everything fails eventually — disks, nodes, zones, networks, and the software itself.
A system with no redundancy has an uptime ceiling set by its least reliable single part,
and that part *will* fail, usually at the worst time. The trap is that redundancy is
invisible until the failure: a system with one database looks identical to one with a
replica right up until the primary dies and one keeps running while the other is a
multi-hour outage. Availability is also a numbers game — "three nines" (99.9%) allows
~8.7 hours of downtime a year, "four nines" ~52 minutes — and each nine costs more, so
you must design to a target, not to "as much as possible."

## Core Principles

- **Eliminate single points of failure.** Any component whose loss takes down the system
  must be made redundant — app servers, load balancers, databases, and the network path.
  One of anything critical is a liability.
- **Redundancy plus automatic failover.** Spare capacity only helps if traffic moves to it
  without a human. A standby that requires a manual switch is downtime, not availability.
- **Design to a target, not to perfection.** Pick an SLO (e.g. 99.9%) and spend to meet it.
  Each additional nine multiplies cost and complexity; match it to what the business needs.
- **Health checks must reflect real readiness.** Route traffic only to instances that can
  actually serve; a process that is "up" but cannot reach its database must report unhealthy.
- **Remove the human from the critical path.** Failover, restarts, and traffic shifting must
  be automatic. Manual recovery is too slow and too error-prone during an incident.

## Best Practices

- Run at least N+1 redundancy for every critical tier, spread across failure domains
  (availability zones), so losing one zone loses at most a fraction of capacity.
- Put stateless services behind a load balancer with health checks; unhealthy instances are
  pulled from rotation automatically (statelessness is covered in [scalability](13-scalability.md)).
- Configure the database for HA: a primary with synchronous replicas and automatic failover,
  and test the failover regularly — an untested failover is a hope, not a control.
- Separate **liveness** (is the process alive?) from **readiness** (can it serve now?) probes,
  so a warming-up or dependency-blocked instance is not sent traffic prematurely.
- Deploy with zero-downtime strategies — rolling, blue-green, or canary — so releases do not
  cause outages (see [deployment](24-deployment.md)).
- Provision headroom so the loss of one node does not overload the survivors into a cascading
  failure; running at 100% capacity means the first failure is fatal.
- Define and rehearse recovery objectives (RTO/RPO) with backups and restores you have
  actually tested end to end.

## Examples

**Good Example** — readiness probe gates traffic on real dependencies

```yaml
# Readiness fails when the DB is unreachable, so the load balancer stops routing to
# this instance instead of serving errors. WHY: an instance that cannot do its job
# is removed from rotation automatically — traffic shifts to healthy nodes with no
# human in the loop.
readinessProbe:
  httpGet: { path: /ready, port: 8080 }   # /ready checks the DB connection
  periodSeconds: 5
  failureThreshold: 2
livenessProbe:
  httpGet: { path: /alive, port: 8080 }   # only restarts if the PROCESS is wedged
  periodSeconds: 10
replicas: 3
topologySpreadConstraints:                # spread across zones, not one failure domain
  - topologyKey: topology.kubernetes.io/zone
    maxSkew: 1
```

**Bad Example** — single instance, health check that lies

```yaml
# One replica: any crash, deploy, or node loss is a full outage — a single point of
# failure with no failover target.
replicas: 1
livenessProbe:
  httpGet: { path: /alive, port: 8080 }
  # /alive returns 200 as long as the web server is up, even when the DB is down.
  # WHY this is dangerous: the instance keeps receiving traffic and returning 500s
  # instead of being pulled from rotation — the health check hides the failure.
```

## Common Mistakes

- Leaving a single point of failure — one database, one load balancer, one node — that quietly
  caps availability until it fails.
- Provisioning a standby but relying on a human to fail over, so the "redundant" system is still
  a multi-minute outage.
- Health checks that report healthy while the instance cannot actually serve, so the load
  balancer keeps sending traffic into errors.
- Running all replicas in one availability zone, so a zone outage is a total outage.
- No spare capacity, so losing one node overloads the rest and triggers a cascade.
- Backups that have never been restored — an untested backup is not a recovery plan.
- Deploys that require downtime, making every release a scheduled outage.

## Production Tips

- Track availability against the SLO with an error budget; when the budget is spent, stop
  shipping features and fix reliability.
- Run game days / chaos experiments that kill a node or zone in a controlled way to prove
  failover actually works before an incident does the test for you.
- Alert on redundancy loss (e.g. "now running on one replica"), not only on full outage — the
  window between losing redundancy and losing the service is your chance to act.
- Document and rehearse the incident runbook so recovery does not depend on one person's memory.

## AI Review Checklist

- Is every critical tier redundant (N+1) and spread across failure domains?
- Does failover happen automatically, with no human in the critical path?
- Do readiness checks reflect real ability to serve (dependencies), separate from liveness?
- Is there enough headroom that losing one node does not cascade into overload?
- Are deployments zero-downtime (rolling/blue-green/canary)?
- Is there a tested backup/restore and a defined, rehearsed RTO/RPO?
- Is the design sized to a stated availability SLO rather than "as much as possible"?

## Related

- `knowledge/architecture/17-fault-tolerance.md`
- `knowledge/architecture/13-scalability.md`
- `knowledge/architecture/21-distributed-systems.md`
- `knowledge/architecture/22-cloud-architecture.md`
- `knowledge/architecture/24-deployment.md`
