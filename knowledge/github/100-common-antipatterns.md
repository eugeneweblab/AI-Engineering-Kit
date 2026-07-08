---
id: github/100-common-antipatterns
topic: github
slug: common-antipatterns
title: "Common Antipatterns"
type: doc
order: 100
status: ready
tags: [github, common-antipatterns]
related: [github/08-actions, github/17-branch-protection, github/16-secret-scanning, github/06-pull-requests, github/30-engineering-principles]
when_to_use: "Read before configuring GitHub workflows, branch rules, or access, to avoid known failure modes."
---
# Common Antipatterns

## Purpose

This document catalogs the recurring mistakes teams make with GitHub — in workflows,
branch rules, access, and process — and gives the correct fix for each. It exists so an
agent can recognize a bad pattern in a diff or a settings screen and replace it with a
safe one, rather than reproducing the mistake.

## Why It Matters

Most GitHub incidents are not novel — they are the same handful of anti-patterns repeated:
a mutable Action tag, a broad token, an unprotected branch. Each looks harmless in
isolation and each has caused real supply-chain compromises. Naming them makes them
catchable.

## Anti-Patterns

### 1. Referencing Actions by mutable tag

Using `uses: some/action@v4` or `@main`.

**Why it is wrong:** A tag is a movable pointer. If the action's maintainer (or an
attacker who compromises them) moves `v4` to a malicious commit, your next run executes
that code with your workflow's permissions and secrets. You reviewed one version and ran
another.

**The fix:** Pin to a full commit SHA and record the version in a comment:
`uses: some/action@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2`. Let Dependabot
propose SHA bumps you can review.

### 2. Granting `write-all` or default-broad token permissions

Leaving `permissions: write-all` or relying on the legacy default read/write token.

**Why it is wrong:** Every step in the job — including third-party Actions — gets full
write access to code, issues, and packages. One compromised dependency can push commits
or publish packages. The token is a standing liability.

**The fix:** Set the org/repo default `GITHUB_TOKEN` to read-only and grant per-job with
an explicit `permissions:` block listing only what that job needs.

### 3. `pull_request_target` that checks out untrusted PR code

Using `pull_request_target` (which has secrets access) and then checking out and running
the fork's code.

**Why it is wrong:** `pull_request_target` runs in the context of the base repo *with
secrets*, but you are executing arbitrary attacker-controlled code from the fork. This is
the canonical secret-exfiltration vulnerability.

**The fix:** Use `pull_request` for anything that runs PR code (no secrets by default).
If you need labels or comments, split into a separate, minimal-privilege workflow that
never checks out the untrusted head.

### 4. Unprotected default branch (or admin bypass)

Allowing direct pushes to `main`, or enabling "allow administrators to bypass."

**Why it is wrong:** Review and CI become optional exactly for the people who make the
riskiest changes. A single force-push can rewrite shared history for everyone.

**The fix:** Apply a [ruleset](18-rulesets.md) or
[branch protection](17-branch-protection.md) that requires PRs and status checks, blocks
force-pushes, and includes administrators. See [engineering principles](30-engineering-principles.md).

### 5. Secrets committed to the repo

Pasting an API key into code, a `.env` file, or a workflow YAML.

**Why it is wrong:** Git history is permanent and often public or widely cloned. Deleting
the file does not remove the secret from history — it is already leaked and must be
rotated.

**The fix:** Store secrets as encrypted Actions/environment secrets. Enable
[secret scanning](16-secret-scanning.md) with push protection to block the commit before
it lands. If a secret leaks, rotate it immediately — do not just rewrite history.

### 6. Script injection via unescaped context

Writing `run: echo "${{ github.event.pull_request.title }}"` in a shell step.

**Why it is wrong:** A PR title (or branch name, or comment) is attacker-controlled. When
interpolated directly into a shell command it can inject arbitrary commands that run with
the job's permissions.

**The fix:** Pass untrusted values through an `env:` variable and reference `"$TITLE"` in
the script, so the shell treats it as data, not code.

### 7. Long-lived, broad personal access tokens

Sharing a classic PAT with `repo` scope across scripts and CI.

**Why it is wrong:** A broad, non-expiring token is a master key. If it leaks, the
attacker gets everything it can touch, indefinitely, with no easy revocation trail.

**The fix:** Use fine-grained PATs scoped to specific repos and permissions with an
expiry, or a GitHub App / `GITHUB_TOKEN` for CI. Rotate and audit regularly.

### 8. Advisory-only checks and merge-anyway culture

Marking CI as informational, or routinely using "merge without waiting for checks."

**Why it is wrong:** A gate that can be skipped is not a gate. Broken code reaches `main`,
and the green checkmark stops meaning anything.

**The fix:** Make the checks *required* in branch protection. Fix flaky checks rather than
working around them — flakiness is what trains people to bypass gates.

### 9. Giant, mixed-purpose pull requests

One PR that refactors, adds a feature, and reformats a thousand lines.

**Why it is wrong:** No one can review it carefully, so bugs slip through, and it cannot
be reverted cleanly because the good and bad changes are entangled.

**The fix:** Split into small, single-purpose [PRs](06-pull-requests.md). Separate
mechanical changes (formatting, renames) from logic changes.

### 10. Granting access to individuals instead of teams

Adding collaborators one by one to each repo.

**Why it is wrong:** Access sprawls with no single source of truth. Offboarding misses
repos, and no one can answer "who can touch this?" quickly.

**The fix:** Manage access through [teams](20-teams.md) with least-privilege
[permissions](21-permissions.md); add and remove people from teams, not repos.

## AI Review Checklist

- [ ] Are all Actions SHA-pinned rather than referenced by mutable tag?
- [ ] Do workflows use least-privilege `permissions:` instead of `write-all`?
- [ ] Is untrusted PR code kept out of secret-bearing (`pull_request_target`) contexts?
- [ ] Is the default branch protected for everyone, with required checks that cannot be skipped?
- [ ] Are secrets stored as encrypted secrets, with scanning/push-protection on?
- [ ] Is access managed via teams and fine-grained, expiring tokens?

## Related

- `knowledge/github/08-actions.md`
- `knowledge/github/17-branch-protection.md`
- `knowledge/github/16-secret-scanning.md`
- `knowledge/github/06-pull-requests.md`
- `knowledge/github/30-engineering-principles.md`
