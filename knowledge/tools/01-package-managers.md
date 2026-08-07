---
id: tools/01-package-managers
topic: tools
slug: package-managers
title: "Package Managers"
type: doc
order: 1
status: ready
tags: [tools, package-managers, package.json, packageManager, node_modules, node-version-file, devDependencies, composer.lock]
related: [tools/02-version-management, tools/18-monorepo-tools, tools/27-dependency-management, tools/00-overview, tools/30-engineering-principles, tools/19-task-runners]
when_to_use: "Read before choosing or changing a package manager, adding dependencies, or debugging an install that differs between machines and CI."
---
# Package Managers

## Purpose

This document defines how to manage dependencies with npm, pnpm, yarn, and Composer: which
lockfile discipline makes installs reproducible, how to pin the manager itself, and how to
avoid the install that works locally and fails in CI.

## Why It Matters

A package manager decides what code actually runs in production. Two developers with the same
`package.json` and different lockfile handling get different dependency trees — and the bug
only appears on one machine. The failure is expensive because it looks like an application
bug: a subtle behavior difference in a transitive dependency nobody chose directly.

Reproducibility is the entire job. Speed differences between managers matter far less than
whether every install produces the same tree.

## Core Principles

- **Commit the lockfile.** Always, including for libraries. The lockfile records what was
  tested; `package.json` records only what is permitted.
- **One manager per repository.** Two lockfiles mean two dependency trees, and CI resolves a
  different one than the developer did.
- **Use the CI install command, not the developer one.** `npm ci` and
  `pnpm install --frozen-lockfile` fail when the lockfile is stale instead of silently
  updating it.
- **Pin the manager itself** with `packageManager`, so everyone resolves dependencies the
  same way.
- **Dependencies vs devDependencies is a production decision.** Anything imported by shipped
  code is a dependency, regardless of when it runs.

## Best Practices

- Enable Corepack so the pinned manager version is used automatically:

```json
{
  "packageManager": "pnpm@9.12.0",
  "engines": { "node": ">=24.19", "pnpm": ">=9" }
}
```

- Prefer **pnpm** for monorepos and for disk efficiency; its strict `node_modules` layout also
  catches undeclared dependencies that npm's flat tree hides.
- Keep `package.json` scripts as the single entry point — `npm run verify` should work
  regardless of which tools sit behind it.
- Use overrides to force a transitive version rather than forking a package:

```json
{ "overrides": { "semver": "^7.6.3" } }
```

- For PHP, commit `composer.lock` and install with `--no-dev` in production:

```bash
composer install --no-dev --optimize-autoloader --no-interaction
```

## Examples

**Good Example** — a CI install that cannot drift

```yaml
- uses: actions/setup-node@v4
  with:
    node-version-file: '.nvmrc'   # one source of truth for the runtime
    cache: 'pnpm'

- run: corepack enable            # uses the version from "packageManager"
- run: pnpm install --frozen-lockfile   # fails if the lockfile is out of date
- run: pnpm run verify
```

**Bad Example** — three ways to get a different tree than the developer had

```yaml
- run: npm install                # rewrites the lockfile; CI tests an unreviewed tree
- run: npm install -g some-cli    # global state, invisible to the repository
- run: npm install --force        # silences the conflict rather than resolving it
```

**Bad Example** — dependency classification that breaks the build

```json
{
  "dependencies": { "eslint": "^9.0.0" },        // dev tool shipped to production
  "devDependencies": { "react-dom": "^19.0.0" }  // runtime dep missing from a --production install
}
```

## Common Mistakes

- A lockfile in `.gitignore`, or committed from two different managers.
- `npm install` in CI instead of `npm ci`.
- `--force` or `--legacy-peer-deps` used as a default rather than a documented exception.
- Globally installed CLIs that the repository depends on but does not declare.
- Runtime dependencies in `devDependencies`, discovered only by a production install.
- Manual edits to a lockfile.
- Deleting `node_modules` and the lockfile together to "fix" a conflict — that discards the
  tested tree.
- Ignoring peer-dependency warnings that indicate a genuine version mismatch.

## Production Tips

- Run `npm ci --omit=dev` (or the manager's equivalent) in the production image so dev tools
  never ship.
- Cache by lockfile hash in CI; caching by branch produces stale trees.
- Audit on a schedule rather than on every install, so a new advisory does not block an
  unrelated deploy — see [Dependency Management](27-dependency-management.md).
- Keep the install step separate from the build step in Docker layers, so dependency caching
  actually works.

## AI Review Checklist

- Is exactly one lockfile present, and is it committed?
- Does CI use the frozen-lockfile install command?
- Is the package manager pinned via `packageManager`, with Corepack enabled?
- Are runtime and dev dependencies correctly separated?
- Are `--force` and `--legacy-peer-deps` absent, or justified in a comment?
- Does any command depend on a globally installed tool?
- Are overrides documented with the reason they exist?

## Related

- `knowledge/tools/02-version-management.md`
- `knowledge/tools/18-monorepo-tools.md`
- `knowledge/tools/27-dependency-management.md`
- `knowledge/tools/00-overview.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/tools/19-task-runners.md`
