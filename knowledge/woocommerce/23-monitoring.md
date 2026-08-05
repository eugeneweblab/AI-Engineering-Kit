---
id: woocommerce/23-monitoring
topic: woocommerce
slug: monitoring
title: "WooCommerce Monitoring"
type: doc
order: 23
status: ready
tags: [woocommerce, monitoring, add_action, wc_get_order, wc_get_logger, warning, print_r, wc_get_orders]
related: [woocommerce/22-deployment, woocommerce/08-payments, woocommerce/15-performance, woocommerce/05-orders]
when_to_use: "Read before shipping a store to production or when deciding what to log, measure, and alert on for WooCommerce."
---
# WooCommerce Monitoring

## Purpose

This document defines what to observe in a production WooCommerce store and how: business
signals (order rate, payment success, renewals), technical signals (errors, slow queries,
queue health), and the logging and alerting that turn those signals into action before
customers notice. It is written so an agent instruments a store to catch revenue-affecting
failures early, without logging sensitive data.

WooCommerce ships a structured logger (`wc_get_logger()`), a system-status report, and
Action Scheduler as the backbone of background work. Effective monitoring layers business
KPIs on top of ordinary application observability, because in a store a "healthy" server
with zero orders is an emergency — see [deployment](22-deployment.md).

## Why It Matters

In a store, the most expensive failures are invisible to standard monitoring. The server
returns HTTP 200, CPU is fine, uptime checks pass — and yet a broken payment gateway means
no order has completed in an hour. Technical dashboards show green while revenue is zero.
The only reliable alarm is a *business* signal: order rate, payment success rate, renewal
volume. WooCommerce also does critical work asynchronously — emails, renewals, webhook
processing all run through Action Scheduler — so a silently stalled queue stops billing and
mail while the storefront looks perfect. Because the difference between "up" and "making
money" is exactly the gap most monitoring ignores, WooCommerce needs business-aware
observability, not just server metrics.

## Core Principles

- **Alert on business signals, not just server health.** A drop in orders or payment
  success rate is the earliest, truest sign something broke.
- **Watch the async backbone.** Action Scheduler queue depth, failed actions, and staleness
  are leading indicators; a stalled queue silently stops renewals and email.
- **Log with structure and context, never with secrets.** Use `wc_get_logger()` with a
  source and order id; never log card data, tokens, passwords, or full PII.
- **Instrument the money paths.** Checkout success/failure, gateway response time, and
  webhook processing outcomes deserve explicit metrics — see [payments](08-payments.md).
- **Make alerts actionable.** Every alert should map to a runbook step; noisy alerts get
  muted and then the real one is missed.

## Best Practices

- Track a small set of golden business metrics: orders/minute, payment success rate,
  average checkout duration, renewal success rate; alert on deviation from baseline.
- Monitor Action Scheduler: alert when pending actions exceed a threshold, when failed
  actions appear, or when the oldest pending action ages past its schedule.
- Use `wc_get_logger()->error( $msg, [ 'source' => 'my-gateway' ] )` for structured logs;
  ship logs to a central store (not the local filesystem) so they survive deploys.
- Capture gateway and webhook outcomes as metrics (success/decline/timeout counts and
  latency) so a gateway degradation is visible before customers complain.
- Add application performance monitoring (New Relic, Sentry) to surface slow DB queries and
  fatal errors with stack traces — see [performance](15-performance.md).
- Reconcile WooCommerce orders against gateway settlements on a schedule to catch charges
  that succeeded at the gateway but failed to record locally.
- Run a synthetic checkout on a schedule (a canary order) so you detect a broken funnel
  even during zero organic traffic.

## Examples

**Good Example** — structured, secret-free logging plus a business alert

```php
// Structured log with a source and order id — searchable, and safe.
add_action( 'woocommerce_order_status_failed', function ( $order_id ) {
    $order  = wc_get_order( $order_id );
    $logger = wc_get_logger();
    $logger->warning( 'Order failed at payment', [
        'source'       => 'checkout-monitor',
        'order_id'     => $order_id,
        'gateway'      => $order->get_payment_method(),
        // Log the outcome and identifiers, NEVER the card, token, or PII body.
    ] );
} );

// Business alert: if no order completed in the last 30 minutes during open hours,
// something is broken even though the server is "up".
add_action( 'my_store_healthcheck', function () {
    $recent = wc_get_orders( [
        'status'       => 'completed',
        'date_created' => '>' . ( time() - 30 * MINUTE_IN_SECONDS ),
        'limit'        => 1,
        'return'       => 'ids',
    ] );
    if ( empty( $recent ) && is_business_hours() ) {
        alerts_notify( 'No completed orders in 30m — check gateway/checkout' );
    }
} );
```

**Bad Example** — logs secrets, only watches the server

```php
add_action( 'woocommerce_checkout_order_processed', function ( $order_id ) {
    $order = wc_get_order( $order_id );
    // Logging full request state dumps card number, CVV, and customer PII into
    // plaintext log files — a breach and a PCI violation.
    error_log( 'Checkout: ' . print_r( $_POST, true ) );
    // "Monitoring" is a single uptime ping on the homepage. It returns 200 while
    // the gateway is down and zero orders complete — the real failure is invisible.
} );
```

## Common Mistakes

- Monitoring only server health/uptime, so a zero-orders outage shows all green.
- Logging card data, CVV, tokens, passwords, or full `$_POST`/PII into log files.
- Ignoring Action Scheduler, so a stalled queue silently halts renewals and email.
- Writing logs to the local filesystem, where they vanish on the next atomic deploy.
- Unstructured `error_log()` strings that cannot be searched, filtered, or alerted on.
- No baseline for business metrics, so a 40% drop in orders is never detected.
- Alert fatigue from noisy, non-actionable alarms that hide the one that matters.

## Production Tips

- Define per-store baselines and alert on relative deviation; absolute thresholds break as
  traffic scales.
- Keep a runbook link in every alert so the on-call action is obvious at 3am.
- Retain order/error history long enough for accounting and dispute resolution; never
  retain PII longer than policy allows.
- Rehearse a gateway-outage scenario so you know the business alert fires and the runbook
  works before it happens for real — see [deployment](22-deployment.md).

## AI Review Checklist

- Are there business-signal alerts (order rate, payment success), not just server uptime?
- Is Action Scheduler queue depth, failure, and staleness monitored?
- Do logs use `wc_get_logger()` with structure and a source, and exclude secrets/PII?
- Are gateway and webhook outcomes and latencies captured as metrics?
- Are logs shipped off-box so they survive atomic deploys?
- Is there a synthetic/canary checkout to detect a broken funnel at low traffic?
- Does every alert map to an actionable runbook step?

## Related

- `knowledge/woocommerce/22-deployment.md`
- `knowledge/woocommerce/08-payments.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/05-orders.md`
