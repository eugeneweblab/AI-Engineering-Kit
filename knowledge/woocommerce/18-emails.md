---
id: woocommerce/18-emails
topic: woocommerce
slug: emails
title: "Emails"
type: doc
order: 18
status: ready
tags: [woocommerce, emails, wc_get_order, __construct, send, add_action, wp_mail, add_filter]
related: [woocommerce/05-orders, woocommerce/12-hooks, woocommerce/17-customization, woocommerce/23-monitoring]
when_to_use: "Read before adding, customizing, or debugging any WooCommerce transactional email or its deliverability."
---
# Emails

## Purpose

This document defines how to send, customize, and deliver WooCommerce transactional
emails correctly: order confirmations, processing/completed notices, refunds, new-account
mails, and custom notifications. It is written so an agent can register a new email or
override a template without breaking delivery, translation, or the customer's trust.

WooCommerce emails are driven by the `WC_Emails` manager and individual `WC_Email`
subclasses. Each email is a class registered through the `woocommerce_email_classes`
filter, triggered by an action, and rendered through an overridable template. Treat email
as a first-class part of the order lifecycle — see [orders](05-orders.md) — not an
afterthought bolted onto checkout.

## Why It Matters

Transactional email is the customer's primary record that a purchase happened. If the
"Processing order" mail never arrives, the customer assumes payment failed and either
disputes the charge or orders again. Broken deliverability is invisible in the admin — the
order looks fine while the customer sees silence — so these failures surface late, through
support tickets and chargebacks. Email also leaks: a template that echoes raw user input,
or a "resend" endpoint with no capability check, exposes order data to the wrong person.
Because email affects revenue, sender reputation with mailbox providers, and PII exposure
at once, hold it to the same bar as checkout code.

## Core Principles

- **Send through WooCommerce, not `wp_mail()` directly.** Registering a `WC_Email` gives
  you the enable/disable toggle, recipient config, template override, and translation that
  merchants and other plugins expect.
- **Trigger from order status transitions, not from checkout code.** Hook the canonical
  status actions so retries, admin edits, and API updates all send the same mail.
- **Never build email content by concatenating user data.** Escape every dynamic value; a
  customer name or order note is untrusted input.
- **Deliverability is infrastructure, not code.** Authenticate the sending domain (SPF,
  DKIM, DMARC) and send through a real transactional provider. `wp_mail()` from the web
  host will land in spam.
- **Emails must be idempotent and observable.** The same status transition may fire twice;
  log what was sent so you can prove delivery during a dispute.

## Best Practices

- Register custom emails via the `woocommerce_email_classes` filter and extend `WC_Email`;
  put templates in `templates/emails/` and honor overrides in the active theme.
- Trigger on WooCommerce status hooks such as `woocommerce_order_status_processing` or
  `woocommerce_order_status_completed`, then call `$email->trigger( $order_id )`.
- Override templates by copying to `yourtheme/woocommerce/emails/…` — never edit core
  plugin files, which are wiped on update. See [customization](17-customization.md).
- Escape output with `esc_html()`, `wp_kses_post()`, and `esc_url()`; wrap every
  user-facing string in `__()` / `esc_html__()` with your text domain.
- Reuse `WC()->mailer()` headers and recipients rather than hardcoding addresses.
- Send through an SMTP/API transactional service (Postmark, SES, SendGrid) via a mail
  plugin; set a `From` on your authenticated domain and a `Reply-To` the customer can use.
- Provide a plain-text fallback; many clients block or strip HTML.
- Queue slow or bulk sends through Action Scheduler so a provider outage does not block
  checkout.

## Examples

**Good Example** — a registered email triggered by a status transition

```php
// Register the class so merchants get a toggle and a template override.
add_filter( 'woocommerce_email_classes', function ( array $emails ) {
    $emails['WC_Email_Backorder_Shipped'] = new WC_Email_Backorder_Shipped();
    return $emails;
} );

class WC_Email_Backorder_Shipped extends WC_Email {
    public function __construct() {
        $this->id            = 'backorder_shipped';
        $this->title         = __( 'Backorder shipped', 'my-plugin' );
        $this->template_html = 'emails/backorder-shipped.php';
        $this->template_base = MY_PLUGIN_PATH . '/templates/';
        // Fire on a real status transition, not from the checkout handler,
        // so admin edits and API updates also send it.
        add_action( 'woocommerce_order_status_completed', [ $this, 'trigger' ], 10, 2 );
        parent::__construct();
    }

    public function trigger( int $order_id, ?WC_Order $order = null ): void {
        $order = $order ?: wc_get_order( $order_id );
        if ( ! $order || ! $this->is_enabled() ) {
            return; // respect the merchant's on/off toggle
        }
        $this->recipient = $order->get_billing_email();
        $this->object    = $order;
        // send() runs the template through wp_kses_post and the configured mailer.
        $this->send( $this->recipient, $this->get_subject(), $this->get_content(), $this->get_headers(), [] );
    }
}
```

**Bad Example** — bypasses WooCommerce, unescaped, fired from checkout

```php
add_action( 'woocommerce_checkout_order_processed', function ( $order_id ) {
    $order = wc_get_order( $order_id );
    // Raw wp_mail: no merchant toggle, no template override, no From on an
    // authenticated domain — lands in spam and cannot be turned off.
    wp_mail(
        $order->get_billing_email(),
        'Your order',
        // Customer name injected unescaped → HTML/script injection into the inbox.
        'Thanks ' . $order->get_billing_first_name() . '! Order #' . $order_id
    );
    // Fired only at checkout: a manual status change or a retried async
    // payment never re-sends, so gateway-async orders get no confirmation.
} );
```

## Common Mistakes

- Calling `wp_mail()` directly, losing the merchant toggle, template override, and i18n.
- Triggering email from `woocommerce_checkout_order_processed` instead of a status hook,
  so asynchronous gateways and admin edits send nothing.
- Editing core email templates in the plugin directory; updates silently revert them.
- Echoing customer names, addresses, or order notes without escaping.
- Sending from the web host with no SPF/DKIM/DMARC, so mail lands in spam or is rejected.
- No plain-text alternative, so clients that strip HTML show an empty message.
- Sending bulk mail synchronously in a request, timing out checkout when the provider slows.

## Production Tips

- Route all mail through a transactional provider and consume its bounce/complaint
  webhooks; alert on a bounce-rate spike — see [monitoring](23-monitoring.md).
- Log every send (order id, email id, recipient, timestamp) so you can prove delivery in a
  chargeback dispute; never log full message bodies containing PII.
- Keep a staging environment that rewrites all recipients to a catch-all so test orders
  never mail real customers.
- Warm a new sending domain gradually; a cold domain blasting volume gets throttled.

## AI Review Checklist

- Is the email a registered `WC_Email` (merchant toggle + template override), not raw `wp_mail()`?
- Is it triggered by an order status hook so retries and admin edits also send?
- Are all dynamic values escaped and all strings wrapped for translation?
- Are templates overridden in the theme, never edited in the plugin/core directory?
- Is the sending domain authenticated (SPF/DKIM/DMARC) via a transactional provider?
- Is there a plain-text fallback, and are bulk sends queued off the request?
- Are sends logged for dispute evidence without logging PII-laden bodies?

## Related

- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/17-customization.md`
- `knowledge/woocommerce/23-monitoring.md`
