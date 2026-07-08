---
id: github/06-pull-requests
topic: github
slug: pull-requests
title: "Pull Requests"
type: doc
order: 6
status: ready
tags: [github, pull-requests]
related: [github/07-code-review, github/17-branch-protection, github/09-workflows, github/23-cli, github/03-issues]
when_to_use: "Read before opening, structuring, or automating any pull request against a shared repository."
---
# Pull Requests

## Purpose

This document defines how to author and manage a GitHub pull request (PR) so that it
is reviewable, mergeable, and safe. A PR is the unit of change: it proposes a diff from
a head branch into a base branch and carries the discussion, checks, and approvals that
gate the merge. This doc covers scope, description, checks, and merge strategy. It does
not cover the reviewer's job — that is [code review](07-code-review.md).

A PR is a request, not a right. Its purpose is to make a change *easy to verify*, not
just to land code.

## Why It Matters

The PR is the last checkpoint before code reaches the base branch, and the base branch
is what ships. A PR that is too large, poorly described, or green only because checks
were skipped defeats every downstream control — review, CI, and branch protection all
degrade to rubber stamps. Small, well-framed PRs get real review and merge fast; a
2,000-line PR gets an "LGTM" that catches nothing. The size and shape of the PR directly
determines whether bugs are caught here or in production.

## Core Principles

- **One PR, one intent.** A PR should do a single logical thing. Mixing a refactor, a
  feature, and a formatting sweep makes the diff unreviewable and the revert impossible.
- **The description is part of the change.** State *what* changed, *why*, and *how it was
  verified*. Link the issue it closes. A reviewer should not have to guess intent.
- **Green means green.** Never merge with failing or skipped required checks. If a check
  is wrong, fix the check — do not bypass it.
- **Keep it small and short-lived.** Aim for under ~400 lines of diff and merge within a
  day or two. Long-lived branches drift and rot; the cost of a stale branch is silent
  merge conflicts and lost context.
- **The author drives it to merge.** Requesting review, resolving threads, and rebasing
  are the author's responsibility, not the reviewer's.

## Best Practices

- Open the PR against the correct **base branch** and confirm the head branch is up to
  date with base before requesting review, so reviewers see the real diff.
- Write the title as an imperative summary (`Add rate limiting to login endpoint`) and
  keep it aligned with your commit convention so it can be used as the squash message.
- Fill the description with a template: context, change summary, testing done, and
  `Closes #123` so the linked issue auto-closes on merge.
- Open as a **draft** while work is in progress; mark ready for review only when CI is
  green and you would approve it yourself.
- Push fixes as new commits during review (do not force-push mid-review) so reviewers can
  see incremental changes; squash on merge to keep base history clean.
- Enable **auto-merge** so the PR lands the moment required checks pass and approvals are
  in, instead of waiting on a human to click the button.
- Delete the head branch on merge to keep the branch list navigable.

## Examples

**Good Example** — scoped PR opened with a full description via the CLI

```bash
# One intent: a focused feature branch off an up-to-date base.
git switch -c feat/login-rate-limit main
git push -u origin feat/login-rate-limit

# The body explains why + how it was verified; Closes links the issue.
gh pr create \
  --base main \
  --title "Add rate limiting to login endpoint" \
  --body "$(cat <<'EOF'
## Why
Login had no brute-force protection (see #482).

## What
- Adds a 5/min per-IP limiter to POST /login.
- Returns 429 with Retry-After on limit.

## Testing
- Unit tests for limiter window + reset.
- Manual: 6th request in a minute returns 429.

Closes #482
EOF
)"
```

**Bad Example** — a grab-bag PR with an empty description

```bash
git checkout -b updates            # vague branch, no single intent
git add -A                         # sweeps unrelated formatting + a feature + a fix
git commit -m "updates"            # tells the reviewer nothing
git push origin updates
gh pr create --fill                # title/body copied from a useless commit message
# Reviewer cannot tell what changed or why; the diff is 1,800 lines across 40 files.
```

## Common Mistakes

- Bundling unrelated changes so the diff cannot be reviewed or cleanly reverted.
- An empty or one-word description that forces reviewers to reverse-engineer intent.
- Force-pushing during active review, which destroys the "changes since last review" view.
- Merging a branch that is behind base, so untested integration lands on the base branch.
- Leaving the PR in draft with green CI, or requesting review while CI is still red.
- Not linking the issue, so the tracker and the code drift out of sync.
- Merging with an unrelated failing check "temporarily" — it never gets un-temporary.

## Production Tips

- Configure a `.github/pull_request_template.md` so every PR starts with the required
  sections; CI can even fail a PR whose body is empty.
- Require branches to be **up to date before merge** in branch protection so stale diffs
  cannot merge silently.
- Use squash-merge as the default for a linear, one-commit-per-PR history that is easy to
  bisect and revert.
- For risky changes, open the PR early as a draft to get design feedback before the code
  is fully written — cheaper than reworking a finished PR.

## AI Review Checklist

- Does the PR do exactly one logical thing, small enough to review in one sitting?
- Does the description state what changed, why, and how it was verified?
- Is the head branch up to date with the base, with all required checks green?
- Is the linked issue referenced with a closing keyword (`Closes #N`)?
- Is the title suitable as the squash-merge commit message?
- Are there no force-pushes after review started and no bypassed required checks?

## Related

- `knowledge/github/07-code-review.md`
- `knowledge/github/17-branch-protection.md`
- `knowledge/github/09-workflows.md`
- `knowledge/github/23-cli.md`
- `knowledge/github/03-issues.md`
