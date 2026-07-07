# Engineering Knowledge Base

## Overview

This repository contains the engineering standards, best practices, architectural guidelines, AI instructions, workflows and technology documentation used across projects.

The goal of this Knowledge Base is to provide a single source of truth for both engineers and AI coding assistants.

---

## How to use this knowledge base

- **AI agents:** start at [`../AGENTS.md`](../AGENTS.md).
- **Find a document:** use [`INDEX.json`](INDEX.json) (machine-readable) or
  [`INDEX.md`](INDEX.md) (human-readable). Filter to `status: "ready"` and match on
  `topic` / `tags` / `when_to_use`.
- **Write a document:** follow [`engineering/WRITING_STANDARD.md`](engineering/WRITING_STANDARD.md)
  and start from [`TEMPLATE.md`](TEMPLATE.md). See [`CONTRIBUTING.md`](CONTRIBUTING.md).

### Structure & metadata

Each standard topic follows the same layout: `README.md`, `00-overview.md`,
`01-…` through `30-…`, then `98-production-checklist.md`, `99-ai-review-checklist.md`,
`100-common-antipatterns.md`. The canonical file list is frozen in
[`../docs/structure/canonical-file-list.md`](../docs/structure/canonical-file-list.md).

Every document starts with YAML frontmatter (`id`, `topic`, `slug`, `title`, `type`,
`order`, `status`, `tags`, `related`, `when_to_use`). `status: ready` means the doc is
complete and safe to rely on; `status: draft` is a placeholder to be filled. **Order
docs by the `order` field, not by filename** (`100` sorts before `11` lexically).

Regenerate metadata after edits: `python3 scripts/inject-frontmatter.py` then
`python3 scripts/build-index.py`.

---

# Sections

## Engineering

General engineering principles.

- Decision making
- Code review
- Debugging
- Task execution
- Context-first development

---

## AI

Guidelines for AI-assisted development.

- Context gathering
- Planning
- Code generation
- Refactoring
- Bug fixing
- Self verification

---

## Frontend

- HTML
- CSS
- JavaScript
- TypeScript
- React
- Next.js
- Tailwind

---

## Backend

- Node.js
- NestJS
- PHP
- REST API
- GraphQL

---

## CMS

- WordPress
- WooCommerce
- Divi

---

## Database

- SQL
- PostgreSQL
- MySQL
- Prisma
- Redis

---

## Infrastructure

- Docker
- Kubernetes
- Nginx
- Linux
- AWS
- DevOps
- CI/CD

---

## Quality

- Testing
- Security
- Performance
- Accessibility
- SEO

---

## Architecture

System Design, DDD, Clean Architecture, Microservices, Distributed Systems.

---

## Workflows

Real development workflows.

---

## Examples

Production examples.

---

## Templates

Reusable templates.

---

## Snippets

Useful code snippets.

---

## Checklists

Production checklists.

---

## Playbooks

Step-by-step engineering guides.