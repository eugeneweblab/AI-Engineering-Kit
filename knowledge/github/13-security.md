---
id: github/13-security
topic: github
slug: security
title: "GitHub Security"
type: doc
order: 13
status: ready
tags: [github, security, SECURITY.md, "permissions:", GITHUB_TOKEN, "@main", runs-on]
related: [github/14-codeql, github/15-dependabot, github/16-secret-scanning, github/17-branch-protection, github/21-permissions]
when_to_use: "Read before configuring repository security or hardening a CI/CD supply chain on GitHub."
---
# GitHub Security

## Purpose

This document maps GitHub's repository security surface and defines how to configure it as
a defense-in-depth system rather than a checklist of isolated toggles. It is the hub for
the deeper docs: [CodeQL](14-codeql.md) (code scanning), [Dependabot](15-dependabot.md)
(dependency security), [secret scanning](16-secret-scanning.md), and
[branch protection](17-branch-protection.md). It also covers the parts that live only
here: the security policy, private vulnerability reporting, the advisory workflow, and —
most importantly — GitHub Actions supply-chain hardening.

Repository security on GitHub is layered: **prevent** (branch protection, permissions),
**detect** (code scanning, secret scanning, Dependabot), and **respond** (advisories,
private reporting). A secure repo uses all three; any one alone leaves a gap.

## Why It Matters

A source repository is a high-value target: it holds the code, the CI credentials, and the
keys to production. The dominant attack today is the **supply chain** — a malicious
dependency, a compromised third-party Action pinned to a mutable tag, or a leaked token in
a workflow log. These do not trip application-level defenses because the attacker runs
inside your trusted CI. GitHub's native tools close these gaps at the platform layer, but
only if configured; every feature here is off or permissive by default on new repos.

## Core Principles

- **Defense in depth.** No single control is sufficient. Layer prevention, detection, and
  response so a bypass of one is caught by another.
- **Least privilege everywhere.** Default `GITHUB_TOKEN` to `contents: read`; grant each
  workflow only the scopes it needs. Broad tokens are the blast radius of a CI compromise.
- **Pin what you execute.** Third-party Actions are remote code running with your secrets.
  Pin them to a full commit SHA, never a mutable tag like `@v4` or `@main`.
- **Shift left, but enforce at the gate.** Detection tools add value only when their
  findings block merge via required status checks — advisory-only scanning gets ignored.
- **Secrets belong in a secrets store, never in the repo.** Rotate on suspected exposure;
  detection is a backstop, not a substitute for keeping them out.

## Best Practices

- Enable the full detection stack: code scanning (CodeQL), Dependabot alerts + version
  updates, and secret scanning with push protection. Wire each into required checks.
- Set `permissions:` explicitly at the top of every workflow. Start from
  `permissions: {}` or `contents: read` and add scopes per job.
- Pin third-party Actions to a 40-char commit SHA and let Dependabot update the pins.
  Trust `actions/*` and `github/*` (first-party) with tags only if you accept the risk.
- Add a `SECURITY.md` with a disclosure policy and enable **private vulnerability
  reporting** so researchers have a non-public channel.
- Guard deployment secrets behind **environments** with required reviewers, so a PR from a
  fork or a compromised branch cannot reach production credentials.
- Enable organization-wide security defaults (security configurations) so new repos are
  born hardened instead of relying on per-repo memory.

## Examples

**Good Example** — hardened workflow: least privilege + SHA-pinned Action

```yaml
# Read-only by default; each job opts into exactly what it needs.
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      # Third-party Action pinned to a full commit SHA — an attacker who moves the
      # tag cannot swap in malicious code, because the SHA is immutable.
      - uses: dtolnay/rust-toolchain@a54c7afa936fefeb4456b2dd8068152669aa8203
      - run: cargo test
```

**Bad Example** — write-all token running an unpinned third-party Action

```yaml
permissions: write-all            # every scope granted to every step — huge blast radius
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: some-org/deploy-action@main   # mutable ref: today's code != tomorrow's
        with:
          token: ${{ secrets.PROD_DEPLOY_TOKEN }}  # prod creds handed to unpinned 3P code
```

## Common Mistakes

- Leaving `GITHUB_TOKEN` at the default write scope, or using `permissions: write-all`.
- Pinning third-party Actions to `@v4`/`@main` — mutable refs are a supply-chain backdoor.
- Enabling scanning but not making it a required check, so findings never block a merge.
- Storing secrets as plain repo/org variables instead of encrypted secrets + environments.
- No `SECURITY.md` and no private reporting channel, forcing public 0-day disclosure.
- Treating detection as prevention — a secret-scanning alert means the secret already leaked.

## Production Tips

- Turn on GitHub's **security configurations** at the org level and apply them to all repos
  so new repositories inherit hardened defaults automatically.
- Audit workflow permissions and Action pins in CI with a linter (e.g. `zizmor`,
  `actionlint`) as a required check.
- Route Dependabot, code-scanning, and secret-scanning alerts to a security team via the
  org security overview; unrouted alerts rot.
- Prefer OIDC (`id-token: write`) to federate into cloud providers instead of long-lived
  static cloud keys stored as secrets.

## AI Review Checklist

- Does every workflow declare explicit, least-privilege `permissions:`?
- Are all third-party Actions pinned to a full commit SHA?
- Are CodeQL, Dependabot, and secret scanning enabled *and* wired into required checks?
- Are deployment secrets gated behind environments with required reviewers?
- Is there a `SECURITY.md` and private vulnerability reporting enabled?
- Are cloud credentials federated via OIDC rather than stored as static secrets?

## Related

- `knowledge/github/14-codeql.md`
- `knowledge/github/15-dependabot.md`
- `knowledge/github/16-secret-scanning.md`
- `knowledge/github/17-branch-protection.md`
- `knowledge/github/21-permissions.md`
