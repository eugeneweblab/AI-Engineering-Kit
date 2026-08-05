---
id: tools/30-engineering-principles
topic: tools
slug: engineering-principles
title: "Tools Engineering Principles"
type: doc
order: 30
status: ready
tags: [tools, engineering-principles, "@echo", "node:20", "node:latest", engine-strict, engines]
related: [tools/00-overview, tools/19-task-runners, tools/16-git-hooks, tools/99-ai-review-checklist, tools/100-common-antipatterns]
when_to_use: "Read before adding, replacing, or configuring any development tool, as the baseline every tooling decision must satisfy."
---
# Tools Engineering Principles

## Purpose

This document defines the non-negotiable principles for a project's tooling: what must be reproducible, what must be automated, and what must never depend on a particular developer's machine. It is the baseline applied to every tool added or changed, independent of language or ecosystem.

## Why It Matters

Tooling problems are cheap individually and expensive in aggregate. A version that is not pinned costs an afternoon once; multiplied across a team and a year it is a recurring tax nobody attributes to its cause. The same is true of a check that only runs in CI, a hook slow enough to bypass, or a setup step that lives in someone's shell history.

The compounding effect runs the other way too. A project where one command installs everything, one command verifies everything, and CI runs exactly what developers run has a shorter path from clone to first contribution — and every later decision inherits that.

## Core Principles

- **Reproducibility over speed.** A build that is fast and occasionally different is worse than one that is slower and always the same. Pin versions, commit lockfiles, run the same commands everywhere.
- **Configuration lives in the repository.** Not in a developer's editor settings, not in a CI dashboard, not in a wiki page. If it affects the output, it is versioned alongside the code.
- **CI runs what developers run.** A workflow that invokes tools directly instead of project scripts is a second source of truth, and it will drift.
- **One tool per job.** Two formatters, two linters, or two package managers will disagree, and reconciling them becomes permanent overhead.
- **Automate consistency; review substance.** Formatting, import order, and commit shape are machine decisions. Reviewer attention is a scarce resource — spend it on logic.
- **Every gate must be runnable locally.** A check that can only fail in CI is a check developers cannot fix without a push-and-wait cycle.
- **Match the check to the moment.** Editor on save, hook on staged files, CI on everything. A check placed too early gets bypassed; too late and it costs a round trip.
- **Fail loudly.** A warning nobody fixes is a check that does not exist. Run linters with zero-tolerance flags or lower the rule set until zero is achievable.
- **Every tool is a maintenance obligation.** Each one is a config file, an upgrade path, and a supply-chain surface. Removing one is as valuable as adding one.
- **Choose by ecosystem, not benchmark.** Plugin availability, documentation, and community answers outlive speed advantages.

## Best Practices

- Provide exactly one install command and one verify command; make them the entry point for CI and for humans.
- Pin the runtime in a file the tooling reads (`.nvmrc`, `.tool-versions`) and enforce it (`engines` + `engine-strict`).
- Keep the pre-commit budget under a few seconds by operating on staged files only.
- Commit editor configuration that affects behavior; never commit personal preferences.
- Record the reason for every non-default configuration option, override, and suppression.
- Adopt formatters and linters in an isolated commit, recorded in `.git-blame-ignore-revs`.
- Treat tool upgrades like dependency upgrades: scheduled, reviewed, tested.

## Examples

**Bad Example** — a setup that cannot be reproduced

```yaml
# CI: tools invoked directly, versions floating
- uses: actions/setup-node@v4
  with: { node-version: '20' }          # resolves to whatever 20.x is current
- run: npm install                       # rewrites the lockfile
- run: npx eslint src --max-warnings 50  # a backlog, and different from local
- run: npx tsc --project tsconfig.ci.json
```

```
README: "Install pnpm globally, copy .env.example, ask Sergey for the API key,
         then run the migrations twice if the first one fails."
```

Nothing here is reproducible: the runtime floats, the dependency tree is rewritten, the lint threshold differs from local, and setup depends on a colleague.

**Good Example** — the same project, made reproducible

```json
// package.json — one entry point per operation
{
  "packageManager": "pnpm@9.12.0",
  "engines": { "node": ">=20.11 <21" },
  "scripts": {
    "typecheck": "tsc --noEmit",
    "lint": "eslint . --max-warnings 0",
    "test": "vitest run",
    "verify": "pnpm typecheck && pnpm lint && pnpm test",
    "prepare": "husky"
  }
}
```

```yaml
# CI calls the same script a developer does
- uses: actions/setup-node@v4
  with: { node-version-file: '.nvmrc', cache: 'pnpm' }
- run: corepack enable
- run: pnpm install --frozen-lockfile
- run: pnpm verify
```

```makefile
up:  ## Start everything a new contributor needs
	docker compose up -d
	pnpm install --frozen-lockfile
	pnpm db:migrate && pnpm db:seed
	@echo "Ready at http://localhost:3000"
```

Clone, `make up`, `pnpm verify` — and the result is identical to CI.

## Common Mistakes

- Floating runtime and image versions (`node:20`, `node:latest`, bare majors).
- `npm install` in CI instead of the frozen-lockfile command.
- Checks that exist only in CI, or only in an editor.
- Warning backlogs tolerated indefinitely.
- Hooks slow enough that `--no-verify` becomes habit.
- Setup steps documented in prose rather than automated.
- Two tools owning the same job.
- Overrides and suppressions with no recorded reason.
- Tools accumulated and never removed.

## Production Tips

- Measure the clone-to-running time for a new contributor once a quarter; it is the single best proxy for tooling health.
- Keep a `verify` script green on `main` at all times — a permanently red baseline destroys the signal for everyone.
- When a tool is bypassed repeatedly, fix the tool rather than the people; a bypassed gate is feedback about its cost.
- Prefer the boring, widely adopted option for anything load-bearing in the build. Exit cost dominates.

## AI Review Checklist

- Can the project be installed and verified with one command each?
- Are runtime, package manager, and image versions pinned in the repository?
- Does CI call project scripts rather than invoking tools directly?
- Is every gate runnable locally with identical results?
- Is exactly one tool responsible for each job?
- Are warnings treated as failures?
- Is the pre-commit hook fast enough to survive?
- Is configuration committed, with non-default choices explained?
- Has anything been removed recently, or only added?

## Related

- `knowledge/tools/00-overview.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/16-git-hooks.md`
- `knowledge/tools/99-ai-review-checklist.md`
- `knowledge/tools/100-common-antipatterns.md`
