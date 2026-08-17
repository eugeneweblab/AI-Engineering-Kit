---
id: github/16-secret-scanning
topic: github
slug: secret-scanning
title: "Secret Scanning"
type: doc
order: 16
status: ready
tags: [github, secret-scanning, API_TOKEN, gitleaks, STRIPE_KEY, runs-on]
related: [github/13-security, github/14-codeql, github/15-dependabot, github/17-branch-protection, github/08-actions]
when_to_use: "Read before enabling secret scanning or responding to a leaked-credential alert."
---
# Secret Scanning

## Purpose

This document defines how to use GitHub **secret scanning** and **push protection** to
keep credentials — API keys, tokens, private keys, connection strings — out of the
repository, and how to respond correctly when one leaks. It covers detection vs. push
protection, custom patterns, the validity check, and the non-negotiable rotate-first
response.

Secret scanning is the "leaked credentials" leg of the security stack, alongside
[CodeQL](14-codeql.md) (your code) and [Dependabot](15-dependabot.md) (dependencies). Of
the three, it is the one whose alerts mean **the damage may already be done**.

## Why It Matters

A credential committed to git is compromised the instant it is pushed, even if you delete
it seconds later: it lives in git history forever, is visible to anyone with read access,
and — on public repos — is harvested by automated scrapers within minutes. Deleting the
commit does not help; the secret is already copied. This is one of the most common and most
damaging breaches precisely because it feels harmless in the moment ("I'll fix it in the
next commit"). **Push protection** is the only feature here that prevents the leak instead
of reporting it — which is why it is the priority.

## Core Principles

- **Push protection is prevention; scanning is detection.** Enable push protection to stop
  the secret before it enters history. Scanning-only tells you after it's too late.
- **A pushed secret is a compromised secret.** The response is always **rotate first**,
  then remove. Never assume "I removed it fast enough."
- **Removing the commit does not remove the secret.** It persists in history, forks, and
  clones. Revocation at the provider is the only real fix.
- **Keep secrets out by construction.** Use GitHub Actions secrets, a secrets manager, or
  OIDC federation — so there is nothing to scan for in the first place.
- **Tune, don't disable.** Add custom patterns for your internal tokens; suppress
  false-positive locations, never turn scanning off to silence noise.

## Best Practices

- Enable secret scanning **and** push protection on every repo; org security defaults
  should make both automatic for new repos.
- Add **custom patterns** for internal/first-party secret formats (internal service tokens,
  legacy API keys) that GitHub's partner patterns don't cover.
- Rely on **partner validity checks** where available — GitHub can confirm with the
  provider whether a leaked token is still live, so you triage real exposure first.
- When push protection blocks a push, **fix it, don't bypass it.** Reserve the bypass path
  for audited false positives; every bypass is logged for review.
- Never commit `.env`, `*.pem`, `id_rsa`, or credential files — add them to `.gitignore`
  and provide a committed `.env.example` with placeholder values.
- Use OIDC (`id-token: write`) to federate into cloud providers so there is no long-lived
  cloud key to leak at all.

## Examples

**Good Example** — secret injected at runtime, nothing to scan

```yaml
# The token never touches the repo; it is an encrypted Actions secret, injected at run time.
jobs:
  deploy:
    runs-on: ubuntu-24.04
    environment: production        # secret is gated behind an environment + reviewers
    steps:
      - run: ./deploy.sh
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}   # not in git; managed and rotatable
```

**Bad Example** — real key hard-coded, and the wrong response to the leak

```python
# config.py — a live key committed to the repo: compromised the moment it is pushed
STRIPE_KEY = "sk_live_51Hb9...real..."   # scraped by bots within minutes on public repos

# WRONG response: "just remove it in the next commit"
#   git rm config.py && git commit -m "remove key"
# The key is still in history, forks, and clones. Correct response: ROTATE the key at
# Stripe first, THEN purge history — deletion alone changes nothing.
```

## Common Mistakes

- Enabling detection but not **push protection**, so leaks are reported instead of prevented.
- Responding to a leak by deleting the commit without rotating — the secret is still live.
- Bypassing push protection routinely instead of fixing the underlying commit.
- Committing `.env`/key files because they weren't in `.gitignore`.
- Assuming a private repo is safe — collaborators, forks, and future public visibility all
  expose committed secrets.
- Disabling scanning to stop false-positive noise instead of adding pattern suppressions.

## Production Tips

- Turn on push protection org-wide via a security configuration; do not rely on each repo
  opting in.
- Review the **bypass audit log** — a spike in bypasses signals a workflow that keeps
  producing false positives (fix the pattern) or a team routing around the control.
- Wire secret-scanning alerts to an on-call/security channel; a live-token alert is an
  incident, not a backlog item.
- Pre-empt leaks locally with a client-side scanner (e.g. `gitleaks`) as a pre-commit hook,
  so the developer catches it before the push even reaches GitHub.

## AI Review Checklist

- Are secret scanning **and** push protection both enabled on the repo?
- Are there custom patterns for internal/first-party secret formats?
- Does the incident response **rotate the credential first**, then purge history?
- Are `.env`, `*.pem`, and key files git-ignored, with a placeholder `.env.example`?
- Are runtime secrets injected via Actions secrets/OIDC rather than committed?
- Is the push-protection bypass path audited, not used as a routine escape hatch?

## Related

- `knowledge/github/13-security.md`
- `knowledge/github/14-codeql.md`
- `knowledge/github/15-dependabot.md`
- `knowledge/github/17-branch-protection.md`
- `knowledge/github/08-actions.md`
