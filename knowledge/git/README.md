---
id: git/readme
topic: git
slug: readme
title: "Git Engineering Standards"
type: index
order: -1
status: ready
tags: [git, readme, rebase, revert, reset]
related: []
when_to_use: "Read first when starting any git work, to see how this section's docs fit together."
---
# Git Engineering Standards

## Purpose

This section defines the engineering standards, mental models, and day-to-day
practices for using Git as a version control system. It treats Git not as a set of
commands to memorize, but as a content-addressable object model whose behavior becomes
predictable once commits, trees, refs, and the reflog are understood.

The objective is a consistent, low-risk workflow: clean commit history, safe branching
and integration, deliberate history rewriting, and reliable recovery when something goes
wrong. It covers both the local mechanics (commits, branches, rebase, reset, revert,
stash) and the collaborative surface (remotes, fetch/pull/push, conflict resolution,
hooks, submodules) that teams depend on every day.

These standards apply to both human developers and AI coding assistants, so that
automated changes follow the same commit hygiene, branching model, and safety rules as
hand-authored ones.

---

## Scope

This documentation covers:

- The Git object model and version control fundamentals
- Installation and repository setup
- Commits, branches, and merging
- History rewriting: rebase, cherry-pick, reset, revert
- Stash, tags, and the reflog
- Remotes: fetch, pull, push, and conflict resolution
- Hooks, submodules, and Git LFS
- Branching strategies: Git Flow, trunk-based, monorepos
- Debugging with Git, security, and tooling
- Engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations

- 00. Overview
- 01. Version Control
- 02. Installation
- 03. Repository

### Core Local Workflow

- 04. Commits
- 05. Branches
- 06. Merging
- 07. Rebasing
- 08. Cherry-Pick
- 09. Reset
- 10. Revert
- 11. Stash
- 12. Tags

### Collaboration & Remotes

- 13. Remote Repositories
- 14. Fetch
- 15. Pull
- 16. Push
- 17. Conflict Resolution
- 18. History
- 19. Reflog
- 20. Hooks
- 21. Submodules

### Workflows & Scale

- 22. Git Flow
- 23. Trunk-Based Development
- 24. Monorepo
- 25. LFS

### Practice & Hardening

- 26. Debugging
- 27. Best Practices
- 28. Security
- 29. Tooling
- 30. Engineering Principles

### Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every Git operation should satisfy the following principles:

- Treat history as a communication tool: small, atomic, well-described commits.
- Never rewrite history that others have already pulled from a shared branch.
- Prefer `revert` for shared history; reserve `reset` and `rebase` for local, private work.
- Keep branches short-lived and integrate frequently to reduce conflict surface.
- Resolve conflicts deliberately; understand both sides before choosing a resolution.
- Use the reflog as a safety net — almost nothing is lost until it is garbage-collected.
- Automate policy with hooks, but keep hooks fast and non-blocking where possible.
- Never commit secrets; scan history and rotate credentials if one slips in.
- Choose a branching model (Git Flow, trunk-based, monorepo) intentionally and apply it consistently.
- Keep the working tree and index in a known state before switching context.

---

## Intended Audience

These standards are intended for:

- Software Engineers
- Tech Leads
- DevOps and Platform Engineers
- Release Managers
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps Git history clean, collaboration predictable, and
recovery straightforward — so version control accelerates a team instead of surprising it.
