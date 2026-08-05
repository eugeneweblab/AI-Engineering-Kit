---
id: cicd/readme
topic: cicd
slug: readme
title: "CI/CD Engineering Standards"
type: index
order: -1
status: ready
tags: [cicd, readme]
related: []
when_to_use: "Read first when starting any CI/CD work, to see how this section's docs fit together."
---
# CI/CD Engineering Standards

## Purpose

This section defines the engineering standards for CI/CD — the automated path that turns a
commit into a verified, deployable, and deployed artifact. CI proves a change is safe by
building and testing every commit; CD ships that proven change by packaging and rolling it
out with minimal human intervention. A correct pipeline does both, in that order, and never
lets an unproven change reach users.

The pipeline is the single gate every line of code passes through before production, so it
is infrastructure held to the same bar as the application it ships. The docs cover the
pipeline model, each verification stage, the delivery and deployment strategies, and the
cross-cutting concerns of secrets, environments, and platform tooling.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- CI/CD fundamentals and pipeline design
- Build, test, quality-gate, and security-scanning stages
- Artifacts and versioning
- Release management and deployment
- Blue-green, canary, feature flags, and rollbacks
- Secrets and environments
- Platform guides: GitHub Actions, GitLab CI, Bitbucket Pipelines, Jenkins
- Docker and Kubernetes integration
- Monitoring, notifications, debugging, and performance

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. Overview
- 01. CI/CD Fundamentals
- 02. Pipeline Design
- 30. Engineering Principles

## Verification Stages

- 03. Build Stage
- 04. Test Stage
- 05. Quality Gates
- 06. Security Scanning
- 07. Artifacts
- 08. Versioning

## Delivery & Deployment

- 09. Release Management
- 10. Deployment
- 11. Blue-Green Deployment
- 12. Canary Deployment
- 13. Feature Flags
- 14. Rollbacks

## Cross-Cutting Concerns

- 15. Secrets
- 16. Environments
- 21. Docker Integration
- 22. Kubernetes Integration

## Platforms & Tooling

- 17. GitHub Actions
- 18. GitLab CI
- 19. Bitbucket Pipelines
- 20. Jenkins
- 29. Tooling

## Operate

- 23. Monitoring
- 24. Notifications
- 25. Debugging
- 26. Performance
- 27. Best Practices
- 28. Production

## Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every pipeline change should satisfy the following principles:

- Build once and promote the identical artifact through every environment.
- Gate every merge behind an automated proof; no green pipeline, no merge.
- Fail fast and loud, ordering cheap checks before expensive ones.
- Treat pipelines as code: version-controlled, reviewed, and revertible.
- Keep runs deterministic — pin versions, isolate from the network, reproduce results.
- Keep the whole CI run fast enough (~10 minutes) that developers trust it.
- Run the pipeline on pull requests and on the protected branch after merge.
- Make jobs idempotent and independent so they retry and parallelize safely.
- Never retry flaky tests until green; a flaky test is a broken test.
- Automate deploy and rollback; no step should live only in someone's head.

---

## Intended Audience

These standards are intended for:

- DevOps and Platform Engineers
- SRE and Release Engineers
- Backend and Fullstack Engineers
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps the delivery pipeline fast, deterministic, and trustworthy,
so only proven changes reach production and every one of them can be recovered.
