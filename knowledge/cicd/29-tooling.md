---
id: cicd/29-tooling
topic: cicd
slug: tooling
title: "CI/CD Tooling"
type: doc
order: 29
status: ready
tags: [cicd, tooling, "@main", runs-on]
related: [cicd/17-github-actions, cicd/18-gitlab-ci, cicd/20-jenkins, cicd/21-docker-integration, cicd/27-best-practices]
when_to_use: "Read before selecting a CI/CD platform or adding a new tool to the pipeline toolchain."
---
# CI/CD Tooling

## Purpose

This document defines how to choose and combine the tools that make up a CI/CD
system: the orchestrator ([GitHub Actions](17-github-actions.md),
[GitLab CI](18-gitlab-ci.md), [Jenkins](20-jenkins.md)), the runners, the
container tooling, and the supporting scanners, linters, and deploy utilities. It
is about picking the right tool for the constraint and wiring tools together
without lock-in or hidden fragility.

The orchestrator is a scheduler and a secret store, not where your build logic
should live. The recurring theme here is: keep logic in portable scripts, keep the
platform thin, and choose tools you can reason about and replace.

## Why It Matters

Tooling decisions are sticky. The orchestrator you pick shapes how every pipeline
is written, where secrets live, and how hard it is to migrate later. Teams that
pour build logic into vendor-specific YAML find themselves locked in — a change of
platform means rewriting everything, so they don't, even when the tool no longer
fits.

Tool sprawl is the opposite failure: every problem answered with a new action or
plugin, until the pipeline depends on a dozen unmaintained third-party components,
each a supply-chain risk and a potential break. The skill is choosing few,
well-understood tools and keeping the logic they run portable.

## Core Principles

- **Keep logic in scripts, not in the platform.** Business/build logic lives in
  `Makefile`, shell, or task-runner scripts the pipeline *calls*. This keeps builds
  runnable locally and portable across orchestrators.
- **Choose tools for your constraints, not hype.** Managed (GitHub/GitLab SaaS) for
  low ops overhead; self-hosted (Jenkins, self-hosted runners) for control,
  compliance, or special hardware. Name the constraint before naming the tool.
- **Pin and vet every third-party component.** A third-party action or plugin runs
  with your credentials. Pin it to a full commit SHA, review it, and prefer
  first-party or widely-audited ones.
- **Prefer standards and portability over proprietary features.** OCI images,
  standard test formats (JUnit XML), and SARIF for scan results move between tools;
  proprietary equivalents lock you in.
- **Fewer tools, understood deeply.** Each tool added is a dependency to maintain,
  secure, and debug. Add one only when it clearly beats scripting it yourself.

## Best Practices

- Put build/test/deploy commands behind a `Makefile` or task runner so `make test`
  works identically locally and in CI — the orchestrator just calls it.
- Pin third-party GitHub Actions to a full commit SHA (not a tag) and enable
  Dependabot on them, because tags are mutable and a compromised action steals your
  secrets.
- Standardize outputs: emit JUnit XML for tests and SARIF for
  [security scans](06-security-scanning.md) so any platform can display them.
- Use [Docker](21-docker-integration.md) to define the build environment so the
  toolchain is versioned and identical everywhere, rather than relying on whatever
  the runner has installed.
- Choose managed runners by default; introduce self-hosted runners only for a
  concrete need (GPU, on-prem access, cost at scale) and isolate them, since they
  can be an attack surface.
- Keep the orchestrator config small and declarative; when a step grows complex,
  push the complexity into a versioned script the step invokes.
- Reuse via templates/composite actions/reusable workflows instead of copy-pasting
  the same tool invocations across pipelines.

## Examples

**Good Example** — thin platform, portable logic, pinned dependency

```yaml
# Orchestrator just calls scripts that also run locally -> portable, testable.
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22' }
      - run: make ci            # logic lives in Makefile: `make ci` works on a laptop too
      - uses: github/codeql-action/upload-sarif@4c...f9   # third-party action pinned to full SHA
        with: { sarif_file: results.sarif }               # standard format, portable across tools
```

```makefile
# Makefile — the real logic, orchestrator-agnostic
ci: lint test build
lint:  ; npm run lint
test:  ; npm test -- --reporters=jest-junit   # standard JUnit XML output
build: ; npm run build
```

**Bad Example** — logic trapped in vendor YAML, unpinned actions

```yaml
jobs:
  ci:
    steps:
      # 40 lines of inline shell + vendor-specific syntax: impossible to run locally,
      # painful to migrate off this platform.
      - uses: some-org/magic-deploy@v1       # floating tag: mutable, runs with your secrets
      - uses: another/scanner-action@main    # `@main` -> whatever they push today runs in your pipeline
      - run: |
          # bespoke deploy logic pasted here and in three other pipelines, now drifting
          ...
```

## Common Mistakes

- Embedding all build logic in orchestrator-specific YAML, making builds
  un-runnable locally and migration prohibitively expensive.
- Referencing third-party actions by mutable tag (`@v1`, `@main`) instead of a
  pinned commit SHA, exposing secrets to a compromised upstream.
- Adopting a self-hosted CI server for a problem a managed platform solves, then
  owning its upkeep and security forever.
- Adding a new plugin/action for every task until the pipeline depends on a dozen
  fragile, unmaintained components.
- Producing proprietary report formats that only one tool can read, locking in the
  whole toolchain.
- Copy-pasting tool invocations across pipelines instead of extracting a reusable
  template.

## Production Tips

- Keep a short, documented list of approved actions/plugins and their pinned
  versions; audit it when Dependabot flags an update.
- Isolate self-hosted runners (ephemeral, least privilege, no long-lived secrets)
  so a poisoned job can't pivot into your network.
- Prototype a migration path off your orchestrator once: if `make ci` runs
  everything, switching platforms is changing a thin YAML wrapper, not a rewrite.

## AI Review Checklist

- Does build/test/deploy logic live in portable scripts the orchestrator merely
  calls?
- Are all third-party actions/plugins pinned to full commit SHAs and reviewed?
- Is the platform choice justified by a real constraint (ops overhead, control,
  hardware), not hype?
- Are outputs in standard, portable formats (JUnit XML, SARIF, OCI images)?
- Are self-hosted runners isolated and least-privilege where used?
- Is shared tooling reused via templates rather than copy-pasted across pipelines?

## Related

- `knowledge/cicd/17-github-actions.md`
- `knowledge/cicd/18-gitlab-ci.md`
- `knowledge/cicd/20-jenkins.md`
- `knowledge/cicd/21-docker-integration.md`
- `knowledge/cicd/27-best-practices.md`
