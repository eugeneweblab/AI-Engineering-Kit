---
id: github/04-projects
topic: github
slug: projects
title: "Projects"
type: doc
order: 4
status: ready
tags: [github, projects, GraphQL, runs-on]
related: [github/03-issues, github/05-discussions, github/26-automation, github/22-api, github/23-cli]
when_to_use: "Read before setting up or automating a Projects (v2) board or roadmap to plan and track work across repositories."
---
# Projects

## Purpose

GitHub Projects (v2) is a flexible planning layer built on top of Issues and Pull
Requests. It organizes work items into boards, tables, and roadmaps with custom
fields, so a team can see status, priority, and timeline across many repositories.
This document defines how to model a Project so it reflects reality automatically
instead of rotting into a stale board nobody trusts.

## Why It Matters

A Project is only useful if it is *true*. The moment status has to be updated by
hand, it drifts from reality and stops being a planning tool. Projects v2's value
is that it can derive state from the underlying Issues and PRs — closing an Issue
moves its card, opening a PR flips a status — so the board maintains itself. An
agent that understands this builds automation that keeps the plan honest; one that
does not creates a second source of truth that immediately contradicts the first.

## Core Principles

- **Items are references, not copies.** A Project item points to a real Issue or PR;
  the underlying object remains the source of truth for title, state, and assignee.
- **Fields belong to the Project, not the Issue.** Custom fields (Status, Priority,
  Iteration, Estimate) live on the Project, letting the same Issue appear in
  multiple Projects with different context.
- **State should be derived, not typed.** Prefer built-in workflows and Actions that
  move items on Issue/PR events over manual drag-and-drop.
- **Projects v2 is a GraphQL citizen.** REST does not fully model Projects v2; use
  the [GraphQL API](22-api.md) (node IDs, `updateProjectV2ItemFieldValue`) to automate.
- **One Project, one planning question.** A team board, a release roadmap, and a bug
  triage queue are different Projects, not one overloaded view.

## Best Practices

- Define a minimal, agreed field set (Status, Priority, Iteration) and use views
  (board, table, roadmap) rather than duplicating data into new fields.
- Enable the built-in workflows: auto-add items from a repo, set Status to "Done"
  when an Issue/PR closes, set "In Progress" when a linked PR opens.
- Automate cross-repo intake with an Action on `issues.opened` that adds the Issue
  to the Project and sets initial fields.
- Use Iterations for time-boxed planning instead of hand-maintained "sprint" labels.
- Keep archived/closed items out of active views with a filter so the board shows
  only live work.

## Examples

**Good Example** — auto-add new Issues to a Project via GraphQL/Action

```yaml
# .github/workflows/add-to-project.yml
# Runs when any Issue is opened and adds it to the team Project automatically,
# so the board reflects reality without anyone remembering to add cards.
on:
  issues:
    types: [opened]
jobs:
  track:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/add-to-project@v1  # illustrative ref; pin the reviewed SHA in production
        with:
          project-url: https://github.com/orgs/acme/projects/12
          github-token: ${{ secrets.ADD_TO_PROJECT_PAT }}  # scoped: project + issues
```

```graphql
# Set a custom field via GraphQL — Projects v2 is NOT fully in REST, so this is
# the supported path. Note it operates on node IDs, not Issue numbers.
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDO...", itemId: "PVTI_lADO...",
    fieldId: "PVTF_lADO...", value: { singleSelectOptionId: "In Progress" }
  }) { projectV2Item { id } }
}
```

**Bad Example** — a manually maintained board that drifts

```text
Team keeps a Project board where every status change is drag-and-drop by hand.
- An Issue is closed via PR, but its card still sits in "In Progress".
- Priority is a free-text field, so it reads "high", "High", "P1", and "urgent".
Result: the board contradicts the Issues it mirrors and nobody trusts it.
# Fix: derive Status from Issue/PR state; make Priority a single-select field.
```

## Common Mistakes

- Updating card status by hand instead of deriving it from Issue/PR events.
- Reaching for the REST API to automate Projects v2, which needs GraphQL.
- Free-text fields (priority, status) that fragment into inconsistent values.
- Duplicating Issue data (title, assignee) into Project fields, creating drift.
- One mega-Project trying to be board, roadmap, and triage queue at once.

## Production Tips

- Store the Project and field node IDs as repo/org variables so automation does not
  re-query them on every run.
- Use `gh project` CLI commands for scripted item and field operations.
- Grant the automation token only `project` + `issues` scope; a Project PAT does not
  need repo-write.

## AI Review Checklist

- Are Project items references to real Issues/PRs, not duplicated data?
- Is status derived from Issue/PR state via workflows, not manual drag-and-drop?
- Does automation use the GraphQL API and node IDs for Projects v2?
- Are custom fields single-select/typed rather than free text?
- Does each Project answer one clear planning question?

## Related

- `knowledge/github/03-issues.md`
- `knowledge/github/05-discussions.md`
- `knowledge/github/26-automation.md`
- `knowledge/github/22-api.md`
- `knowledge/github/23-cli.md`
