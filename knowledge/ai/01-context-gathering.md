# Context Gathering

## Purpose

This document defines how an AI coding agent should gather context before making engineering decisions.

The quality of generated code is directly proportional to the quality of the collected context.

AI should spend more effort understanding the project than generating code.

---

# Core Principle

Never generate code using only the user's request.

The user's request is only one source of information.

Engineering decisions should also be based on:

- project architecture;
- existing code;
- documentation;
- configuration;
- dependencies;
- established conventions.

---

# Context Priority

Always gather context in the following order.

## Level 1 — User Request

Understand:

- what is requested;
- expected outcome;
- constraints;
- explicit requirements;
- implicit assumptions.

Questions should be asked whenever requirements are incomplete.

---

## Level 2 — Repository Structure

Understand the repository.

Inspect:

- folders;
- modules;
- package structure;
- naming conventions;
- technology stack.

The repository often reveals architectural decisions before any documentation does.

---

## Level 3 — Existing Implementation

Before creating anything new, inspect similar implementations.

Search for:

- components;
- services;
- utilities;
- API routes;
- hooks;
- models;
- migrations;
- tests.

Existing implementations are the strongest source of engineering context.

---

## Level 4 — Configuration

Inspect configuration files.

Examples:

- package.json
- tsconfig.json
- composer.json
- eslint.config.js
- prettier.config.js
- next.config.js
- nest-cli.json
- wp-config.php
- docker-compose.yml

Configuration often explains architectural decisions.

---

## Level 5 — Documentation

Read available documentation.

Examples:

- README
- architecture documents
- ADRs
- playbooks
- contribution guides
- coding standards

Documentation explains decisions that code alone cannot.

---

## Level 6 — Dependencies

Determine which libraries are already available.

Never introduce a new dependency before verifying whether the project already contains an appropriate solution.

Additional dependencies increase maintenance cost.

---

# Repository Investigation

Before implementation, AI should answer:

What technologies are used?

How is the project organized?

Which architectural pattern is followed?

How are files named?

How are components organized?

How are services organized?

How is state managed?

How are errors handled?

How are tests written?

How is styling implemented?

If these questions cannot be answered, additional investigation is required.

---

# Searching Strategy

Never stop after the first search result.

Search multiple locations.

Examples:

Component search

- components/
- ui/
- shared/
- common/

Utility search

- utils/
- helpers/
- lib/
- shared/

API search

- api/
- routes/
- controllers/

Service search

- services/
- providers/

Large repositories often contain multiple valid implementations.

---

# Detect Existing Conventions

Before writing code, identify conventions for:

Naming

Folder organization

Imports

Error handling

Logging

Testing

Comments

Documentation

Formatting

Architecture

Follow existing conventions unless there is a clear engineering reason not to.

---

# Missing Context

If important context is unavailable, AI should explicitly identify what is missing.

Examples:

"I could not determine how authentication is implemented."

"No existing component follows this pattern."

"The repository does not appear to contain testing guidelines."

Missing context should be communicated before implementation.

---

# When To Ask Questions

AI should ask questions when:

requirements are ambiguous;

multiple implementations are equally valid;

repository conventions are unclear;

business rules are missing;

implementation affects security;

implementation affects public APIs;

implementation changes architecture.

Questions reduce incorrect assumptions.

---

# Context Checklist

Before implementation verify:

- I understand the requested outcome.
- I understand the repository structure.
- I inspected similar implementations.
- I identified project conventions.
- I checked configuration.
- I reviewed documentation.
- I searched for reusable code.
- I understand the affected architecture.
- I identified possible side effects.
- I know which files should change.

Implementation should not begin until every applicable item has been completed.

---

# Anti-patterns

Avoid:

Generating code after reading only one file.

Creating new components without searching the repository.

Ignoring existing architecture.

Adding dependencies unnecessarily.

Assuming coding conventions.

Using examples from unrelated projects instead of repository code.

Treating every task as a greenfield implementation.

---

# Summary

Context gathering is the highest return activity in AI-assisted software development.

The best AI agents are not those that generate code the fastest.

They are the ones that understand the repository the best before generating a single line of code.