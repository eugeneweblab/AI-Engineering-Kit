---
id: tools/02-version-management
topic: tools
slug: version-management
title: "Version Management"
type: doc
order: 2
status: ready
tags: [tools, version-management]
related: [tools/01-package-managers, tools/20-local-environments, tools/00-overview, tools/27-dependency-management, tools/30-engineering-principles, docker/00-overview]
when_to_use: "Read before pinning language runtimes for a project — Node, PHP, or Python versions across developers, CI, and production."
---
# Version Management

## Purpose

This document defines how to pin and switch language runtimes: declaring the version a
project requires, making every developer and CI job use it, and keeping local, CI, and
production on the same major.

## Why It Matters

The runtime version is a dependency that people forget to declare. A project built on Node 22
and deployed to Node 18 fails on syntax that was fine locally; a PHP 8.3 codebase on a
PHP 8.1 host fails on typed constants. These failures surface at deploy time — the most
expensive moment to discover them — and the fix is always the same one line that was never
written down.

## Core Principles

- **Declare the version in the repository.** A version that lives in someone's shell profile
  is not declared.
- **One source of truth per project.** CI, Docker, and the local switcher should all read the
  same file.
- **Match production's major version locally.** Minor drift is tolerable; a major difference
  makes local testing meaningless.
- **Enforce, do not document.** `engines` with `engine-strict` fails the install; a line in
  the README does not.

## Best Practices

Pin the runtime in a file the tooling already understands:

```bash
# .nvmrc — read by nvm, fnm, and actions/setup-node via node-version-file
20.11.1
```

```bash
# .tool-versions — asdf and mise, for projects with more than one runtime
nodejs 20.11.1
php 8.3.6
```

Enforce it in `package.json` so a mismatched install fails immediately:

```json
{
  "engines": { "node": ">=20.11 <21", "pnpm": ">=9" },
  "packageManager": "pnpm@9.12.0"
}
```

```ini
; .npmrc — without this, "engines" is only advisory
engine-strict=true
```

Make the switcher automatic rather than a step people forget:

```bash
# fnm — switches on cd into a directory containing .nvmrc
eval "$(fnm env --use-on-cd)"
```

For PHP, declare the requirement where the tooling checks it:

```json
{
  "require": { "php": "^8.3" },
  "config": { "platform": { "php": "8.3.6" } }
}
```

The `platform` setting is the important one: it makes Composer resolve dependencies for the
production PHP version even when the developer runs a different one.

## Examples

**Good Example** — one pinned version, used everywhere

```yaml
# .github/workflows/ci.yml
- uses: actions/setup-node@v4
  with:
    node-version-file: '.nvmrc'    # same file the developer's shell reads
    cache: 'pnpm'
```

```dockerfile
# Dockerfile — the same version, explicit rather than "latest"
FROM node:20.11.1-alpine AS build
```

**Bad Example** — three different versions, none of them declared

```yaml
- uses: actions/setup-node@v4
  with: { node-version: '20' }     # resolves to whatever 20.x is current today
```

```dockerfile
FROM node:latest                    # changes under you between builds
```

```bash
# Developer's machine: whatever nvm happened to have active
$ node -v
v18.17.0
```

Nothing here is wrong on its own, and together they guarantee that "works locally" carries no
information.

## Common Mistakes

- No `.nvmrc` or `.tool-versions`, so the version lives in tribal knowledge.
- `node-version: '20'` in CI while the developer runs 20.11.1 — a floating minor.
- `FROM node:latest` or `FROM php:8` in a Dockerfile.
- `engines` declared without `engine-strict`, making it decorative.
- Composer resolving against the developer's PHP rather than production's, via a missing
  `config.platform`.
- Upgrading a major version in CI without upgrading it locally, or the reverse.
- Global tool installs tied to one runtime version, breaking after a switch.

## Production Tips

- Track the runtime's end-of-life dates and schedule upgrades before support ends, not after
  a security advisory forces it.
- Upgrade one major at a time, on a branch, with the full test suite — runtime upgrades break
  transitive dependencies more often than application code.
- Keep the Docker base image on a specific patch tag and update it deliberately; `latest` and
  bare majors defeat reproducible builds.
- When production is managed by a host that controls the runtime (many WordPress hosts), pin
  local and CI to exactly what the host runs, and re-check after their upgrades.

## AI Review Checklist

- Is the runtime version declared in a file in the repository?
- Do CI, Docker, and local tooling all read that same version?
- Is `engines` enforced rather than advisory?
- For PHP, does `config.platform` match the production runtime?
- Are Docker base images pinned to a patch version rather than `latest`?
- Is the pinned version still supported upstream?

## Related


- `knowledge/tools/01-package-managers.md`
- `knowledge/tools/20-local-environments.md`
- `knowledge/tools/00-overview.md`
- `knowledge/tools/27-dependency-management.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/docker/00-overview.md`
