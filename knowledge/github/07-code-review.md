---
id: github/07-code-review
topic: github
slug: code-review
title: "Code Review"
type: doc
order: 7
status: ready
tags: [github, code-review]
related: [github/06-pull-requests, github/17-branch-protection, github/18-rulesets, github/27-best-practices, github/13-security]
when_to_use: "Read before reviewing a pull request or configuring how reviews gate merges."
---
# Code Review

## Purpose

This document defines how to review a pull request on GitHub: what to inspect, how to
comment, and how approvals gate a merge. Review is a correctness and knowledge-sharing
control, not a gate for personal preference. It complements the author's job described in
[pull requests](06-pull-requests.md) — the author makes the change easy to verify; the
reviewer verifies it.

The goal of review is a working, maintainable change and a second person who understands
it — not a diff that matches the reviewer's style.

## Why It Matters

Review is the cheapest place to catch a defect: fixing it in a PR costs minutes, fixing
it in production costs an incident. But review only works if it is real. A review that
rubber-stamps in ten seconds provides false confidence — the check is green, so everyone
assumes the code is safe when nobody actually looked. Conversely, a review that nitpicks
whitespace while missing an injection bug wastes everyone's time and trains authors to
tune out feedback. The quality of review directly sets the quality of what ships.

## Core Principles

- **Review behavior, then design, then style.** Correctness and security first; naming
  and formatting last (and ideally automated away). Never block a PR on taste.
- **Understand before you approve.** If you cannot explain what the change does, you are
  not qualified to approve it. Approval means "I checked this," not "I skimmed it."
- **Comment on the code, not the coder.** Ask questions and propose alternatives; never
  make it personal. The review is about the diff.
- **Distinguish blocking from optional.** Mark nits as nits. A reviewer who blocks on
  everything is as useless as one who blocks on nothing.
- **Required reviews must come from someone other than the author.** Self-approval is not
  review; enforce this with branch protection, not trust.

## Best Practices

- Pull the branch and run it for non-trivial changes; do not review purely by reading the
  diff. Bugs hide in behavior the diff does not show.
- Check the **security-relevant surfaces** every time: input validation, authz checks,
  secrets, SQL/shell construction, and new dependencies.
- Use **Request changes** only for blocking issues, **Comment** for questions, and
  **Approve** when the change is correct and you would ship it.
- Prefer **suggested changes** (GitHub's suggestion blocks) for small fixes so the author
  applies them in one click instead of a round trip.
- Require **CODEOWNERS** review for sensitive paths (auth, billing, CI config) so the
  right expert is auto-requested.
- Re-review after force-pushes or large updates; do not let an approval carry over onto
  substantially different code (enable "dismiss stale approvals").
- Resolve conversations only when actually addressed; leave them open otherwise so the
  merge gate reflects reality.

## Examples

**Good Example** — a review that blocks on a real bug with a concrete fix

```markdown
<!-- On the diff line that builds a query -->
**Request changes:** This interpolates `req.query.id` straight into SQL, which is
injectable. Use a parameterized query instead:

```suggestion
const rows = await db.query("SELECT * FROM orders WHERE id = $1", [req.query.id]);
```

Nit (non-blocking): `orders` could be a const above the loop.
```

**Bad Example** — a review that rubber-stamps and nitpicks

```markdown
LGTM 👍
<!-- Approved in 8 seconds on a 900-line diff touching auth. Nobody ran it. -->

<!-- Elsewhere, the only substantive comment: -->
Please use single quotes here to match my preference.
<!-- Blocks the PR on style while the SQL injection two lines down ships. -->
```

## Common Mistakes

- Approving without running or fully reading the change ("LGTM" on a large diff).
- Blocking on personal style that a linter or formatter should enforce automatically.
- Missing the security surfaces (authz, input, secrets) while polishing cosmetics.
- Letting a stale approval carry over onto code that was rewritten after review.
- Marking a conversation resolved when the concern was not actually addressed.
- Reviewing your own PR, or approving a teammate's PR you were told to "just approve."
- Dumping 50 comments with no signal on which are blocking versus optional.

## Production Tips

- Move all mechanical checks (format, lint, type, test coverage) into CI so humans review
  logic, not spacing. Every style debate in review is a missing lint rule.
- Set a review SLA (e.g., first response within one business day) so PRs do not rot.
- Use CODEOWNERS plus required-review rules so sensitive files cannot merge without the
  owning team, even for admins.
- For AI-generated diffs, review with extra scrutiny on invented APIs, unhandled errors,
  and silently dropped edge cases — the surface *looks* correct, so read the logic.

## AI Review Checklist

- Did the review verify behavior (run/tests), not just read the diff?
- Were security surfaces — input validation, authz, secrets, injection — checked?
- Are blocking issues clearly separated from optional nits?
- Did the approval come from someone other than the author?
- Are stale approvals dismissed after significant new commits?
- Are resolved conversations actually addressed, not just closed?
- Are style-only comments backed by an automated rule rather than personal taste?

## Related

- `knowledge/github/06-pull-requests.md`
- `knowledge/github/17-branch-protection.md`
- `knowledge/github/18-rulesets.md`
- `knowledge/github/27-best-practices.md`
- `knowledge/github/13-security.md`
