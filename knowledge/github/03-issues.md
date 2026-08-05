---
id: github/03-issues
topic: github
slug: issues
title: "Issues"
type: doc
order: 3
status: ready
tags: [github, issues, logs, GitHub]
related: [github/04-projects, github/05-discussions, github/06-pull-requests, github/26-automation, github/23-cli]
when_to_use: "Read before opening, triaging, or automating Issues, so each one is actionable, deduplicated, and correctly linked to code."
---
# Issues

## Purpose

An Issue is a tracked unit of work or a reported defect: something with a definite
outcome that can be opened, discussed, assigned, and closed. This document defines
how to write, label, link, and automate Issues so a backlog stays a reliable list
of actionable work rather than a graveyard of vague, duplicated notes.

## Why It Matters

Issues are the project's task ledger and its permanent record of *why* a change was
made. A well-formed Issue lets any contributor — human or agent — reproduce a bug,
understand the acceptance criteria, and close it with a linked PR that survives long
after memory fades. A poorly formed backlog does the opposite: duplicates pile up,
"it's broken" tickets can never be verified, and real work is lost in noise. The
discipline of Issue hygiene is what keeps a team's throughput measurable.

## Core Principles

- **One Issue, one outcome.** An Issue tracks a single bug or a single deliverable
  with a definable "done." Split anything larger into linked child Issues.
- **Reproducible or it does not exist.** A bug report without steps, expected vs.
  actual, and environment is not actionable — it is a wish.
- **Search before you open.** Duplicates fragment discussion and waste triage;
  always search open and closed Issues first.
- **Link, do not narrate.** Reference the PR, commit, or related Issue with GitHub's
  linking syntax so the graph is navigable and closing is automatic.
- **Issues are tasks, not conversations.** Open-ended questions belong in
  [Discussions](05-discussions.md); Issues have an end state.

## Best Practices

- Use **Issue templates** (`.github/ISSUE_TEMPLATE/*.yml`) to force the fields that
  make a report actionable: steps, expected, actual, version.
- Write titles as a specific symptom or goal ("Login 500s when email has `+` alias"),
  not a category ("login bug").
- Apply a small, consistent label taxonomy: type (`bug`/`feature`), priority, and
  area. Too many labels is as useless as none.
- Close Issues via PRs using closing keywords (`Closes #123`) so the link and the
  close happen atomically on merge.
- Track parent/child work with task lists and Issue links rather than one giant
  Issue with a 40-item checklist.
- Automate triage: auto-label from templates, auto-add to a [Project](04-projects.md),
  and stale-bot Issues with no activity after a defined window.

## Examples

**Good Example** — reproducible report, closed by its PR

```markdown
### Title: Checkout returns 500 when quantity is 0

**Steps to reproduce**
1. Add any item to cart
2. Set quantity to `0` in the cart view
3. Click "Checkout"

**Expected:** validation error "quantity must be at least 1"
**Actual:** HTTP 500, stack trace in logs (see below)
**Environment:** v3.4.1, prod, Chrome 137

<details><summary>stack trace</summary>...</details>
```

```markdown
<!-- In the PR that fixes it: the keyword makes GitHub close #482 on merge and
     records the exact commit that resolved it, so the link is permanent. -->
Closes #482
```

**Bad Example** — unverifiable, duplicated, unlinked

```markdown
### Title: it's broken

checkout doesn't work sometimes, please fix asap
<!-- No steps, no version, no expected/actual → nobody can reproduce or verify.
     No search was done, so this duplicates #482.
     The eventual fix is committed with "fixed stuff", linking nothing. -->
```

## Common Mistakes

- Filing "it's broken" with no reproduction steps, expected/actual, or version.
- Opening a duplicate because open and closed Issues were not searched first.
- Cramming many unrelated tasks into one Issue so "done" can never be reached.
- Closing an Issue manually instead of via `Closes #N`, losing the PR link.
- Using an Issue for an open-ended question that belongs in Discussions.
- Label sprawl: dozens of overlapping labels nobody applies consistently.

## Production Tips

- Enforce templates repo-wide and disable blank Issues so every report has structure.
- Use saved searches / query dashboards (`is:open label:bug no:assignee`) for triage.
- Automate with the `gh` CLI or Actions: `gh issue list`, auto-assign, auto-project.
- Convert a stray Discussion into an Issue only once it has a concrete, closeable
  outcome — do not promote every question.

## AI Review Checklist

- Does the Issue describe a single, closeable outcome?
- For a bug: are steps, expected, actual, and environment all present?
- Was a duplicate search implied/done before opening?
- Is the fixing PR linked with a closing keyword (`Closes #N`)?
- Are labels from the project's defined taxonomy, not ad hoc?
- Should this have been a [Discussion](05-discussions.md) instead?

## Related

- `knowledge/github/04-projects.md`
- `knowledge/github/05-discussions.md`
- `knowledge/github/06-pull-requests.md`
- `knowledge/github/26-automation.md`
- `knowledge/github/23-cli.md`
