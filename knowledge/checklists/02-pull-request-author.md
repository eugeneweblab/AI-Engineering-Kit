---
id: checklists/02-pull-request-author
topic: checklists
slug: pull-request-author
title: "Pull Request Author Checklist"
type: checklist
order: 2
status: ready
tags: [checklists, pull-request-author, getOrders, debugger, CreateOrderItemDto, console.log]
related: [templates/01-pull-request, workflows/05-review-pull-request, engineering/02-code-review, tools/99-ai-review-checklist, checklists/01-pre-launch]
when_to_use: "Run before requesting review on a change, to catch what a reviewer would otherwise spend their attention on."
---
# Pull Request Author Checklist

## Purpose

The checks an author runs before asking for review. Its purpose is to spend the reviewer's
attention on logic rather than on things a script or a second read would have caught.

The reviewer's counterpart is [Workflow — Review a Pull Request](../workflows/05-review-pull-request.md).

---

## Before Opening

☐ The branch is up to date with the base, and conflicts are resolved.

☐ `verify` (or the project's equivalent) passes locally — typecheck, lint, format, tests.

☐ Commits follow the project's convention, and the squash title will too.

☐ No debugging leftovers: `console.log`, `dd()`, `debugger`, commented-out code, `.only` on
a test.

☐ No credentials, tokens, or `.env` values in the diff.

☐ Generated files are regenerated rather than hand-edited.

---

## Read Your Own Diff

☐ You have read the entire diff, top to bottom, as a reviewer would.

☐ Every changed file belongs to this change — no incidental refactors, renames, or
formatting swept in.

☐ Nothing is left half-done with an intention to follow up in a later PR that does not exist
yet.

☐ Naming is consistent with the surrounding code, not with your preference.

☐ The change reads like the code around it — same idioms, same comment density.

---

## Scope

☐ The PR does one thing. If the description needs "and", consider splitting.

☐ It is small enough to review properly — if it is over a few hundred meaningful lines,
there is usually a natural split.

☐ Formatting-only changes are in their own commit, or their own PR.

☐ Dependency additions are justified and mentioned in the description.

---

## Correctness

☐ Edge cases are handled: empty, null, zero, one, many, very long, unauthorized.

☐ Errors are handled rather than swallowed; failures surface where someone will see them.

☐ New queries are bounded and indexed on what they filter by.

☐ Any user-supplied value reaching output is escaped for its context.

☐ Any state-changing endpoint checks permission on the specific object.

☐ Nothing added inside a loop performs I/O that could be batched.

---

## Tests

☐ New behavior is covered by a test that fails without the change.

☐ For a bug fix, the regression test fails on the old code — verified, not assumed.

☐ Tests assert behavior through the public interface, not implementation details.

☐ No test depends on ordering, real time, real network, or another test's leftovers.

☐ The suite passes repeatedly, not just once.

---

## User-Facing Changes

☐ Verified in a browser, at the breakpoints the design defines.

☐ Keyboard-operable, with a visible focus indicator.

☐ Loading, empty, and error states exist and were checked.

☐ Copy is final, translated where required, and free of placeholder text.

☐ Screenshots or a short recording are attached for anything visual.

---

## Risk

☐ The description states what could break and who would notice first.

☐ Rollback is possible — or the reason it is not is stated explicitly.

☐ Migrations are additive and reversible, or the plan is documented.

☐ Anything behind a feature flag has a stated default and a removal plan.

☐ Deployment ordering matters? Say so in the description.

---

## The Description

☐ States why, not just what.

☐ Points reviewers at the parts that carry the risk.

☐ Links the issue, in a footer rather than the title.

☐ Contains no unedited generated summary of the diff.

See [Templates — Pull Request](../templates/01-pull-request.md).

---

## Sign-off

The PR is ready when you have read the whole diff yourself, `verify` is green, the
description explains why, and you can name what would break if it is wrong.

## Examples

**Good Example** — the author does the reviewer's first pass first

```bash
# Read your own diff before anyone else does. Most review comments are things
# the author would have caught here.
git diff --stat main...HEAD
git diff main...HEAD -- ':!*.lock' ':!*.snap'

# The same commands CI runs, run locally, before the PR exists.
npm run verify

# Does the new test actually catch the bug?
git stash -- src/ && npm test -- --grep "quantity"   # expect FAIL
git stash pop && npm test -- --grep "quantity"       # expect PASS
```

```markdown
## What and why
Zero-quantity order items created zero-total orders (#481 fixed the invoice
symptom; this fixes the cause). Adds `@Min(1)` to `CreateOrderItemDto`.

## How to verify
`POST /api/orders` with `quantity: 0` now returns 400. Test added; it fails on
`main` at 4a91c2e.

## Risk
Low. One validation rule, one path. Rollback: revert this commit.

## Not included
`getOrders()` has the same missing timeout — separate commit on this branch.
```

**Bad Example** — the diff is the description

```markdown
## fix stuff

fixes the bug
```

A 900-line diff with a reformatted file, an unrelated rename, and the actual fix somewhere in
the middle. The reviewer has to reconstruct the intent, cannot tell which lines matter, and
has no way to verify the claim.

---

## Related

- `knowledge/templates/01-pull-request.md`
- `knowledge/workflows/05-review-pull-request.md`
- `knowledge/engineering/02-code-review.md`
- `knowledge/tools/99-ai-review-checklist.md`
- `knowledge/checklists/01-pre-launch.md`
