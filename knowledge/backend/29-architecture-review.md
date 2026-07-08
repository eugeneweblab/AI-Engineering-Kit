---
id: backend/29-architecture-review
topic: backend
slug: architecture-review
title: "Architecture Review"
type: doc
order: 29
status: ready
tags: [backend, architecture-review]
related: [backend/01-backend-architecture, backend/03-clean-architecture, backend/25-code-organization, backend/28-best-practices, backend/99-ai-review-checklist]
when_to_use: "Read before reviewing a design doc, a new service proposal, or a large PR that changes system structure."
---
# Architecture Review

## Purpose

This document defines how to review a backend design or a structurally significant change:
what to look for, what questions to force, and how to judge whether a proposed architecture
will survive contact with production. It applies to design docs, new-service proposals, and
PRs that move boundaries — not to routine bug fixes. The goal is to catch expensive mistakes
while they are still cheap: on a page, before they are cast into code and data.

## Why It Matters

Architecture decisions are the ones you cannot easily undo. A wrong function is a five-minute
fix; a wrong service boundary, a leaked domain into the database schema, or a synchronous call
that should have been an event can take quarters to unwind and often never gets unwound. Reviews
are the last cheap moment. A review that only checks style and misses the boundary error has
failed at the one thing that mattered. The reviewer's job is to find the irreversible mistake
before it is made.

## Core Principles

- **Review boundaries first, details last.** Where are the seams between modules/services, and
  who depends on whom? A wrong boundary invalidates every detail inside it.
- **Follow the dependencies.** Confirm they point inward (domain depends on nothing external)
  and never form a cycle. Dependency direction is the spine of the architecture.
- **Judge against requirements, not taste.** Every added abstraction, service, or queue must
  earn its place by solving a real, stated requirement. Complexity is a cost, not a virtue.
- **Probe the failure modes, not the happy path.** Ask what happens when each dependency is
  down, slow, or returns garbage. Designs that only describe success are incomplete.
- **Insist on reversibility.** Prefer decisions that can be changed later. Where a decision is
  one-way (data model, public API, service split), demand the highest scrutiny.

## Best Practices

- Start from the requirements and constraints (load, latency, consistency, team size); reject
  or right-size any design that does not trace to them.
- Check that the **domain core is independent** of frameworks, databases, and transport, so it
  stays testable and portable. (See [clean architecture](03-clean-architecture.md).)
- Verify **dependency direction and acyclicity** across modules; a cycle is a boundary error,
  not a nuisance.
- Scrutinize **consistency and transaction boundaries**: what is atomic, what is eventually
  consistent, and is that acceptable for the business rule?
- Interrogate **every synchronous cross-service call**: could it be an event? What is its
  timeout, retry, and fallback? (See [production](27-production.md).)
- Confirm **data-migration and rollout** plans for schema changes are backward-compatible and
  reversible. (See [deployment](26-deployment.md).)
- Demand an **ADR** for each significant, hard-to-reverse decision, with the alternatives that
  were rejected and why.
- Prefer boring, proven technology; a new datastore or paradigm must justify its operational
  cost.

## Examples

**Good Example** — a review comment that targets a boundary and a failure mode

```md
Review: "Checkout" design doc

- Boundary: `orders` writes directly to the `payments` table. This couples two
  bounded contexts through the schema — a change to payments' storage breaks orders.
  Suggest orders call the payments *service* (or emit an event) so the boundary is
  an API, not a shared table.  [why: schema coupling is irreversible and blocks
  independent change]
- Failure mode: the doc shows the happy path only. What happens when the payment
  provider times out mid-checkout? Define the timeout, whether the order is created
  pending, and how a stuck order is reconciled.  [why: this is the case that pages]
- Consistency: order + inventory decrement are described as one step but span two
  services. Is this atomic? If eventually consistent, what reconciles a failed
  decrement?  [decision needs an ADR — it is hard to reverse]
```

**Bad Example** — a review that only sees the surface

```md
Review: "Checkout" design doc

- LGTM overall.
- Nit: rename `doCheckout` to `checkout`.
- Add a comment on the loop.
# Approves a design that couples two contexts through a shared table and never
# defines what happens when payment fails — the two things that will actually hurt.
```

## Common Mistakes

- Reviewing naming and formatting while the module boundaries are wrong.
- Approving a synchronous chain of service calls with no timeout, retry, or fallback story.
- Missing a shared-database coupling between two services or contexts.
- Not asking about the failure paths, so the design only works when everything is up.
- Accepting new abstractions or services that no stated requirement justifies.
- Letting an irreversible decision (data model, public API, split) ship without an ADR.
- Confusing "this is how I would build it" with "this will not work" — reviewing taste, not risk.

## Production Tips

- Timebox the review to the risky parts; spend the attention on boundaries and failure modes,
  not on line-by-line reading.
- Write the concern as a question ("what happens when X is down?") — it forces the author to
  design the answer rather than defend a choice.

## AI Review Checklist

- Does every proposed boundary trace to a real requirement, and is it in the right place?
- Do dependencies point inward and form no cycles?
- Is the domain core independent of frameworks, ORM, and transport?
- Are transaction and consistency boundaries explicit and appropriate for each rule?
- Does every cross-service call define its timeout, retry, and fallback?
- Are schema/rollout changes backward-compatible and reversible?
- Is each hard-to-reverse decision recorded in an ADR with rejected alternatives?

## Related

- `knowledge/backend/01-backend-architecture.md`
- `knowledge/backend/03-clean-architecture.md`
- `knowledge/backend/25-code-organization.md`
- `knowledge/backend/28-best-practices.md`
- `knowledge/backend/99-ai-review-checklist.md`
