---
id: security/23-dependency-security
topic: security
slug: dependency-security
title: "Dependency Security"
type: doc
order: 23
status: ready
tags: [security, dependency-security, poetry.lock, go.sum, package-lock.json, package.json]
related: [security/24-supply-chain-security, security/16-secrets-management, security/28-owasp-top10, security/25-monitoring]
when_to_use: "Read before adding a dependency, updating a lockfile, or setting up dependency scanning in CI."
---
# Dependency Security

## Purpose

This document defines how to keep third-party dependencies from becoming your vulnerability:
choosing packages, pinning versions, scanning for known flaws, and patching on a schedule.
It is written so an agent can add and maintain dependencies without importing a known CVE or
an unmaintained package into production.

Most application code by volume is dependencies you did not write. "Vulnerable and outdated
components" is a standing entry in the [OWASP Top 10](28-owasp-top10.md). This doc covers
*known-vulnerable and unmaintained* packages; the deeper problem of *malicious* packages and
compromised build pipelines is [supply-chain security](24-supply-chain-security.md).

## Why It Matters

A single vulnerable transitive dependency — one you never chose directly — can hand an
attacker remote code execution across your fleet. These flaws are public: the moment a CVE
is published, attackers scan the internet for unpatched instances, often faster than teams
patch. The failure mode is not exotic; it is a `package.json` that drifted for a year. The
work is unglamorous but decisive: know exactly what you depend on, be told the day a
component becomes vulnerable, and have a fast, boring path to update it.

## Core Principles

- **Pin with a committed lockfile.** A lockfile (`package-lock.json`, `poetry.lock`,
  `Cargo.lock`, `go.sum`) makes builds reproducible and records the exact resolved tree you
  scanned. Without it, `latest` pulls a different, unscanned tree each build.
- **Scan continuously, not once.** New CVEs are disclosed against versions you already ship.
  A scan in CI plus a daily scan of `main` catches flaws disclosed after you merged.
- **Fewer dependencies is safer.** Every package is attack surface and maintenance debt.
  Prefer the standard library or a small, audited package over a large one pulled in for a
  one-line helper.
- **Update on a cadence, patch out-of-band for criticals.** Routine small updates are cheap
  and safe; a year of skipped updates is a risky big-bang migration. Critical CVEs jump the
  queue.
- **Judge the package, not just the version.** Maintenance status, release recency, and
  maintainer count predict future risk better than the current CVE count.

## Best Practices

- Commit the lockfile and install with the frozen/CI flag (`npm ci`, `pip install
  --require-hashes`, `pnpm install --frozen-lockfile`) so builds fail on lockfile drift.
- Run a vulnerability scanner in CI (`npm audit`, `pip-audit`, `osv-scanner`, Snyk,
  Dependabot/Renovate) and fail the pipeline on high/critical findings.
- Enable automated update PRs (Dependabot/Renovate) with grouped minor updates and a strong
  test suite, so upgrades are continuous and low-risk.
- Before adding a dependency, check: last release date, open-vs-closed issue trend, number
  of maintainers, download count, and whether a smaller alternative exists.
- Generate an SBOM (CycloneDX/SPDX) so you can answer "are we affected?" within minutes of a
  disclosure, including transitive packages.
- Remove unused dependencies; they carry risk while providing no value.

## Examples

**Good Example** — reproducible install, scan gate in CI

```yaml
# CI: install exactly the scanned tree, then fail on known vulnerabilities.
steps:
  - run: npm ci                                  # install from committed lockfile, no drift
  - run: npm audit --audit-level=high            # fail the build on high/critical CVEs
  - run: osv-scanner --lockfile=package-lock.json # cross-check against the OSV database
```

```json
// Dependabot: continuous, grouped update PRs so upgrades stay small and testable.
{ "version": 2, "updates": [
  { "package-ecosystem": "npm", "directory": "/", "schedule": { "interval": "daily" },
    "groups": { "minor-patch": { "update-types": ["minor", "patch"] } } }
]}
```

**Bad Example** — floating versions, no scan

```json
// No lockfile committed; ranges float. Every build resolves a different, unscanned tree.
{ "dependencies": {
  "left-pad": "*",        // whatever version publishes today ships to prod
  "express": "^4"         // silently pulls new transitive deps, none of them scanned
}}
// CI runs `npm install` (not `npm ci`) and never runs an audit → CVEs ship unnoticed.
```

## Common Mistakes

- Not committing the lockfile, so builds are irreproducible and scans meaningless.
- Running `npm install` in CI instead of `npm ci`, letting the tree drift from what you
  reviewed.
- Scanning once at setup and never again, missing CVEs disclosed later.
- Ignoring transitive dependencies, where most vulnerabilities actually live.
- Letting update PRs pile up until upgrading is a scary, deferred migration.
- Adding a heavy package for a trivial helper, expanding attack surface needlessly.
- Suppressing audit warnings without recording why (no expiry, no review).

## Production Tips

- Store the SBOM as a build artifact and keep it queryable; when the next big CVE drops, you
  want the answer in minutes, not a day of grepping.
- Track mean-time-to-patch for critical CVEs as a metric; a rising number is technical debt
  accruing silently.
- Gate merges on the scanner but allow a documented, time-boxed exception process so a false
  positive does not block all delivery.

## AI Review Checklist

- Is a lockfile committed and installed with a frozen/CI flag?
- Does CI run a vulnerability scanner and fail on high/critical findings?
- Are automated update PRs enabled so upgrades are continuous?
- Was each new dependency vetted for maintenance status and a smaller alternative?
- Is an SBOM generated so impact of a new CVE can be assessed quickly?
- Are transitive dependencies covered by the scan, not just direct ones?
- Are suppressed findings documented with a reason and an expiry?

## Related

- `knowledge/security/24-supply-chain-security.md`
- `knowledge/security/16-secrets-management.md`
- `knowledge/security/28-owasp-top10.md`
- `knowledge/security/25-monitoring.md`
