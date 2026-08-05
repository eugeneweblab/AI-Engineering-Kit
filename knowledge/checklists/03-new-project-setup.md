---
id: checklists/03-new-project-setup
topic: checklists
slug: new-project-setup
title: "New Project Setup Checklist"
type: doc
order: 3
status: ready
tags: [checklists, new-project-setup, "@github", CLAUDE.md, AGENTS.md, README.md, engine-strict, packageManager]
related: [checklists/01-pre-launch, tools/98-production-checklist, tools/19-task-runners, tools/20-local-environments, tools/26-ai-coding-tools, templates/02-architecture-decision-record]
when_to_use: "Run when starting a new repository, before writing the first feature."
---
# New Project Setup Checklist

## Purpose

What to establish before the first feature, while it is still cheap. Every item here becomes
harder to add once there is code: a formatter applied in month six rewrites the whole
repository, a test framework chosen in month twelve inherits a codebase built without tests.

---

## Repository

☐ `README.md` states what this is, how to run it, and how to verify it — in that order.

☐ `.gitignore` covers dependencies, build output, environment files, and editor state.

☐ `.gitattributes` normalizes line endings (`* text=auto eol=lf`).

☐ Branch protection on the default branch: no direct pushes, CI required.

☐ A licence file, if the answer to "can someone else use this" is not obviously no.

---

## Reproducibility

☐ Runtime version pinned in a committed file (`.nvmrc`, `.tool-versions`).

☐ One package manager, pinned via `packageManager` or equivalent.

☐ Lockfile committed from the first install.

☐ `engines` declared and enforced (`engine-strict`).

☐ Docker base images pinned to a patch tag, if containerized.

See [Tools — Version Management](../tools/02-version-management.md).

---

## Entry Points

☐ One command installs everything.

☐ One command starts the application, including services and seed data.

☐ One `verify` command runs every check and exits non-zero on failure.

☐ CI calls those scripts rather than invoking tools directly.

☐ A reset command returns the local environment to a known-good state.

See [Tools — Task Runners](../tools/19-task-runners.md).

---

## Quality Gates

☐ Formatter configured, run on save and on staged files.

☐ Linter configured with zero tolerance for warnings.

☐ Type checking runs as a separate step from bundling.

☐ Test runner configured, with one example test that passes.

☐ Git hooks install automatically and complete in seconds.

☐ Secret detection runs before commit.

☐ Commit message convention chosen and enforced.

**Do this on day one.** Adopting a formatter later means one commit that touches every file
and destroys `git blame` — recoverable with `.git-blame-ignore-revs`, but avoidable entirely
by starting with it.

---

## Local Environment

☐ Services run in containers, at production's major versions.

☐ `.env.example` committed, listing every variable the app needs.

☐ Environment variables validated at startup with an error naming what is missing.

☐ Seed data exists and reflects realistic volume, not three rows.

☐ Outgoing mail is caught locally.

☐ `.env` and credentials are gitignored, and no secret has ever been committed.

See [Tools — Local Environments](../tools/20-local-environments.md).

---

## CI

☐ Runs on every pull request, not only on the default branch.

☐ Installs with the frozen-lockfile command.

☐ Runs the same `verify` script developers run.

☐ Caches dependencies by lockfile hash.

☐ Actions pinned to a commit SHA rather than a mutable tag.

☐ Fails the build on any check — no soft warnings.

---

## Conventions Written Down

☐ Project instructions file (`AGENTS.md` / `CLAUDE.md`) stating stack, conventions, and
constraints.

☐ Folder structure decided and documented, rather than emerging.

☐ Naming conventions stated where they are not obvious from the framework.

☐ Where business logic belongs, and what must stay out of the presentation layer.

☐ A PR template, so descriptions answer why from the first change.

See [Tools — AI Coding Tools](../tools/26-ai-coding-tools.md).

---

## Delivery

☐ Deployment target chosen, and a trivial change deployed end to end — before there is
anything to lose.

☐ Rollback path tested once, deliberately.

☐ Error tracking configured with a release marker.

☐ Structured logging in place, with a request identifier.

☐ Dependency update automation configured with grouping and a schedule.

---

## Decide Early, Write It Down

Some choices are expensive to reverse and worth an ADR on day one:

☐ How money, dates, and timezones are represented.

☐ Where authoritative state lives, and what is cache.

☐ Authentication and session model.

☐ Multi-tenancy — or the explicit decision that there is none.

See [Templates — Architecture Decision Record](../templates/02-architecture-decision-record.md).

---

## Sign-off

The project is set up when someone can clone it, run two commands, and get a working
application identical to what CI sees — and when the first real feature can be written
without deciding any of the above.

## Examples

**Good Example** — the setup is a command, and the checks are enforced

```bash
# One documented command takes a new machine to a running app.
git clone git@github.com:acme/app.git && cd app
cp .env.example .env          # every required variable, no values
pnpm install --frozen-lockfile
pnpm db:up && pnpm db:migrate && pnpm db:seed
pnpm dev                      # http://localhost:3000
```

```json
{
  "scripts": {
    "verify": "pnpm typecheck && pnpm lint && pnpm test && pnpm build",
    "prepare": "husky"
  },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --max-warnings 0 --fix", "prettier --write"]
  },
  "packageManager": "pnpm@9.12.0"
}
```

```yaml
# The same `verify` in CI, plus a branch protection rule that requires it.
- run: pnpm install --frozen-lockfile
- run: pnpm verify
```

Formatting, linting, and the test suite are decided once, run identically on every machine,
and enforced before merge rather than argued about in review.

**Bad Example** — a README with steps and good intentions

```markdown
## Setup

1. Install Node (we're on 18 or 20, either is fine)
2. `npm install`
3. Set up your `.env` — ask someone on the team for the values
4. Point it at the staging database

We use Prettier, please format your code before committing.
```

Two Node versions means two lockfile resolutions. "Ask someone" means the required variables
are undocumented. Pointing local development at the shared staging database means one
developer's test data is everyone's. "Please format" is not enforcement.

---

## Related

- `knowledge/checklists/01-pre-launch.md`
- `knowledge/tools/98-production-checklist.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/20-local-environments.md`
- `knowledge/tools/26-ai-coding-tools.md`
- `knowledge/templates/02-architecture-decision-record.md`
