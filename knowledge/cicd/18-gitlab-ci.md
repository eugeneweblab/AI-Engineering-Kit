---
id: cicd/18-gitlab-ci
topic: cicd
slug: gitlab-ci
title: "GitLab CI"
type: doc
order: 18
status: ready
tags: [cicd, gitlab-ci, cache, "image:", "default:", DEPLOY_TOKEN, only, needs]
related: [cicd/02-pipeline-design, cicd/15-secrets, cicd/17-github-actions, cicd/21-docker-integration]
when_to_use: "Read before writing or reviewing a .gitlab-ci.yml pipeline."
---
# GitLab CI

## Purpose

This document defines how to write a correct, secure `.gitlab-ci.yml` pipeline. It covers
stages and jobs, `rules`-based execution, caching versus artifacts, protected variables,
and runner selection — enough for an agent to build or review a GitLab pipeline without
introducing a supply-chain hole or a flaky, unpinned job.

GitLab CI is a *config-as-code* runner: a single YAML file at the repo root drives every
build. The same [pipeline design](02-pipeline-design.md) principles apply here as anywhere;
this doc is about the GitLab-specific mechanics that agents get wrong.

## Why It Matters

The pipeline has write access to your registry, your production cluster, and your secrets.
A misconfigured job — an unpinned image, a variable exposed on a fork, a `script` that
`echo`s a token — hands an attacker the keys to everything downstream. GitLab's defaults
are convenient, not safe: variables flow into every job, `latest` images drift, and
`only/except` silently skips jobs you meant to run. Precision in this file is a security
control, not a style preference.

## Core Principles

- **Pin every image by digest or exact tag.** `image: node:22.11.0` is reproducible;
  `image: node:latest` rebuilds differently tomorrow. The cost of pinning is a periodic
  bump; the payoff is a build that means the same thing every run.
- **Use `rules`, not `only/except`.** `only/except` is legacy and cannot express `changes`
  + branch + variable logic cleanly. `rules` is evaluated top-to-bottom; the first match
  wins. Migrating removes a whole class of "why did this job run?" surprises.
- **Separate cache from artifacts.** *Cache* is a best-effort speedup (dependencies) that
  may be missing. *Artifacts* are guaranteed hand-offs between stages (build output). Never
  depend on cache for correctness.
- **Fail closed on secrets.** Mark sensitive variables **Protected** and **Masked**, and
  never expose them to pipelines triggered from forks.
- **One job, one responsibility.** A job that builds *and* deploys cannot be retried
  safely. Split stages so each is independently re-runnable.

## Best Practices

- Define explicit `stages:` and assign every job a stage; jobs in the same stage run in
  parallel, so order dependencies with stages, not luck.
- Scope secrets: keep them in **CI/CD Variables** (or an external vault via
  [OIDC](15-secrets.md)), mark Protected + Masked, and restrict to protected branches.
- Set `interruptible: true` on non-deploy jobs so a new push cancels superseded pipelines
  and saves runner minutes.
- Pin the cache with a stable `key` (e.g. a `files:` key on the lockfile) and set
  `policy: pull` on jobs that only read it, so parallel jobs do not clobber each other.
- Use `needs:` to build a DAG and start independent jobs early instead of waiting for the
  whole previous stage.
- Prefer `id_tokens` (OIDC) to authenticate to cloud providers and registries — short-lived
  tokens beat long-lived static credentials stored as variables.
- Set a `default:` `image` and `retry:` policy for transient failures (`retry: max: 2`),
  but never blanket-retry test failures — that hides flakiness.

## Examples

**Good Example** — pinned image, `rules`, artifacts vs cache, masked secret

```yaml
stages: [build, test, deploy]

default:
  image: node:22.11.0            # exact tag → reproducible builds
  interruptible: true            # new push cancels this run

build:
  stage: build
  cache:
    key:
      files: [package-lock.json] # cache invalidates only when deps change
    paths: [node_modules/]
    policy: pull-push
  script: [npm ci, npm run build]
  artifacts:
    paths: [dist/]               # guaranteed hand-off to later stages
    expire_in: 1 week

deploy:
  stage: deploy
  needs: [build]                 # DAG: starts as soon as build finishes
  id_tokens:                     # OIDC → short-lived cloud creds, no static secret
    AWS_TOKEN: { aud: https://gitlab.example.com }
  script: [./deploy.sh]
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'   # deploy only from main, explicitly
```

**Bad Example** — unpinned image, legacy `only`, secret leaked to logs

```yaml
deploy:
  image: node:latest            # drifts silently; today's green build breaks tomorrow
  only: [main]                  # legacy syntax; cannot combine with changes/variables
  script:
    - echo "$DEPLOY_TOKEN"      # prints the secret into the job log for anyone to read
    - npm ci && npm run build && ./deploy.sh  # build + deploy in one job → not retryable
```

## Common Mistakes

- Using `image: <name>:latest`, so builds are non-reproducible and drift without warning.
- Relying on `cache` to pass build output between stages — cache can be evicted; use
  `artifacts`.
- Leaving secrets unmasked/unprotected, so they surface in logs or run on fork pipelines.
- `echo`-ing tokens for debugging and forgetting to remove it.
- Keeping `only/except` instead of `rules`, then being surprised when jobs run (or skip).
- Retrying every failure blindly, masking a genuinely flaky test.
- One monolithic job that builds, tests, and deploys — impossible to re-run one part.

## Production Tips

- Use **protected branches + protected variables** together; a protected variable is still
  exposed if the branch is not protected.
- Tag runners and require `tags:` on privileged jobs so production deploys only run on
  hardened runners, not shared shell runners.
- Enable **merge request pipelines** (`$CI_PIPELINE_SOURCE == "merge_request_event"`) so
  you test the merged result, not just the branch tip.
- Watch pipeline duration and runner minutes; `interruptible` + `needs` DAGs are the two
  highest-leverage speedups.

## AI Review Checklist

- Is every `image:` pinned to an exact tag or digest, never `latest`?
- Does the pipeline use `rules` rather than `only/except`?
- Are build outputs passed via `artifacts`, with `cache` used only for speedups?
- Are secrets Masked, Protected, and restricted from fork-triggered pipelines?
- Does any `script` print a secret to the log?
- Are build, test, and deploy in separate, independently retryable stages/jobs?
- Is cloud/registry auth done via `id_tokens` (OIDC) instead of static credentials?

## Related

- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/15-secrets.md`
- `knowledge/cicd/17-github-actions.md`
- `knowledge/cicd/21-docker-integration.md`
