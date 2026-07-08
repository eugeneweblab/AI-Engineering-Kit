---
id: graphql/00-overview
topic: graphql
slug: overview
title: "Overview"
type: doc
order: 0
status: ready
tags: [graphql, overview]
related: [graphql/01-graphql-fundamentals, graphql/02-schema, graphql/04-queries, graphql/05-mutations, graphql/07-resolvers]
when_to_use: "Read first when starting any GraphQL work, to see how the topic's docs fit together."
---
# Overview

## Purpose

This document is the map for the `graphql` topic. It orients an agent to what
GraphQL is, which decisions matter, and which sibling doc answers each question.
Read it first, then jump to the specific doc for the task at hand.

GraphQL is a query language for APIs and a runtime for fulfilling those queries
against a typed schema. A client asks for exactly the fields it needs in one
request; the server resolves each field and returns a matching, strongly-typed
JSON shape. The contract is the schema, not the transport.

## Why It Matters

The strengths of GraphQL — a single flexible endpoint, client-driven field
selection, a self-documenting type system — are also where it fails in
production if built naively. The same flexibility that lets a client fetch a
whole object graph in one call lets a hostile client craft a query that fans out
into millions of database rows. The same resolver-per-field model that keeps
code modular is the exact mechanism that produces N+1 query storms. Getting
GraphQL right means understanding these trade-offs before writing resolvers, not
after an incident.

## Core Principles

- **The schema is the contract.** Design the schema for the client's needs and
  the domain, not as a thin mirror of your database tables.
- **Every field is a resolver, and resolvers run per-parent.** A list of N items
  runs child resolvers N times. Assume this and batch, or you will ship N+1.
- **The client controls cost.** Because clients pick fields and depth, the server
  must bound query complexity, depth, and rate — the client cannot be trusted.
- **Errors are data, not exceptions.** A GraphQL response can be partially
  successful; model expected failures in the schema, not as thrown 500s.
- **Types are checked, values are not.** The type system guarantees shape, never
  business validity. Validate inputs in resolvers regardless.

## How the Docs Fit Together

- **Foundations** — start here to understand the model.
  [Fundamentals](01-graphql-fundamentals.md) explains the request/response model
  and how GraphQL differs from REST.
- **Defining the API** — [Schema](02-schema.md) covers the SDL and schema design;
  [Types](03-types.md) covers objects, enums, interfaces, unions, and non-null;
  [Scalars](09-scalars.md) and [Input Types](10-input-types.md) cover leaf and
  argument types; [Directives](11-directives.md) covers schema and query
  directives.
- **Operations** — [Queries](04-queries.md) (reads),
  [Mutations](05-mutations.md) (writes), and
  [Subscriptions](06-subscriptions.md) (real-time). [Fragments](12-fragments.md)
  keep client selections reusable.
- **Execution** — [Resolvers](07-resolvers.md) and [Context](08-context.md) are
  how fields get their values. [Pagination](13-pagination.md) and
  [Filtering](14-filtering.md) shape list fields.
- **Performance** — the [N+1 problem](15-n1-problem.md),
  [DataLoader](16-dataloader.md), [Caching](21-caching.md), and
  [Performance](22-performance.md) keep the graph fast.
- **Safety** — [Security](17-security.md), [Authentication](18-authentication.md),
  [Authorization](19-authorization.md), and [Error Handling](20-error-handling.md)
  keep it safe.
- **Scale and lifecycle** — [Federation](23-federation.md),
  [Testing](24-testing.md), [Monitoring](25-monitoring.md),
  [Schema Evolution](29-schema-evolution.md), and [Production](27-production.md).
- **Cross-cutting** — [Best Practices](26-best-practices.md),
  [Tooling](28-tooling.md), [Engineering Principles](30-engineering-principles.md),
  and [Common Anti-patterns](100-common-antipatterns.md).

## Best Practices

- Read [Fundamentals](01-graphql-fundamentals.md) and [Schema](02-schema.md)
  before writing any SDL — most costly mistakes are design mistakes baked into
  the schema early.
- Before shipping any list field, confirm you have read
  [N+1](15-n1-problem.md) and [Pagination](13-pagination.md); unbounded lists
  and N+1 are the two most common production failures.
- Treat [Security](17-security.md) as mandatory for any public endpoint — a
  GraphQL endpoint with no depth or complexity limit is a denial-of-service
  vector by default.

## Common Mistakes

- Treating GraphQL as REST-over-POST and designing one query per screen instead
  of a reusable graph.
- Skipping the performance docs and shipping resolvers that issue one query per
  item in every list.
- Exposing the full database schema through GraphQL, leaking internal structure
  and creating a tight coupling that blocks refactoring.
- Assuming the type system validates business rules — it does not.

## AI Review Checklist

- Does the change start from schema/type design rather than resolver plumbing?
- Have the relevant performance docs (N+1, DataLoader, pagination) been applied
  to any new list field?
- Are security limits (depth, complexity, rate) present on public endpoints?
- Are expected failures modeled per [Error Handling](20-error-handling.md)
  rather than thrown as generic errors?

## Related

- `knowledge/graphql/01-graphql-fundamentals.md`
- `knowledge/graphql/02-schema.md`
- `knowledge/graphql/04-queries.md`
- `knowledge/graphql/05-mutations.md`
- `knowledge/graphql/07-resolvers.md`
