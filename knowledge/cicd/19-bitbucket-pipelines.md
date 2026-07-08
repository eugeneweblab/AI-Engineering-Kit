---
id: cicd/19-bitbucket-pipelines
topic: cicd
slug: bitbucket-pipelines
title: "Bitbucket Pipelines"
type: doc
order: 19
status: ready
tags: [cicd, bitbucket-pipelines]
related: [cicd/02-pipeline-design, cicd/15-secrets, cicd/18-gitlab-ci, cicd/21-docker-integration]
when_to_use: "Read before writing or reviewing a bitbucket-pipelines.yml configuration."
---
# Bitbucket Pipelines

## Purpose

This document defines how to write a correct `bitbucket-pipelines.yml`. It covers the
step/stage model, caches and artifacts, secured repository/deployment variables, OIDC
authentication, and the build-minute economics that shape how you structure jobs. The goal
is an agent that can build or review a Bitbucket pipeline without leaking secrets or
wasting the (metered) minutes budget.

Bitbucket Pipelines runs each step in a fresh Docker container defined by an `image:`. The
general [pipeline design](02-pipeline-design.md) rules apply; this doc covers the
Bitbucket-specific structure and its sharp edges.

## Why It Matters

Bitbucket bills by the build minute and runs every step in a disposable container, so two
things bite agents: correctness (state does not survive between steps unless you declare an
artifact) and cost (an unpinned image or an uncached dependency install burns minutes on
every run). On top of that, *secured* variables are only masked in logs — a `cat` of a file
that contains one, or a pull request from a fork, can still expose it. Getting the
structure right is both a money and a security concern.

## Core Principles

- **Every step is ephemeral.** The container is destroyed after each step. Anything a later
  step needs must be declared as an `artifacts:` path; anything you want to reuse for speed
  goes in `caches:`. Do not confuse the two — artifacts are correctness, caches are speed.
- **Pin the `image`.** `image: node:22.11.0` is reproducible; `node:latest` is not. Pinning
  costs a periodic bump and buys a build that behaves identically next month.
- **Secured variables are masked, not sealed.** Marking a variable *Secured* hides it from
  the log *if printed directly*, but it can still leak via files or fork PRs. Treat every
  secret as spillable and never echo it.
- **Deployments are gated resources.** Use `deployment:` environments (test/staging/prod)
  so production variables and approvals bind to the environment, not to a loose step.
- **Fail fast, parallelize independent work.** Steps in a `parallel:` block share the
  minute budget efficiently; a linear chain of independent steps wastes wall-clock time.

## Best Practices

- Store secrets as **repository/deployment variables**, mark them **Secured**, and scope
  production secrets to a `deployment: production` step so they are unavailable elsewhere.
- Prefer **OIDC** (`oidc: true` + web-identity) to authenticate to AWS/GCP with short-lived
  tokens instead of storing long-lived cloud keys as variables.
- Cache dependencies with the built-in `node`/`docker` caches or a custom cache keyed on
  the lockfile path, so `npm ci` does not re-download the world each run.
- Use `artifacts:` to pass `dist/` or test reports between steps; assume nothing else
  carries over.
- Set `max-time:` on steps to cap runaway jobs and protect your minute budget.
- Use `parallel:` for independent test shards and `condition: changesets:` to skip steps
  when the relevant paths did not change.
- Enable pipelines only where needed with `branches:`/`pull-requests:` sections rather than
  running the full pipeline on every push to every branch.

## Examples

**Good Example** — pinned image, cache vs artifact, secured deploy via OIDC

```yaml
image: node:22.11.0                 # exact tag → reproducible container

definitions:
  caches:
    npm: node_modules               # reused across runs for speed only

pipelines:
  branches:
    main:
      - step:
          name: Build & Test
          caches: [npm]
          script:
            - npm ci
            - npm run build
            - npm test
          artifacts: [dist/**]      # guaranteed hand-off to the deploy step
      - step:
          name: Deploy
          deployment: production     # binds prod variables + approvals to this step
          oidc: true                 # short-lived cloud creds, no static key stored
          max-time: 10               # cap runaway minutes
          script:
            - ./deploy.sh            # dist/ is present because it was an artifact
```

**Bad Example** — unpinned image, secret echoed, state assumed to persist

```yaml
image: node:latest                  # drifts; a passing build silently breaks later
pipelines:
  default:                          # runs on every branch → wastes the minute budget
    - step:
        script:
          - npm ci && npm run build
          - echo "$PROD_TOKEN"      # secured var still printed → visible in log
    - step:
        script:
          - ./deploy.sh             # FAILS: dist/ was never declared as an artifact
```

## Common Mistakes

- Assuming files from an earlier step exist in a later one without an `artifacts:` entry.
- Using `image: <name>:latest`, producing non-reproducible builds.
- `echo`-ing a Secured variable, or reading it into a file that gets logged.
- Running the pipeline on `default:` for every branch instead of scoping to `main`/PRs,
  burning build minutes.
- Storing long-lived AWS/GCP keys as variables instead of using `oidc: true`.
- Treating `caches:` as a reliable store — a cache miss then breaks the build.
- No `max-time:`, so a hung step drains the monthly minute allowance.

## Production Tips

- Put production credentials on a **deployment environment** with required reviewers, so a
  prod deploy needs an explicit approval, not just a merge.
- Split slow test suites with `parallel:` shards; Bitbucket bills wall-clock per step, so
  parallelism directly cuts elapsed time.
- Use **self-hosted runners** for jobs that need private-network access or more resources
  than the hosted size tiers provide.
- Monitor the build-minutes dashboard; the biggest wins are caching installs and scoping
  which branches trigger pipelines.

## AI Review Checklist

- Is `image:` pinned to an exact tag, never `latest`?
- Is every cross-step file passed via `artifacts:` rather than assumed to persist?
- Are secrets Secured and scoped to a `deployment:` environment where possible?
- Does any step `echo` or log a secured variable?
- Is cloud auth done via `oidc: true` instead of stored long-lived keys?
- Is the pipeline scoped to relevant branches/PRs instead of running on all pushes?
- Do long-running steps have a `max-time:` cap?

## Related

- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/15-secrets.md`
- `knowledge/cicd/18-gitlab-ci.md`
- `knowledge/cicd/21-docker-integration.md`
