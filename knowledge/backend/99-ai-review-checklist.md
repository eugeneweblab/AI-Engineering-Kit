---
id: backend/99-ai-review-checklist
topic: backend
slug: ai-review-checklist
title: "Backend AI Review Checklist"
type: doc
order: 99
status: ready
tags: [backend, ai-review-checklist]
related: [backend/30-engineering-principles, backend/12-error-handling, backend/23-testing, backend/29-architecture-review, backend/100-common-antipatterns]
when_to_use: "Read before reviewing or generating any backend code change, as the final pass."
---
# Backend AI Review Checklist

## Purpose

This is the checklist an AI agent runs when reviewing or self-reviewing backend code
before it merges. It is deliberately concrete: each item is a yes/no an agent can verify
by reading the diff, so a review produces findings, not vibes. Use it as the last gate
after the change is written and the topic-specific docs have been applied.

## Why It Matters

An agent generates plausible code fast, and plausible code hides the exact defects that
survive to production: the missing timeout, the swallowed error, the untested edge case,
the auth check that lives only in the caller. A structured checklist forces the review to
inspect the failure-prone surfaces every time instead of stopping at "it looks right and
the happy path passes."

## How to Use

- Go section by section; for each item, point to the line that satisfies it or flag the
  gap. "Not applicable" is a valid answer, but state why.
- Prioritize correctness and security findings — they block. Style findings do not.
- When an item fails, propose the concrete fix, not just the objection.

## Correctness

**Rules:** [Business Logic](07-business-logic.md) · [Validation](09-validation.md)

- [ ] Are all edge cases handled: empty input, nulls, zero, negative, boundary, max size?
- [ ] Are retryable writes idempotent, and multi-step writes wrapped in one transaction?
- [ ] Is untrusted input validated and normalized at the boundary before use?
- [ ] Are numeric money/quantity values integers or decimals, never floating point?
- [ ] Is concurrent access to shared state safe (no lost updates, no race on read-modify-write)?

## Error Handling

**Rules:** [Error Handling](12-error-handling.md)

- [ ] Is every error either handled where there is context or propagated with its cause intact?
- [ ] Are there zero `catch` blocks that log-and-swallow, hiding failure from the caller?
- [ ] Do errors returned to clients avoid leaking stack traces, SQL, or internal detail?
- [ ] Are external calls guarded by timeouts and bounded retries with backoff?

## Security

**Rules:** [Security](21-security.md) · [Authorization](11-authorization.md)

- [ ] Is authorization enforced on the endpoint/handler itself, not only in the UI or caller?
- [ ] Are queries parameterized (no string-built SQL) and inputs escaped for their sink?
- [ ] Are secrets absent from source, logs, and error messages?
- [ ] Does the change avoid logging PII or credentials? See [security](21-security.md).

## Design and Maintainability

**Rules:** [Code Organization](25-code-organization.md) · [Clean Architecture](03-clean-architecture.md)

- [ ] Is decision logic separated from I/O so it can be tested without mocks?
- [ ] Are dependencies passed explicitly rather than pulled from globals/singletons?
- [ ] Is any new abstraction justified by real, repeated use rather than speculation?
- [ ] Are names intent-revealing, and is there no dead or commented-out code?

## Testing

**Rules:** [Testing](23-testing.md)

- [ ] Do tests cover the failure and edge paths, not just the happy path?
- [ ] Are tests deterministic (no reliance on wall-clock, network, or ordering)?
- [ ] Does the diff include a regression test for the specific bug it fixes?

## Observability

**Rules:** [Observability](22-observability.md)

- [ ] Do new failure branches emit a structured log with a correlation id and a metric?
- [ ] Are logs free of secrets and PII, and at an appropriate level? See [observability](22-observability.md).

## Performance

**Rules:** [Performance](19-performance.md)

- [ ] Are there no N+1 queries or unbounded loads on hot paths?
- [ ] Are list endpoints paginated and expensive queries indexed or cached?

## AI Review Checklist

- Have you cited a line for each satisfied item and flagged every gap with a fix?
- Did you check the failure paths, not just confirm the happy path compiles?
- Are correctness and security findings surfaced as blocking, above style?
- Did you cross-check against [common antipatterns](100-common-antipatterns.md)?

## Related

- `knowledge/backend/30-engineering-principles.md`
- `knowledge/backend/12-error-handling.md`
- `knowledge/backend/23-testing.md`
- `knowledge/backend/29-architecture-review.md`
- `knowledge/backend/100-common-antipatterns.md`
