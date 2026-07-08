---
id: cicd/24-notifications
topic: cicd
slug: notifications
title: "Notifications"
type: doc
order: 24
status: ready
tags: [cicd, notifications]
related: [cicd/23-monitoring, cicd/25-debugging, cicd/14-rollbacks, cicd/09-release-management, cicd/05-quality-gates]
when_to_use: "Read before wiring pipeline events (build, deploy, failure) to Slack, email, or paging so alerts are actionable and not noise."
---
# Notifications

## Purpose

This document defines how a CI/CD pipeline should tell humans what happened: a
build broke, a deploy shipped, a canary is degrading, a nightly job silently
failed. It covers *what* to send, *to whom*, *through which channel*, and *how
loud*. The goal is that every notification is either acted on or deliberately
ignored — never both.

A notification is a routing decision, not a feature. It sits downstream of
[monitoring](23-monitoring.md) (which detects) and upstream of
[debugging](25-debugging.md) (which diagnoses). Get the routing wrong and you
either page people for nothing or stay silent during an outage.

## Why It Matters

Notifications fail in two opposite directions, both fatal. Too many, and the team
mutes the channel — the one real outage arrives in a stream people stopped
reading. Too few, and a broken `main` branch or a failed production deploy goes
unnoticed for hours. Because alert fatigue is invisible until an incident, teams
routinely over-notify and only discover the cost during a postmortem.

Notifications are also the first artifact a responder sees under stress. If the
message lacks the branch, the commit, the environment, and a link to logs, the
responder burns minutes gathering context before they can even start. The quality
of an alert directly sets the mean time to recovery.

## Core Principles

- **Notify on state change, not on state.** Alert when green turns red or red
  turns green — not on every successful run. Repeated "success" messages train
  people to ignore the channel.
- **Match urgency to channel.** A broken `main` build is a chat message; a failed
  production deploy or a firing SLO is a page. Never route a page-worthy event to
  an inbox nobody watches at 2am.
- **Every alert names an owner and an action.** "Deploy failed" is noise;
  "Deploy of `checkout@a1b2c3` to prod failed — rollback link, logs link, on-call
  @jordan" is actionable.
- **Deduplicate and throttle.** One failing cron that fires every 5 minutes must
  produce one alert, not 288 a day. Group by root cause, not by occurrence.
- **Failure paths must themselves be reliable.** If the notifier depends on the
  service that just went down, you get silence exactly when you need the alert.

## Best Practices

- Send failure notifications for pipelines on protected branches (`main`,
  release branches). Skip success spam; a green checkmark in the UI is enough.
- Include in every message: repository, branch, commit SHA (short), triggering
  actor, environment, job/stage name, and a deep link to the run and its logs.
- Route by severity: informational -> chat channel; actionable-but-not-urgent ->
  chat with `@mention`; urgent/production -> pager (PagerDuty/Opsgenie) with an
  escalation policy.
- Store webhook URLs and API tokens as [secrets](15-secrets.md), never in the
  pipeline YAML. A leaked Slack webhook lets anyone post as your CI.
- Notify on deploy start and finish for production so the timeline is auditable
  and responders can correlate an incident with the exact release.
- Make notifications idempotent and rate-limited so a flapping job cannot storm
  the channel.
- Send only on `failure` for scheduled/nightly jobs — a silent cron is the most
  common way a broken backup goes unnoticed for weeks.

## Examples

**Good Example** — notify only on failure of protected branches, with context

```yaml
# GitHub Actions: one actionable Slack message, only when main breaks.
notify:
  needs: [build, test, deploy]
  if: failure() && github.ref == 'refs/heads/main'  # state change on protected branch
  runs-on: ubuntu-latest
  steps:
    - uses: slackapi/slack-github-action@v2
      with:
        webhook: ${{ secrets.SLACK_WEBHOOK }}   # secret, not hardcoded
        webhook-type: incoming-webhook
        payload: |
          {
            "text": ":red_circle: *main* failed — ${{ github.workflow }}\n
              commit `${{ github.sha }}` by ${{ github.actor }}\n
              <${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View logs>"
          }
```

**Bad Example** — notifies on everything, no context, secret in plaintext

```yaml
notify:
  if: always()                       # fires on every run, including success -> muted channel
  runs-on: ubuntu-latest
  steps:
    - run: |
        curl -X POST https://hooks.slack.com/services/T00/B00/XXXXXXXX \  # hardcoded webhook
          -d '{"text":"pipeline finished"}'   # no branch, commit, actor, or log link
```

## Common Mistakes

- Firing a notification on every successful run, so the channel becomes noise and
  the one real failure is scrolled past.
- Omitting the commit SHA, environment, and a log link, forcing responders to hunt
  for basic context under pressure.
- Hardcoding webhook URLs or tokens in pipeline files instead of using secrets.
- Routing production incidents to a chat channel nobody monitors overnight instead
  of a pager with escalation.
- No deduplication, so a flapping job posts hundreds of identical messages.
- Not alerting on failed scheduled jobs, letting silent cron failures accumulate.
- Building the notifier on top of the same infrastructure it is meant to watch.

## Production Tips

- Separate an "informational" channel (deploys, releases) from an "actionable"
  channel (failures, incidents). People can mute the first without missing the
  second.
- Attach a runbook link to production alerts so the responder's first click is the
  fix procedure, not a search.
- Review alert volume monthly. Any alert nobody acted on is a candidate to delete
  or downgrade — measure and prune, do not accumulate.
- Test the notification path in a drill: force a failure and confirm the page
  actually reaches the on-call, including escalation.

## AI Review Checklist

- Does the pipeline notify on failure of protected branches rather than on every
  run?
- Does each message include repository, branch, commit, actor, environment, and a
  log link?
- Is urgency matched to channel (chat vs. pager) with an escalation policy for
  production?
- Are webhook URLs and tokens stored as [secrets](15-secrets.md), not inline?
- Are notifications deduplicated and rate-limited against flapping jobs?
- Do scheduled/nightly jobs alert on silent failure?

## Related

- `knowledge/cicd/23-monitoring.md`
- `knowledge/cicd/25-debugging.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/09-release-management.md`
- `knowledge/cicd/05-quality-gates.md`
