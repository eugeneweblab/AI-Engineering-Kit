---
id: rest-api/22-swagger
topic: rest-api
slug: swagger
title: "Swagger"
type: doc
order: 22
status: ready
tags: [rest-api, swagger]
related: [rest-api/21-openapi, rest-api/24-security, rest-api/14-versioning, rest-api/23-testing, rest-api/27-best-practices]
when_to_use: "Read before serving interactive API docs or wiring Swagger UI / Codegen tooling around an OpenAPI spec."
---
# Swagger

## Purpose

This document defines how to use the Swagger toolset — chiefly Swagger UI, Swagger
Editor, and Codegen — to turn an [OpenAPI](21-openapi.md) contract into interactive
documentation, generated clients, and a browsable "try it out" console. "Swagger" is
the tooling ecosystem; "OpenAPI" is the specification it consumes. This guide is about
the tools; the contract itself is covered in the OpenAPI doc.

Swagger answers "how do people and machines *consume* my OpenAPI spec?" — rendering it
as docs, exercising it live, and generating code from it.

## Why It Matters

A precise spec that no one can read helps no one. Swagger UI renders your OpenAPI
document as navigable, always-current documentation with a live request console, which
is often the first thing a new integrator touches. Because it is generated straight from
the contract, it cannot drift the way hand-written docs do. But the same tooling, wired
carelessly, becomes a liability: an exposed "try it out" console on production, a stale
bundled spec, or a UI that leaks internal endpoints turns a documentation aid into an
attack surface and a source of confusion. The value of Swagger comes entirely from it
reflecting the real, current contract — and from not exposing more than it should.

## Core Principles

- **Swagger renders the spec; it is not the spec.** Point Swagger UI at your single
  source-of-truth OpenAPI document. Never let the UI carry a separately edited copy that
  drifts from the running API.
- **Generated docs beat written docs.** Because Swagger UI is produced from the
  contract, it stays accurate for free. Prefer it over prose docs that must be updated
  by hand and won't be.
- **The interactive console is a real client.** "Try it out" sends real requests with
  real credentials. Treat it with the same auth, CORS, and environment care as any
  client — especially in production.
- **Version the docs with the API.** Serve docs for each supported API version so
  consumers see the contract that matches the endpoint they call; see
  [versioning](14-versioning.md).
- **Generated SDKs inherit the spec's quality.** Codegen output is only as good as the
  `operationId`s, schemas, and types in the spec. Fix the contract, not the generated
  code.

## Best Practices

- Serve Swagger UI from the live `/openapi.json` your app publishes, not from a checked-in
  static copy, so the docs update whenever the contract does.
- Configure the UI's `securitySchemes` so testers can authenticate in the console; do
  not embed real API keys or tokens in the served spec or examples.
- Restrict or disable the docs UI in production if the API is internal — put it behind
  auth, a VPN, or a non-public path. Public APIs may expose read-only docs but should
  still gate the interactive console appropriately.
- Set the correct `servers` list so "try it out" targets the intended environment, not
  accidentally production from a staging docs page.
- Lint and validate the spec (see [OpenAPI](21-openapi.md)) before it reaches Swagger UI;
  the renderer will happily display an invalid or misleading contract.
- Regenerate clients with Codegen from the published spec in CI, so SDKs never lag the
  contract.

## Examples

**Good Example** — UI served from the live spec, scoped and versioned

```ts
import swaggerUi from "swagger-ui-express";

// Serve the SAME document the app validates requests against — no second copy.
const spec = buildOpenApiSpec(); // generated from the running routes/schemas
spec.servers = [{ url: process.env.PUBLIC_API_URL }]; // console targets the right env

app.get("/openapi.json", (_req, res) => res.json(spec)); // single source of truth

// Docs live under a versioned path and, for an internal API, behind auth.
app.use("/docs/v1", requireInternalAuth, swaggerUi.serve, swaggerUi.setup(spec));
```

**Bad Example** — stale static copy, open console on production

```ts
// A hand-edited file that no longer matches the code. The console lies to every reader.
const spec = JSON.parse(fs.readFileSync("./docs/swagger.json", "utf8"));

// No auth, no server scoping. "Try it out" fires real, unauthenticated requests
// straight at production — a public write console for anyone who finds the URL.
app.use("/docs", swaggerUi.serve, swaggerUi.setup(spec));
```

## Common Mistakes

- Serving a checked-in static spec that has drifted from the actual API.
- Exposing the interactive console on production for an internal API with no auth.
- Embedding real credentials or tokens in the served spec or its examples.
- Leaving `servers` pointing at the wrong environment, so testers hit production by
  accident.
- Editing Codegen output by hand instead of fixing the spec and regenerating.
- Treating Swagger UI as the contract and editing it directly, bypassing the spec.

## Production Tips

- Gate merges on the served spec matching the running app via a contract test, so the
  docs cannot silently go stale.
- For public APIs, consider a read-only docs deployment (console disabled or sandboxed)
  and a separate, authenticated environment for live trials.
- Cache the rendered UI assets but never the spec endpoint with a long TTL — the
  contract must reflect the current deploy.

## AI Review Checklist

- Does Swagger UI render the live, single-source spec rather than a static copy?
- Is the interactive console appropriately restricted (auth/network) in production?
- Are `servers` scoped to the correct environment?
- Are real credentials kept out of the served spec and examples?
- Are docs versioned alongside the API?
- Are generated SDKs produced from the published spec in CI, not hand-edited?

## Related

- `knowledge/rest-api/21-openapi.md`
- `knowledge/rest-api/24-security.md`
- `knowledge/rest-api/14-versioning.md`
- `knowledge/rest-api/23-testing.md`
- `knowledge/rest-api/27-best-practices.md`
