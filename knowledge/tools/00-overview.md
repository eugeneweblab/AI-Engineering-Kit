---
id: tools/00-overview
topic: tools
slug: overview
title: "Tooling Overview"
type: doc
order: 0
status: ready
tags: [tools, overview]
related: [tools/01-package-managers, tools/04-eslint, tools/16-git-hooks, tools/19-task-runners, tools/30-engineering-principles]
when_to_use: "Read first when setting up tooling for a project, to understand which categories of tool are needed and how they fit together."
---
# Tooling Overview

## Purpose

This document is the entry point to the tools topic. It describes the categories of tooling a
project needs, how they compose into a single feedback loop, and which document covers which
decision.

---

## The Shape of a Working Setup

Good tooling forms one pipeline with progressively wider scope. Each stage is cheap enough to
run at its trigger point:

```
editor (on keystroke)   → formatter, language server, type hints
pre-commit (seconds)    → format staged files, lint staged files
pre-push (tens of secs) → type check, unit tests
CI (minutes)            → everything, on every file, plus e2e and build
release                 → version, changelog, publish, deploy
```

The rule that keeps this working: **each stage must be faster than the developer's patience
at that moment**. A pre-commit hook running the full test suite is bypassed with
`--no-verify` within a week, and the check then exists only in theory.

---

## Categories

**Dependency and runtime management** — reproducibility starts here.
[01. Package Managers](01-package-managers.md) · [02. Version Management](02-version-management.md) ·
[27. Dependency Management](27-dependency-management.md)

**Correctness before runtime** — the cheapest defects to fix are the ones found without
running the code.
[03. TypeScript Compiler](03-typescript-compiler.md) · [08. Static Analysis](08-static-analysis.md) ·
[04. ESLint](04-eslint.md) · [06. Stylelint](06-stylelint.md) · [07. PHP Code Standards](07-php-code-standards.md)

**Consistency** — decided once, then never discussed again.
[05. Prettier](05-prettier.md) · [17. Commit Conventions](17-commit-conventions.md) ·
[25. Editor Setup](25-editor-setup.md)

**Build** — turning source into what ships.
[09. Vite](09-vite.md) · [10. Webpack](10-webpack.md) · [11. esbuild and SWC](11-esbuild-and-swc.md) ·
[12. Babel](12-babel.md) · [18. Monorepo Tools](18-monorepo-tools.md) · [19. Task Runners](19-task-runners.md)

**Verification** — proving it works.
[13. Test Runners](13-test-runners.md) · [14. Playwright](14-playwright.md) · [15. Storybook](15-storybook.md)

**Local development** — the environment the work happens in.
[20. Local Environments](20-local-environments.md) · [21. Debuggers](21-debuggers.md) ·
[22. Profilers](22-profilers.md) · [23. API Clients](23-api-clients.md) · [24. Database Tools](24-database-tools.md)

**Automation and delivery.**
[16. Git Hooks](16-git-hooks.md) · [28. Release Tools](28-release-tools.md) ·
[29. Observability Tools](29-observability-tools.md)

**Working with assistants.**
[26. AI Coding Tools](26-ai-coding-tools.md)

---

## Choosing Tools

Four questions, in order of importance:

1. **What does the ecosystem use?** A tool with plugins, examples, and Stack Overflow answers
   is worth more than a faster one without them. This is why ESLint outlives every "faster
   linter" and why Webpack still matters in codebases Vite would build in a tenth of the time.
2. **Does it run identically in CI?** If a check cannot be reproduced locally, developers
   cannot fix what it reports.
3. **What is the exit cost?** A formatter is cheap to remove. A bundler with custom plugins,
   a monorepo orchestrator, or a test framework with thousands of assertions is not.
4. **Who maintains it?** A single-maintainer tool at the center of the build is a risk that
   materializes at the worst time.

Speed is the fifth question, not the first.

---

## What Belongs in the Repository

```
.
├── package.json          scripts, dependencies — the entry point for every task
├── package-lock.json     committed, always
├── composer.json / .lock committed, always
├── .nvmrc / .tool-versions   runtime version, pinned
├── tsconfig.json
├── eslint.config.js
├── .prettierrc
├── phpcs.xml
├── .editorconfig         editor-agnostic basics
├── .github/workflows/    the same commands developers run locally
└── .vscode/extensions.json   recommendations, never enforced settings
```

The test of a correct setup: a new developer clones the repository, runs one install command
and one verify command, and gets exactly what CI gets. Anything requiring a global install, a
manual step, or a Slack message is a defect in the tooling.

---

## Common Failure Modes

- **Two package managers** in one repository, producing two lockfiles that disagree.
- **A formatter added without `.git-blame-ignore-revs`**, destroying `git blame` for the
  whole codebase.
- **Linting and formatting rules that conflict**, so each tool undoes the other.
- **Checks that exist only in CI**, leaving developers unable to reproduce failures.
- **A hook slow enough to be bypassed.**
- **Unpinned runtime versions**, so Node 18 and Node 22 produce different builds.
- **Tools accumulated and never removed** — each one is a config file, an upgrade
  obligation, and a supply-chain surface.

---

## Related Topics

- [CI/CD](../cicd/00-overview.md) — where these tools run automatically.
- [Testing](../testing/00-overview.md) — what to test; this topic covers what runs the tests.
- [Git](../git/00-overview.md) — hooks, history, and conventions.
- [Docker](../docker/00-overview.md) — containerized local environments.
- [Security](../security/23-dependency-security.md) — dependency and supply-chain risk.

---

## Summary

Tooling exists to make defects cheap to find and consistency automatic. Compose it as a
pipeline where each stage matches the developer's patience, pin every version, keep
configuration in the repository, and choose tools by ecosystem support and exit cost rather
than by benchmark.
