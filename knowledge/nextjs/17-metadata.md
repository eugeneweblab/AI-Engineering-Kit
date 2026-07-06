# Next.js Metadata

## Purpose

This document defines the engineering standards for configuring metadata in Next.js applications.

The objective is to ensure every page provides accurate, complete, and search-engine-friendly metadata while supporting rich previews, accessibility, and modern web standards.

Metadata should be generated on the server and remain closely aligned with the content of each page.

---

# Core Principle

Metadata describes content.

Every page should provide metadata that accurately represents its purpose.

Avoid generic or duplicated metadata.

---

# Metadata Goals

Every page should strive for:

- meaningful titles;
- unique descriptions;
- accurate canonical URLs;
- rich social previews;
- proper indexing;
- accessibility.

Metadata should improve both user experience and discoverability.

---

# Metadata Hierarchy

Metadata follows the routing hierarchy.

```
Root Layout

↓

Nested Layout

↓

Page
```

Layouts provide defaults.

Pages override only what is necessary.

---

# Page Title

Every page should define a unique and descriptive title.

A good title:

- identifies the content;
- remains concise;
- reflects user intent;
- supports SEO.

Avoid generic titles such as:

```
Home

Dashboard

Page

Index
```

---

# Meta Description

Provide a meaningful description for every indexable page.

Descriptions should:

- summarize the content;
- encourage clicks;
- remain accurate;
- avoid duplication.

Do not generate descriptions from unrelated content.

---

# Canonical URL

Every indexable page should define a canonical URL.

Canonical URLs help:

- prevent duplicate content;
- consolidate ranking signals;
- improve search engine understanding.

Only one canonical URL should exist for each resource.

---

# Open Graph

Configure Open Graph metadata for social sharing.

Include:

- title;
- description;
- image;
- URL;
- type.

Open Graph metadata should accurately reflect page content.

---

# Twitter Cards

Configure Twitter Card metadata.

Typical properties include:

- title;
- description;
- image;
- card type.

Ensure previews remain visually consistent across platforms.

---

# Metadata Images

Social preview images should:

- represent the content;
- have appropriate dimensions;
- remain readable;
- avoid excessive text.

Maintain consistent branding across the application.

---

# Robots

Configure robots metadata intentionally.

Examples:

- index;
- noindex;
- follow;
- nofollow.

Administrative and private pages should not be indexed.

---

# Viewport

Define viewport metadata consistently.

Ensure responsive behavior across supported devices.

---

# Theme Color

Provide theme colors where appropriate to improve browser integration and mobile appearance.

---

# Icons

Configure application icons centrally.

Examples:

- favicon;
- Apple Touch Icon;
- shortcut icon.

Keep branding consistent.

---

# Structured Metadata

Metadata should accurately describe:

- page type;
- language;
- author;
- publication date;
- modification date.

Structured metadata improves interoperability.

---

# Dynamic Metadata

Generate metadata dynamically when it depends on fetched content.

Examples:

- blog articles;
- products;
- user-generated content;
- CMS pages.

Metadata generation should reuse existing server-side data whenever practical.

---

# Localization

Localized pages should provide metadata in the appropriate language.

Ensure:

- translated titles;
- translated descriptions;
- correct language information.

Avoid mixing languages within metadata.

---

# Accessibility

Metadata should support accessibility by:

- providing meaningful document titles;
- identifying document language;
- improving navigation history.

Accessibility begins before the page is rendered.

---

# Performance

Metadata generation should:

- execute efficiently;
- avoid duplicate data requests;
- reuse cached data where possible.

Metadata should not become a performance bottleneck.

---

# Security

Do not expose:

- private identifiers;
- confidential information;
- internal implementation details.

Metadata is publicly visible.

---

# AI Execution Checklist

## Investigation

☐ Review page purpose.

☐ Determine indexing requirements.

☐ Review social sharing needs.

☐ Review localization.

---

## Planning

☐ Create unique title.

☐ Write meaningful description.

☐ Configure canonical URL.

☐ Configure social metadata.

---

## Verification

☐ Metadata unique.

☐ Canonical URL correct.

☐ Open Graph configured.

☐ Robots configured.

☐ Accessibility supported.

☐ Performance reviewed.

---

# Common Mistakes

Avoid:

Duplicated page titles.

Generic descriptions.

Missing canonical URLs.

Incorrect Open Graph images.

Indexing private pages.

Generating metadata on the client.

Exposing sensitive information.

Ignoring localization.

---

# Completion Criteria

Metadata implementation is complete when:

- every page has a unique title;
- descriptions accurately summarize content;
- canonical URLs are configured;
- social metadata is complete;
- indexing rules are appropriate;
- accessibility and performance have been considered.

---

# Summary

Metadata is an essential part of every modern web application.

By generating accurate server-side metadata, defining canonical URLs, configuring social previews, and maintaining consistency across layouts and pages, Next.js applications become more discoverable, accessible, and professional.