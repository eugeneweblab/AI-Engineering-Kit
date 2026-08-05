---
id: tools/98-production-checklist
topic: tools
slug: production-checklist
title: "Tools Production Checklist"
type: doc
order: 98
status: ready
tags: [tools, production-checklist, config.platform, publint, packageManager]
related: [tools/30-engineering-principles, tools/19-task-runners, tools/02-version-management, tools/28-release-tools, tools/29-observability-tools, tools/99-ai-review-checklist, tools/100-common-antipatterns, cicd/98-production-checklist]
when_to_use: "Read before declaring a project's tooling ready — at setup, before onboarding contributors, or before the first production release."
---
# Tools Production Checklist

## Purpose

This is a verifiable checklist for a project's tooling. Every item is a yes/no question an agent can confirm against the repository — not advice to consider. If an item is unchecked, the setup is not ready for a team or for production.

It turns the guidance in [Engineering Principles](30-engineering-principles.md) into a gate.

## Why It Matters

Tooling gaps are invisible while one person works on a project and expensive the moment a second joins or the first release ships. Nobody notices an unpinned runtime until two machines produce different builds, or a missing verify command until a broken commit reaches `main`. Each item below is a control whose absence only surfaces at the worst time.

---

## Reproducibility

**Rules:** [Package Managers](01-package-managers.md) · [Version Management](02-version-management.md)

☐ Runtime version is pinned in a committed file (`.nvmrc`, `.tool-versions`, or equivalent).

☐ CI, Docker, and local tooling all read that same version.

☐ Exactly one package manager is in use, pinned via `packageManager` or equivalent.

☐ Lockfiles are committed for every ecosystem in the repository.

☐ CI installs with the frozen-lockfile command, not the developer install command.

☐ Docker base images are pinned to a specific patch tag, not `latest` or a bare major.

☐ For PHP projects, `config.platform` matches the production runtime.

---

## Entry Points

**Rules:** [Task Runners](19-task-runners.md) · [Monorepo Tools](18-monorepo-tools.md)

☐ One documented command installs everything.

☐ One command (`verify` or equivalent) runs every check and exits non-zero on failure.

☐ One command starts the application locally, including services and seed data.

☐ CI calls those scripts rather than invoking tools directly.

☐ There is a reset path that returns the local environment to a known-good state.

---

## Correctness Gates

**Rules:** [ESLint](04-eslint.md) · [Test Runners](13-test-runners.md)

☐ Type checking runs as a required CI check (`tsc --noEmit` or equivalent).

☐ Linting runs with zero tolerance for warnings.

☐ Formatting is verified in CI (`--check`), not applied.

☐ Tests run in CI and pass on `main`.

☐ For PHP, static analysis runs with a level the codebase sustains, plus a baseline for legacy debt.

☐ Every gate can be reproduced locally with the same result.

---

## Configuration in the Repository

**Rules:** [Prettier](05-prettier.md) · [Editor Setup](25-editor-setup.md)

☐ `.editorconfig` exists and covers every language in use.

☐ `.gitattributes` normalizes line endings.

☐ Linter, formatter, and type-checker configs are committed.

☐ Committed editor settings contain project behavior only, no personal preferences.

☐ Every non-default option, override, and suppression has a recorded reason.

---

## Automation

**Rules:** [— Git Hooks](16-git-hooks.md) · [Commit Conventions](17-commit-conventions.md)

☐ Git hooks install automatically on dependency install.

☐ Pre-commit operates on staged files only and completes in a few seconds.

☐ Secret detection runs before commit.

☐ Every hook check also runs in CI.

☐ Dependency updates are automated with grouping and a schedule.

☐ Security advisories bypass the update schedule.

---

## Local Environment

**Rules:** [Local Environments](20-local-environments.md)

☐ Service versions match production majors.

☐ A committed `.env.example` lists every required variable.

☐ Environment variables are validated at startup with clear errors.

☐ Seed data exists and reflects realistic volume.

☐ Outgoing mail is caught locally and cannot reach real addresses.

☐ No secrets are committed; `.env` and credentials are gitignored.

---

## Release and Observability

**Rules:** [Release Tools](28-release-tools.md) · [Observability Tools](29-observability-tools.md)

☐ Version numbers are derived by tooling, not hand-edited.

☐ Publishing happens from CI, with short-lived credentials where the registry supports them.

☐ Published artifacts are validated before release (`npm pack --dry-run`, `publint`).

☐ Error tracking is configured with release, environment, and uploaded sourcemaps.

☐ Logs are structured and carry a request identifier.

☐ Redaction of secrets and PII happens in the application, not only vendor-side.

☐ Alerts fire on user-visible symptoms and name an action.

---

## Sign-off

The tooling is ready when a new contributor can clone the repository, run the install command and the verify command, and get exactly what CI gets — with no manual steps, no missing credentials, and nobody to ask.

## Related

- `knowledge/tools/30-engineering-principles.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/02-version-management.md`
- `knowledge/tools/28-release-tools.md`
- `knowledge/tools/29-observability-tools.md`
- `knowledge/tools/99-ai-review-checklist.md`
- `knowledge/tools/100-common-antipatterns.md`
- `knowledge/cicd/98-production-checklist.md`
