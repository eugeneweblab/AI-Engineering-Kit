---
id: woocommerce/26-debugging
topic: woocommerce
slug: debugging
title: "WooCommerce Debugging"
type: doc
order: 26
status: ready
tags: [woocommerce, debugging]
related: [woocommerce/23-monitoring, woocommerce/21-testing, woocommerce/27-production, woocommerce/12-hooks, woocommerce/29-ai-review]
when_to_use: "Read before diagnosing a broken checkout, a fatal error, a stuck background job, or an intermittent order bug."
---
# WooCommerce Debugging

## Purpose

This document defines how to find the cause of a WooCommerce failure — a white screen,
a checkout that hangs, an order stuck in `pending`, a background job that never runs —
using the platform's own tooling. The goal is a reproducible root cause, not a guess.
Debugging in production has its own rules, because the tools you reach for can leak data
or break the site further.

## Why It Matters

A WooCommerce bug is rarely in one place: a fatal error may come from a third-party plugin,
a slow checkout from a database query, a missing order email from a failed scheduled action.
Guessing wastes hours and often makes things worse — enabling display errors on a live store
can dump credentials to shoppers. Structured debugging, using logs and the right tool for the
layer, turns a vague "checkout is broken" report into a specific, fixable line of code.

## Core Principles

- **Read the logs before touching code.** WooCommerce, PHP, and the web server all log.
  The answer is usually already written down.
- **Never show errors to visitors.** Log errors; do not display them. Display errors on a
  live store is both a security leak and an availability risk.
- **Reproduce in staging.** Change nothing on production you cannot instantly revert.
  Reproduce the bug on a clone with real data first.
- **Isolate by bisection.** Deactivate plugins and switch to a default theme to find the
  culprit; a conflict is a plugin/theme problem until proven a core one.
- **Instrument the right layer.** Front-end, PHP, SQL, and async each have a different tool;
  using the wrong one hides the bug.

## Best Practices

- Enable logging without display: set `WP_DEBUG=true`, `WP_DEBUG_LOG=true`,
  `WP_DEBUG_DISPLAY=false`, and `display_errors=Off`. Errors go to `wp-content/debug.log`,
  not the browser.
- Use the **WooCommerce logger** (`wc_get_logger()`) for your own diagnostics; read logs at
  **WooCommerce → Status → Logs**. Tag entries with a `source` so they group in one file.
- Install **Query Monitor** on staging to see slow queries, hooks fired, HTTP calls, and PHP
  notices per request. Never leave it active on production.
- Check **WooCommerce → Status → Scheduled Actions** for stuck or failed Action Scheduler
  jobs when emails, syncs, or webhooks silently do not fire.
- Read **System Status** (`WooCommerce → Status`) first for a conflict report — outdated
  templates, missing tables, PHP limits, and unsupported versions are flagged there.
- Bisect conflicts with a **health-check / troubleshooting** flow that disables plugins for
  your session only, so live shoppers are unaffected.
- Escalate PHP fatals via the **`wp_fatal_error_handler`** log and the recovery-mode email
  WordPress sends automatically.

## Examples

**Good Example** — structured, sourced logging you can grep later

```php
// Levels and a source tag mean this lands in wc-logs/payment-*.log and is
// filterable in Status → Logs, without exposing anything to the shopper.
$logger  = wc_get_logger();
$context = [ 'source' => 'payment' ];

try {
    $result = $gateway->charge( $order );
    $logger->info( sprintf( 'Charged order %d: %s', $order->get_id(), $result->id ), $context );
} catch ( \Exception $e ) {
    // Log the detail; show the customer a generic failure. Never echo $e->getMessage().
    $logger->error( 'Charge failed: ' . $e->getMessage(), $context );
    throw new \Exception( __( 'Payment could not be processed.', 'acme' ) );
}
```

**Bad Example** — debugging by leaking to production

```php
// Turns the live storefront into a debugger: notices, paths, and query text render
// mid-checkout for real shoppers, and var_dump aborts the response.
ini_set( 'display_errors', 1 );
error_reporting( E_ALL );
var_dump( $order->get_meta_data() );   // dumps customer data to the page, then die
die();                                  // checkout never completes
```

## Common Mistakes

- Enabling `WP_DEBUG_DISPLAY` or `display_errors` on production, leaking paths and data.
- `echo`/`var_dump` debugging in live payment or checkout hooks, breaking the response.
- Ignoring **Scheduled Actions** when async work "does nothing" — the job failed, not the code.
- Skipping the System Status report and missing an obvious version or template conflict.
- Debugging on production directly instead of reproducing on a staging clone.
- Leaving Query Monitor or a debug plugin active on the live site.
- Blaming core before bisecting plugins and switching to a default theme.

## Production Tips

- Ship a **correlation id** (order id, request id) into every log line so a single failed
  checkout can be traced across payment, email, and sync logs.
- Wire fatal errors and error-log growth into alerting from [monitoring](23-monitoring.md);
  a spike in `debug.log` size is often the first sign of a bad deploy.
- Rotate and size-cap `debug.log` and `wc-logs/`; an unbounded log can fill the disk and
  take the store down on its own.

## AI Review Checklist

- Is logging enabled (`WP_DEBUG_LOG`) with display disabled (`WP_DEBUG_DISPLAY=false`)?
- Does custom code use `wc_get_logger()` with a `source`, not `echo`/`var_dump`?
- Are error details logged while the customer sees only a generic message?
- Were Scheduled Actions checked for failed/stuck jobs on any async bug?
- Was the issue reproduced in staging before any production change?
- Is Query Monitor (and any debug plugin) confirmed inactive on production?
- Are debug logs rotated and size-capped so they cannot fill the disk?

## Related

- `knowledge/woocommerce/23-monitoring.md`
- `knowledge/woocommerce/21-testing.md`
- `knowledge/woocommerce/27-production.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/29-ai-review.md`
