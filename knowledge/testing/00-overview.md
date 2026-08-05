---
id: testing/00-overview
topic: testing
slug: overview
title: "Testing Overview"
type: doc
order: 0
status: ready
tags: [testing, overview]
related: [testing/01-testing-fundamentals, testing/02-unit-testing, testing/03-integration-testing, testing/04-e2e-testing, testing/28-testing-strategy]
when_to_use: "Read first when you need to know which testing doc answers your question."
---
# Testing Overview

## Purpose

This topic teaches an agent how to write tests that catch real defects and stay
trustworthy over time. It is a map: it tells you *which* document to open for a given
task and how the pieces fit, not the details themselves. Read this first, then jump to
the specific doc.

Tests exist to answer one question cheaply and repeatedly: *does the code still do what
it is supposed to do?* Every guideline in this topic serves that goal. A test that does
not increase your confidence in that answer is waste — or worse, a liability.

## Why It Matters

Untested code is a guess about behavior; tested code is a claim you can verify. But tests
are not free — they are code you must read, run, and maintain. A bad test suite is worse
than none: it is slow, flaky, and lies about what it covers, so the team learns to ignore
red builds. The difference between a suite that accelerates a team and one that drags it
down is discipline about *what* to test, at *what* level, and *how* to keep it honest.
This topic encodes that discipline so an agent applies it by default.

## Core Principles

- **Test behavior, not implementation.** A test should survive a refactor that keeps
  behavior the same. Coupling tests to internals makes every change break the suite.
- **Pick the cheapest level that gives real confidence.** A bug catchable by a unit test
  should not require a browser. See the [testing pyramid](01-testing-fundamentals.md).
- **A test must be able to fail.** A test that passes no matter what the code does is
  worse than no test — it is false assurance.
- **Determinism is non-negotiable.** The same code and inputs must produce the same
  result every run. Non-determinism is a bug in the test, not bad luck.

## The Documents

- **[01 Testing Fundamentals](01-testing-fundamentals.md)** — the mental model: the
  pyramid, Arrange-Act-Assert, what makes a test good, when to test at all. Start here.
- **[02 Unit Testing](02-unit-testing.md)** — testing a single unit in isolation: fast,
  deterministic, the base of the pyramid.
- **[03 Integration Testing](03-integration-testing.md)** — testing how units collaborate
  across real boundaries (database, HTTP, queues).
- **[04 E2E Testing](04-e2e-testing.md)** — driving the whole system through its real
  entry point (a browser or public API) to verify critical user journeys.
- **[05 Test Doubles](05-test-doubles.md)** — stubs, mocks, fakes, and spies: how to
  replace a collaborator without lying about its contract.

Supporting docs extend these: [test data](07-test-data.md),
[fixtures](10-fixtures.md), [assertions](09-assertions.md),
[test organization](08-test-organization.md), [flaky tests](22-flaky-tests.md), and the
overall [testing strategy](28-testing-strategy.md).

## How To Use This Topic

1. Deciding *what kind* of test to write? Read **01 Fundamentals** and **28 Strategy**.
2. Writing a test for one function or class? Read **02 Unit Testing**.
3. Crossing a real boundary (DB, HTTP)? Read **03 Integration Testing**.
4. Verifying a whole user flow? Read **04 E2E Testing**.
5. Need to replace a dependency? Read **05 Test Doubles** *before* reaching for a mock.

## AI Review Checklist

- Is each test written at the cheapest level that gives real confidence?
- Does every test assert behavior a user or caller cares about, not internals?
- Can each test actually fail if the code under test breaks?
- Is the suite deterministic — no reliance on time, order, network, or randomness?
- Are test doubles used deliberately, not by reflex, and do they honor the real contract?

## Related

- `knowledge/testing/01-testing-fundamentals.md`
- `knowledge/testing/02-unit-testing.md`
- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/28-testing-strategy.md`
