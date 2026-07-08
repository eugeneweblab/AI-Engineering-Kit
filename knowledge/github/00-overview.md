---
id: github/00-overview
topic: github
slug: overview
title: "Overview"
type: doc
order: 0
status: ready
tags: [github, overview]
related: [github/01-github-platform, github/02-repositories, github/03-issues, github/06-pull-requests, github/08-actions]
when_to_use: "Read first when you need to know which GitHub doc in this topic answers your question."
---
# Overview

## Purpose

This topic teaches an AI agent how to operate GitHub correctly: not just *what*
buttons exist, but *why* a repository is laid out a certain way, when to open an
Issue versus a Discussion, and how to make changes that survive branch protection
and review. It is a map, not a tutorial. Each document below is a self-contained
reference; this page tells you which one to open.

## Why It Matters

GitHub is the system of record for most software: the code, the change history,
the review trail, the CI gates, and the security posture all live here. An agent
that treats GitHub as a dumb file host will fight branch protection, open
duplicate Issues, force-push over a colleague's work, or leak a token in a public
log. Understanding the platform's model — repository, ref, PR, check, permission —
is what lets an agent make a change that actually merges instead of one that gets
rejected or, worse, silently breaks the trunk.

## Core Principles

- **The remote is shared state, not your workspace.** Every push, comment, and
  label change is visible to the whole team immediately and is hard to undo. Act
  with the same care you would editing production data.
- **Prefer the smallest durable artifact.** A tracked Issue beats a Slack message;
  a reviewed PR beats a direct push; a pinned Discussion beats tribal knowledge.
- **Automate through the documented interfaces.** Use the [REST/GraphQL API](22-api.md)
  and [`gh` CLI](23-cli.md), not screen-scraping or guessing URLs.
- **Least privilege by default.** Tokens, Actions, and integrations should hold the
  narrowest scope that completes the task. See [permissions](21-permissions.md).

## How The Docs Fit Together

- **Foundations** — [GitHub Platform](01-github-platform.md) explains the object
  model and hosting tiers. [Repositories](02-repositories.md) covers the unit that
  holds code, history, and settings.
- **Planning and communication** — [Issues](03-issues.md) track work,
  [Projects](04-projects.md) organize it into boards and roadmaps, and
  [Discussions](05-discussions.md) hold open-ended conversation that is not a task.
- **Changing code** — [Pull Requests](06-pull-requests.md) and
  [Code Review](07-code-review.md) are how edits enter a protected branch.
- **Automation** — [Actions](08-actions.md), [Workflows](09-workflows.md),
  [Packages](10-packages.md), and [Releases](11-releases.md) build, test, and ship.
- **Security and governance** — [branch protection](17-branch-protection.md),
  [rulesets](18-rulesets.md), [CodeQL](14-codeql.md), [Dependabot](15-dependabot.md),
  [secret scanning](16-secret-scanning.md), and org-level
  [organizations](19-organizations.md)/[teams](20-teams.md)/[permissions](21-permissions.md).
- **Interfaces and end-to-end guidance** — [API](22-api.md), [CLI](23-cli.md),
  [Codespaces](24-codespaces.md), [Copilot](25-copilot.md),
  [automation](26-automation.md), [best practices](27-best-practices.md),
  and [common anti-patterns](100-common-antipatterns.md).

## Best Practices

- Start from the doc that names your object (Issue, PR, workflow) rather than
  guessing behavior; GitHub's defaults change and each doc is kept current for 2026.
- When a task spans docs (e.g. "open a PR that passes required checks"), read the
  primary doc plus the governance doc it links to, so you do not get blocked by a
  rule you did not know existed.
- Treat the [AI review checklist](99-ai-review-checklist.md) as the exit gate before
  you consider a GitHub task done.

## Common Mistakes

- Diving into a task without checking [branch protection](17-branch-protection.md)
  or [rulesets](18-rulesets.md), then being surprised the push is rejected.
- Confusing Issues, Projects, and Discussions and putting content in the wrong place.
- Automating with a raw personal token when a scoped app or `GITHUB_TOKEN` would do.

## AI Review Checklist

- Did you open the specific doc for the object you are manipulating?
- Did you check the relevant governance rule (protection, permissions) before acting?
- Are you using a documented interface (API/CLI), not an undocumented URL?
- Did you choose the smallest durable artifact for the communication?

## Related

- `knowledge/github/01-github-platform.md`
- `knowledge/github/02-repositories.md`
- `knowledge/github/03-issues.md`
- `knowledge/github/06-pull-requests.md`
- `knowledge/github/08-actions.md`
