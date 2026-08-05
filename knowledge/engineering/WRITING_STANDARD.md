---
id: engineering/WRITING_STANDARD
topic: engineering
slug: writing-standard
title: "Writing Standard"
type: doc
order: 999
status: ready
tags: [engineering, writing-standard, notes]
related: [engineering/00-engineering-principles, engineering/02-code-review, ai/06-self-verification]
when_to_use: "Read before authoring or editing knowledge base documents to follow the repository's writing standard."
---
# Writing Standard

## Audience

This repository is written for:

- Software engineers
- Engineering managers
- Technical leads
- AI coding agents

When a conflict exists, optimize for the engineer first.

## Non-goals

This repository is not intended to:

- teach programming from scratch
- replace official documentation
- prescribe one technology stack
- replace engineering judgment

## Purpose

Define a single writing style for the entire AI Engineering Kit repository.

Every document in this repository must follow the same structure, tone, and quality bar. Consistency makes the kit easier to read, maintain, and apply—whether the reader is an engineer or an AI agent consuming the content as context.

---

## Philosophy

Documentation in this repository serves two audiences: engineers who need to make decisions and ship work, and AI agents that retrieve and apply knowledge during development.

The human reader always comes first. Write for clarity, judgment, and practical use—not for keyword density or prompt tricks.

AI should consume documentation naturally. Well-structured prose, explicit rules, and concrete examples give agents reliable context without custom prompt engineering per document. If a human can follow the doc, an agent should be able to use it too.

---

## Document Structure

Every document should follow this order whenever possible:

1. **Title** — One clear name for the topic.
2. **Purpose** — What the document covers and who it is for.
3. **Why it matters** — The problem, risk, or outcome this knowledge addresses.
4. **Principles** — High-level beliefs that guide decisions in this area.
5. **Rules** — Specific, enforceable guidance. State what to do and what to avoid.
6. **Good examples** — Patterns that demonstrate correct application.
7. **Bad examples** — Anti-patterns with brief explanation of why they fail.
8. **Checklist** — A short list the reader can run before finishing work.
9. **Related documents** — Links to adjacent topics in this repository.

Not every topic needs every section. Skip a section only when it would add no value. When in doubt, include it.

---

## Writing Style

### Rules

- Use simple English. Prefer common words over jargon.
- Prefer short paragraphs. One idea per paragraph.
- Avoid buzzwords (`synergy`, `leverage`, `best-in-class`, `world-class`).
- Avoid marketing language. Do not sell the idea—explain it.
- Never exaggerate. Do not claim something is always true unless it is.
- Never write vague recommendations. Replace "consider improving performance" with a concrete action.
- Every recommendation must be actionable. The reader should know what to do next.
- Explain why. State the reason behind each rule or principle.
- Explain trade-offs. Most engineering choices have costs; name them.

### Good Example

> Cache static API responses at the edge when data changes less than once per hour. This reduces origin load and improves time to first byte. Trade-off: stale data until the cache expires or is invalidated. Define a TTL and invalidation path before enabling cache.

### Bad Example

> Leverage cutting-edge caching strategies to supercharge your API performance and deliver an amazing user experience.

---

## Examples

Whenever possible, provide both a good example and a bad example. Pair them so the contrast is obvious.

Use good examples to show correct structure, naming, and reasoning. Use bad examples to show common mistakes—vagueness, missing trade-offs, or rules that cannot be enforced.

Label them explicitly:

- **Good Example**
- **Bad Example**

Keep examples short. They should illustrate one point, not document an entire system.

---

## Checklists

Every practical document should end with a checklist.

Checklists turn guidance into verification. Each item should be answerable with yes or no. Prefer observable outcomes over subjective judgment.

### Good Example

- [ ] Purpose of the change is documented in the PR description.
- [ ] Error responses use a consistent shape across endpoints.
- [ ] Tests cover the failure path, not only the happy path.

### Bad Example

- [ ] Code quality is good.
- [ ] Think about security.
- [ ] Make sure everything works.

---

## File Naming

Use lowercase and kebab-case for all markdown files.

### Rules

- All letters lowercase.
- Words separated by hyphens.
- No spaces, underscores, or camelCase.
- Name files after the topic, not the format (`guide`, `doc`, `notes`).

### Examples

- `component-design.md`
- `api-design.md`
- `wordpress-security.md`

### Bad Examples

- `ComponentDesign.md`
- `api_design.md`
- `WordPress Security.md`

---

## Tone

- **Professional** — Respect the reader's time. Be direct.
- **Educational** — Teach the reasoning, not only the conclusion.
- **Objective** — Prefer evidence, constraints, and outcomes over preference.
- **Opinionated only when backed by engineering reasoning** — Strong recommendations are welcome when you explain the cost of ignoring them.

Do not hedge every sentence. Do not preach. State what works, what fails, and under which conditions.

---

## AI Compatibility

Documents should avoid references to specific AI models, products, or vendors whenever possible.

Knowledge in this repository should remain tool-independent. Describe practices, constraints, and patterns—not how to prompt a particular assistant. If a workflow depends on a tool, name the capability (e.g., "static analysis", "code review") rather than a branded product.

### Good Example

> Run automated linting in CI before merge. Fix violations or document an explicit exception with justification.

### Bad Example

> Ask ChatGPT to review your code and paste the output into the PR.

Tool-specific configuration belongs under `agents/` when it is intentionally scoped to an integration. General engineering knowledge belongs here and should read the same in five years.

---

## Definition of Done

A document is complete only if all of the following are true:

- **Purpose is clear** — A reader knows what the document is for within the first few lines.
- **Examples exist** — At least one good example; bad examples included when they clarify common mistakes.
- **Checklist exists** — For practical guidance, the reader can verify completion without guessing.
- **Reader can immediately apply the knowledge** — Rules and steps are specific enough to act on in real work.

If any item is missing, the document is a draft—not ready for the repository.

---

## Related documents

- [engineering/](.) — Engineering knowledge base root
- [../README.md](../README.md) — Knowledge directory overview
