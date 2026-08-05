---
id: examples/readme
topic: examples
slug: readme
title: "Examples"
type: index
order: -1
status: ready
tags: [examples]
related: []
when_to_use: "Read first to find a relevant worked example in this collection."
---
# Examples

## Purpose

Complete worked implementations, end to end. Where [snippets](../snippets/README.md) show a
fragment and the topic docs explain a concept, these show how the pieces fit together for
one realistic feature — including the states, the tests, and the parts usually left out of
a tutorial.

Each example implements the same domain — an events feature — so the layers can be read
together.

---

## What's Here

| Example | Covers |
|---|---|
| [01. REST Endpoint](01-rest-endpoint.md) | Contract, validation, service, error handling, tests |
| [02. React Component](02-react-component.md) | Props contract, every state, accessibility, tests |
| [03. WordPress Feature](03-wordpress-feature.md) | Post type, meta, admin, front end, security |

---

## How to Read an Example

- **Read the whole file before copying part of it.** The pieces depend on each other — the
  validation exists because of what the service assumes.
- **The comments carry the reasoning.** They explain why a line is the way it is, which is
  what makes an example worth more than a code dump.
- **Adapt, do not transplant.** These follow common conventions, not your project's. Match
  the surrounding code.
- **Note what is omitted.** Each example says what a real implementation would add —
  pagination, rate limiting, observability — so the gaps are deliberate rather than assumed
  complete.

---

## Related Topics

- [Snippets](../snippets/README.md) — fragments rather than complete features.
- [Workflows](../workflows/README.md) — the process that produces work like this.
- [REST API](../rest-api/00-overview.md) · [React](../react/00-overview.md) · [WordPress](../wordpress/00-overview.md)

---

## Summary

Three complete implementations of one feature across different layers, with the reasoning in
the comments and the omissions stated explicitly.
