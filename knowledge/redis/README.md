---
id: redis/readme
topic: redis
slug: readme
title: "Redis Engineering Standards"
type: index
order: -1
status: ready
tags: [redis, readme, SCAN, EXPIRE]
related: []
when_to_use: "Read first when starting any Redis work, to see how this section's docs fit together."
---
# Redis Engineering Standards

## Purpose

This section defines the engineering standards and best practices for using Redis — a
single-threaded, in-memory key/value store that also persists to disk — as a cache, session
store, message queue, rate limiter, and coordination layer. Redis is fast because it is
simple: one thread executes one command at a time, entirely in RAM. That model is also the
source of every common mistake.

The objective is to use Redis correctly under its constraints: choosing the right data type
for the access pattern, respecting the cost of every command, and avoiding the operational
traps — a single `KEYS *` that blocks the server, an unbounded collection that exhausts
memory, a cache with no persistence or invalidation strategy that serves stale data — that
only surface in production. From data types through application patterns, replication,
clustering, persistence, and security, these docs teach the discipline behind the commands.

These standards are written for both human engineers and AI coding assistants, so that
either can design, review, and operate Redis to the same bar.

---

## Scope

This documentation covers:

- Installation and the full data-type menu
- Strings, lists, sets, sorted sets, hashes, and streams
- Pub/Sub, transactions, Lua scripting, and expiration
- Caching, rate limiting, session storage, message queues, and distributed locks
- Replication, clustering, and persistence
- Security, monitoring, and performance
- Testing, debugging, and observability
- Best practices, production, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations
- [00. Overview](00-overview.md)
- [01. Installation](01-installation.md)
- [02. Data Types](02-data-types.md)

### Data Types In Depth
- [03. Strings](03-strings.md)
- [04. Lists](04-lists.md)
- [05. Sets](05-sets.md)
- [06. Sorted Sets](06-sorted-sets.md)
- [07. Hashes](07-hashes.md)
- [08. Streams](08-streams.md)

### Messaging & Coordination
- [09. Pub/Sub](09-pub-sub.md)
- [10. Transactions](10-transactions.md)
- [11. Lua Scripting](11-lua-scripting.md)
- [12. Expiration](12-expiration.md)

### Application Patterns
- [13. Caching](13-caching.md)
- [14. Rate Limiting](14-rate-limiting.md)
- [15. Session Storage](15-session-storage.md)
- [16. Message Queues](16-message-queues.md)
- [17. Distributed Locks](17-distributed-locks.md)

### Operations
- [18. Replication](18-replication.md)
- [19. Clustering](19-clustering.md)
- [20. Persistence](20-persistence.md)
- [21. Security](21-security.md)
- [22. Monitoring](22-monitoring.md)
- [23. Performance](23-performance.md)

### Engineering Discipline
- [24. Testing](24-testing.md)
- [25. Debugging](25-debugging.md)
- [26. Best Practices](26-best-practices.md)
- [27. Production](27-production.md)
- [28. Observability](28-observability.md)
- [29. Tooling](29-tooling.md)
- [30. Engineering Principles](30-engineering-principles.md)

### Verification
- [98. Production Checklist](98-production-checklist.md)
- [99. AI Review Checklist](99-ai-review-checklist.md)
- [100. Common Anti-Patterns](100-common-antipatterns.md)

---

## Engineering Principles

Every Redis change should satisfy the following principles:

- Know the time complexity of every command; `O(N)` commands over large keys stall all clients.
- Model the access pattern first, then pick the data type that makes it `O(1)`.
- Give every key a lifecycle — an `EXPIRE`, a cap, or an explicit delete; unbounded memory is an outage.
- Prefer `SCAN` over `KEYS`, and never run `O(N)` commands against production.
- Choose persistence (RDB vs AOF) and eviction policy explicitly per deployment.
- Treat Redis as a shared remote resource; batch with pipelines and avoid chatty per-item calls.
- Namespace keys with a consistent scheme so they are debuggable and safe to scan by prefix.
- Understand Redis's durability model before using it as a system of record.
- Use server-side scripts or transactions where multi-command atomicity is required.
- Match the persistence and durability requirement to config, and state it explicitly.

---

## Intended Audience

These standards are intended for:

- Backend Engineers
- Platform and DevOps Engineers
- Site Reliability Engineers
- Tech Leads
- Software Architects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps Redis fast and bounded — the right data type, a lifecycle
on every key, and a stated durability model — instead of an outage waiting to happen.
