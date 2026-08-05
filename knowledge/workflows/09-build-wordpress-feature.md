---
id: workflows/09-build-wordpress-feature
topic: workflows
slug: build-wordpress-feature
title: "Workflow — Build a WordPress Feature"
type: doc
order: 9
status: ready
tags: [workflows, build-wordpress-feature]
related:
  - wordpress/01-wordpress-architecture
  - wordpress/03-best-practices
  - wordpress/04-code-style
  - wordpress/05-performance
  - wordpress/06-security
  - wordpress/07-testing
  - wordpress/98-production-checklist
  - wordpress/99-ai-review-checklist
  - php/13-security
  - security/09-input-validation
  - woocommerce/12-hooks
  - divi/16-wordpress-hooks
when_to_use: "Follow this workflow when implementing a new feature in a WordPress project."
---
# Workflow — Build a WordPress Feature

## Purpose

This workflow defines the standard engineering process for implementing a new feature in a WordPress project.

It applies to both traditional and headless WordPress architectures and covers themes, plugins, custom post types, REST API endpoints, Gutenberg blocks, Divi modules, WooCommerce extensions, and integrations.

The objective is to build features that follow WordPress best practices while respecting the project's existing architecture and coding standards.

---

## Goal

Deliver a feature that:

- integrates naturally with the existing project;
- follows WordPress coding standards;
- reuses existing functionality;
- minimizes technical debt;
- remains compatible with future WordPress updates;
- is easy to maintain and extend.

---

## Workflow Overview

```
Understand Requirements
        ↓
Analyze Existing Project
        ↓
Identify WordPress Integration Points
        ↓
Search Existing Implementations
        ↓
Design the Solution
        ↓
Implement
        ↓
Verify
        ↓
Optimize
        ↓
Document
        ↓
Complete
```

---

## Step 1 — Understand the Requirements

Before writing code determine:

- business objective;
- user workflow;
- administrator workflow;
- frontend requirements;
- backend requirements;
- integrations;
- performance expectations.

Do not assume WordPress should handle everything.

Determine whether functionality belongs in WordPress or another system.

---

## Step 2 — Analyze the Existing Project

Identify the project architecture.

Examples:

- Classic Theme
- Block Theme
- Headless WordPress
- WooCommerce
- Multisite
- Bedrock
- Custom Plugin Architecture

Review:

- active plugins;
- custom plugins;
- theme structure;
- REST API usage;
- hooks;
- coding conventions.

The implementation should match the existing architecture.

Relevant knowledge:

- [WordPress — WordPress Architecture](../wordpress/01-wordpress-architecture.md) — the load order, hook system, and template hierarchy the feature plugs into.
- [WordPress — Project Structure](../wordpress/02-project-structure.md) — where theme, plugin, and `mu-plugins` code belongs.
- [WordPress — Code Style](../wordpress/04-code-style.md) — the WordPress Coding Standards this project is checked against.
- [Divi — Architecture](../divi/01-architecture.md) — when the site is built on Divi, the builder owns page rendering.

---

## Step 3 — Identify Integration Points

Determine where the feature belongs.

Examples:

Theme

Plugin

Custom Post Type

REST API

Admin UI

Cron Job

CLI Command

Gutenberg Block

Divi Module

Customizer

Widget

Shortcode

The chosen integration point should match the feature's responsibility.

Use the workflow that matches the integration point you selected:

- [Workflow — Build a Gutenberg Block](11-build-gutenberg-block.md) — editor-side content components.
- [Workflow — Build a Divi Module](10-build-divi-module.md) — builder modules on a Divi site.
- [Workflow — Add an API Endpoint](07-add-api-endpoint.md) — the contract rules also apply to `register_rest_route`.

Relevant knowledge:

- [Divi — WordPress Hooks](../divi/16-wordpress-hooks.md) — the actions and filters available at each stage of the request.
- [Divi — REST API](../divi/17-rest-api.md) and [WooCommerce — REST API](../woocommerce/13-rest-api.md) — extending the existing REST surface rather than adding a parallel one.
- [WooCommerce — Hooks](../woocommerce/12-hooks.md) — the extension points to prefer on a store before touching templates.

---

## Step 4 — Search Before Creating

Search for existing:

- hooks;
- filters;
- helper functions;
- REST endpoints;
- services;
- utilities;
- custom fields;
- reusable templates;
- reusable blocks.

Never duplicate existing functionality.

Relevant knowledge:

- [WordPress — Best Practices](../wordpress/03-best-practices.md) — the core APIs that already solve most requirements.
- [WooCommerce — Customization](../woocommerce/17-customization.md) — override through hooks and template overrides, never by editing plugin files.
- [Engineering — Engineering Principles](../engineering/00-engineering-principles.md) — reuse before creation.

---

## Step 5 — Follow WordPress Architecture

Respect WordPress conventions.

Use:

Actions

Filters

REST API

Template hierarchy

Capability checks

Nonces

Internationalization

Escaping

Sanitization

Validation

Avoid bypassing the WordPress ecosystem unless the project architecture explicitly requires it.

Relevant knowledge:

- [PHP — Modern PHP](../php/23-modern-php.md) and [PHP — Namespaces](../php/05-namespaces.md) — namespaced, autoloaded classes instead of a flat `functions.php`.
- [PHP — Dependency Injection](../php/20-dependency-injection.md) — testable services behind the hook callbacks.
- [PHP — PSR Standards](../php/24-psr-standards.md) — autoloading and interoperability conventions.

---

## Step 6 — Implement the Feature

During implementation:

- separate business logic from presentation;
- reuse existing services;
- avoid global state when possible;
- keep hooks focused;
- keep templates simple.

Business logic should not be embedded inside templates.

Relevant knowledge:

- [WordPress — Best Practices](../wordpress/03-best-practices.md) — template parts, conditional loading, and hook hygiene.
- [PHP — Clean Code](../php/22-clean-code.md) — keeping callbacks short and intention-revealing.
- [Divi — Custom Fields](../divi/15-custom-fields.md) and [Divi — Dynamic Content](../divi/07-dynamic-content.md) — surfacing editable data without hardcoding it in a template.

---

## Step 7 — Security Review

Verify:

- capability checks;
- nonce verification;
- input validation;
- sanitization;
- escaping;
- SQL safety;
- file upload validation;
- REST permissions.

Security should be part of implementation from the beginning.

The three rules that cover most WordPress vulnerabilities: check the capability
(`current_user_can`), verify the nonce (`check_admin_referer` / `wp_verify_nonce`), and
escape at the point of output (`esc_html`, `esc_attr`, `esc_url`, `wp_kses_post`) rather
than at the point of storage.

Relevant knowledge:

- [WordPress — Security](../wordpress/06-security.md) — capabilities, nonces, sanitization, and escaping in context.
- [PHP — Security](../php/13-security.md) — the language-level failure modes underneath.
- [Security — Input Validation](../security/09-input-validation.md) and [Security — Output Encoding](../security/10-output-encoding.md) — validate on the way in, encode on the way out.
- [Security — SQL Injection](../security/13-sql-injection.md) — always `$wpdb->prepare()` when a direct query is unavoidable.
- [Security — File Upload Security](../security/15-file-upload-security.md) — for features that accept media.
- [WooCommerce — Security](../woocommerce/16-security.md) and [Divi — Security](../divi/19-security.md) — platform-specific concerns.

---

## Step 8 — Performance Review

Review:

- unnecessary database queries;
- repeated queries;
- object caching;
- transient usage;
- REST performance;
- image optimization;
- lazy loading;
- asset loading.

Performance should scale with content growth.

Relevant knowledge:

- [WordPress — Performance](../wordpress/05-performance.md) — object cache, transients, and query discipline.
- [Databases — Query Optimization](../databases/08-query-optimization.md) and [Databases — Indexing](../databases/07-indexing.md) — the cost of an unindexed meta query grows with the content table.
- [Performance — Caching](../performance/08-caching.md) — page, object, and CDN layers and what each invalidates.
- [Performance — Images](../performance/11-images.md) — responsive sizes and modern formats for media-heavy features.
- [Divi — Performance](../divi/10-performance.md) and [WooCommerce — Performance](../woocommerce/15-performance.md) — builder and store specifics.

---

## Step 9 — Compatibility Review

Verify compatibility with:

- supported PHP version;
- supported WordPress version;
- active plugins;
- active theme;
- multisite (if applicable);
- translations;
- caching;
- CDN.

Avoid assumptions about the production environment.

Relevant knowledge:

- [WordPress — Testing](../wordpress/07-testing.md) — verifying the feature against a realistic install.
- [PHP — Production](../php/27-production.md) — version constraints and runtime configuration.
- [Divi — Deployment](../divi/22-deployment.md) and [WooCommerce — Deployment](../woocommerce/22-deployment.md) — staging-to-production practice for WordPress sites.

---

## AI Execution Checklist

## Investigation

☐ Understand the business requirements.

☐ Identify project architecture.

☐ Review existing plugins.

☐ Review theme structure.

☐ Review coding conventions.

☐ Search similar implementations.

---

## Planning

☐ Select the correct integration point.

☐ Identify reusable code.

☐ Define implementation strategy.

☐ Estimate risks.

---

## Implementation

☐ Follow WordPress coding standards.

☐ Use hooks correctly.

☐ Separate business logic.

☐ Preserve project architecture.

☐ Avoid duplicate functionality.

---

## Verification

☐ Verify frontend behavior.

☐ Verify administrator workflow.

☐ Verify REST API (if applicable).

☐ Verify security.

☐ Verify performance.

☐ Verify translations.

☐ Update documentation.

---

## WordPress Engineering Principles

Prefer:

WordPress APIs

Hooks

Reusable services

Template parts

REST API

Capability checks

Core functionality

Avoid:

Direct database queries when APIs exist.

Duplicating WordPress functionality.

Hardcoded URLs.

Hardcoded IDs.

Direct output without escaping.

Large template files containing business logic.

---

## Common Mistakes

Avoid:

Ignoring existing hooks.

Writing business logic inside templates.

Skipping nonce validation.

Skipping capability checks.

Ignoring escaping.

Ignoring translation functions.

Ignoring object caching opportunities.

Creating duplicate REST endpoints.

---

## Completion Criteria

The workflow is complete only if:

- requirements are satisfied;
- WordPress conventions are respected;
- project architecture remains consistent;
- security has been verified;
- performance has been reviewed;
- compatibility has been confirmed;
- documentation has been updated where necessary.

---

## Expected AI Output

After completing this workflow, the AI should explain:

- where the feature was integrated;
- why that integration point was selected;
- which WordPress APIs were used;
- which existing code was reused;
- security measures implemented;
- performance considerations;
- verification performed.

---

## Self-Verification — Topic Checklists

Before marking the feature complete, run it through the checklists of the topics it touched:

- WordPress — [Production Checklist](../wordpress/98-production-checklist.md), [AI Review Checklist](../wordpress/99-ai-review-checklist.md), [Common Antipatterns](../wordpress/100-common-antipatterns.md).
- PHP — [Production Checklist](../php/98-production-checklist.md), [AI Review Checklist](../php/99-ai-review-checklist.md), [Common Antipatterns](../php/100-common-antipatterns.md).
- Security — [Production Checklist](../security/98-production-checklist.md), [AI Review Checklist](../security/99-ai-review-checklist.md), [Common Antipatterns](../security/100-common-antipatterns.md).

Add the platform checklists that apply: for a store,
[WooCommerce — Production Checklist](../woocommerce/98-production-checklist.md) and
[WooCommerce — AI Review](../woocommerce/29-ai-review.md); for a Divi build,
[Divi — Production Checklist](../divi/98-production-checklist.md) and
[Divi — AI Review Checklist](../divi/99-ai-review-checklist.md). Features that render public
pages should also pass [SEO — Production Checklist](../seo/98-production-checklist.md) and
[Accessibility — Production Checklist](../accessibility/98-production-checklist.md).

---

## Summary

A high-quality WordPress feature integrates seamlessly into both the WordPress ecosystem and the existing project architecture.

It respects WordPress conventions, minimizes custom complexity, prioritizes security and performance, and remains maintainable over time.