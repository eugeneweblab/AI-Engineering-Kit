---
id: cicd/17-github-actions
topic: cicd
slug: github-actions
title: "GitHub Actions"
type: doc
order: 17
status: ready
tags: [cicd, github-actions, timeout-minutes, concurrency, "permissions:", cancel-in-progress, pull_request, pull_request_target]
related: [github/09-workflows, cicd/15-secrets, cicd/16-environments, cicd/02-pipeline-design, cicd/06-security-scanning, cicd/07-artifacts]
defers_to: github/09-workflows
when_to_use: "Read before writing or reviewing a GitHub Actions workflow file."
---
# GitHub Actions

## Purpose

This document defines how to write GitHub Actions workflows that are secure, reproducible,
and fast. It is written so an agent can author a `.github/workflows/*.yml` that does not
leak secrets, does not break on supply-chain changes, and enforces the quality gates a
pipeline needs.

GitHub Actions runs workflows — sets of jobs made of steps — triggered by repository
events. The security-critical facts are that third-party actions execute in your context
with access to whatever permissions and secrets you grant, and that the default token
permissions are broader than most jobs need. Design workflows to grant the least
possible.

## Why It Matters

A CI workflow is production infrastructure with write access to your code and deploy
credentials. Two failure modes dominate. First, supply chain: an action referenced by a
mutable tag (`@v4`) can be re-pointed by its maintainer — or a compromised maintainer — to
malicious code that runs with your secrets. Second, over-privilege: the default
`GITHUB_TOKEN` and blanket `secrets` exposure let a compromised or malicious step
exfiltrate credentials or push to your repo. Both are silent until exploited. Pinning,
least-privilege tokens, and OIDC turn a workflow from a standing liability into a bounded,
auditable process.

## Core Principles

- **Pin third-party actions to a full commit SHA.** A tag is mutable and can be moved
  under you; a SHA is immutable. Pin `owner/action@<40-char-sha>`, not `@v4`.
- **Grant least-privilege permissions explicitly.** Set `permissions:` to the minimum
  (default `contents: read`) at the workflow or job level; never rely on the broad default.
- **Prefer OIDC over stored secrets.** Exchange a short-lived OIDC token for cloud
  credentials rather than storing long-lived keys — see [secrets](15-secrets.md).
- **Never expose secrets to untrusted code.** `pull_request` from forks must not receive
  repository secrets; treat `pull_request_target` and workflow inputs as attack surface.
- **Make workflows reproducible.** Pin runner images and tool versions, cache
  deterministically, and keep the pipeline logic in the repo, not in console clicks.

## Best Practices

- Scope `permissions` per job; add `id-token: write` only on the job that needs OIDC, and
  keep `contents: read` everywhere else.
- Pin actions to SHAs and let Dependabot propose updates, so upgrades are reviewed rather
  than silently pulled.
- Use `concurrency` with `cancel-in-progress` to stop superseded runs on the same branch,
  saving minutes and avoiding races.
- Gate deploys with a protected [environment](16-environments.md) that requires approval
  and restricts which branches can deploy.
- Cache dependencies keyed on the lockfile hash for speed, but never cache secrets or
  auth state.
- Set a `timeout-minutes` on jobs so a hung step cannot burn runner minutes indefinitely.
- Keep secrets referenced by name (`${{ secrets.NAME }}`) and never `echo` them; enable
  step-level masking.
- Split reusable logic into composite actions or reusable workflows to avoid copy-paste
  drift across repos.

## Examples

**Good Example** — SHA-pinned, least privilege, OIDC, gated deploy

```yaml
name: deploy
on:
  push: { branches: [main] }
concurrency:                       # cancel superseded runs on the same ref
  group: deploy-${{ github.ref }}
  cancel-in-progress: true
permissions:
  contents: read                   # least privilege by default
jobs:
  deploy:
    runs-on: ubuntu-24.04          # pinned runner, not a moving 'latest'
    environment: production        # protected env: requires approval to proceed
    timeout-minutes: 15
    permissions:
      contents: read
      id-token: write              # OIDC only where needed
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2, SHA-pinned
      - uses: aws-actions/configure-aws-credentials@ececac1a45f3b08a01d2dd070d28d111c5fe6722 # v4.1.0
        with:
          role-to-assume: arn:aws:iam::111111111111:role/deploy  # short-lived, scoped
          aws-region: us-east-1
      - run: ./deploy.sh           # no long-lived key ever stored
```

**Bad Example** — mutable tags, broad permissions, echoed secret

```yaml
on: [push]
# No `permissions:` block → inherits the broad default write token for every job.
jobs:
  deploy:
    runs-on: ubuntu-latest         # moving image; builds are not reproducible
    steps:
      - uses: actions/checkout@v4                      # mutable tag: can be re-pointed
      - uses: some-org/deploy-action@main              # 'main' = whatever ships tonight
        env:
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET }} # long-lived static key
      - run: echo "key=${{ secrets.AWS_SECRET }}"      # secret printed into the build log
```

## Common Mistakes

- Referencing third-party actions by mutable tag or branch (`@v4`, `@main`) instead of a
  pinned commit SHA.
- Omitting `permissions:`, so every job runs with the broad default `GITHUB_TOKEN`.
- Storing long-lived cloud keys as secrets when OIDC federation is available.
- Exposing repository secrets to fork `pull_request`/`pull_request_target` workflows.
- Echoing secrets or passing them as visible arguments, leaking them into logs.
- Using `ubuntu-latest` and unpinned tool versions, so builds are not reproducible.
- No `timeout-minutes` or `concurrency`, wasting runner minutes on hung or superseded runs.

## Production Tips

- Turn on org-level "require actions pinned to SHA" and an allow-list of permitted
  actions to enforce supply-chain hygiene centrally.
- Use reusable workflows to standardize security settings across many repos instead of
  duplicating them.
- Review the workflow's effective permissions in the run summary; if a job has write scope
  it never uses, remove it.

## AI Review Checklist

- Are all third-party actions pinned to a full commit SHA, not a tag or branch?
- Is `permissions:` set explicitly to least privilege (default `contents: read`)?
- Does deployment use OIDC short-lived credentials instead of stored long-lived keys?
- Are secrets kept out of fork pull-request workflows and never echoed to logs?
- Is the runner image pinned and are tool versions deterministic?
- Do production deploys go through a protected environment requiring approval?
- Are `timeout-minutes` and `concurrency` set to bound cost and cancel superseded runs?

## Related

- `knowledge/github/09-workflows.md`
- `knowledge/cicd/15-secrets.md`
- `knowledge/cicd/16-environments.md`
- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/06-security-scanning.md`
- `knowledge/cicd/07-artifacts.md`
