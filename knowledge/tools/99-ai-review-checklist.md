---
id: tools/99-ai-review-checklist
topic: tools
slug: ai-review-checklist
title: "AI Review Checklist"
type: doc
order: 99
status: ready
tags: [tools, ai-review-checklist]
related: [tools/98-production-checklist, tools/100-common-antipatterns, tools/30-engineering-principles, tools/27-dependency-management, tools/26-ai-coding-tools]
when_to_use: "Read when reviewing a change that touches tooling — configuration, CI workflows, dependencies, hooks, or build setup."
---
# AI Review Checklist

## Purpose

This is the checklist an agent runs when **reviewing** a change to tooling: a config edit, a CI workflow, a dependency bump, a new hook. Each item is a concrete thing to look for in the diff and flag if wrong.

Where the [production checklist](98-production-checklist.md) gates a project, this gates a *change*.

## Why It Matters

Tooling diffs get less review attention than application code — they look like plumbing, and they usually are. That is exactly why defects survive: a floating version tag, a disabled check, or a widened suppression passes review because it is one line in a config file nobody reads closely.

The failures are also delayed. A lockfile rewritten in CI does not break today; it breaks the week a transitive dependency ships a regression, and by then nobody connects it to the diff.

---

## Version and Dependency Changes

☐ Does a new dependency justify itself — is it maintained, right-sized, and not already provided by the platform?

☐ Is the lockfile updated in the same commit, and does its diff contain only expected changes?

☐ Does the diff introduce a second package manager or a second lockfile?

☐ Are `--force` or `--legacy-peer-deps` being added, and is there a stated reason?

☐ Is a runtime dependency being added to `devDependencies`, or vice versa?

☐ Does an override or resolution appear without a comment explaining what it fixes and when it can go?

☐ Are GitHub Actions pinned to a commit SHA rather than a mutable tag?

---

## Weakened Checks

☐ Is a lint rule being disabled, downgraded to a warning, or suppressed file-wide?

☐ Does a suppression comment name the specific rule and give a reason?

☐ Is `--max-warnings 0` being relaxed, or a warning backlog being accepted?

☐ Is a type error being silenced with `any`, a non-null assertion, or `@ts-ignore` instead of `@ts-expect-error` with a reason?

☐ Is `strict` or a strict sub-option being turned off in `tsconfig.json`?

☐ Is a static-analysis baseline being regenerated rather than reduced?

☐ Is a failing test being skipped, deleted, or edited into passing?

☐ Are security sniffs being excluded from a PHP ruleset?

---

## CI and Reproducibility

☐ Does CI invoke tools directly where a project script exists?

☐ Is the install step using the frozen-lockfile command?

☐ Are runtime versions read from the repository rather than hardcoded in the workflow?

☐ Does a new check exist only in CI, with no way to run it locally?

☐ Is a Docker base image tagged `latest` or with a bare major?

☐ Does the release workflow have a concurrency guard?

---

## Hooks and Local Gates

☐ Does a new hook operate on staged files only?

☐ Would the hook plausibly push pre-commit past a few seconds?

☐ Are tests or type checks being added to pre-commit rather than pre-push?

☐ Do fixers re-stage the files they modify?

☐ Does the hook introduce an interactive prompt?

☐ Does every new hook check also exist in CI?

---

## Configuration Hygiene

☐ Are two tools now responsible for the same job — two formatters, two linters?

☐ Is `eslint-config-prettier` still last in the config array?

☐ Are path aliases mirrored across `tsconfig.json`, the bundler, and the test runner?

☐ Are personal editor preferences being committed as project settings?

☐ Is a large formatting change mixed into a functional commit?

☐ If a formatter was applied repo-wide, is the commit recorded in `.git-blame-ignore-revs`?

---

## Secrets and Data

☐ Does the diff add a credential, token, or `.env` file to version control?

☐ Does a new MCP server, database client, or script point at production?

☐ Is a secret being passed to a tool via a committed config rather than the environment?

☐ Does new instrumentation risk sending PII to a third party?

---

## Release Changes

☐ Are version numbers being hand-edited where tooling should derive them?

☐ Does a breaking change carry the marker that produces a major bump?

☐ Do `files` and `exports` still describe what should ship?

☐ Is publishing moving from CI to a local step?

---

## Flagging

Report anything above as a finding with the file, the line, and what it would cost. Distinguish clearly between what blocks the merge — a committed secret, a silenced type error, a disabled security check — and what is a recommendation, such as a dependency that could be avoided.

## Related

- `knowledge/tools/98-production-checklist.md`
- `knowledge/tools/100-common-antipatterns.md`
- `knowledge/engineering/02-code-review.md`
- `knowledge/tools/27-dependency-management.md`
