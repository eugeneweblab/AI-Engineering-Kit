---
id: github/29-integrations
topic: github
slug: integrations
title: "Integrations"
type: doc
order: 29
status: ready
tags: [github, integrations, admin, write, timingSafeEqual, digest, github-actions]
related: [github/22-api, github/21-permissions, github/16-secret-scanning, github/26-automation, github/08-actions]
when_to_use: "Read before installing a GitHub App, issuing a token, or reviewing how a third party accesses your repos."
---
# Integrations

## Purpose

This document defines how external services connect to GitHub — **GitHub Apps, OAuth Apps,
personal access tokens (PATs), webhooks, and Marketplace listings** — and how to grant them
access safely. It covers choosing the right integration type, scoping permissions, verifying
webhook payloads, and rotating credentials. The concern is that every integration is a third
party you hand a key to; the key must open the fewest doors, for the shortest time, and you
must be able to prove who used it.

Pick the integration model deliberately. A GitHub App with fine-grained permissions is almost
always the right answer; a broad classic PAT tied to a person is almost always the wrong one.

## Why It Matters

An integration's token can read your code, read your secrets, and push commits. If it is
over-scoped, a breach of that third party becomes a breach of your repos. If it is a classic PAT
belonging to an employee, it carries that human's full access and dies (or lingers dangerously)
when they leave. If a webhook receiver does not verify signatures, anyone who learns the URL can
forge events and drive your automation. These failures are common precisely because integrations
are set up once, granted generous scopes "to be safe," and then forgotten — a standing liability
that no one is watching.

## Core Principles

- **Prefer GitHub Apps over OAuth Apps and PATs.** Apps have fine-grained, per-repo permissions,
  short-lived installation tokens, their own identity, and independent rate limits. The cost is a
  slightly heavier setup; the benefit is least-privilege, attributable, revocable access.
- **Grant the minimum permission set.** Give an app read where read suffices; never request
  `write` or `admin` scopes it does not use. Unused scope is pure downside if the app is breached.
- **Use short-lived, scoped tokens.** Installation tokens expire in an hour; **fine-grained PATs**
  with expiry and repo limits beat classic PATs. Never use a long-lived unscoped classic PAT.
- **Verify every webhook.** Validate the `X-Hub-Signature-256` HMAC with your secret and reject
  mismatches — an unverified webhook endpoint is an open command channel.
- **Own the credential lifecycle.** Set expiry, rotate on a schedule, revoke on offboarding, and
  store secrets in a manager — never in code or config.

## Best Practices

- Choose a **GitHub App** for services acting on repos (bots, CI, deploy). Use an **OAuth App**
  only when you need to act *as a user*; avoid it for machine-to-machine work.
- Request the **narrowest fine-grained permissions** and scope the installation to specific
  repositories, not "all repositories," unless genuinely required.
- Replace classic PATs with **fine-grained PATs** (expiry + repo + permission limits); for
  automation prefer an App installation token over any PAT. See [automation](26-automation.md).
- **Verify webhook signatures** with a constant-time HMAC comparison and reject on failure; treat
  the webhook secret like any other secret. Use HTTPS endpoints only.
- Store integration secrets in a secrets manager and reference them by name; enable
  [secret-scanning](16-secret-scanning.md) so a leaked token is caught.
- Review installed apps and OAuth authorizations regularly; remove unused ones and downgrade
  over-broad permissions.
- For cloud CI, prefer **OIDC** over storing provider credentials as GitHub secrets — see
  [actions](08-actions.md).

## Examples

**Good Example** — verify the webhook signature before acting

```ts
import crypto from "node:crypto";

function verify(req): boolean {
  const sig = req.headers["x-hub-signature-256"] ?? "";
  const expected =
    "sha256=" + crypto.createHmac("sha256", process.env.WEBHOOK_SECRET!) // secret from manager
      .update(req.rawBody).digest("hex");
  // Constant-time compare: a normal !== leaks the secret one byte at a time via timing.
  return sig.length === expected.length &&
    crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected));
}

app.post("/webhook", (req, res) => {
  if (!verify(req)) return res.status(401).end(); // reject forged/unsigned events
  handleEvent(req.body);
});
```

**Bad Example** — unverified webhook, over-scoped long-lived token

```ts
app.post("/webhook", (req, res) => {
  // No signature check: anyone who learns this URL can forge events and drive automation.
  handleEvent(req.body);
  res.status(200).end();
});

// Classic PAT with full scope, no expiry, committed in config — a person's entire access,
// forever, for a job that only needs to read one repo.
const token = "ghp_fullaccessnoexpiry...";
```

## Common Mistakes

- Using a classic PAT (broad, long-lived, personal) instead of a GitHub App or fine-grained PAT.
- Requesting `write`/`admin` scopes an integration never uses, or installing on "all repositories."
- Not verifying webhook signatures, leaving the endpoint open to forged events.
- Comparing signatures with `===` instead of a constant-time compare (timing leak).
- Committing tokens/webhook secrets to the repo instead of a secrets manager.
- Never rotating or expiring credentials, and not revoking them when an employee leaves.
- Choosing an OAuth App for machine automation where a GitHub App would be least-privilege.

## Production Tips

- Prefer App installation tokens for automation: short-lived, per-repo scoped, attributable to
  the app rather than a departing employee.
- Set expiry on every fine-grained PAT and calendar its rotation; audit `github-actions` and app
  tokens for staleness.
- Log which integration made which change (App tokens are attributable) so incidents are traceable.
- Vet Marketplace/third-party apps before install: review requested permissions and the vendor's
  security posture; an app you install can read what you grant it.

## AI Review Checklist

- Is the integration a GitHub App (or fine-grained PAT) rather than a broad classic PAT?
- Are the requested permissions the minimum needed, scoped to specific repositories?
- Are tokens short-lived and set to expire, with a rotation and offboarding-revocation plan?
- Do webhook endpoints verify the HMAC signature with a constant-time compare over HTTPS?
- Are all integration secrets stored in a secrets manager, not in code, and scanned for leaks?
- Is cloud CI auth done via OIDC rather than stored provider credentials?
- Are installed apps and authorizations reviewed periodically and unused ones removed?

## Related

- `knowledge/github/22-api.md`
- `knowledge/github/21-permissions.md`
- `knowledge/github/16-secret-scanning.md`
- `knowledge/github/26-automation.md`
- `knowledge/github/08-actions.md`
