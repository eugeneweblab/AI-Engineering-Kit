---
id: github/01-github-platform
topic: github
slug: github-platform
title: "GitHub Platform"
type: doc
order: 1
status: ready
tags: [github, github-platform, GITHUB_TOKEN, GitHub, handle, X-RateLimit-Remaining, X-Hub-Signature-256, If-None-Match]
related: [github/02-repositories, github/19-organizations, github/21-permissions, github/22-api, github/23-cli]
when_to_use: "Read before writing any GitHub automation, to understand the object model, hosting tiers, and auth surfaces you are targeting."
---
# GitHub Platform

## Purpose

This document describes GitHub as a *system*: its object model (users, orgs,
repositories, refs, pull requests, checks), its hosting tiers (github.com,
GitHub Enterprise Cloud, GitHub Enterprise Server), and its programmable surfaces
(REST, GraphQL, webhooks, Apps, Actions). An agent that knows this model can pick
the right interface and predict how a change will propagate, instead of treating
GitHub as an opaque website.

## Why It Matters

Almost every GitHub mistake traces back to a wrong mental model. An agent that
does not know a fork is a full repository copy will look for a branch that does not
exist. One that does not know GraphQL is required for Projects v2 will burn calls
on a REST endpoint that returns 404. One that hardcodes `api.github.com` breaks the
moment it runs on GitHub Enterprise Server. Getting the platform model right is the
difference between automation that works everywhere and automation that works once.

## Core Principles

- **Everything is an addressable object with a stable ID.** Repos, Issues, PRs,
  and comments each have a numeric/node ID; automation should key on IDs, not on
  titles or URLs, which change.
- **Git and GitHub are separate layers.** Git owns commits, trees, and refs;
  GitHub adds PRs, reviews, checks, and permissions on top. Branch protection is a
  GitHub concept, not a Git one.
- **There are three account tiers, not one.** github.com (SaaS), GitHub Enterprise
  Cloud (isolated SaaS tenant), and GitHub Enterprise Server (self-hosted). API base
  URLs and available features differ; never assume github.com.
- **Two API dialects coexist.** REST for most resources; GraphQL where you need
  nested data in one round trip or a Projects v2 / Discussions object REST does not
  fully expose. Pick per resource, not per preference.
- **Identity is scoped.** Actions run as `GITHUB_TOKEN`; automation should run as a
  [GitHub App](21-permissions.md) with least-privilege permissions, not a human PAT.

## Best Practices

- Resolve the API base URL from `GITHUB_API_URL` (Actions) or configuration, so the
  same code runs on github.com and Enterprise Server.
- Authenticate automation as a GitHub App installation token (short-lived, scoped)
  over a fine-grained PAT over a classic PAT — in that order of preference.
- Use conditional requests (`ETag`/`If-None-Match`) and respect the
  `X-RateLimit-Remaining` and `Retry-After` headers; do not hammer on 403.
- Subscribe to **webhooks** for event-driven work instead of polling; verify the
  `X-Hub-Signature-256` HMAC on every delivery.
- Prefer the [`gh` CLI](23-cli.md) for one-off and scripted operations — it handles
  auth, pagination, and Enterprise base URLs for you.

## Examples

**Good Example** — portable base URL, scoped token, signature verification

```bash
# Resolve the host instead of hardcoding github.com so this runs on Enterprise too.
API="${GITHUB_API_URL:-https://api.github.com}"

# Use the short-lived, workflow-scoped token, not a personal PAT.
curl -sS -H "Authorization: Bearer ${GITHUB_TOKEN}" \
     -H "Accept: application/vnd.github+json" \
     -H "X-GitHub-Api-Version: 2022-11-28" \
     "${API}/repos/${GITHUB_REPOSITORY}/pulls?state=open"
```

```python
# Webhook receiver: reject any delivery whose HMAC does not match our secret,
# because an unverified payload can be forged by anyone who knows the URL.
import hmac, hashlib
def verify(secret: bytes, body: bytes, header: str) -> bool:
    expected = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header)  # constant-time compare
```

**Bad Example** — hardcoded host, personal token, unverified webhook

```bash
# Breaks on GitHub Enterprise Server, and leaks a broad personal token.
curl -H "Authorization: token ghp_myPersonalToken123" \
     https://api.github.com/repos/acme/app/pulls   # host will 404 on GHES
```

```python
def handle(body):        # no signature check → anyone can POST fake events
    do_deploy(body)      # trusting an unauthenticated payload
```

## Common Mistakes

- Hardcoding `api.github.com`, so the code fails on Enterprise Server.
- Reaching for REST when the resource (Projects v2, Discussions) needs GraphQL.
- Keying automation on Issue/PR titles instead of stable node IDs.
- Using a long-lived classic PAT with broad scopes for CI, instead of `GITHUB_TOKEN`
  or an App token.
- Polling the API on a tight loop and getting secondary-rate-limited.

## Production Tips

- Cache installation tokens for their full ~1 hour lifetime; minting one per request
  wastes calls and can trip rate limits.
- Log the `x-github-request-id` header on every API error; GitHub Support can trace
  an incident from it.
- Test automation against a scratch org or repo before pointing it at production.

## AI Review Checklist

- Is the API base URL derived from environment/config, not hardcoded?
- Does automation authenticate with the least-privilege token available?
- Are webhook payloads HMAC-verified before any side effect?
- Does the code key on stable IDs rather than mutable titles or URLs?
- Are rate-limit and retry headers respected?

## Related

- `knowledge/github/02-repositories.md`
- `knowledge/github/19-organizations.md`
- `knowledge/github/21-permissions.md`
- `knowledge/github/22-api.md`
- `knowledge/github/23-cli.md`
