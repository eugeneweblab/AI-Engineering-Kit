---
id: tools/27-dependency-management
topic: tools
slug: dependency-management
title: "Dependency Management"
type: doc
order: 27
status: ready
tags: [tools, dependency-management, update-types, react-dom, open-pull-requests-limit, SECURITY.md, structuredClone, runs-on]
related: [tools/01-package-managers, tools/28-release-tools, tools/02-version-management, tools/26-ai-coding-tools, tools/30-engineering-principles, security/23-dependency-security, security/24-supply-chain-security]
when_to_use: "Read before adding a dependency or setting up update automation — evaluating a package, configuring Renovate or Dependabot, or responding to a vulnerability advisory."
---
# Dependency Management

## Purpose

This document defines how to keep dependencies current and trustworthy: evaluating a package before adding it, automating updates so they arrive in reviewable batches, and responding to advisories without dropping everything.

## Why It Matters

Every dependency is code you ship without reviewing, executing with your application's privileges. That is usually a good trade — reimplementing a date library is worse — but it is a trade, and projects tend to make it without noticing.

The compounding problem is deferral. A dependency updated monthly is a small diff; the same dependency updated after two years is a major-version migration with breaking changes stacked on top of each other, undertaken under pressure because an advisory forced it.

## Core Principles

- **Adding a dependency is a permanent decision.** Removing one after it spreads through the codebase is far harder than not adding it.
- **Update continuously, in small batches.** Frequent small updates are individually reviewable; a deferred backlog is not.
- **Automate the proposal, not the merge.** A bot that opens pull requests is leverage; a bot that merges them unattended ships unreviewed code.
- **Lockfiles are the source of truth** for what actually runs — see [Package Managers](01-package-managers.md).
- **An advisory is an input to triage, not an emergency.** Severity plus reachability decides urgency.

## Before Adding a Dependency

Five questions, in order:

1. **Does the platform already do this?** `structuredClone`, `Intl.NumberFormat`, `crypto.randomUUID`, `Array.prototype.at` — a decade of small packages have been absorbed into the runtime.
2. **What does it weigh?** Check install size and transitive count, not just the package itself. A one-function utility pulling forty transitive dependencies is forty supply-chain surfaces.
3. **Is it maintained?** Last release, open issue age, number of maintainers. A single-maintainer package at the center of your build is a risk that materializes at the worst time.
4. **What is the exit cost?** A formatting helper is trivial to replace; an ORM, a router, or a state library is a rewrite.
5. **Could you write it in an afternoon?** Then the maintenance cost of writing it is often lower than the maintenance cost of depending on it.

Weigh the answers rather than counting them: a well-maintained framework with many dependencies can be the right choice, and a tiny abandoned package the wrong one.

## Automating Updates

```json
// renovate.json — group and schedule so review happens in batches
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "timezone": "Europe/Berlin",
  "schedule": ["before 6am on Monday"],
  "prConcurrentLimit": 5,

  "packageRules": [
    {
      "description": "Dev tooling: batch and auto-merge once CI is green.",
      "matchDepTypes": ["devDependencies"],
      "matchUpdateTypes": ["minor", "patch"],
      "groupName": "dev dependencies",
      "automerge": true
    },
    {
      "description": "Runtime deps: group patches, review minors individually.",
      "matchDepTypes": ["dependencies"],
      "matchUpdateTypes": ["patch"],
      "groupName": "runtime patches"
    },
    {
      "description": "Majors always get their own PR and a human.",
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "labels": ["breaking-change"]
    },
    {
      "description": "Framework upgrades need coordination — never automatic.",
      "matchPackageNames": ["next", "react", "react-dom", "prisma"],
      "automerge": false,
      "labels": ["needs-planning"]
    }
  ],

  "vulnerabilityAlerts": {
    "labels": ["security"],
    "schedule": ["at any time"],
    "prPriority": 10
  }
}
```

Dependabot is the lighter alternative — less configurable, zero setup on GitHub:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule: { interval: "weekly" }
    open-pull-requests-limit: 5
    groups:
      dev-dependencies:
        dependency-type: "development"
        update-types: ["minor", "patch"]
  - package-ecosystem: "composer"
    directory: "/"
    schedule: { interval: "weekly" }
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: { interval: "monthly" }
```

Two details worth copying: **grouping** turns twenty PRs into three, and **security alerts bypass the schedule** so a real vulnerability is not queued behind next Monday.

Auto-merge is defensible for dev-tooling patches where CI is genuinely comprehensive — a formatter bump that passes typecheck, lint, and tests is not worth a human. It is not defensible for runtime dependencies: CI does not catch a subtly changed default.

## Auditing

```bash
npm audit --audit-level=high        # npm
pnpm audit --prod                   # runtime deps only — the ones that ship
composer audit                      # PHP
```

Run audits on a schedule and in CI, but **do not block unrelated deploys on them**. A new advisory published against a transitive dev dependency should not stop a hotfix from shipping.

```yaml
# Nightly, not on every PR
name: security-audit
on:
  schedule: [{ cron: "0 6 * * *" }]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm audit --prod --audit-level=high
```

## Triaging an Advisory

Severity alone is a poor prioritizer. Three questions decide urgency:

1. **Is the vulnerable code reachable from your application?** A prototype-pollution bug in a build-time-only package is not the same as one in a request handler.
2. **Is the vulnerable path reachable by untrusted input?** A ReDoS in a parser you run on user-supplied strings is urgent; the same parser run on your own config file is not.
3. **Is there a fix?** If not, the options are pinning, patching, or replacing — and a documented accepted risk is a legitimate fourth.

```bash
# What pulls in the vulnerable package, and at what depth?
npm ls semver
pnpm why semver
composer why vendor/package
```

When the fix exists only in a transitive dependency's newer release, force it rather than waiting for the direct dependency to update:

```json
{ "overrides": { "semver": "^7.6.3" } }        // npm / pnpm
{ "resolutions": { "semver": "^7.6.3" } }      // yarn
```

Record why every override exists — an undocumented override outlives the vulnerability and silently pins a package for years.

## Supply-Chain Hygiene

- **Commit lockfiles** and review lockfile diffs on dependency PRs. An unexpected new transitive package is worth a question.
- **Pin GitHub Actions to a commit SHA**, not a moving tag — a compromised tag is a supply-chain attack with your CI secrets.
- **Disable install scripts** where the ecosystem allows it (`npm config set ignore-scripts true`), and re-enable per package when genuinely needed.
- **Check for typosquats** when adding a package: `react-dom` versus `reactdom`, `@types/node` versus `types-node`.
- **Prefer fewer, larger, well-maintained dependencies** over many small ones. Surface area scales with package count, not with lines of code.

See [Security — Dependency Security](../security/23-dependency-security.md) and [Security — Supply Chain Security](../security/24-supply-chain-security.md).

## Removing Dependencies

Removal is as valuable as addition and nobody schedules it:

```bash
npx depcheck                          # unused and missing dependencies
npx knip                              # unused files, exports, and dependencies
composer why-not vendor/package 2.0   # what blocks an upgrade
```

Run this quarterly. The usual finds: packages replaced during a migration but never uninstalled, polyfills for browsers no longer supported, and utilities superseded by the standard library.

## Examples

**Good Example** — a lockfile in CI, updates in reviewable batches

```yaml
# .github/workflows/ci.yml — the install must fail if the lockfile is stale.
- run: pnpm install --frozen-lockfile
- run: pnpm audit --audit-level=high
- run: pnpm verify
```

```json
{
  "renovate": {
    "extends": ["config:recommended"],
    "schedule": ["before 6am on Monday"],
    "packageRules": [
      { "matchUpdateTypes": ["minor", "patch"], "groupName": "non-major", "automerge": true },
      { "matchUpdateTypes": ["major"], "dependencyDashboardApproval": true }
    ],
    "vulnerabilityAlerts": { "labels": ["security"], "schedule": ["at any time"] }
  }
}
```

Patch and minor updates arrive weekly, grouped, and merge themselves when the suite passes.
Majors wait for a human. Security advisories bypass the schedule entirely.

**Bad Example** — updates deferred, lockfile optional

```yaml
# `install` without --frozen-lockfile resolves fresh versions in CI, so CI can
# pass on a dependency tree that no developer has ever run.
- run: npm install
- run: npm test
```

```bash
# Six months later, all at once. Two majors, a transitive breaking change, and
# no way to tell which of the 240 updated packages caused the failure.
npm update && npm audit fix --force
```

`audit fix --force` installs breaking major versions to resolve advisories. Running it without
reading the plan is how a security fix becomes an outage.

---

## Common Mistakes

- Deferring updates until an advisory forces a large, risky migration.
- Auto-merging runtime dependency updates because CI is green.
- Blocking every deploy on `npm audit`, training the team to ignore it.
- Treating severity as priority without checking reachability.
- Undocumented overrides that outlive the problem they solved.
- Lockfile diffs approved without a glance.
- GitHub Actions pinned to a mutable tag.
- Adding a package for something the runtime already provides.
- Never removing anything.

## Production Tips

- Keep a `SECURITY.md` or equivalent stating how advisories are triaged, so urgency is a policy rather than a debate during an incident.
- Batch updates by risk, not by ecosystem — dev tooling, runtime patches, and framework majors deserve different review depth.
- Schedule dependency work as recurring maintenance, not as something done when convenient. See [WordPress — Maintenance](../wordpress/29-maintenance.md) for a cadence that generalizes.
- Before a major-version upgrade, read the changelog and migration guide rather than relying on tests to find the breakage — tests only cover what you thought to test.
- Track dependency count as a standing metric. It only goes up unless someone is watching.

## AI Review Checklist

- Is the new dependency justified against the five questions above?
- Are updates automated with grouping and a schedule, and are security alerts exempt from that schedule?
- Is auto-merge limited to dev tooling with genuinely comprehensive CI?
- Do audits run on a schedule rather than blocking unrelated work?
- Are advisories triaged by reachability, not severity alone?
- Is every override documented with a reason and an exit condition?
- Are lockfiles committed and their diffs reviewed?
- Are CI actions pinned to immutable references?
- Has anything been removed lately?

## Related

- `knowledge/tools/01-package-managers.md`
- `knowledge/tools/28-release-tools.md`
- `knowledge/tools/02-version-management.md`
- `knowledge/tools/26-ai-coding-tools.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/security/23-dependency-security.md`
- `knowledge/security/24-supply-chain-security.md`
