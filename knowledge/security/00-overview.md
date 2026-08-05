---
id: security/00-overview
topic: security
slug: overview
title: "Security Overview"
type: doc
order: 0
status: ready
tags: [security, overview]
related: [security/01-security-fundamentals, security/02-threat-modeling, security/03-authentication, security/28-owasp-top10, security/99-ai-review-checklist]
when_to_use: "Read first to orient yourself in the security topic and find the right doc for a task."
---
# Security Overview

## Purpose

This document is the map for the `security` topic. It explains what these docs
cover, how they relate, and where to go for a specific task. Security is not one
feature you add at the end — it is a property of every layer of the system. These
docs teach an agent to build and review code so that property holds.

Read this page to locate the right document. Read that document before you write or
review the code it governs.

## Why It Matters

Security defects are different from ordinary bugs. A functional bug annoys one user;
a security bug hands the system to an attacker while the app keeps working perfectly.
The failure is silent, the blast radius is often total, and the fix after a breach is
far more expensive than the discipline before one. Because of this asymmetry, security
code is held to a higher bar: assume every input is hostile, fail closed, and never
trust the client.

## How These Docs Fit Together

The topic moves from principles to specific defenses to operations.

- **Foundations** — start here to build the right mental model.
  - [Security Fundamentals](01-security-fundamentals.md): the core principles
    (least privilege, defense in depth, fail closed) that every other doc applies.
  - [Threat Modeling](02-threat-modeling.md): how to decide *what* to defend before
    you write a line of code.

- **Identity** — proving who a user is and what they may do.
  - [Authentication](03-authentication.md): verifying identity (login, sessions, MFA).
  - [Authorization](04-authorization.md): enforcing permissions once identity is known.
  - [Password Security](05-password-security.md), [Session Management](06-session-management.md),
    [JWT](07-jwt.md), [OAuth](08-oauth.md): the mechanisms behind identity.

- **Handling untrusted data** — the source of most injection classes.
  - [Input Validation](09-input-validation.md), [Output Encoding](10-output-encoding.md),
    [XSS](11-xss.md), [CSRF](12-csrf.md), [SQL Injection](13-sql-injection.md),
    [Command Injection](14-command-injection.md), [File Upload Security](15-file-upload-security.md).

- **Secrets and transport** — protecting data at rest and in motion.
  - [Secrets Management](16-secrets-management.md), [Encryption](17-encryption.md),
    [HTTPS](18-https.md), [CORS](19-cors.md), [CSP](20-csp.md),
    [Security Headers](22-security-headers.md).

- **Platform and supply chain** — the risks outside your own code.
  - [Rate Limiting](21-rate-limiting.md), [Dependency Security](23-dependency-security.md),
    [Supply Chain Security](24-supply-chain-security.md).

- **Operations** — assume something will go wrong.
  - [Monitoring](25-monitoring.md), [Incident Response](26-incident-response.md).

- **Reference and gates** — use these to check work.
  - [Best Practices](27-best-practices.md), [OWASP Top 10](28-owasp-top10.md),
    [Security Review](29-security-review.md), [Engineering Principles](30-engineering-principles.md),
    [Production Checklist](98-production-checklist.md), [AI Review Checklist](99-ai-review-checklist.md),
    [Common Anti-patterns](100-common-antipatterns.md).

## How to Use This Topic

- **Writing a new feature?** Start with [Threat Modeling](02-threat-modeling.md) to
  identify the attack surface, then pull the specific defense docs it points to.
- **Reviewing a pull request?** Run the [AI Review Checklist](99-ai-review-checklist.md)
  and the relevant per-topic checklist at the bottom of each doc.
- **Shipping to production?** Gate the release on the [Production Checklist](98-production-checklist.md).
- **Unsure a pattern is safe?** Search [Common Anti-patterns](100-common-antipatterns.md)
  for it before you commit.

## Core Principles

- **Security is layered, not localized.** No single doc makes a system secure; the
  guarantees compose. A perfect login is worthless behind a missing authorization check.
- **Prefer standards over invention.** Every doc points to vetted libraries and protocols.
  Custom crypto and bespoke auth fail in ways you cannot see.
- **Verifiable rules over theory.** Each doc ends with a checklist an agent can apply
  mechanically. When in doubt, the checklist is the contract.

## AI Review Checklist

- Did you identify which doc(s) in this topic govern the code under review?
- Does the change touch identity, untrusted input, secrets, or transport — and did you
  read the matching doc before editing?
- Did you run the relevant per-doc AI Review Checklist, not just skim the prose?
- Are security guarantees preserved across layers, not just in the file you changed?

## Related


- `knowledge/security/01-security-fundamentals.md`
- `knowledge/security/02-threat-modeling.md`
- `knowledge/security/03-authentication.md`
- `knowledge/security/28-owasp-top10.md`
- `knowledge/security/99-ai-review-checklist.md`
