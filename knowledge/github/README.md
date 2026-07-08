---
id: github/readme
topic: github
slug: readme
title: "GitHub Engineering Standards"
type: index
order: -1
status: ready
tags: [github]
related: []
when_to_use: "Read first when starting any github work, to see how this section's docs fit together."
---
# GitHub Engineering Standards

## Purpose

This section defines the engineering standards and platform practices for using GitHub
as the collaboration, automation, and supply-chain hub for software delivery. It goes
beyond hosting repositories to cover how teams plan work, review code, ship releases,
and enforce security and governance at scale.

The objective is a consistent, auditable delivery workflow: issues and projects that
track real work, pull requests and reviews that raise code quality, Actions and workflows
that automate testing and deployment, and security features (CodeQL, Dependabot, secret
scanning, branch protection, rulesets) that keep the software supply chain trustworthy.
It also covers organizational concerns — teams, permissions, enterprise settings — and
programmatic access via the API, CLI, and Codespaces.

These standards apply to both human developers and AI coding assistants, so automated
contributions follow the same review gates, protection rules, and security policies as
human ones.

---

## Scope

This documentation covers:

- The GitHub platform and repository management
- Issues, Projects, and Discussions
- Pull requests and code review
- Actions, workflows, and Packages
- Releases and Pages
- Security: CodeQL, Dependabot, secret scanning
- Branch protection and rulesets
- Organizations, teams, and permissions
- API, CLI, Codespaces, and Copilot
- Automation, enterprise, and integrations
- Engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations

- 00. Overview
- 01. GitHub Platform
- 02. Repositories

### Planning & Collaboration

- 03. Issues
- 04. Projects
- 05. Discussions
- 06. Pull Requests
- 07. Code Review

### Automation & Delivery

- 08. Actions
- 09. Workflows
- 10. Packages
- 11. Releases
- 12. Pages

### Security & Governance

- 13. Security
- 14. CodeQL
- 15. Dependabot
- 16. Secret Scanning
- 17. Branch Protection
- 18. Rulesets

### Organization & Access

- 19. Organizations
- 20. Teams
- 21. Permissions
- 22. API
- 23. CLI
- 24. Codespaces
- 25. Copilot

### Scale & Practice

- 26. Automation
- 27. Best Practices
- 28. Enterprise
- 29. Integrations
- 30. Engineering Principles

### Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every GitHub workflow should satisfy the following principles:

- Make the default branch protected; require reviews and passing checks before merge.
- Treat pull requests as the unit of change — small, reviewable, and CI-gated.
- Automate everything repeatable with Actions; keep workflows least-privileged.
- Pin and scope tokens and Action versions; never grant more permission than needed.
- Enable Dependabot, CodeQL, and secret scanning by default and act on their findings.
- Encode governance as rulesets and org policy, not tribal knowledge.
- Model access through teams and roles, not individual grants.
- Keep issues and projects as the single source of truth for planned work.
- Treat releases as immutable, versioned, and traceable to their commits.
- Prefer the CLI and API for reproducible operations over ad-hoc UI clicks.

---

## Intended Audience

These standards are intended for:

- Software Engineers
- Tech Leads
- DevOps and Platform Engineers
- Security Engineers
- Engineering Managers
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards makes GitHub a reliable delivery platform — where collaboration,
automation, and security reinforce each other instead of competing for attention.
