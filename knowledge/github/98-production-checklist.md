---
id: github/98-production-checklist
topic: github
slug: production-checklist
title: "GitHub Production Checklist"
type: doc
order: 98
status: ready
tags: [github, production-checklist]
related: [github/17-branch-protection, github/13-security, github/08-actions, github/16-secret-scanning, github/30-engineering-principles]
when_to_use: "Read before marking a GitHub repository production-ready or onboarding it to CI/CD."
---
# GitHub Production Checklist

## Purpose

This is the verifiable checklist for a GitHub repository that ships production software.
Each item is a yes/no fact you can confirm in the repo's settings, files, or Actions
logs — not an opinion. Treat an unchecked box as a release blocker, not a nice-to-have.

## Why It Matters

A repository that "works" in day-to-day use can still be one unprotected branch or one
leaked token away from a supply-chain incident. The failures this list guards against are
silent until they are catastrophic: a force-push that rewrites history, a secret committed
in plaintext, an Action that exfiltrates credentials. Checking these boxes converts
invisible risk into visible, auditable state.

## Branch Protection & Merge Rules

- [ ] The default branch has a [ruleset](18-rulesets.md) or
      [branch protection](17-branch-protection.md) rule applied.
- [ ] Direct pushes to the default branch are blocked for everyone, including admins.
- [ ] Pull requests require at least one approving review before merge.
- [ ] Required status checks must pass before merge, and "require branches up to date"
      is on so checks run against the merge result.
- [ ] Force-pushes and branch deletion are blocked on protected branches.
- [ ] A `CODEOWNERS` file exists and code-owner review is required for owned paths.
- [ ] Stale approvals are dismissed when new commits are pushed.

## CI/CD & Actions

- [ ] Every merge to production is gated by a required CI workflow (tests, lint, build).
- [ ] Workflows declare `permissions:` explicitly and default the `GITHUB_TOKEN` to
      `contents: read`.
- [ ] All third-party [Actions](08-actions.md) are pinned to a full commit SHA.
- [ ] Deployment [workflows](09-workflows.md) use environments with required reviewers
      for production.
- [ ] Secrets are stored as encrypted Actions/environment secrets, never in workflow YAML
      or committed files.
- [ ] `pull_request_target` and self-hosted runners on public repos are avoided or
      strictly guarded (they run with elevated trust).
- [ ] Workflow logs have been checked to confirm no secret is printed.

## Security & Supply Chain

- [ ] [Secret scanning](16-secret-scanning.md) with push protection is enabled.
- [ ] [Dependabot](15-dependabot.md) alerts and security updates are enabled.
- [ ] [CodeQL](14-codeql.md) or an equivalent SAST scan runs on PRs to the default branch.
- [ ] A `SECURITY.md` documents how to report vulnerabilities.
- [ ] Dependency review is enabled to block PRs that introduce known-vulnerable packages.
- [ ] The dependency graph is enabled so alerts and reviews have data to work from.

## Access & Permissions

- [ ] Repository access is granted through [teams](20-teams.md), not to individuals.
- [ ] [Permissions](21-permissions.md) follow least privilege — no unnecessary admins.
- [ ] Deploy keys and machine tokens are scoped to a single repo and rotated.
- [ ] Fine-grained personal access tokens are used instead of classic broad-scope tokens.
- [ ] Outside collaborators are reviewed and time-boxed.

## Releases & Traceability

- [ ] [Releases](11-releases.md) are tagged and immutable; artifacts are attached or
      published to [Packages](10-packages.md).
- [ ] Release notes are generated from merged PRs so every shipped change is traceable.
- [ ] Tags are protected by a ruleset so they cannot be moved or deleted.
- [ ] The commit deployed to production maps to an exact, reachable tag or SHA.

## Repository Hygiene

- [ ] Issue and PR templates exist and capture required context.
- [ ] A `README.md` explains how to build, test, and run locally.
- [ ] `.gitignore` prevents committing build output, `.env`, and credentials.
- [ ] Repository visibility (private/internal/public) matches the data sensitivity.
- [ ] Archived or unmaintained repos are marked archived, not left ambiguous.

## AI Review Checklist

- [ ] Is the default branch protected against direct pushes and force-pushes, for admins too?
- [ ] Does every production merge pass a required, deterministic CI gate?
- [ ] Are Actions SHA-pinned and workflow tokens scoped to least privilege?
- [ ] Are secret scanning, Dependabot, and SAST all enabled and green?
- [ ] Is repository access granted via teams with least-privilege permissions?
- [ ] Can the production deployment be traced to an immutable tag or SHA?

## Related

- `knowledge/github/17-branch-protection.md`
- `knowledge/github/13-security.md`
- `knowledge/github/08-actions.md`
- `knowledge/github/16-secret-scanning.md`
- `knowledge/github/30-engineering-principles.md`
