---
id: woocommerce/readme
topic: woocommerce
slug: readme
title: "WooCommerce Engineering Standards"
type: index
order: -1
status: ready
tags: [woocommerce, readme, WC_Customer, WC_Product, WC_Order]
related: []
when_to_use: "Read first when starting work on a WooCommerce store, to see how this section's docs fit together and which extension point applies."
---
# WooCommerce Engineering Standards

## Purpose

This section defines the engineering standards for building and maintaining WooCommerce
stores: the data model, the extension points, and the operational discipline that money and
customer data require.

A store differs from a content site in one respect that governs everything here: mistakes have
direct financial consequences. A broken checkout does not degrade the experience — it stops
revenue. A mishandled tax rule creates a compliance problem. A leaked order export is a data
breach. These standards are correspondingly conservative about touching the paths where money
moves.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- WooCommerce architecture and installation
- The catalog: product types and product management
- The order lifecycle: orders, customers, checkout, payments
- Commercial rules: shipping, taxes, coupons, subscriptions
- Extension points: hooks, REST API, headless, customization
- Emails and customer communication
- Performance, security, scaling, and multisite
- Testing, debugging, deployment, monitoring, and production practice

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. [Overview](00-overview.md)
- 01. [Architecture](01-architecture.md)
- 02. [Installation](02-installation.md)
- 30. [Engineering Principles](30-engineering-principles.md)

## Catalog

- 03. [Product Types](03-product-types.md)
- 04. [Product Management](04-product-management.md)

## Orders and Customers

- 05. [Orders](05-orders.md)
- 06. [Customers](06-customers.md)
- 07. [Checkout](07-checkout.md)
- 08. [Payments](08-payments.md)

## Commercial Rules

- 09. [Shipping](09-shipping.md)
- 10. [Taxes](10-taxes.md)
- 11. [Coupons](11-coupons.md)
- 19. [Subscriptions](19-subscriptions.md)

## Extending the Store

- 12. [Hooks](12-hooks.md)
- 17. [Customization](17-customization.md)
- 13. [REST API](13-rest-api.md)
- 14. [Headless](14-headless.md)
- 18. [Emails](18-emails.md)

## Correctness and Speed

- 15. [Performance](15-performance.md)
- 16. [Security](16-security.md)
- 21. [Testing](21-testing.md)
- 26. [Debugging](26-debugging.md)

## Operations

- 20. [Multisite](20-multisite.md)
- 22. [Deployment](22-deployment.md)
- 23. [Monitoring](23-monitoring.md)
- 24. [Scaling](24-scaling.md)
- 27. [Production](27-production.md)

## Applied Guidance

- 25. [Best Practices](25-best-practices.md)
- 28. [Real-World Patterns](28-real-world-patterns.md)
- 29. [AI Review](29-ai-review.md)

## Verification

- 98. [Production Checklist](98-production-checklist.md)
- 99. [AI Review Checklist](99-ai-review-checklist.md)
- 100. [Common Antipatterns](100-common-antipatterns.md)

---

## Engineering Principles

Every store change should satisfy the following principles:

- Extend through hooks and template overrides; never edit WooCommerce core files.
- Use the CRUD classes (`WC_Order`, `WC_Product`, `WC_Customer`) rather than reading or
  writing post meta directly — the storage layer is not a stable contract.
- Treat checkout and payment as critical paths: change them deliberately, test them end to
  end, and have a rollback ready.
- Never store card data. Delegate to the gateway and keep the store out of PCI scope.
- Money is not a float. Use WooCommerce's formatting and rounding helpers consistently.
- Order and customer records are personal data — control access, limit exports, and know the
  retention rules that apply.
- Verify webhooks and callbacks from payment providers; an unverified callback is an
  authorization bypass.
- Assume the catalog grows: bound queries, index what you filter on, and test with realistic
  data volumes.
- Keep tax and shipping logic in configuration where possible; hardcoded rules become
  compliance debt.
- Test after every WooCommerce update on staging, especially templates you have overridden —
  overrides go stale silently.

---

## Intended Audience

These standards are intended for:

- WooCommerce and WordPress Developers
- Backend and Fullstack Engineers
- Agency Tech Leads
- Store Maintainers
- AI Coding Assistants
- Code Reviewers

---

## Summary

A WooCommerce store is an application where defects cost money. Extend through hooks and CRUD
classes rather than core edits or raw meta, guard the checkout and payment paths, treat order
data as personal data, and re-verify template overrides after every update.
