---
id: backend/24-documentation
topic: backend
slug: documentation
title: "Documentation"
type: doc
order: 24
status: ready
tags: [backend, documentation]
related: [backend/06-api-design, backend/25-code-organization, backend/22-observability, backend/28-best-practices]
when_to_use: "Read before shipping an API, writing a README, or documenting a service others will run or call."
---
# Documentation

## Purpose

This document defines what backend documentation must exist, where it lives, and how to
keep it correct. It covers the machine-readable contract (OpenAPI, schemas), the
human-readable operational docs (README, runbooks, ADRs), and the in-code documentation
that explains intent. The goal: an engineer or agent who has never seen the service can
run it, call it, and change it safely without reading every line.

Documentation is not prose *about* the code; it is part of the contract the code must
honor. Treat drift between docs and behavior as a bug.

## Why It Matters

Backend services outlive the people who wrote them. Undocumented behavior forces every
future change to be reverse-engineered from source, and reverse-engineering guesses
wrong — it captures what the code does, not what it is *supposed* to do. Missing
operational docs turn a 3 a.m. incident into an archaeology dig. Stale API docs are
worse than none: callers trust them, integrate against them, and break in production.
Good documentation is what lets a system be changed with confidence instead of fear.

## Core Principles

- **Document intent, not mechanics.** Code already shows *what* it does; docs must
  capture *why* and the constraints that are not visible in a single function.
- **Keep docs next to the thing they describe.** API contract in the repo, runbook in
  the service, ADRs in version control. Distance from the code guarantees drift.
- **Generate the contract; do not hand-write it.** Derive OpenAPI/JSON Schema from code
  or types so it cannot lie about the running behavior.
- **Every doc has an owner and an expiry test.** If nothing fails when a doc goes stale,
  it will go stale. Tie contracts to tests and CI.
- **Write for the reader who is paged, not the author who is fresh.** Optimize for the
  stranger under pressure, not the expert with full context.

## Best Practices

- Expose an **OpenAPI 3.1** (or GraphQL SDL) contract, generated from code, and validate
  requests/responses against it in CI so drift fails the build.
- Give every service a README that answers five questions: what it does, how to run it
  locally, how to run its tests, what it depends on, and who owns it.
- Write **runbooks** for on-call: how to deploy, roll back, read the dashboards, and
  respond to each named alert. Link them from the alert itself.
- Record significant decisions as **ADRs** (Architecture Decision Records): context,
  decision, alternatives, consequences. One short file per decision, never edited —
  superseded instead.
- Use doc comments on public functions to state contracts (preconditions, error modes,
  units), not to restate the signature.
- Document error responses and status codes as rigorously as success responses; callers
  code against failures too.
- Keep a `CHANGELOG` for anything with external consumers, and version breaking changes.

## Examples

**Good Example** — a doc comment that captures the contract

```python
def charge_card(customer_id: str, amount_cents: int) -> ChargeResult:
    """Charge a customer's default card.

    amount_cents must be > 0; the caller is responsible for currency conversion.
    Idempotent per (customer_id, amount_cents, day): a repeat within 24h returns
    the original charge instead of double-charging.
    Raises CardDeclined on issuer rejection; raises no exception on network retry.
    """
    # The "why" (idempotency window, who owns currency) is invisible in the code,
    # so it lives here where the next caller will actually read it.
```

**Bad Example** — a comment that restates the obvious and hides nothing useful

```python
def charge_card(customer_id: str, amount_cents: int) -> ChargeResult:
    # This function charges the card.        <- restates the name, adds nothing
    # customer_id: the customer id           <- restates the type
    # amount_cents: the amount               <- no units, no bounds, no rules
    return processor.charge(customer_id, amount_cents)
    # Idempotency? Declines? Currency? The reader must guess or read the processor.
```

## Common Mistakes

- Hand-writing OpenAPI YAML separately from the code, so it silently diverges from
  reality.
- README that lists features but never says how to run the service locally.
- Comments that narrate the code (`i++ // increment i`) instead of explaining intent.
- Runbooks that exist but are not linked from the alerts that need them, so no one finds
  them at 3 a.m.
- Documenting only the happy path and leaving error codes, rate limits, and pagination
  undefined.
- Editing an ADR in place, erasing the history of why a superseded decision was made.
- Treating docs as a one-time launch task rather than something CI enforces on change.

## Production Tips

- Fail CI when the generated API contract differs from the committed one; this makes docs
  self-updating and prevents silent drift.
- Publish the OpenAPI spec at a stable URL and let consumers generate their own clients.
- Add a "last verified" date to runbooks and review them after every incident that used
  them.

## AI Review Checklist

- Is there a generated, CI-validated API contract (OpenAPI/SDL), not a hand-written one?
- Does the README explain how to run, test, and deploy the service, and who owns it?
- Are error responses, status codes, and pagination documented, not just success cases?
- Do doc comments state contracts (bounds, units, error modes), not restate signatures?
- Do named alerts link to a runbook with rollback steps?
- Are architectural decisions captured as immutable, versioned ADRs?

## Related

- `knowledge/backend/06-api-design.md`
- `knowledge/backend/25-code-organization.md`
- `knowledge/backend/22-observability.md`
- `knowledge/backend/28-best-practices.md`
