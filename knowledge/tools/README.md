---
id: tools/readme
topic: tools
slug: readme
title: "Developer Tooling Standards"
type: index
order: -1
status: ready
tags: [tools]
related: []
when_to_use: "Read first when setting up or changing project tooling, to see how this section's docs fit together and which tool owns which job."
---
# Developer Tooling Standards

## Purpose

This section defines the engineering standards for the tools around the code: package
managers, linters, formatters, type checkers, bundlers, test runners, debuggers, and the
automation that runs them.

Tooling decisions look reversible and are not. A lockfile committed by the wrong package
manager, a formatter added to a mature codebase without a blame-ignore file, or a build tool
chosen for its benchmark rather than its plugin ecosystem — each of those costs weeks later.
The standards here favor boring, reproducible setups over fast ones, because tooling that
fails intermittently is worse than tooling that is merely slower.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Package and version management for JavaScript and PHP
- Type checking and static analysis
- Linting and formatting across languages
- Build tooling: bundlers, transpilers, and monorepo orchestration
- Test runners and browser automation
- Local environments and containerized development
- Debugging and profiling
- Git hooks, commit conventions, and release automation
- Dependency maintenance and security scanning
- Editor configuration, API clients, database tools, and AI coding assistants

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. [Overview](00-overview.md)
- 01. [Package Managers](01-package-managers.md)
- 02. [Version Management](02-version-management.md)
- 30. [Engineering Principles](30-engineering-principles.md)

## Correctness Before Runtime

- 03. [TypeScript Compiler](03-typescript-compiler.md)
- 04. [ESLint](04-eslint.md)
- 05. [Prettier](05-prettier.md)
- 06. [Stylelint](06-stylelint.md)
- 07. [PHP Code Standards](07-php-code-standards.md)
- 08. [Static Analysis](08-static-analysis.md)

## Building

- 09. [Vite](09-vite.md)
- 10. [Webpack](10-webpack.md)
- 11. [esbuild and SWC](11-esbuild-and-swc.md)
- 12. [Babel](12-babel.md)
- 18. [Monorepo Tools](18-monorepo-tools.md)
- 19. [Task Runners](19-task-runners.md)

## Testing and Verification

- 13. [Test Runners](13-test-runners.md)
- 14. [Playwright](14-playwright.md)
- 15. [Storybook](15-storybook.md)

## Local Development

- 20. [Local Environments](20-local-environments.md)
- 21. [Debuggers](21-debuggers.md)
- 22. [Profilers](22-profilers.md)
- 23. [API Clients](23-api-clients.md)
- 24. [Database Tools](24-database-tools.md)
- 25. [Editor Setup](25-editor-setup.md)

## Automation

- 16. [Git Hooks](16-git-hooks.md)
- 17. [Commit Conventions](17-commit-conventions.md)
- 27. [Dependency Management](27-dependency-management.md)
- 28. [Release Tools](28-release-tools.md)

## Working With Assistants and Production

- 26. [AI Coding Tools](26-ai-coding-tools.md)
- 29. [Observability Tools](29-observability-tools.md)

## Verification

- 98. [Production Checklist](98-production-checklist.md)
- 99. [AI Review Checklist](99-ai-review-checklist.md)
- 100. [Common Antipatterns](100-common-antipatterns.md)

---

## Engineering Principles

Every tooling decision should satisfy the following principles:

- Pin versions and commit lockfiles. "Works on my machine" is nearly always an unpinned
  dependency or an unpinned runtime.
- One tool per job. Two formatters, two linters, or two package managers in one repository
  will disagree, and the disagreement becomes a permanent tax.
- Configuration lives in the repository, not in a developer's editor settings or shell
  history.
- Every check that gates a merge must be runnable locally with one command, and produce the
  same result there as in CI.
- Prefer the tool the ecosystem already uses over the faster alternative nobody else has
  adopted — plugin availability outlives benchmark wins.
- Automate formatting; never spend review time on it.
- Fail fast and loudly: a warning nobody reads is a check that does not exist.
- Keep the feedback loop short. A pre-commit hook that takes 30 seconds gets bypassed with
  `--no-verify`.
- Treat tool upgrades like dependency upgrades — scheduled, reviewed, and tested, not
  deferred until forced.
- Every tool added is a permanent maintenance obligation; removing one is as valuable as
  adding one.

---

## Intended Audience

These standards are intended for:

- Frontend, Backend, and Fullstack Engineers
- DevOps and Platform Engineers
- Tech Leads setting up new projects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Tooling should be boring, reproducible, and identical for every developer and for CI. Pin
everything, keep configuration in the repository, give each job exactly one tool, and make
every gate runnable locally with a single command.
