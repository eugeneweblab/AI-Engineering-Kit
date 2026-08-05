---
id: tools/19-task-runners
topic: tools
slug: task-runners
title: "Task Runners"
type: doc
order: 19
status: ready
tags: [tools, task-runners]
related: [tools/01-package-managers, tools/18-monorepo-tools, tools/16-git-hooks, tools/20-local-environments, tools/30-engineering-principles, cicd/00-overview]
when_to_use: "Read before organizing project commands — npm scripts, Make, or a task runner — so the same commands work locally and in CI."
---
# Task Runners

## Purpose

This document defines how to expose a project's operations as commands: naming them
consistently, composing them without duplication, and ensuring CI runs exactly what developers
run.

## Why It Matters

Every project accumulates operations — install, build, test, lint, migrate, seed, deploy. Where
those live determines whether a new developer is productive in ten minutes or spends a day
asking questions.

The specific failure this prevents: CI running a subtly different command than the developer.
When `pnpm test` locally and `vitest run --coverage --reporter=json` in CI diverge, a green
local run means nothing, and debugging happens through push-and-wait cycles.

## Core Principles

- **One documented entry point per operation.** If a task needs a comment explaining the flags,
  those flags belong in the script, not in the README.
- **CI calls the same scripts developers do.** A workflow file containing tool invocations is
  duplication that will drift.
- **Compose, do not duplicate.** `verify` should call `lint`, `typecheck`, and `test` rather
  than restate them.
- **Names should be predictable.** `dev`, `build`, `test`, `lint`, `format`, `verify` mean the
  same thing in every project; inventing new names costs onboarding time.

## Best Practices

```json
{
  "scripts": {
    "dev": "vite",
    "build": "pnpm typecheck && vite build",
    "preview": "vite preview",

    "typecheck": "tsc --noEmit",
    "lint": "eslint . --max-warnings 0",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check .",

    "test": "vitest run",
    "test:watch": "vitest",
    "test:e2e": "playwright test",

    "db:migrate": "prisma migrate deploy",
    "db:seed": "tsx scripts/seed.ts",

    "verify": "pnpm typecheck && pnpm lint && pnpm format:check && pnpm test",

    "prepare": "husky"
  }
}
```

`verify` is the important one. It is what CI runs, what a developer runs before pushing, and
what a reviewer can run on a branch — a single command whose success means "this is
mergeable".

```yaml
# CI calls the script, not the tools
- run: pnpm install --frozen-lockfile
- run: pnpm verify
- run: pnpm build
```

For polyglot projects — PHP and JS in one repository, or anything with shell steps — a
Makefile provides one interface over several ecosystems:

```makefile
.DEFAULT_GOAL := help
.PHONY: help install verify test lint fix up down

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies
	composer install
	pnpm install --frozen-lockfile

verify: lint test  ## Run every check

lint:  ## Lint PHP and JS
	vendor/bin/phpcs
	vendor/bin/phpstan analyse
	pnpm lint

test:  ## Run all test suites
	vendor/bin/phpunit
	pnpm test

up:  ## Start the local environment
	docker compose up -d
	@echo "Ready at http://localhost:8080"
```

The self-documenting `help` target matters more than it looks: `make help` replaces the
section of the README that always goes stale.

## Examples

**Good Example** — a workflow that cannot drift from local behavior

```yaml
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version-file: '.nvmrc', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm verify        # identical to what developers run
```

**Bad Example** — CI as a second, divergent source of truth

```yaml
- run: npx eslint src --ext .ts,.tsx --max-warnings 0 --format junit
- run: npx tsc --noEmit --project tsconfig.build.json
- run: npx vitest run --coverage --reporter=junit --outputFile=results.xml
```

None of this is reproducible locally. When it fails, the developer's only option is to guess
and push again.

**Bad Example** — scripts that hide required setup

```json
{
  "scripts": {
    "dev": "vite"
  }
}
```

```
README: "Before running dev, copy .env.example to .env, start Docker,
run migrations, and seed the database."
```

Four manual steps that a `predev` script or a `make up` target would perform automatically.

## Common Mistakes

- CI invoking tools directly instead of project scripts.
- No composite `verify` script, so "did I run everything?" has no answer.
- Setup steps documented in prose rather than automated.
- Scripts requiring environment variables with no defaults and no validation.
- Long shell pipelines inline in `package.json`, where they cannot be read or tested.
- Different names for the same operation across repositories.
- `npm-run-all` or `concurrently` used where `&&` would do, adding a dependency for nothing.
- Scripts assuming a specific shell, breaking on Windows.

## Production Tips

- Keep anything longer than a line or two in `scripts/*.ts` or `scripts/*.sh` and call it from
  the script entry — that code can then be linted and tested.
- Use `--continue-on-error` semantics (via `npm-run-all --continue-on-error` or `make -k`) for
  verification runs, so one run reports every failure rather than only the first.
- Validate required environment variables at the start of any script that needs them, with a
  message naming the missing variable.
- In a monorepo, root scripts should delegate to the orchestrator (`turbo run test`) rather
  than iterating packages by hand — see [Monorepo Tools](18-monorepo-tools.md).
- Prefix scripts by domain (`db:`, `test:`, `docker:`) once there are more than a dozen; the
  grouping makes `npm run` output navigable.

## AI Review Checklist

- Does every operation have a named script?
- Is there a single `verify` command that runs all checks?
- Does CI call scripts rather than tools directly?
- Is environment setup automated rather than documented?
- Are complex commands extracted into files instead of inline strings?
- Do script names follow the conventional set?
- Are required environment variables validated with clear errors?

## Related

- `knowledge/tools/01-package-managers.md`
- `knowledge/tools/18-monorepo-tools.md`
- `knowledge/tools/16-git-hooks.md`
- `knowledge/tools/20-local-environments.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/cicd/00-overview.md`
