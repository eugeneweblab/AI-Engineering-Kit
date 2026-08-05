---
id: tools/23-api-clients
topic: tools
slug: api-clients
title: "API Clients"
type: doc
order: 23
status: ready
tags: [tools, api-clients]
related: [tools/24-database-tools, tools/14-playwright, tools/29-observability-tools, tools/19-task-runners, tools/30-engineering-principles, rest-api/21-openapi, testing/12-api-testing]
when_to_use: "Read before testing or documenting an HTTP API by hand — using curl, HTTPie, or a GUI client, and keeping request collections in version control."
---
# API Clients

## Purpose

This document defines how to exercise HTTP APIs during development: command-line tools for
quick checks, file-based collections that live in the repository, and the practices that keep
credentials out of shared workspaces.

## Why It Matters

Every API gets called by hand during development. The question is whether that knowledge is
captured — a reproducible request another engineer can run — or lost in someone's terminal
history and a GUI workspace nobody else has.

The second concern is credentials. GUI clients with cloud sync have leaked production tokens
by default more than once; a token pasted into a shared workspace is a token in a third party's
database.

## Core Principles

- **Requests belong in the repository**, next to the code they exercise.
- **Credentials come from the environment**, never from a saved request.
- **Prefer file-based clients** for anything shared; a GUI workspace is a personal artifact.
- **A hand-made request is not a test.** Reproducing a call by hand is exploration; the check
  that must not regress belongs in an automated test.

## Command Line

```bash
# curl — always available, and the form to paste into a bug report
curl -sS -X POST https://api.example.com/v1/orders \
  -H "Authorization: Bearer $API_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"sku":"blue-widget","qty":2}' \
  -w '\nHTTP %{http_code} in %{time_total}s\n'

# Headers and body, for debugging a redirect or a caching problem
curl -sS -i https://api.example.com/v1/orders/42

# Pretty output with jq, plus a filter
curl -sS https://api.example.com/v1/orders | jq '.data[] | {id, status, total}'
```

```bash
# HTTPie — friendlier syntax, JSON by default
http POST api.example.com/v1/orders \
  Authorization:"Bearer $API_TOKEN" \
  sku=blue-widget qty:=2          # := sends a number rather than a string
```

The `-w '%{http_code} %{time_total}'` flag is worth building a habit around: it turns every
manual call into a rough latency measurement.

## Collections in the Repository

File-based clients keep requests reviewable and diffable. The `.http` format is supported by
the VS Code REST Client extension and by JetBrains IDEs:

```http
### requests/orders.http
@baseUrl = {{$dotenv BASE_URL}}
@token = {{$dotenv API_TOKEN}}

### List orders
GET {{baseUrl}}/v1/orders?status=pending
Authorization: Bearer {{token}}

### Create an order
# @name createOrder
POST {{baseUrl}}/v1/orders
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "sku": "blue-widget",
  "qty": 2
}

### Fetch the order just created — chained from the previous response
GET {{baseUrl}}/v1/orders/{{createOrder.response.body.id}}
Authorization: Bearer {{token}}
```

```gitignore
.env            # holds BASE_URL and API_TOKEN; never committed
```

Two properties make this preferable to a GUI workspace: requests change in pull requests
alongside the API, and there is no cloud account holding your tokens.

For OpenAPI-described APIs, generate the client instead of hand-writing requests — the spec is
the contract, and a generated client stays in sync with it. See
[REST API — OpenAPI](../rest-api/21-openapi.md).

## GUI Clients

Postman, Insomnia, Bruno, and Hoppscotch all work; the differences that matter are storage and
sync:

- **Bruno** stores collections as plain files in the repository — the best fit for team work.
- **Insomnia** and **Postman** sync to their cloud by default. Turn that off for anything
  touching production, or use them only against local environments.
- Whichever is chosen, keep secrets in environment variables the client reads at runtime, not
  in the saved collection.

## Examples

**Good Example** — a reproducible request in a bug report

```bash
# Reproduces the 500 on staging (order 4471, coupon SPRING25):
curl -sS -i -X POST https://staging.example.com/api/v1/orders/4471/apply-coupon \
  -H "Authorization: Bearer $STAGING_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"code":"SPRING25"}'

# → HTTP/1.1 500
# → {"error":"internal_error","request_id":"01J4X..."}
```

Anyone can run this, and the `request_id` links it to the server-side trace.

**Bad Example** — the credential that leaks

```json
// orders.postman_collection.json — committed to the repository
{
  "auth": {
    "type": "bearer",
    "bearer": [{ "key": "token", "value": "sk_live_51H8xK2eZvKYlo2C..." }]
  }
}
```

A live key in version control must be rotated, not deleted — it is in every clone and in the
platform's history.

## Common Mistakes

- Tokens saved inside collections, then committed or synced to a vendor cloud.
- Collections that exist only in one person's client.
- Production credentials in a workspace used for casual exploration.
- Manual requests treated as regression coverage.
- No `Content-Type` header, producing confusing 400s or silently-empty request bodies.
- `-k` / `--insecure` used habitually, masking real certificate problems.
- Copying a full browser request including session cookies into a shared document.
- Collections that drift from the API because nothing links them to the code.

## Production Tips

- Store a working request for each endpoint next to its tests; it becomes the fastest
  onboarding artifact the API has.
- Use separate environment files per target (`local`, `staging`) and never define a production
  environment in a client that syncs.
- Capture `request_id` or trace headers in responses and quote them in bug reports — that is
  what connects a client-side symptom to a server-side trace, see
  [Observability Tools](29-observability-tools.md).
- When an API call must keep working, promote it from a `.http` file to a contract test — see
  [Testing — Contract Testing](../testing/11-contract-testing.md).
- `curl --compressed` and `-H 'Accept-Encoding: gzip'` are worth using when debugging response
  sizes; without them you measure the uncompressed payload.

## AI Review Checklist

- Are request collections stored in the repository rather than a personal workspace?
- Do requests read credentials from the environment?
- Is any token committed or synced to a vendor cloud?
- Are production credentials excluded from exploratory tooling?
- Are critical calls covered by automated tests rather than manual requests?
- Do collections stay current with the API, ideally generated from a spec?

## Related


- `knowledge/tools/24-database-tools.md`
- `knowledge/tools/14-playwright.md`
- `knowledge/tools/29-observability-tools.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/rest-api/21-openapi.md`
- `knowledge/testing/12-api-testing.md`
