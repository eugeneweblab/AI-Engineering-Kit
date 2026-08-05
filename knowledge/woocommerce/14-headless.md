---
id: woocommerce/14-headless
topic: woocommerce
slug: headless
title: "WooCommerce Headless"
type: doc
order: 14
status: ready
tags: [woocommerce, headless, btoa, stringify, WooCommerce]
related: [woocommerce/13-rest-api, woocommerce/16-security, woocommerce/08-payments, woocommerce/15-performance, woocommerce/07-checkout]
when_to_use: "Read before building a decoupled storefront (Next.js, mobile, PWA) on top of WooCommerce."
---
# WooCommerce Headless

## Purpose

This document defines how to run WooCommerce **headless** — using WordPress/WooCommerce
as a backend commerce engine while a separate frontend (Next.js, Nuxt, a mobile app, a
PWA) renders the storefront and talks to it over an API. It is written so an agent can
decouple the frontend without exposing secrets, breaking checkout/payment security, or
recreating server logic in the browser.

Headless trades WooCommerce's built-in theme and template rendering for full control of
the frontend. That control is worth it for custom UX and performance, but it moves
responsibility for security, SEO, and checkout integrity onto you.

## Why It Matters

The single most dangerous headless mistake is putting a write-scoped API key in the
frontend so the browser can "just call WooCommerce directly." That key is then public,
and anyone can read customers and mutate orders. Payment capture, coupon validation, and
tax calculation are trust-sensitive and must stay server-side; a headless architecture
that pushes them to the client invites price tampering. Done right, headless is a clean
backend-for-frontend boundary; done wrong, it is a store with its credentials printed on
every page.

## Core Principles

- **Secrets live on a server, never in the client.** The browser talks to *your*
  backend (a BFF / API route); that backend holds the WooCommerce key. Ship no consumer
  secret in a JS bundle.
- **Trust the server for money, never the client.** Prices, discounts, taxes, stock, and
  payment capture are computed and verified server-side. Treat client-sent totals as
  hints, never as truth.
- **Prefer the Store API for shopper-facing flows.** WooCommerce's `wc/store/v1` Store
  API is cart/nonce-based and designed for public frontends; the admin REST API
  (`wc/v3`) is for trusted server-to-server calls.
- **Payment goes through the gateway, on the server.** Never hold card data; use the
  gateway's client SDK for tokenization and confirm/capture from your backend — see
  payments.
- **Own SEO and rendering yourself.** No theme means no automatic meta, sitemaps, or
  canonical tags; render them in the frontend or you will deindex the store.

## Best Practices

- Split the two APIs by trust: **Store API** (`wc/store/v1`) for browsing and cart from
  the browser; **admin REST** (`wc/v3`) only from your server with a scoped key.
- Put a Backend-for-Frontend layer (Next.js Route Handler, serverless function) between
  browser and WooCommerce; validate and re-price every mutation there.
- Pass the Store API cart token / nonce through so the shopper's cart and totals are
  server-authoritative; do not compute the payable amount in React.
- Cache read-heavy catalog data (products, categories) at the edge/CDN with short TTLs
  and revalidation; never cache authenticated cart or order responses.
- Render SEO essentials server-side (SSR/SSG): titles, meta description,
  `Product`/`Offer` structured data, canonical URLs, and a generated sitemap.
- Keep webhooks server-to-server: WooCommerce → your backend for order/payment events,
  with signature verification.

## Examples

**Good Example** — browser hits your BFF; secret stays server-side; price verified

```ts
// app/api/checkout/route.ts (Next.js server) — the key never reaches the browser.
export async function POST(req: Request) {
  const { cartToken } = await req.json();

  // Re-fetch the authoritative cart from the Store API using the shopper's token.
  const cart = await fetch("https://shop.example.com/wp-json/wc/store/v1/cart", {
    headers: { "Cart-Token": cartToken }, // server verifies contents & totals
  }).then((r) => r.json());

  // Trust WooCommerce's computed total, not any amount the client sent.
  const amount = cart.totals.total_price; // integer minor units from the Store API

  const intent = await stripe.paymentIntents.create({
    amount: Number(amount),
    currency: cart.totals.currency_code,
  });
  return Response.json({ clientSecret: intent.client_secret }); // no secret key exposed
}
```

**Bad Example** — write key in the browser, client-computed total

```tsx
// BAD: consumer secret shipped to every visitor in the bundle.
const WC = { key: "ck_live_abc", secret: "cs_live_xyz" }; // public the moment it loads

async function pay(cartItems) {
  // BAD: total computed in the browser — a user edits it in devtools and pays $0.01.
  const total = cartItems.reduce((s, i) => s + i.price * i.qty, 0);

  // BAD: browser writes the order directly with a write-scoped admin key.
  await fetch("https://shop.example.com/wp-json/wc/v3/orders", {
    method: "POST",
    headers: { Authorization: "Basic " + btoa(`${WC.key}:${WC.secret}`) },
    body: JSON.stringify({ total, set_paid: true }), // client declares itself paid
  });
}
```

## Common Mistakes

- Embedding a consumer key/secret (especially write-scoped) in frontend code.
- Computing prices, discounts, or the payable amount client-side and trusting it.
- Using the admin `wc/v3` API from the browser instead of the cart-aware Store API.
- Marking orders paid from the client instead of confirming payment on the server via
  the gateway/webhook.
- Forgetting SSR SEO, so the headless store ships empty meta tags and gets deindexed.
- Caching authenticated cart/customer responses at the CDN, leaking one shopper's data
  to another.

## Production Tips

- Keep the WooCommerce origin behind the BFF and, where possible, not publicly branded,
  to reduce direct-to-backend abuse; rate-limit the BFF.
- Verify webhook signatures and make order/payment handlers idempotent — networks retry.
- Monitor the two layers separately (frontend and WooCommerce) with shared correlation
  IDs so a failed checkout can be traced end to end.

## AI Review Checklist

- Does the browser talk only to your backend, with no WooCommerce secret in the bundle?
- Are prices, taxes, discounts, and the payable amount computed/verified server-side?
- Are shopper flows on the Store API (`wc/store/v1`) and admin operations on `wc/v3`
  server-side only?
- Is payment confirmed via the gateway/webhook on the server, not by a client "paid"
  flag?
- Are SEO essentials (meta, structured data, canonical, sitemap) server-rendered?
- Are authenticated responses excluded from shared/CDN caches?

## Related

- `knowledge/woocommerce/13-rest-api.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/08-payments.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/07-checkout.md`
