---
id: github/22-api
topic: github
slug: api
title: "API"
type: doc
order: 22
status: ready
tags: [github, api]
related: [github/23-cli, github/21-permissions, github/26-automation, github/29-integrations, github/08-actions]
when_to_use: "Read before writing any code that calls the GitHub REST or GraphQL API, handles pagination, or manages rate limits."
---
# API

## Purpose

This document defines how to call the GitHub **API** — REST and GraphQL — correctly:
authenticating, paginating, respecting rate limits, and handling errors. It is written
so an agent can write an integration that does not silently truncate data, get itself
throttled, or leak a token.

GitHub exposes two APIs. **REST** is resource-oriented and broad; **GraphQL** lets you
fetch exactly the fields you need in one round-trip and reach data REST does not expose
(Projects v2, some org insights). Choose per task, not by habit.

## Why It Matters

API integrations run unattended, so their failures are the worst kind: a script that
paginates wrong reports "3 open PRs" when there are 300, and nobody notices until a
decision is made on bad data. A client that ignores rate limits gets the whole
integration — and every other tool sharing that token — throttled. A leaked token grants
whatever [permissions](21-permissions.md) it holds. Because these programs are trusted to
be correct without a human watching, correctness and safety are non-negotiable.

## Core Principles

- **Authenticate with the narrowest, shortest-lived credential.** Prefer a **GitHub App
  installation token** or **fine-grained PAT** over a classic PAT; in Actions, use the
  built-in `GITHUB_TOKEN`. Never hardcode a token — read it from a secret.
- **Always paginate to completion.** A single response is a *page*, not the full set.
  Follow the `Link` header (REST) or `pageInfo.hasNextPage` cursor (GraphQL) until done.
- **Respect rate limits proactively.** Check `X-RateLimit-Remaining`/`Reset`; on `403`
  or `429` with `Retry-After`, back off — do not hammer. Secondary limits punish bursts.
- **Send conditional requests.** Use `ETag`/`If-None-Match`; a `304 Not Modified` does
  not count against your primary rate limit and saves bandwidth.
- **Fail on the status code, not the body.** Check for `2xx`; treat `4xx`/`5xx` as errors
  with their `message` and `documentation_url`, and honor `Retry-After` on `5xx`.

## Best Practices

- Use an official SDK (**Octokit** for JS/TS, or a maintained client for your language).
  It handles pagination, auth token refresh, and retry/backoff so you do not reinvent them.
- Pin the API version with the `X-GitHub-Api-Version` header so a future breaking change
  does not silently alter responses.
- For bulk reads that touch many related fields, use **GraphQL** to avoid N+1 REST calls;
  for simple single-resource actions, REST is clearer.
- Cache with `ETag`s and only refetch on change; this keeps you under rate limits at scale.
- For webhooks, **verify the `X-Hub-Signature-256` HMAC** before trusting the payload,
  and respond `2xx` fast — do heavy work asynchronously.
- Scope tokens per repository and per resource (see [permissions](21-permissions.md));
  rotate and store them in a secrets manager, never in code or logs.

## Examples

**Good Example** — paginate fully, back off, verify status (Octokit)

```ts
import { Octokit } from "@octokit/rest";

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,          // from a secret, never hardcoded
  request: { headers: { "X-GitHub-Api-Version": "2022-11-28" } }, // pinned version
});

// paginate() follows the Link header to the LAST page — no silent truncation.
const prs = await octokit.paginate(octokit.pulls.list, {
  owner: "acme", repo: "billing", state: "open", per_page: 100,
});
// Octokit retries on secondary rate limits with backoff by default.
console.log(`open PRs: ${prs.length}`);   // the true count, not just page 1
```

**Bad Example** — first page only, no error or rate-limit handling

```ts
// Fetches ONE page (default 30) and treats it as the whole set → undercounts silently.
const res = await fetch(
  "https://api.github.com/repos/acme/billing/pulls?state=open",
  { headers: { Authorization: `token ${TOKEN}` } }  // classic full-scope PAT, hardcoded
);
const prs = await res.json();              // no status check: a 403 rate-limit body
console.log(`open PRs: ${prs.length}`);    // becomes "0 PRs" with no error raised
```

## Common Mistakes

- Reading only the first page and reporting truncated counts as complete.
- Ignoring `X-RateLimit-*` and retrying tight loops until the token is throttled.
- Not checking the HTTP status, so an error body (a `403` object) is parsed as data.
- Hardcoding a classic, broadly scoped PAT instead of a fine-grained or App token.
- Skipping webhook signature verification and acting on forged payloads.
- Making dozens of REST calls where one GraphQL query would do, exhausting rate budget.

## Production Tips

- Log the `X-RateLimit-Remaining` and `Reset` on responses so throttling is observable
  before it bites.
- For high-volume automation, use a **GitHub App** — it gets a higher rate limit per
  installation and short-lived tokens, unlike a shared PAT.
- Add jitter to retry backoff so parallel workers do not synchronize and trip secondary
  limits together.

## AI Review Checklist

- Does the client paginate to completion (Link header / GraphQL cursor)?
- Is the credential a fine-grained PAT, App token, or `GITHUB_TOKEN` — never a hardcoded
  classic PAT?
- Are rate limits checked and `Retry-After`/`403`/`429` honored with backoff?
- Is the HTTP status checked before the body is treated as data?
- Is the API version pinned via `X-GitHub-Api-Version`?
- Are webhook payloads HMAC-verified before use?
- Is GraphQL used for related-field bulk reads to avoid N+1 REST calls?

## Related

- `knowledge/github/23-cli.md`
- `knowledge/github/21-permissions.md`
- `knowledge/github/26-automation.md`
- `knowledge/github/29-integrations.md`
- `knowledge/github/08-actions.md`
