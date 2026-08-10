---
id: templates/01-pull-request
topic: templates
slug: pull-request
title: "Pull Request Template"
type: template
order: 1
status: ready
tags: [templates, pull-request, getOrders, install, opening, template]
related: [templates/02-architecture-decision-record, workflows/05-review-pull-request, engineering/02-code-review, tools/17-commit-conventions, checklists/02-pull-request-author]
when_to_use: "Copy when opening a pull request, or install as .github/PULL_REQUEST_TEMPLATE.md for a repository."
---
# Pull Request Template

## Purpose

A PR description exists to answer the questions a reviewer would otherwise have to ask: why
this change, why this approach, and what to look at closely. The diff answers *what*.

Install at `.github/PULL_REQUEST_TEMPLATE.md` so it appears automatically.

---

## The Template

```markdown
## What

One or two sentences on what this change does, in plain language.

## Why

The problem this solves, or the requirement it implements. Link the issue rather than
restating it, but say enough that a reviewer does not have to open it to start reading.

Closes #

## Approach

Only when the approach is not obvious from the diff: what alternatives were considered and
why this one. Skip this section for straightforward changes — an empty section is better
than a padded one.

## Review focus

Where you want attention, and why. For example:
- `src/pricing/discount.ts` — the rounding rule changed; confirm it matches the spec.
- The migration is additive and reversible, but it touches a replicated table.

## Testing

What you ran, and what you verified by hand.
- [ ] Unit tests added or updated
- [ ] Verified locally: <the specific scenario>
- [ ] Verified at the breakpoints / on a real device (UI changes)

## Risk and rollback

- Risk: <what could break, and who would notice first>
- Rollback: <revert this PR / feature flag / requires a follow-up migration>

## Screenshots

Before and after, for anything user-visible.
```

---

## Filling It In

**"What" is one sentence.** If it takes a paragraph, the PR is probably doing more than one
thing — split it.

**"Why" is the part reviewers actually need.** A change that looks wrong is usually a change
whose reason was not stated. This is also what `git log` preserves after the PR is closed —
see [Commit Conventions](../tools/17-commit-conventions.md).

**"Review focus" is where the template earns its cost.** A reviewer given 600 changed lines
reads none of them carefully; the same reviewer told which 40 lines carry the risk reads
those properly.

**"Risk and rollback" turns an implicit assumption into a stated one.** "Revert this PR" is
a perfectly good answer — the point is that someone checked before merging, rather than
discovering during an incident that the migration was destructive.

---

## What Not to Include

- **A restatement of the diff.** Reviewers can read the diff; they cannot read your intent.
- **A changelog entry.** That belongs in the changeset or commit message.
- **Checkbox theater.** A list of twelve boxes everyone ticks blindly is worse than three
  that are genuinely checked. Cut the ones nobody reads.
- **Generated summaries left unedited.** A machine-written description of what changed adds
  length without adding the reasoning the template exists to capture.

---

## A Filled Example

```markdown
## What

Plan prices now render from the Stripe API instead of the hardcoded table.

## Why

Prices were duplicated between Stripe and `src/data/plans.ts`, and drifted after the
January increase — three customers were quoted the old amount.

Closes #482

## Approach

Fetched server-side and cached for 5 minutes rather than at build time: pricing changes
should not require a deploy. Considered a webhook to invalidate on change, but the
5-minute window is well within what finance asked for.

## Review focus

- `src/server/pricing.ts` — the cache key includes currency; confirm that is right for
  the multi-currency rollout.
- Amounts stay in integer cents end to end. Worth a second pair of eyes on the formatter.

## Testing

- [x] Unit tests for the formatter, including a zero-decimal currency (JPY)
- [x] Verified locally against Stripe test mode, including the empty-plans case
- [x] Checked the pricing page at 1440 / 768 / 390

## Risk and rollback

- Risk: Stripe unavailable → pricing page shows the cached copy, then an error state.
- Rollback: revert; no migration, no schema change.
```

---

## Examples

**Good Example** — filled in so a reviewer can start reviewing

```markdown
## What and why
Zero-quantity order items produced zero-total orders. #481 hid them on the
invoice screen; this fixes the cause by rejecting the input at the boundary.

## How to verify
`POST /api/orders` with `"quantity": 0` returns 400.
`npm test -- --grep quantity` — the new test fails on `main` at 4a91c2e.

## Risk and rollback
Low: one validation rule on one path. Existing zero-quantity orders are
unaffected (a separate data-cleanup ticket, #489). Rollback: revert this commit.

## Not included
`getOrders()` has a missing timeout with the same shape. Fixing it here would
mix two changes; opened #490.

## Screenshots
Error state: <image>   (400 response rendered in the checkout form)
```

**Bad Example** — the template left as headings

```markdown
## What and why
Fixes the bug.

## How to verify
Should work now.

## Risk and rollback
Low risk.

## Screenshots
N/A
```

The template was filled in without being answered. The reviewer still has to work out which
bug, how to reproduce it, what "low risk" is based on, and whether the 900-line diff contains
anything besides the fix.

---

## Related

- `knowledge/templates/02-architecture-decision-record.md`
- `knowledge/workflows/05-review-pull-request.md`
- `knowledge/engineering/02-code-review.md`
- `knowledge/tools/17-commit-conventions.md`
- `knowledge/checklists/02-pull-request-author.md`
