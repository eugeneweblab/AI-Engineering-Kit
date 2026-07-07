---
id: wordpress/readme
topic: wordpress
slug: readme
title: "WordPress Engineering Standards"
type: index
order: -1
status: ready
tags: [wordpress]
related: []
when_to_use: "Read first when building, reviewing, or maintaining a WordPress project (themes, plugins, or custom builds)."
---
# WordPress Engineering Standards

## Purpose

This section defines the engineering standards, architectural principles, and best
practices for building and maintaining WordPress projects — custom themes, plugins,
and integrations.

The objective is a consistent approach to secure, performant, and maintainable
WordPress code that follows platform conventions instead of fighting them.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- WordPress architecture
- Project structure
- Best practices and code style
- Performance
- Security
- Testing
- Common mistakes and review criteria

> **Structure note:** This is a focused section with a custom layout (`01`–`10`), not
> the standard `00`–`30 / 98 / 99 / 100` scheme used by most topics. Order documents by
> the `order` field in each file's frontmatter.

---

## Learning Path

Study the documents in the following order.

## Foundations

- 01. WordPress Architecture
- 02. Project Structure

## Writing Code

- 03. Best Practices
- 04. Code Style
- 05. Performance
- 06. Security

## Quality

- 07. Testing
- 08. Common Mistakes
- 09. AI Checklist
- 10. Review Checklist

---

## Engineering Principles

Every WordPress feature should satisfy the following principles:

- Follow WordPress coding standards and naming conventions.
- Use hooks (actions and filters) instead of modifying core.
- Escape output, sanitize input, and validate all data.
- Never trust user input or third-party data.
- Enqueue scripts and styles properly; do not hardcode assets.
- Keep themes presentational and move logic into plugins.
- Prefer the WordPress APIs over reinventing existing functionality.
- Optimize database queries; avoid queries inside loops.
- Build for accessibility and internationalization.
- Measure performance before optimizing.

---

## Intended Audience

These standards are intended for:

- WordPress Developers
- Frontend and Fullstack Engineers
- Theme and Plugin Authors
- Tech Leads
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps WordPress projects secure, performant, and maintainable
while staying aligned with platform conventions and upgrade paths.
