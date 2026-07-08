---
id: devops/29-tooling
topic: devops
slug: tooling
title: "Tooling"
type: doc
order: 29
status: ready
tags: [devops, tooling]
related: [devops/05-build-pipelines, devops/08-infrastructure-as-code, devops/10-containerization, devops/12-monitoring, devops/28-best-practices]
when_to_use: "Read before selecting or reviewing a DevOps tool for CI/CD, IaC, orchestration, or observability."
---
# Tooling

## Purpose

This document defines how to choose, integrate, and reason about DevOps tools without
letting the tools dictate the process. It is written so an agent can select tooling for a
given job by category and requirement, and can review a proposed toolchain for lock-in,
redundancy, and gaps — rather than reaching for whatever is trendy.

Tools implement practices; they do not replace them. A CI server does not give you
continuous integration if you branch for weeks; a monitoring stack does not give you
observability if you never instrument. Pick the practice first (see the rest of this
topic), then pick the smallest tool that serves it.

## Why It Matters

Tooling decisions are sticky and expensive. A tool becomes load-bearing — pipelines,
scripts, dashboards, and muscle memory grow around it — so a bad choice is paid for over
years, not weeks. Two failure modes dominate. One is **cargo-culting**: adopting
Kubernetes or a service mesh because large companies do, incurring their operational cost
without their scale problem. The other is **tool sprawl**: five overlapping tools nobody
fully owns, each a partial source of truth. The goal is the *fewest* tools that cover
your real requirements with clear ownership.

## Core Principles

- **Requirements before tools.** Write down what the job actually needs (scale, team
  size, compliance, existing stack) before comparing vendors. A tool is only "good"
  relative to a requirement.
- **Prefer standards and open formats.** Choose tools that speak portable interfaces
  (OCI images, OpenTelemetry, standard Git) so you can swap components. Proprietary
  formats are how lock-in happens quietly.
- **Everything-as-code.** Favor tools whose configuration is declarative text in Git over
  point-and-click consoles. A ClickOps change is invisible, unreviewable, and
  unreproducible.
- **Right-size complexity.** Match tool complexity to your actual scale. A managed
  platform or a single VM often beats a self-run cluster until you have the problems the
  cluster solves.
- **Integrate over accumulate.** A new tool must connect to your existing pipeline,
  identity, and alerting. An unintegrated tool becomes a neglected silo.

## Best Practices

- Map tools to categories and pick deliberately in each: **VCS** (Git), **CI/CD**
  ([build pipelines](05-build-pipelines.md)), **IaC**
  ([infrastructure as code](08-infrastructure-as-code.md)), **containers/orchestration**
  ([containerization](10-containerization.md), [orchestration](11-orchestration.md)),
  **observability** ([monitoring](12-monitoring.md), [logging](14-logging.md)),
  **secrets** ([secrets management](17-secrets-management.md)), and **incident/on-call**.
- Pin tool versions and manage them as dependencies; a floating tool version is an
  un-reproducible build waiting to break.
- Prefer managed services when they remove undifferentiated operational toil, unless
  compliance or cost dictates self-hosting. Weigh the *total* operational cost, not just
  the license.
- Adopt OpenTelemetry for instrumentation so telemetry is portable across backends.
- Keep tool configuration in version control and apply it through the same pipeline as
  application code — same review, same audit trail.
- Consolidate before adding: if an existing tool covers the need adequately, extend it
  rather than introducing a sixth dashboard.

## Examples

**Good Example** — pinned, declarative, portable

```dockerfile
# Pin the exact toolchain so every build is reproducible.
FROM golang:1.24.3-alpine        # exact version, not :latest
# ...
# CI config lives in Git and runs the same steps locally and in CI:
#   task lint && task test && task build
# WHY: version-pinned + declarative + Git-tracked = anyone can reproduce the build,
# and swapping CI providers only means porting one YAML file.
```

**Bad Example** — floating versions, ClickOps, lock-in

```dockerfile
FROM node:latest                 # unpinned: today's build != tomorrow's
RUN npm i -g some-cli            # unpinned global tool, silently drifts
# Deploy is configured by clicking through a vendor console — nothing in Git.
# Telemetry uses a proprietary agent format tied to one vendor.
# WHY WRONG: builds aren't reproducible, the deploy can't be reviewed or reverted,
# and migrating vendors means re-instrumenting every service.
```

## Common Mistakes

- Choosing a tool by popularity or resume value instead of by requirement.
- Adopting heavy orchestration/service-mesh tooling before you have the scale for it.
- Configuring infrastructure by clicking in a console (ClickOps) with nothing in Git.
- Floating/`latest` tool versions, making builds non-reproducible.
- Tool sprawl: overlapping tools with no clear owner and multiple sources of truth.
- Locking into proprietary telemetry or image formats that block later migration.

## Production Tips

- Keep an inventory of your toolchain with an owner per tool; an unowned tool rots.
- Run a periodic review to retire redundant tools — sprawl accumulates by default.
- Prefer tools with a strong local-development story so CI reproduces what engineers run.
- Budget for the operational cost of self-hosted tools (upgrades, backups, on-call), not
  just their sticker price, when comparing against managed options.

## AI Review Checklist

- Was the tool chosen against written requirements, not popularity?
- Is its configuration declarative and stored in version control, not ClickOps?
- Are tool versions pinned so builds are reproducible?
- Does it speak open standards (OCI, OpenTelemetry) to avoid lock-in?
- Does it integrate with the existing pipeline, identity, and alerting?
- Does it fill a real gap rather than duplicating an existing tool?

## Related

- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/08-infrastructure-as-code.md`
- `knowledge/devops/10-containerization.md`
- `knowledge/devops/12-monitoring.md`
- `knowledge/devops/28-best-practices.md`
