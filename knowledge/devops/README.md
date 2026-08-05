---
id: devops/readme
topic: devops
slug: readme
title: "DevOps Engineering Standards"
type: index
order: -1
status: ready
tags: [devops, readme]
related: []
when_to_use: "Read first when starting any devops work, to see how this section's docs fit together."
---
# DevOps Engineering Standards

## Purpose

This section defines the engineering standards for shortening the distance between a code
change and that change running safely in production — and keeping it running. It teaches how
work flows from a branch, through a pipeline, into an environment, and how you detect and
recover when something breaks.

Most production incidents are not caused by exotic bugs; they are caused by process — an
untested change merged straight to `main`, a manual deploy step someone forgot, a secret
committed to Git, a rollback that was never tested. DevOps turns those fragile human rituals
into automated, repeatable, observable systems. The docs follow the lifecycle of a change,
from culture and source control, through build and deployment, into infrastructure and
operations.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- DevOps culture and the development lifecycle
- Git workflow and branching strategies
- Build pipelines, release management, and deployment strategies
- Infrastructure as code and configuration management
- Containerization and orchestration
- Monitoring, observability, logging, and alerting
- Security, secrets management, disaster recovery, and high availability
- Scalability, performance, and testing
- Change and incident management, postmortems, and SRE principles

---

## Learning Path

Study the documents in the following order.

## Culture & Process

- 00. Overview
- 01. DevOps Culture
- 02. Development Lifecycle
- 30. Engineering Principles

## Source Control

- 03. Git Workflow
- 04. Branching Strategies

## Build & Ship

- 05. Build Pipelines
- 06. Release Management
- 07. Deployment Strategies

## Infrastructure

- 08. Infrastructure as Code
- 09. Configuration Management
- 10. Containerization
- 11. Orchestration

## Operate

- 12. Monitoring
- 13. Observability
- 14. Logging
- 15. Alerting
- 25. Incident Management
- 26. Postmortems
- 27. SRE Principles

## Resilience & Quality

- 16. Security
- 17. Secrets Management
- 18. Disaster Recovery
- 19. High Availability
- 20. Scalability
- 21. Performance
- 22. Testing
- 23. Quality Gates
- 24. Change Management
- 28. Best Practices
- 29. Tooling

## Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every DevOps change should satisfy the following principles:

- Automate the path to production; every manual step is one that will eventually be skipped.
- Make changes small and reversible, and build reversibility as a feature.
- Version everything — code, infrastructure, configuration, and pipelines — in Git.
- Push detection left: fast, loud feedback in a linter, a test, or a canary.
- Enforce quality gates in the pipeline, not by convention.
- Treat DevOps as a practice of ownership and automation, not a specific tool.
- Automate deploys and rollbacks together; never leave rollback untested.
- Instrument for observability so failures are detected and diagnosed quickly.
- Learn from incidents with blameless postmortems, not blame.

---

## Intended Audience

These standards are intended for:

- DevOps and Platform Engineers
- SRE Engineers
- Backend and Fullstack Engineers
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards turns delivery into an automated, observable, recoverable system,
so changes reach production safely and stay running.
