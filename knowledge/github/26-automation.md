---
id: github/26-automation
topic: github
slug: automation
title: "GitHub Automation"
type: doc
order: 26
status: ready
tags: [github, automation]
related: [github/08-actions, github/09-workflows, github/22-api, github/23-cli, github/29-integrations]
when_to_use: "Read before scripting GitHub with the API, CLI, webhooks, or scheduled workflows, or reviewing an automation."
---
# GitHub Automation

## Purpose

This document defines how to automate GitHub itself — labeling, triage, releases, merges, and
cross-repo housekeeping — using **workflows, the API, the `gh` CLI, webhooks, and GitHub Apps**.
It covers idempotency, trigger loops, token scope, and rate limits. It is the *orchestration*
layer above individual [actions](08-actions.md) and [workflows](09-workflows.md): the concern
here is automation that acts on your repos with a token, on a schedule or an event, without a
human in the loop.

Good automation is boring: it does the same safe thing every time it runs, and does nothing
when there is nothing to do. Bad automation retriggers itself, floods the API, or acts with
more privilege than the task needs.

## Why It Matters

Automation runs unattended with a token that can modify code, issues, and releases. A workflow
that pushes a commit can retrigger itself into an infinite loop that consumes minutes and API
quota until it is killed. A script that pages through the REST API without backoff hits the
rate limit and fails halfway, leaving a partial mutation. A bot with `write` where it needed
`read` becomes an escalation path if its token leaks. Because these jobs fire on every event
and no human reviews each run, a subtle mistake repeats thousands of times before anyone notices.

## Core Principles

- **Make every automation idempotent.** Running it twice must equal running it once — check
  current state before acting (label already present? PR already merged?). The cost is a read;
  the benefit is retries and duplicate events cannot corrupt state.
- **Prevent trigger loops.** A workflow that writes to the repo can re-fire itself. Guard with
  conditions (`if: github.actor != 'github-actions[bot]'`), path filters, or a token that does
  not retrigger workflows.
- **Least-privilege token per job.** Default `GITHUB_TOKEN` to read-only and elevate only the
  scope a step needs; use a scoped GitHub App or fine-grained PAT for cross-repo work, not a
  broad classic PAT.
- **Respect rate limits.** Handle `403`/`429` with exponential backoff, honor
  `X-RateLimit-Remaining` / `Retry-After`, and prefer GraphQL to fetch exactly the fields you
  need in one call instead of N REST round-trips.
- **Fail loudly, act safely.** On error, stop rather than continuing on partial state; log
  enough to reproduce, and never `echo` the token.

## Best Practices

- Use the built-in `GITHUB_TOKEN` for single-repo automation; use a **GitHub App installation
  token** (scoped, short-lived) for anything touching multiple repos — see [integrations](29-integrations.md).
- Set explicit top-level `permissions:` in every workflow (start `contents: read`) so the token
  is least-privilege by default.
- Guard write-back workflows against self-triggering: filter on actor, paths, or use a
  dedicated token, so a bot commit does not re-run the bot.
- For scheduled jobs, pin the cron and add `concurrency:` so overlapping runs cancel instead of
  stacking; remember `schedule` runs on the default branch only.
- Script with `gh` for readability in CI and GraphQL for efficiency at scale; page with cursors
  and backoff, never a fixed sleep.
- Prefer **auto-merge + required checks** over a custom merge bot — let the platform enforce the
  gate rather than reimplementing it.
- Make bot-authored changes go through PRs and status checks, not direct pushes to protected
  branches.

## Examples

**Good Example** — least-privilege, idempotent, loop-guarded label workflow

```yaml
name: triage
on: { issues: { types: [opened] } }
permissions:
  issues: write            # only the scope this job needs; contents stays default read
concurrency: triage-${{ github.event.issue.number }}  # no overlapping runs per issue
jobs:
  label:
    runs-on: ubuntu-24.04
    if: github.actor != 'github-actions[bot]'          # do not react to our own bot
    steps:
      - name: Add needs-triage if absent            # idempotent: check before mutating
        run: |
          gh issue edit "$NUMBER" --add-label needs-triage
        env:
          NUMBER: ${{ github.event.issue.number }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}     # scoped, short-lived, never echoed
```

**Bad Example** — broad token, self-triggering loop, no backoff

```yaml
name: auto-format
on: { push: {} }                       # fires on every push, including its own commit
permissions: write-all                 # far more scope than formatting needs
jobs:
  fmt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@main
      - run: |
          npm run format
          git commit -am "format" && git push   # push retriggers this same workflow → loop
          # No rate-limit handling anywhere; a paginated API call would fail mid-run.
```

## Common Mistakes

- A write-back workflow that pushes and thereby retriggers itself in an infinite loop.
- Using `permissions: write-all` or a broad classic PAT instead of a scoped token.
- Non-idempotent scripts that duplicate labels, comments, or releases on retry.
- Ignoring rate limits — no backoff, no `Retry-After`, fixed `sleep` instead of cursor paging.
- Assuming `schedule` runs on a feature branch; it only runs on the default branch.
- Reimplementing merge logic in a bot instead of using auto-merge with required checks.
- Bots pushing directly to protected branches, bypassing review and status checks.

## Production Tips

- Prefer GitHub App installation tokens over long-lived PATs: they are short-lived, scoped, and
  attributable to the app, not a person who may leave.
- Add `concurrency` groups and per-workflow timeouts so a stuck or looping job is bounded.
- Monitor Actions minutes and API rate-limit usage; alert on failure spikes, which usually mean
  a loop or an expired token.
- Test automations against a sandbox org before enabling them across production repos.

## AI Review Checklist

- Is the automation idempotent — safe to run twice with the same result?
- Are write-back workflows guarded against triggering themselves?
- Is the token least-privilege (scoped `GITHUB_TOKEN` or App token, not `write-all`/broad PAT)?
- Does API paging handle rate limits with backoff and `Retry-After`?
- Do scheduled jobs use `concurrency` and account for default-branch-only execution?
- Do bot changes go through PRs and required checks rather than direct pushes?
- Is the token never printed to logs?

## Related

- `knowledge/github/08-actions.md`
- `knowledge/github/09-workflows.md`
- `knowledge/github/22-api.md`
- `knowledge/github/23-cli.md`
- `knowledge/github/29-integrations.md`
