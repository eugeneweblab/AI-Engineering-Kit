---
id: nginx/00-overview
topic: nginx
slug: overview
title: "Nginx Overview"
type: doc
order: 0
status: ready
tags: [nginx, overview]
related: [nginx/01-installation, nginx/02-configuration, nginx/03-server-blocks, nginx/05-reverse-proxy, nginx/13-security]
when_to_use: "Read first when starting any nginx task to find the right doc for the job."
---
# Nginx Overview

## Purpose

This document orients an agent to the nginx topic: what nginx is, the mental model
of how it processes a request, and which doc in this topic to open for a given task.
It is a map, not a tutorial. Read it first, then jump to the specific doc you need.

Nginx is an event-driven HTTP server, reverse proxy, and load balancer. Unlike a
thread-per-connection server, a single worker handles thousands of concurrent
connections with a non-blocking event loop, which is why it stays fast under load.

## Why It Matters

Nginx usually sits at the edge of the system — the first thing a client touches and
the last line of defense before your application. A mistake here is a production-wide
mistake: a misordered `location`, a missing `proxy_set_header`, or a wildcard TLS
gap affects every request, not one endpoint. Config errors are also easy to ship,
because nginx will happily start with a subtly wrong (but syntactically valid) config.
Getting the fundamentals right prevents outages, broken redirects, and silent
security holes.

## Core Principles

- **Configuration is declarative and directional.** Directives inherit from outer
  contexts (`http` -> `server` -> `location`) unless overridden. Know the context a
  directive lives in before you write it.
- **The request pipeline is ordered.** nginx picks one `server` block, then one
  `location`, then applies directives. Understanding selection order prevents most bugs.
- **Validate before you reload.** `nginx -t` catches syntax errors; a graceful
  `reload` applies config without dropping connections. Never restart blindly in prod.
- **Explicit beats implicit.** Set headers, timeouts, and buffer sizes deliberately.
  Defaults are conservative and often wrong for proxying real applications.

## Best Practices

- Start from [installation](01-installation.md) to get a supported, current build,
  then learn the file layout and directive model in [configuration](02-configuration.md).
- Model each site or hostname as a [server block](03-server-blocks.md); route paths
  within it using [location blocks](04-location-blocks.md).
- Put an application behind a [reverse proxy](05-reverse-proxy.md), and scale it with
  [load balancing](06-load-balancing.md).
- Treat [SSL/TLS](12-ssl-tls.md), [security](13-security.md), and
  [rate limiting](14-rate-limiting.md) as required, not optional, for any public site.
- Before shipping, walk the [production checklist](98-production-checklist.md).

## How The Docs Fit Together

- **Foundations** — [installation](01-installation.md),
  [configuration](02-configuration.md): get nginx running and understand its config model.
- **Request routing** — [server blocks](03-server-blocks.md),
  [location blocks](04-location-blocks.md): decide which config handles a request.
- **Serving traffic** — [reverse proxy](05-reverse-proxy.md),
  [load balancing](06-load-balancing.md), [static files](07-static-files.md),
  [caching](08-caching.md), [compression](09-compression.md): move bytes efficiently.
- **Protocols** — [HTTP/2](10-http2.md), [HTTP/3](11-http3.md),
  [SSL/TLS](12-ssl-tls.md): modern transport and encryption.
- **Hardening** — [security](13-security.md), [rate limiting](14-rate-limiting.md),
  [authentication](15-authentication.md): protect the edge.
- **Operations** — [logging](16-logging.md), [monitoring](17-monitoring.md),
  [performance](18-performance.md), [debugging](24-debugging.md),
  [production](25-production.md), [troubleshooting](29-troubleshooting.md): run it well.

## Common Mistakes

- Reading a middle doc without the config model, then misplacing directives by context.
- Assuming nginx serves an application directly; most real traffic is proxied.
- Editing config and restarting without running `nginx -t` first.
- Copying a config from the internet without understanding `location` match order or
  which `proxy_set_header` lines are load-bearing.

## AI Review Checklist

- Did you open the specific doc for the task, not just this overview?
- Do you know which context (`http`, `server`, `location`) each directive belongs in?
- Is the config validated with `nginx -t` before reload?
- For public traffic, are TLS, security headers, and rate limiting addressed?

## Related

- `knowledge/nginx/01-installation.md`
- `knowledge/nginx/02-configuration.md`
- `knowledge/nginx/03-server-blocks.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/13-security.md`
