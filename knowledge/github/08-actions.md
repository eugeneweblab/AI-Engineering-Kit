---
id: github/08-actions
topic: github
slug: actions
title: "Actions"
type: doc
order: 8
status: ready
tags: [github, actions]
related: [github/09-workflows, github/16-secret-scanning, github/21-permissions, github/11-releases, github/26-automation]
when_to_use: "Read before adding, pinning, or auditing any GitHub Action in a workflow."
---
# Actions

## Purpose

This document defines how to consume and secure **GitHub Actions** — the reusable steps
(`uses:`) that run inside a workflow job. It covers pinning, permissions, secret handling,
and supply-chain risk. It does not cover the workflow file structure, triggers, or job
graph — that is [workflows](09-workflows.md). Here the concern is: an action is third-party
code you are about to run with access to your repository and secrets.

Every `uses:` line executes someone else's code on your infrastructure. Treat it as a
dependency with the same rigor you apply to any other dependency.

## Why It Matters

An action runs inside your CI with a token that can push code, publish packages, and read
secrets. A compromised or malicious action — or a legitimate one you pinned to a mutable
tag that later changed — can exfiltrate every secret in the environment or inject code
into your release. Supply-chain attacks through Actions are real and have hit widely used
actions. Because CI runs automatically on every push, the blast radius is your entire
software supply chain, and the compromise is invisible until artifacts are already shipped.

## Core Principles

- **Pin to a full commit SHA, not a tag.** Tags are mutable; `@v4` can be repointed to
  malicious code. A 40-character SHA is immutable. The cost is manual bumps — worth it.
- **Grant the least token permission.** Default `GITHUB_TOKEN` to read-only and elevate
  per-job only where needed. A step that lints does not need `contents: write`.
- **Never pass secrets to untrusted actions.** A secret handed to a third-party action is
  a secret you no longer control. Prefer OIDC over long-lived secrets entirely.
- **Prefer first-party and verified actions.** Favor `actions/*` and verified creators;
  audit anything else's source before adding it.
- **Never run untrusted code with secrets on `pull_request_target`.** That trigger runs
  with write access in the base-repo context — a classic exfiltration hole.

## Best Practices

- Pin every third-party action to a commit SHA with the human-readable version in a
  comment: `uses: actions/checkout@<sha> # v4.2.2`.
- Set top-level `permissions:` explicitly (start from `contents: read`) so the token is
  least-privilege by default; widen only in the specific job that needs it.
- Use **Dependabot** to keep pinned SHAs updated so pinning does not mean going stale.
- Replace stored cloud credentials with **OIDC** (`id-token: write` + a cloud trust
  policy) so no long-lived secret exists to leak.
- Reference secrets only via `${{ secrets.NAME }}`; never `echo` a secret or write it to
  a file, and never interpolate untrusted input into a `run:` shell.
- Restrict which actions can run at the org/repo level (allow only verified + a SHA
  allowlist) so a typo cannot pull an unvetted action.
- Set a **per-workflow timeout** and pin the runner image (`ubuntu-24.04`, not
  `ubuntu-latest`) so builds are reproducible.

## Examples

**Good Example** — SHA-pinned actions, least-privilege token, OIDC

```yaml
permissions:
  contents: read            # default: read-only for the whole workflow

jobs:
  deploy:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      id-token: write        # only this job gets OIDC to assume a cloud role
    steps:
      # Pinned to an immutable SHA; comment records the version for humans + Dependabot.
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502 # v4.0.2
        with:
          role-to-assume: arn:aws:iam::111122223333:role/ci-deploy
          aws-region: us-east-1   # no stored AWS keys anywhere
```

**Bad Example** — mutable tag, over-broad token, leaked secret

```yaml
permissions: write-all                    # every job can push code + publish

jobs:
  build:
    runs-on: ubuntu-latest                # non-reproducible runner
    steps:
      - uses: some-org/build-action@main  # mutable ref → can change under you
        with:
          token: ${{ secrets.NPM_TOKEN }} # secret handed to third-party code
      - run: echo "key=${{ secrets.API_KEY }}"  # secret printed to public logs
```

## Common Mistakes

- Referencing actions by tag or branch (`@v4`, `@main`) instead of a commit SHA.
- Leaving `GITHUB_TOKEN` at default write scope, or setting `permissions: write-all`.
- Passing repository secrets into unaudited third-party actions.
- Using `pull_request_target` and then checking out and running PR code with secrets.
- Echoing secrets or writing them to files, exposing them in logs and artifacts.
- Pinning to `latest` runner images, making builds non-reproducible.
- Adding an action once and never updating the pin, accumulating known CVEs.

## Production Tips

- Enable the org policy "Allow select actions" with a verified-creator + SHA allowlist so
  developers cannot introduce arbitrary actions.
- Turn on Dependabot for the `github-actions` ecosystem to auto-open PRs bumping pinned
  SHAs — this reconciles security (pinning) with freshness.
- Audit the source of any composite/third-party action before first use; a composite
  action can run arbitrary shell you never see in your own repo.
- Prefer OIDC federation for all cloud auth; it removes the single most-leaked class of
  CI secret.

## AI Review Checklist

- Is every third-party action pinned to a full commit SHA (not a tag or branch)?
- Are workflow `permissions` least-privilege, defaulting to `contents: read`?
- Are secrets kept out of third-party actions and never echoed to logs?
- Is cloud auth done via OIDC rather than long-lived stored credentials?
- Is `pull_request_target` avoided when running untrusted PR code with secrets?
- Are runner images pinned to a specific version for reproducibility?
- Is Dependabot enabled to keep pinned actions current?

## Related

- `knowledge/github/09-workflows.md`
- `knowledge/github/16-secret-scanning.md`
- `knowledge/github/21-permissions.md`
- `knowledge/github/11-releases.md`
- `knowledge/github/26-automation.md`
