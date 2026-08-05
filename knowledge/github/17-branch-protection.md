---
id: github/17-branch-protection
topic: github
slug: branch-protection
title: "Branch Protection"
type: doc
order: 17
status: ready
tags: [github, branch-protection, CODEOWNERS]
related: [github/18-rulesets, github/13-security, github/07-code-review, github/09-workflows, github/06-pull-requests]
when_to_use: "Read before configuring merge rules, required reviews, or required checks on a default branch."
---
# Branch Protection

## Purpose

This document defines how to protect important branches — `main`, release branches — so
that nothing reaches them except reviewed, tested, verifiable code. It covers required
pull requests, required status checks, required reviews, linear history, signed commits,
and the "prevent" layer of repository security. It also points to
[rulesets](18-rulesets.md), the modern successor to classic branch protection.

Branch protection is the **enforcement point** for everything else: it is what turns
[code review](07-code-review.md), [CodeQL](14-codeql.md), and CI from optional advice into
mandatory gates. A detection tool that isn't a *required check* here is decorative.

## Why It Matters

The default branch is what deploys, what everyone forks from, and what auditors examine.
Without protection, a single `git push --force` or a self-approved merge can rewrite
history, bypass every scanner, or ship unreviewed code straight to production. Protection
is also the only technical enforcement of your review and CI policy — process documents do
not stop a tired engineer at 2 a.m.; a required check does. It is the cheapest, highest-
leverage security control on GitHub, and it is **off by default**.

## Core Principles

- **The protected branch is append-only through PRs.** No direct pushes, no force-pushes,
  no branch deletion. All change arrives via reviewed pull request.
- **Rules apply to everyone, including admins.** An enforcement layer with an admin
  exemption is an enforcement layer attackers and mistakes route around. Enable "include
  administrators."
- **Require review by someone other than the author.** Self-merge defeats the purpose of
  review; require at least one approval, and dismiss stale approvals on new commits.
- **Required checks must be green, not just present.** A check that can be skipped or is
  "expected" but never runs is a silent bypass — require the checks that actually gate risk.
- **Prefer rulesets over classic branch protection.** [Rulesets](18-rulesets.md) are
  layerable, support org-wide application, and expose an evaluation history.

## Best Practices

- Require a pull request before merging, with **≥1 approving review** (2 for high-risk
  repos) and **dismiss stale reviews** when new commits are pushed.
- Require **status checks to pass**: CI/tests, [CodeQL](14-codeql.md), and lint. Also
  enable "require branches to be up to date" so checks run against the post-merge state.
- Require **conversation resolution** before merge, so review threads can't be merged over.
- Block **force pushes** and **branch deletion** on protected branches.
- Enable **"include administrators"** so the rules bind privileged accounts too.
- For auditable histories, require **signed commits** and a **linear history**
  (squash/rebase) so every commit is attributable and the graph stays reviewable.
- Require review from **Code Owners** (`CODEOWNERS`) on sensitive paths (infra, auth, CI).

## Examples

**Good Example** — ruleset enforcing review, checks, and no force-push (via API/CLI)

```bash
# A ruleset: PR required, 1 review, stale reviews dismissed, CI+CodeQL required,
# force-push and deletion blocked, and it applies to admins too.
gh api repos/OWNER/REPO/rulesets -X POST -F name='protect-main' -F enforcement=active \
  -f 'conditions[ref_name][include][]=refs/heads/main' \
  -f 'rules[][type]=pull_request' \
  -F 'rules[][parameters][required_approving_review_count]=1' \
  -F 'rules[][parameters][dismiss_stale_reviews_on_push]=true' \
  -f 'rules[][type]=required_status_checks' \
  -f 'rules[][parameters][required_status_checks][][context]=ci' \
  -f 'rules[][parameters][required_status_checks][][context]=CodeQL' \
  -f 'rules[][type]=non_fast_forward'   # blocks force-push; deletion rule added similarly
```

**Bad Example** — protection that looks configured but isn't enforced

```jsonc
// classic branch-protection settings that give a false sense of safety
{
  "required_pull_request_reviews": { "required_approving_review_count": 0 }, // review optional
  "enforce_admins": false,           // admins bypass everything → the rule is advisory
  "required_status_checks": null,    // CI/CodeQL can be red and still merge
  "allow_force_pushes": true         // history can be rewritten, erasing the audit trail
}
```

## Common Mistakes

- Leaving "include administrators" off, so privileged accounts silently bypass the rules.
- Requiring 0 reviews or allowing self-approval, making review theater.
- Not requiring status checks (or requiring the wrong ones), so red CI/CodeQL still merges.
- Allowing force-pushes on `main`, letting history — and the audit trail — be rewritten.
- Not dismissing stale reviews, so an approval carries over onto code no one reviewed.
- Protecting `main` but leaving release branches wide open.

## Production Tips

- Manage protection as code via **org-level rulesets** so every repo inherits the same
  baseline instead of relying on per-repo configuration drift.
- Use `CODEOWNERS` + required Code Owner review to route auth/infra/CI changes to the right
  reviewers automatically.
- Combine required checks with **merge queue** on busy repos so checks always run against
  the actual merged result, not a stale branch.
- Periodically export ruleset config and diff it in CI to catch someone loosening a rule.

## AI Review Checklist

- Is direct push and force-push to the protected branch blocked?
- Is a PR with ≥1 non-author approval required, with stale reviews dismissed on new commits?
- Are the right status checks (CI, CodeQL, lint) required and the branch kept up to date?
- Is "include administrators" enabled so the rules bind privileged accounts?
- Are sensitive paths gated by `CODEOWNERS` required review?
- Is protection managed via org-level rulesets rather than per-repo drift?

## Related

- `knowledge/github/18-rulesets.md`
- `knowledge/github/13-security.md`
- `knowledge/github/07-code-review.md`
- `knowledge/github/09-workflows.md`
- `knowledge/github/06-pull-requests.md`
