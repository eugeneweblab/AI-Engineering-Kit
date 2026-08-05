---
id: tools/16-git-hooks
topic: tools
slug: git-hooks
title: "Git Hooks"
type: doc
order: 16
status: ready
tags: [tools, git-hooks]
related: [tools/17-commit-conventions, tools/04-eslint, tools/05-prettier, tools/19-task-runners, tools/30-engineering-principles]
when_to_use: "Read before adding pre-commit or pre-push automation — choosing a hook manager, deciding what belongs in each hook, and keeping hooks fast enough to survive."
---
# Git Hooks

## Purpose

This document defines how to use Git hooks as a local quality gate: which checks belong at
which hook, how to keep them fast, and why hooks complement CI rather than replace it.

## Why It Matters

A hook catches a defect seconds after it is written, when the fix costs nothing. The same
defect caught in CI costs a push, a wait, a context switch, and a second commit.

But hooks are also the easiest tooling to make counterproductive. Every second added to
`pre-commit` is paid on every commit by every developer, and the moment it becomes annoying
people commit with `--no-verify`. At that point the hook protects nobody while still costing
everybody.

## Core Principles

- **Hooks are a fast local gate; CI is the authority.** Anything that must never reach main
  belongs in CI as a required check, whether or not a hook also runs it.
- **Check only what changed.** Linting the whole repository on every commit is the most common
  reason hooks get bypassed.
- **Budget the time.** Pre-commit under ~5 seconds, pre-push under ~30. Beyond that, move the
  check to CI.
- **Hooks must be installed automatically.** A hook that requires a manual setup step is a
  hook half the team does not have.

## Best Practices

Modern hook managers install themselves through a `prepare` script:

```json
{
  "scripts": { "prepare": "husky" },
  "devDependencies": { "husky": "^9.1.6", "lint-staged": "^15.2.10" },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix --max-warnings 0", "prettier --write"],
    "*.{css,scss}": ["stylelint --fix", "prettier --write"],
    "*.{json,md,yml}": ["prettier --write"],
    "*.php": ["vendor/bin/phpcbf", "vendor/bin/phpcs"]
  }
}
```

```bash
# .husky/pre-commit — fast: staged files only
pnpm lint-staged
```

```bash
# .husky/pre-push — slower checks, run less often
pnpm typecheck
pnpm test:unit
```

lint-staged is the component that makes this viable: it passes only the staged paths to each
tool and re-stages whatever the fixers modified.

For a lighter alternative without Node in the loop, lefthook is a single binary configured in
YAML:

```yaml
# lefthook.yml
pre-commit:
  parallel: true
  commands:
    lint:
      glob: '*.{ts,tsx}'
      run: pnpm eslint --fix --max-warnings 0 {staged_files}
      stage_fixed: true
    php:
      glob: '*.php'
      run: vendor/bin/phpcs {staged_files}
```

## What Belongs Where

| Check | pre-commit | pre-push | CI |
|---|---|---|---|
| Format staged files | ✓ | | ✓ (verify) |
| Lint staged files | ✓ | | ✓ (all files) |
| Commit message format | ✓ (commit-msg) | | ✓ |
| Type check | | ✓ | ✓ |
| Unit tests | | ✓ | ✓ |
| Integration tests | | | ✓ |
| E2E, build, security scan | | | ✓ |
| Secret detection | ✓ | | ✓ |

Secret detection is the one check worth its cost at pre-commit regardless of speed: a
credential that reaches the remote must be rotated even after the commit is removed, because
it is already in someone's clone and in the platform's reflog.

```bash
# .husky/pre-commit
pnpm lint-staged
npx secretlint --secretlintignore .gitignore "**/*"
```

## Examples

**Good Example** — the escape hatch used correctly

```bash
# A work-in-progress commit on a personal branch, deliberately skipping hooks.
git commit --no-verify -m "wip: exploring the parser rewrite"
```

Hooks should be skippable. What matters is that CI is not, so a bypassed hook delays feedback
rather than defeating it.

**Bad Example** — a hook nobody keeps

```bash
# .husky/pre-commit
pnpm lint          # entire repository
pnpm typecheck     # entire repository
pnpm test          # full suite, including E2E
pnpm build         # production build
```

Four minutes per commit. Within a week, `--no-verify` is in everyone's muscle memory and the
hooks are dead weight.

**Bad Example** — hooks that are not installed

```bash
# README: "After cloning, run `npx husky install` to set up hooks."
```

Documentation is not installation. Without the `prepare` script, hooks exist only for the
people who read that line.

## Common Mistakes

- Running full-repository checks on every commit.
- No `prepare` script, so hooks depend on a manual step.
- Tests in `pre-commit` rather than `pre-push`.
- Fixers that modify files without re-staging them, so the commit contains the unfixed version.
- Hooks that are the only place a check runs, with no CI equivalent.
- Interactive prompts inside hooks, which break GUI clients and IDE integrations.
- No secret detection, the one class of mistake that is expensive to undo.
- Hook scripts not committed (`.git/hooks` is local only) — the manager's directory must be in
  the repository.

## Production Tips

- Measure the hook: `time git commit --allow-empty -m test` tells you what developers actually
  experience.
- Run lint-staged commands in parallel where they touch different file types.
- Keep hook scripts to one line calling a package script, so the logic lives in
  `package.json` and stays testable outside Git.
- If the team uses GUI clients, verify hooks work there — a hook depending on shell aliases or
  interactive input fails in those environments.
- CI must re-run everything the hooks do. Hooks are an optimization for the developer, never a
  guarantee for the repository.

## AI Review Checklist

- Are hooks installed automatically via a `prepare` script or equivalent?
- Does pre-commit operate on staged files only?
- Is the pre-commit budget under a few seconds?
- Are tests and type checks at pre-push rather than pre-commit?
- Does every hook check also run in CI?
- Are fixed files re-staged automatically?
- Is secret detection present?
- Are hooks free of interactive prompts?

## Related

- `knowledge/tools/17-commit-conventions.md`
- `knowledge/tools/04-eslint.md`
- `knowledge/tools/05-prettier.md`
- `knowledge/git/20-hooks.md`
