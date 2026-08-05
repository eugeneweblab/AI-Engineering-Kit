---
id: security/readme
topic: security
slug: readme
title: "Security Engineering Standards"
type: index
order: -1
status: ready
tags: [security]
related: []
when_to_use: "Read first when starting security work, to see how this section's docs fit together and which one covers your problem."
---
# Security Engineering Standards

## Purpose

This section defines the engineering standards for building applications that resist attack:
how identity is established, how input is handled, how secrets are stored, and how a system
behaves when something goes wrong.

Security defects differ from other defects in one respect that shapes everything here: they
do not surface as failures. A missing authorization check, an unescaped output, or a
hardcoded credential works perfectly in every test and every demo. It fails only when someone
looks for it — which is why security has to be verified deliberately rather than observed.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Fundamentals and threat modeling
- Identity: authentication, authorization, sessions, JWT, OAuth, passwords
- Input and output: validation, encoding, XSS, CSRF, injection
- Data protection: encryption, secrets management, HTTPS
- Browser controls: CORS, CSP, security headers
- Supply chain and dependency security
- Rate limiting, monitoring, and incident response
- The OWASP Top 10 and review practice

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. [Overview](00-overview.md)
- 01. [Security Fundamentals](01-security-fundamentals.md)
- 02. [Threat Modeling](02-threat-modeling.md)
- 30. [Engineering Principles](30-engineering-principles.md)

## Identity and Access

- 03. [Authentication](03-authentication.md)
- 04. [Authorization](04-authorization.md)
- 05. [Password Security](05-password-security.md)
- 06. [Session Management](06-session-management.md)
- 07. [JWT](07-jwt.md)
- 08. [OAuth](08-oauth.md)

## Handling Untrusted Data

- 09. [Input Validation](09-input-validation.md)
- 10. [Output Encoding](10-output-encoding.md)
- 11. [XSS](11-xss.md)
- 12. [CSRF](12-csrf.md)
- 13. [SQL Injection](13-sql-injection.md)
- 14. [Command Injection](14-command-injection.md)
- 15. [File Upload Security](15-file-upload-security.md)

## Protecting Data

- 16. [Secrets Management](16-secrets-management.md)
- 17. [Encryption](17-encryption.md)
- 18. [HTTPS](18-https.md)

## Browser and Transport Controls

- 19. [CORS](19-cors.md)
- 20. [CSP](20-csp.md)
- 21. [Rate Limiting](21-rate-limiting.md)
- 22. [Security Headers](22-security-headers.md)

## Supply Chain and Operations

- 23. [Dependency Security](23-dependency-security.md)
- 24. [Supply Chain Security](24-supply-chain-security.md)
- 25. [Monitoring](25-monitoring.md)
- 26. [Incident Response](26-incident-response.md)

## Applied Guidance

- 27. [Best Practices](27-best-practices.md)
- 28. [OWASP Top 10](28-owasp-top10.md)
- 29. [Security Review](29-security-review.md)

## Verification

- 98. [Production Checklist](98-production-checklist.md)
- 99. [AI Review Checklist](99-ai-review-checklist.md)
- 100. [Common Antipatterns](100-common-antipatterns.md)

---

## Engineering Principles

Every change should satisfy the following principles:

- Never trust input, regardless of where it came from — including your own database and
  internal services.
- Validate on the way in against an allow-list; encode on the way out for the exact context.
- Authenticate, then authorize on the specific object; a valid session is not permission.
- Fail closed. When a check cannot be completed, deny.
- Keep secrets out of source control, logs, error messages, and responses.
- Use the platform's audited primitives for crypto, hashing, and tokens; never write your own.
- Grant the least privilege that works, to every user, service, and process.
- Assume a breach: log enough to reconstruct events, and be able to rotate every credential.
- Treat dependencies as code you are responsible for.
- Make security verifiable — a check nobody can test is a check nobody can trust.

---

## Intended Audience

These standards are intended for:

- Backend and Frontend Engineers
- Security Engineers and Reviewers
- DevOps and Platform Engineers
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Security defects are silent by nature, so they must be prevented by discipline and caught by
deliberate review. Validate and encode at the boundaries, authorize every action on its
object, protect secrets, and design so that failure denies rather than allows.
