---
id: react/22-folder-structure
topic: react
slug: folder-structure
title: "React Folder Structure"
type: doc
order: 22
status: ready
tags: [react, folder-structure]
related: []
when_to_use: "Read before creating new files or organizing the folder and directory structure of a React project."
---
# React Folder Structure

## Purpose

This document defines the recommended folder structure for React applications.

The objective is to organize code in a way that improves discoverability, scalability, maintainability, and collaboration between engineers and AI coding assistants.

A consistent project structure reduces cognitive load and makes large applications easier to navigate.

---

## Core Principle

Organize code by feature.

Not by file type.

Files that change together should live together.

---

## Design Principles

Every project structure should follow these principles:

- predictable;
- scalable;
- discoverable;
- reusable;
- framework-independent where practical.

Folder organization should reflect the architecture of the application.

---

## Recommended Structure

```
src/

    app/

    features/

    components/

    hooks/

    services/

    api/

    layouts/

    pages/

    providers/

    contexts/

    store/

    utils/

    types/

    constants/

    assets/

    styles/

    tests/
```

Not every project requires every directory.

Only create folders that provide clear value.

---

## App

The `app` directory contains application-level configuration.

Examples:

- routing;
- providers;
- initialization;
- global configuration.

Avoid placing feature-specific code here.

---

## Features

The `features` directory contains business functionality.

Examples:

```
features/

    authentication/

    dashboard/

    checkout/

    products/

    profile/
```

Each feature should own:

- components;
- hooks;
- services;
- tests;
- types.

Features should remain as self-contained as practical.

---

## Components

The `components` directory contains reusable UI components.

Examples:

```
components/

    Button/

    Modal/

    Card/

    Avatar/

    Spinner/
```

Components in this directory should not depend on business features.

---

## Hooks

Store reusable Custom Hooks.

Examples:

```
hooks/

    useDebounce/

    useBreakpoint/

    useLocalStorage/
```

Feature-specific hooks should remain inside their corresponding feature.

---

## Services

Services contain business logic that is independent of React.

Examples:

- authentication;
- analytics;
- storage;
- notifications.

Avoid placing rendering logic inside services.

---

## API

The `api` directory contains communication with external systems.

Examples:

- HTTP clients;
- request helpers;
- API endpoints;
- response mappers.

Components should communicate through this layer rather than directly performing network requests.

---

## Layouts

Layouts define reusable page structures.

Examples:

- AdminLayout;
- DashboardLayout;
- MarketingLayout.

Layouts coordinate structure rather than business logic.

---

## Providers

The `providers` directory contains application-wide providers.

Examples:

- theme;
- authentication;
- query client;
- localization.

Keep provider configuration centralized.

---

## Contexts

Contexts expose shared application state.

Use Context only when state is naturally shared across multiple branches of the component tree.

Avoid using Context as a replacement for all state management.

---

## Store

Store global application state when required.

Examples:

- authentication;
- user preferences;
- feature flags.

Feature-specific state should remain within the feature whenever possible.

---

## Utils

Utility functions should be:

- pure;
- reusable;
- framework-independent.

Avoid adding business logic to generic utility modules.

---

## Types

Shared TypeScript definitions belong here.

Examples:

- interfaces;
- type aliases;
- enums.

Feature-specific types should remain within the feature.

---

## Constants

Store shared constants.

Examples:

- routes;
- limits;
- configuration values.

Avoid magic numbers and repeated string literals.

---

## Assets

Store static resources.

Examples:

- images;
- icons;
- fonts;
- videos.

Optimize assets before adding them to the project.

---

## Styles

Global styles belong here.

Examples:

- resets;
- typography;
- design tokens;
- theme variables.

Component-specific styles should remain close to the component.

---

## Tests

Shared testing utilities may live here.

Examples:

- render helpers;
- mock data;
- testing configuration.

Feature-specific tests should remain close to the code they verify.

---

## Co-location

Prefer keeping related files together.

Example:

```
ProductCard/

    ProductCard.tsx

    ProductCard.test.tsx

    ProductCard.types.ts

    ProductCard.styles.ts

    index.ts
```

Files that evolve together should remain together.

---

## Naming

Use consistent naming.

Examples:

```
Button/

UserProfile/

CheckoutForm/
```

Avoid:

```
button/

buttonComponent/

newFolder/

misc/
```

Directory names should communicate responsibility.

---

## AI Execution Checklist

## Investigation

☐ Review current project structure.

☐ Identify feature boundaries.

☐ Identify reusable components.

☐ Identify shared modules.

---

## Planning

☐ Organize by feature.

☐ Keep related files together.

☐ Separate reusable code.

☐ Minimize cross-feature dependencies.

---

## Verification

☐ Folder structure remains predictable.

☐ Features remain isolated.

☐ Shared code centralized.

☐ No unnecessary directories.

☐ Naming is consistent.

---

## Common Mistakes

Avoid:

Organizing everything by file type.

Creating generic folders such as `helpers` or `misc`.

Mixing business logic with reusable UI.

Creating deep directory hierarchies.

Duplicating shared utilities.

Moving feature-specific code into global directories.

---

## Completion Criteria

The project structure is complete when:

- features are clearly separated;
- reusable components are centralized;
- shared modules are organized consistently;
- related files are co-located;
- folder names communicate responsibility;
- the architecture supports future growth.

---

## Summary

A well-designed folder structure reflects the architecture of the application rather than individual technologies.

By organizing code around features, responsibilities, and reuse, React projects remain easier to understand, scale, and maintain throughout their lifecycle.