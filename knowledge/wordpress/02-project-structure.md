# WordPress Project Structure

## Purpose

This document defines the recommended project structure for WordPress applications.

The objective is to organize code according to responsibilities rather than file types, making the project easier to understand, maintain, test, and extend.

The exact folder names may vary between projects, but the architectural principles should remain consistent.

---

# Core Principle

A directory should represent a responsibility, not a technology.

Good examples:

- API
- Services
- Modules
- Blocks
- Templates

Poor examples:

- Functions
- Misc
- Helpers2
- New
- Temp

Every folder should communicate its purpose immediately.

---

# High-Level Structure

A typical enterprise WordPress project may be organized as follows:

```text
project/
│
├── app/
├── config/
├── public/
├── storage/
├── vendor/
│
├── wp-content/
│   ├── plugins/
│   ├── mu-plugins/
│   ├── themes/
│   ├── uploads/
│   └── languages/
│
└── tools/
```

The exact layout depends on the project's deployment strategy.

---

# Theme Structure

A modern custom theme may contain:

```text
theme/
│
├── assets/
│   ├── css/
│   ├── js/
│   ├── fonts/
│   └── images/
│
├── blocks/
├── modules/
├── templates/
├── template-parts/
├── services/
├── api/
├── helpers/
├── hooks/
├── inc/
├── languages/
├── tests/
│
├── functions.php
└── style.css
```

Each directory should have a clearly defined responsibility.

---

# Plugin Structure

Large plugins should follow a modular architecture.

Example:

```text
plugin/
│
├── src/
│   ├── Admin/
│   ├── API/
│   ├── CLI/
│   ├── Commands/
│   ├── Controllers/
│   ├── DTO/
│   ├── Helpers/
│   ├── Hooks/
│   ├── Models/
│   ├── Repositories/
│   ├── Services/
│   ├── Validation/
│   └── Views/
│
├── assets/
├── languages/
├── tests/
│
└── plugin.php
```

Business logic should reside inside dedicated classes rather than the bootstrap file.

---

# Responsibility Guidelines

## Templates

Responsible for:

- markup;
- layout;
- presentation.

Templates should not contain business logic.

---

## Services

Responsible for:

- business rules;
- workflows;
- integrations;
- reusable operations.

Services should be framework-independent whenever practical.

---

## API

Responsible for:

- endpoint registration;
- request validation;
- response formatting.

Controllers should delegate work to services.

---

## Hooks

Responsible for:

- registering actions;
- registering filters;
- connecting WordPress events to application logic.

Avoid embedding business logic directly inside callbacks.

---

## Helpers

Responsible for:

- small reusable utility functions;
- formatting;
- conversions;
- lightweight abstractions.

Helpers should not become a second service layer.

---

## Modules

A module groups related functionality.

Example:

```text
Pricing/

Testimonials/

Newsletter/

Products/

Checkout/
```

Each module should encapsulate one feature.

---

# Asset Organization

Separate assets by type.

Example:

```text
assets/

css/

js/

images/

fonts/

icons/
```

Avoid placing unrelated files together.

---

# JavaScript Organization

Modern JavaScript should follow feature-based organization.

Example:

```text
components/

hooks/

services/

pages/

utils/

types/
```

Avoid placing hundreds of files in a single directory.

---

# PHP Organization

Prefer:

Small classes

Single responsibility

Dependency injection

Composition

Namespaces

Avoid:

God classes

Static utility containers

Deep inheritance

Large procedural files

---

# Naming Conventions

Prefer descriptive names.

Good

```text
ProductService.php

NewsletterController.php

ReviewRepository.php
```

Avoid

```text
Functions.php

Utils.php

Helpers.php

Stuff.php

New.php
```

Names should describe responsibilities.

---

# AI Execution Checklist

## Investigation

☐ Understand the existing project structure.

☐ Identify architectural patterns.

☐ Review naming conventions.

☐ Identify feature modules.

---

## Planning

☐ Place new code in the correct directory.

☐ Preserve project conventions.

☐ Avoid creating duplicate responsibilities.

☐ Minimize architectural changes.

---

## Implementation

☐ Respect folder responsibilities.

☐ Keep files cohesive.

☐ Reuse existing modules.

☐ Avoid unnecessary nesting.

---

## Verification

☐ Verify consistency.

☐ Verify discoverability.

☐ Verify maintainability.

☐ Verify documentation.

---

# Common Mistakes

Avoid:

Creating folders without a clear responsibility.

Organizing files by technology instead of feature.

Large "helpers" directories.

Mixing presentation with business logic.

Deep directory nesting.

Duplicate modules.

Inconsistent naming.

---

# Completion Criteria

A project structure is considered successful when:

- every directory has a clear responsibility;
- similar functionality is grouped together;
- new developers can quickly locate code;
- architectural boundaries remain clear;
- future growth can be accommodated without major restructuring.

---

# Summary

A well-organized project structure reduces cognitive load, improves maintainability, and helps both engineers and AI coding agents navigate the codebase efficiently.

The goal is not to create the perfect folder hierarchy, but to create one that communicates architectural intent clearly.