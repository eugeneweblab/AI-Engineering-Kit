---
id: woocommerce/21-testing
topic: woocommerce
slug: testing
title: "WooCommerce Testing"
type: doc
order: 21
status: ready
tags: [woocommerce, testing]
related: [woocommerce/05-orders, woocommerce/08-payments, woocommerce/12-hooks, woocommerce/22-deployment]
when_to_use: "Read before writing or reviewing tests for WooCommerce code, or before shipping a change with no test coverage."
---
# WooCommerce Testing

## Purpose

This document defines how to test WooCommerce code so changes ship without silently
breaking checkout, orders, or payments. It covers what to test (cart, order lifecycle,
payment gateways, hooks), how to test it (PHPUnit with the WP test suite, factories,
gateway mocks, E2E), and where the risk concentrates.

WooCommerce testing builds on the WordPress PHPUnit scaffold (`wp scaffold plugin-tests`),
the WooCommerce test helpers (`WC_Helper_Order`, `WC_Helper_Product`), and Playwright/E2E
for the storefront. The goal is not coverage for its own sake but proving that money-moving
paths behave correctly under failure — see [orders](05-orders.md) and [payments](08-payments.md).

## Why It Matters

WooCommerce code fails where money moves, and those paths are the hardest to reach by
clicking around: an asynchronous gateway callback, a coupon edge case, a duplicate webhook.
Manual testing exercises the happy path and misses exactly the branches that cost revenue.
Untested WooCommerce plugins also break on *upgrade* — a hook signature changes, HPOS flips
on, and a subtle assumption fails in production during a Black Friday sale. Automated tests
that assert the failure paths (declined card, out-of-stock race, replayed webhook) are the
only cost-effective way to keep these branches correct across WooCommerce and WordPress
version bumps. The alternative is discovering the bug from a chargeback.

## Core Principles

- **Test money paths first.** Cart totals, tax and coupon math, order status transitions,
  and payment success/failure carry the most risk per line of code.
- **Assert failure paths, not just success.** Declined payments, stock races, invalid
  coupons, and duplicate webhooks are where real bugs live.
- **Isolate from external gateways.** Mock the payment API; a test suite must never hit a
  live gateway or depend on the network.
- **Use factories, not hand-built fixtures.** `WC_Helper_Order` / `WC_Helper_Product` build
  valid objects; hand-assembled arrays drift from real WooCommerce data shape.
- **Test against the storage mode you ship.** Run the suite with HPOS enabled if production
  uses HPOS; legacy-CPT assumptions pass locally and fail in prod.

## Best Practices

- Scaffold with the WP PHPUnit suite; extend `WC_Unit_Test_Case` so WooCommerce is booted
  and the DB is reset between tests.
- Build fixtures with `WC_Helper_Product::create_simple_product()` and
  `WC_Helper_Order::create_order()`; never insert posts/meta by hand.
- Mock gateways: implement a fake `WC_Payment_Gateway` that returns configurable success,
  decline, and timeout so you can assert each branch — see [payments](08-payments.md).
- Test hooks by asserting side effects: fire the action, then assert the order/product
  state it should have produced — see [hooks](12-hooks.md).
- Run E2E (Playwright) for the full checkout on a seeded store to catch template, JS, and
  block-checkout regressions that unit tests cannot see.
- Run the matrix in CI: supported PHP versions, current and previous WooCommerce, and both
  storage modes; gate merges on it — see [deployment](22-deployment.md).
- Reset global state between tests (`WC()->cart->empty_cart()`, clear session) so order-of-
  execution never changes results.

## Examples

**Good Example** — asserts a failure branch with a mocked gateway

```php
class Test_Checkout_Decline extends WC_Unit_Test_Case {
    public function test_declined_payment_leaves_order_failed_and_restocks(): void {
        $product = WC_Helper_Product::create_simple_product();
        $product->set_stock_quantity( 1 );
        $product->set_manage_stock( true );
        $product->save();

        $order = WC_Helper_Order::create_order();
        $order->add_product( $product, 1 );
        $order->save();

        // Fake gateway forced to decline — no network, deterministic.
        $gateway = new Fake_Gateway( [ 'result' => 'declined' ] );
        $result  = $gateway->process_payment( $order->get_id() );

        // Assert the FAILURE path: status, and that stock was released.
        $this->assertSame( 'fail', $result['result'] );
        $this->assertSame( 'failed', $order->get_status() );
        $this->assertSame( 1, wc_get_product( $product->get_id() )->get_stock_quantity() );
    }
}
```

**Bad Example** — happy path only, real gateway, hand-built order

```php
class Test_Checkout extends WP_UnitTestCase { // not WC_Unit_Test_Case: WC not booted
    public function test_checkout_works(): void {
        // Hand-built post/meta drifts from real WooCommerce order shape and
        // skips totals/tax calculation entirely.
        $order_id = wp_insert_post( [ 'post_type' => 'shop_order' ] );
        update_post_meta( $order_id, '_order_total', '20.00' );

        // Hits the LIVE gateway: flaky, slow, and charges a real sandbox that
        // may be down. Only the success path is ever exercised.
        $txn = StripeApi::charge( 'tok_visa', 2000 );
        $this->assertTrue( $txn->succeeded );
        // No assertion on order status, stock, or the decline branch.
    }
}
```

## Common Mistakes

- Testing only the happy path and never the declined/timeout/duplicate branches.
- Calling a real payment gateway from tests, making the suite flaky and network-bound.
- Building orders and products with `wp_insert_post` + meta instead of WooCommerce factories.
- Extending `WP_UnitTestCase` so WooCommerce (cart, gateways, HPOS) is never booted.
- Leaking state between tests (cart, session, options), so results depend on order.
- Running the suite only in legacy-CPT mode while production runs HPOS.
- No E2E on block checkout, so front-end and JS regressions ship unseen.

## Production Tips

- Run the full matrix (PHP × WooCommerce × storage mode) in CI and block merges on red.
- Seed a disposable store for E2E in CI so tests run against realistic data, then tear it down.
- Add a regression test for every production bug before fixing it, so it cannot return on
  the next WooCommerce upgrade — see [deployment](22-deployment.md).
- Keep the suite fast (mock external calls) so developers actually run it before pushing.

## AI Review Checklist

- Do tests cover failure paths (decline, timeout, stock race, duplicate webhook), not just success?
- Are payment gateways mocked, with zero live network calls in the suite?
- Are orders/products built with `WC_Helper_*` factories, not raw post/meta?
- Do test cases extend `WC_Unit_Test_Case` so WooCommerce is booted?
- Is global state (cart, session, options) reset between tests?
- Does CI run both storage modes if production uses HPOS?
- Is there E2E coverage of the actual checkout, including block checkout?

## Related

- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/08-payments.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/22-deployment.md`
