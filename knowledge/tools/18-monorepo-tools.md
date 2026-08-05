---
id: tools/18-monorepo-tools
topic: tools
slug: monorepo-tools
title: "Monorepo Tools"
type: doc
order: 18
status: ready
tags: [tools, monorepo-tools]
related: [tools/01-package-managers, tools/19-task-runners, tools/28-release-tools, tools/03-typescript-compiler, tools/30-engineering-principles]
when_to_use: "Read before setting up or working in a monorepo — configuring workspaces, task orchestration and caching, or deciding whether a monorepo is warranted."
---
# Monorepo Tools

## Purpose

This document defines how to run a JavaScript monorepo: workspaces for dependency linking,
task orchestration with caching, and the boundaries that keep packages from collapsing into
one implicit application.

## Why It Matters

A monorepo trades per-project independence for atomic cross-project changes. That trade is
good when packages genuinely change together and bad when they do not — and the cost of
getting it wrong is asymmetric: splitting a monorepo later is far harder than merging separate
repositories.

The operational problem is task time. Without caching and affected-detection, every pull
request builds and tests everything, and CI time grows linearly with the number of packages
until nobody waits for it.

## Core Principles

- **Workspaces link; the orchestrator schedules.** The package manager resolves internal
  dependencies; Turborepo or Nx decides what to run and what to skip.
- **Cache by input hash.** If the inputs did not change, the output is already known — that is
  what makes a large monorepo viable.
- **Only build what changed.** Affected-detection is not an optimization at scale; it is the
  difference between a five-minute and a fifty-minute pipeline.
- **Package boundaries must be enforced.** Without a rule, packages start importing each
  other's internals and the boundary exists only in the directory layout.

## Best Practices

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

```json
// package.json at the root
{
  "private": true,
  "packageManager": "pnpm@9.12.0",
  "scripts": {
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "verify": "turbo run typecheck lint test build"
  }
}
```

```json
// turbo.json — the dependency graph between tasks
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],          // build dependencies first
      "inputs": ["src/**", "package.json", "tsconfig.json"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "typecheck": { "dependsOn": ["^build"] },
    "lint": {},
    "dev": { "cache": false, "persistent": true }
  }
}
```

The `outputs` field is what makes caching correct: on a hit, Turborepo restores those paths
instead of running the task. Omitting it produces cache hits that leave `dist/` empty — a
confusing failure that looks like a build bug.

Reference internal packages by name, with the workspace protocol:

```json
// apps/web/package.json
{
  "dependencies": {
    "@acme/ui": "workspace:*",
    "@acme/config": "workspace:*"
  }
}
```

## Enforcing Boundaries

```js
// eslint.config.js — packages may not reach into each other's internals
{
  rules: {
    'no-restricted-imports': ['error', {
      patterns: [
        { group: ['@acme/*/src/*'], message: 'Import the package entry point, not its internals.' },
        { group: ['../../../*'], message: 'Cross-package imports must use the package name.' },
      ],
    }],
  },
}
```

Without this, a monorepo becomes one application with directories, and extracting a package
later means untangling every reach-through import.

## Examples

**Good Example** — CI that scales with change size, not repository size

```yaml
- run: pnpm install --frozen-lockfile
- run: pnpm turbo run verify --filter='...[origin/main]'   # only affected packages, plus dependents
  env:
    TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}                # shared remote cache
    TURBO_TEAM: acme
```

A remote cache is what lets CI reuse a colleague's build result. On a repository with a dozen
packages it commonly removes most of the pipeline's work.

**Bad Example** — everything, every time

```yaml
- run: pnpm install
- run: pnpm -r build      # builds all packages
- run: pnpm -r test       # tests all packages
```

A one-line documentation change rebuilds and retests the entire repository.

**Bad Example** — a monorepo that is not one

```
repo/
├── apps/marketing-site/     Next.js, deployed weekly, owned by team A
├── apps/legacy-php-portal/  deployed quarterly, owned by team B
└── packages/nothing-shared/
```

Nothing is shared, releases are independent, and ownership does not overlap. This is three
repositories paying monorepo tooling costs for no benefit.

## Common Mistakes

- Adopting a monorepo for unrelated projects that never change together.
- No task orchestrator, so every job runs everything.
- `outputs` unset in the task config, producing cache hits with missing artifacts.
- Version numbers instead of `workspace:*` for internal dependencies, causing the published
  version to be installed instead of the local one.
- Deep imports across package boundaries.
- One `tsconfig.json` for the entire repository instead of per-package configs with project
  references.
- Hoisting assumptions from npm carried into pnpm's strict layout, exposing undeclared
  dependencies.
- No release strategy, so publishing several interdependent packages becomes manual.

## Production Tips

- Enable remote caching early. Its benefit grows with team size and it costs almost nothing to
  set up.
- Use `--filter` aggressively: `--filter=@acme/ui...` (the package and its dependents) and
  `--filter=...@acme/ui` (the package and its dependencies) cover most needs.
- For publishing, use Changesets — it handles interdependent version bumps and changelogs
  across packages. See [Release Tools](28-release-tools.md).
- Keep shared configuration in a package (`@acme/config`) exporting ESLint, TypeScript, and
  Prettier bases, so packages extend rather than copy.
- Nx offers more built-in generators and a dependency graph UI; Turborepo is simpler and
  configuration-light. Both solve the same core problem — choose by how much structure the
  team wants imposed.

## AI Review Checklist

- Is a monorepo justified by shared code and coordinated releases?
- Are workspaces configured, with internal dependencies using `workspace:*`?
- Does a task orchestrator define the dependency graph, with correct `inputs` and `outputs`?
- Does CI run only affected packages, with caching enabled?
- Are cross-package imports restricted to package entry points?
- Does each package have its own tsconfig, with project references at the root?
- Is there a release strategy for interdependent packages?

## Related

- `knowledge/tools/01-package-managers.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/28-release-tools.md`
- `knowledge/git/24-monorepo.md`
