---
id: linux/readme
topic: linux
slug: readme
title: "Linux Engineering Standards"
type: index
order: -1
status: ready
tags: [linux, readme, sudo]
related: []
when_to_use: "Read first when starting any linux work, to see how this section's docs fit together."
---
# Linux Engineering Standards

## Purpose

This section defines the engineering standards and operational practices for working with
Linux as the platform that runs most production software. Effective Linux work rests on a
few durable models: everything is a file, processes and permissions govern access, and
the init system (systemd) supervises the services that keep a host doing useful work.

The objective is a consistent, safe approach to administering and operating Linux hosts:
navigating the filesystem and shell, managing users, groups, and permissions, running and
supervising processes and services, and configuring networking, SSH, and storage. It
extends to the production concerns that keep systems reliable — logging, monitoring,
security, performance tuning, debugging, backups, firewalling, containers, and
automation — plus the scripting skills that make all of it repeatable.

These standards apply to both human operators and AI coding assistants, so that generated
commands, scripts, and unit files follow the same safety, permission, and idempotency
rules as hand-authored ones.

---

## Scope

This documentation covers:

- Filesystem, shell, and Bash
- Users, groups, and permissions
- Processes, services, and systemd
- Networking, SSH, and storage
- Package management and environment configuration
- Cron, logging, and monitoring
- Security, performance, and debugging
- Backups, firewall, and containers
- Automation and scripting
- Production operations, troubleshooting, tooling, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations

- 00. Overview
- 01. Filesystem
- 02. Shell
- 03. Bash

### Access & Processes

- 04. Users and Groups
- 05. Permissions
- 06. Processes
- 07. Services
- 08. systemd

### Networking & Storage

- 09. Networking
- 10. SSH
- 11. Storage
- 12. Package Management
- 13. Environment

### Operations

- 14. Cron
- 15. Logging
- 16. Monitoring
- 17. Security
- 18. Performance
- 19. Debugging
- 20. Backups
- 21. Firewall
- 22. Containers

### Automation & Practice

- 23. Automation
- 24. Scripting
- 25. Production
- 26. Best Practices
- 27. Troubleshooting
- 28. Tooling
- 29. System Administration
- 30. Engineering Principles

### Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every Linux operation should satisfy the following principles:

- Prefer least privilege; use `sudo` deliberately, not habitually.
- Set permissions and ownership intentionally — restrict by default.
- Manage services through systemd units, not ad-hoc background processes.
- Make changes idempotent and reproducible; script and version them.
- Read the logs before guessing; observability precedes intervention.
- Harden SSH and the firewall; expose only what must be reachable.
- Automate repetitive tasks, but keep scripts safe with strict modes and error checks.
- Test destructive commands against paths and dry-runs before running them wide.
- Back up before mutating state, and verify that restores actually work.
- Monitor resources proactively so capacity problems surface before outages.

---

## Intended Audience

These standards are intended for:

- System Administrators
- DevOps and Platform Engineers
- Site Reliability Engineers
- Backend Engineers operating their own services
- Security Engineers
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps Linux hosts secure, observable, and reproducible — so
operations stay predictable and recoverable under load and change.
