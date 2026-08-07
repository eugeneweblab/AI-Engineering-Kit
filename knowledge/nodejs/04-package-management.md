---
id: nodejs/04-package-management
topic: nodejs
slug: package-management
title: "Node.js Package Management"
type: doc
order: 4
status: ready
tags: [nodejs, package-management, package.json, dependencies, packageManager, engines, pnpm-lock.yaml, postinstall]
related: [nodejs/03-modules, nodejs/18-security, nodejs/26-deployment, nodejs/00-overview, nodejs/14-environment]
when_to_use: "Read before adding a dependency, editing package.json, setting up CI installs, or auditing the supply chain."
---
# Node.js Package Management

## Purpose

This document defines how to manage Node.js dependencies safely: `package.json`,
lockfiles, reproducible installs, semantic-version ranges, and supply-chain hygiene. An
agent that follows it produces builds that install identically everywhere and resist the
dependency-based attacks that are now the most common way Node apps are compromised.

A Node project is defined by `package.json` (declared dependencies and their allowed
version ranges) and a **lockfile** (`package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock`)
that records the exact resolved versions actually installed.

## Why It Matters

Dependencies are the largest and least-trusted part of most Node apps — often hundreds of
transitive packages written by strangers, executing with your app's full privileges. An
unpinned range can pull a different version tomorrow than it did today, turning a green
build red for no code change. A malicious or compromised package can steal secrets or
inject a backdoor at install time. Reproducibility and supply-chain hygiene are therefore
not niceties; they are the difference between a build you can trust and one you cannot.

## Core Principles

- **Commit the lockfile.** It is the source of truth for exact versions. Without it,
  "the same install" means different bytes on different machines.
- **CI installs from the lock, never resolves fresh.** Use `npm ci` (or `pnpm install
  --frozen-lockfile`), which fails if `package.json` and the lock disagree.
- **Understand semver ranges.** `^1.2.3` allows any `1.x`, `~1.2.3` allows `1.2.x`,
  `1.2.3` pins exactly. Ranges are convenient; the lockfile is what actually protects you.
- **Every dependency is attack surface.** Fewer, well-maintained packages beat many
  incidental ones. Audit before adding.
- **`postinstall` scripts run arbitrary code.** A dependency's install hook executes on
  your machine and in CI with full permissions — treat that as a real risk.

## Best Practices

- Pick one package manager per repo (npm, pnpm, or yarn) and commit only its lockfile;
  mixing them produces conflicting locks and non-reproducible installs.
- Separate `dependencies` from `devDependencies` correctly so production images do not
  ship test and build tooling; install prod with `npm ci --omit=dev`.
- Run `npm audit` (or `pnpm audit`) and an automated updater (Dependabot/Renovate) on a
  schedule; patch known vulnerabilities promptly rather than in a big-bang later.
- Pin the runtime and tooling via `engines` and, for the package manager itself,
  `packageManager` (Corepack) so everyone uses the same versions.
- Prefer packages that are actively maintained, have few transitive deps, and publish
  provenance; avoid abandoned or single-maintainer packages for critical paths.
- Disable install scripts for untrusted deps when feasible (`npm ci --ignore-scripts`)
  and re-enable only where genuinely required.

## Examples

**Good Example** — reproducible, minimal, hardened install

```jsonc
// package.json — ranges declared, but the committed lockfile pins exact versions
{
  "name": "billing-service",
  "type": "module",
  "engines": { "node": ">=24 <25" },   // enforce a runtime that still gets fixes
  "packageManager": "pnpm@9.12.0",     // everyone uses the same package manager
  "dependencies": { "zod": "^3.23.8" },
  "devDependencies": { "vitest": "^2.1.0" }
}
```

```bash
# CI: install exactly what the lockfile says, prod deps only, fail on drift.
npm ci --omit=dev            # NOT `npm install`, which can silently update the lock
```

**Bad Example** — non-reproducible and unaudited

```bash
# Resolves fresh against ranges, so today's build may differ from yesterday's,
# pulls in dev tooling for production, and runs every dependency's install hooks.
npm install                  # mutates the lockfile in CI; no --omit=dev
# ...with no lockfile committed and no `npm audit` ever run
```

## Common Mistakes

- Not committing the lockfile, or using `npm install` in CI so versions drift silently.
- Mixing package managers, producing multiple conflicting lockfiles in one repo.
- Putting build/test tools in `dependencies`, bloating and widening the production image.
- Ignoring `npm audit` warnings until a vulnerability is exploited.
- Blindly running `npm update`/`--force` and shipping without re-testing.
- Deep-importing a dependency's internal files, coupling to its private structure.

## Production Tips

- Build production images with `npm ci --omit=dev` and a lockfile copied in first, so the
  dependency layer is cached and reproducible.
- Generate and store an SBOM (`npm sbom` / CycloneDX) for compliance and fast response
  when a CVE lands in a transitive package.
- Consider a private registry or `npm` allowlist for regulated environments to control
  exactly which packages can be installed.

## AI Review Checklist

- Is a single lockfile committed, and does CI use `npm ci` / `--frozen-lockfile`?
- Are production and dev dependencies correctly separated, with prod installs omitting dev?
- Is the runtime pinned via `engines` and the package manager via `packageManager`?
- Has a new dependency been checked for maintenance status, transitive weight, and CVEs?
- Are install scripts from untrusted packages considered and, where possible, disabled?

## Related

- `knowledge/nodejs/03-modules.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/26-deployment.md`
- `knowledge/nodejs/00-overview.md`
- `knowledge/nodejs/14-environment.md`
