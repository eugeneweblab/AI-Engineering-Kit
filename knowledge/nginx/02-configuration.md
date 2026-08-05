---
id: nginx/02-configuration
topic: nginx
slug: configuration
title: "Nginx Configuration"
type: doc
order: 2
status: ready
tags: [nginx, configuration, location, reload, restart, try_files, server, stream]
related: [nginx/03-server-blocks, nginx/04-location-blocks, nginx/00-overview, nginx/24-debugging, nginx/26-best-practices]
when_to_use: "Read before editing nginx.conf, adding include files, or reasoning about directive inheritance."
---
# Nginx Configuration

## Purpose

This document defines nginx's configuration model: the context hierarchy, how
directives inherit, how files are organized with `include`, and the validate-then-
reload workflow. An agent that understands this places every directive in the right
context and never breaks a running server on reload.

## Why It Matters

Nginx config is deceptively simple to write and easy to get subtly wrong. A directive
in the wrong context is either ignored or rejected; an inherited directive you forgot
about silently changes behavior in a nested block. Worse, nginx will start with any
*syntactically* valid config, so a logic error ships to production and only surfaces as
a broken request later. The validate-before-reload discipline is what separates a safe
change from an outage.

## Core Principles

- **Directives live in contexts.** `main` -> `events` -> `http` -> `server` ->
  `location` (plus `stream`, `upstream`). A directive is only legal in specific
  contexts; putting it elsewhere is an error or a no-op.
- **Inheritance flows inward, and is all-or-nothing per directive.** A child context
  inherits a directive from its parent *until* it sets that directive itself — at which
  point it fully replaces the parent value, it does not merge.
- **Validate, then reload — never restart to apply changes.** `nginx -t` proves the
  config parses; `nginx -s reload` swaps workers gracefully without dropping live
  connections. A restart drops them.
- **Structure for humans.** Split large configs into `include` files (one site per
  file) so changes are reviewable and blast radius is contained.

## Best Practices

- Keep `nginx.conf` thin: global settings plus `include` of `conf.d/*.conf` and/or
  `sites-enabled/*`. Put one `server` block per file.
- Always run `nginx -t` (or `nginx -T` to also dump the effective config) before reload.
  Wire this into CI and into your deploy script as a gate.
- Reload with `nginx -s reload` or `systemctl reload nginx`; reserve restart for binary
  upgrades. The cost of a restart is dropped in-flight requests.
- Set values explicitly at the highest context where they belong, and override only
  where needed — this makes inheritance predictable.
- Use variables (`$host`, `$request_uri`, custom `map` blocks) instead of duplicating
  literals. Prefer `map` over long `if` chains; `if` inside `location` is treacherous.
- Comment *why*, not *what* — the directive name says what; reviewers need the reason.

## Examples

**Good Example** — clear contexts, includes, validated reload

```nginx
# /etc/nginx/nginx.conf
user  nginx;
worker_processes  auto;              # one worker per CPU core

events { worker_connections 4096; }  # per-worker connection cap

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    sendfile      on;                # kernel-level file send, set once and inherited

    include /etc/nginx/conf.d/*.conf;  # one server block per file, reviewable
}
# Apply:  nginx -t && nginx -s reload   (validate first, then graceful reload)
```

**Bad Example** — wrong context, blind restart

```nginx
events {
    sendfile on;   # WRONG context: sendfile is an http directive, nginx -t rejects this
}

http {
    server {
        gzip on;   # fine here, but...
        location /api {
            # forgot gzip is inherited; toggling it here would REPLACE, not merge, parent config
        }
    }
}
# Applied with:  systemctl restart nginx   # drops every in-flight connection unnecessarily
```

## Common Mistakes

- Placing a directive in the wrong context and assuming it took effect.
- Expecting inherited directives to merge; a child that sets the directive replaces it.
- Reloading (or restarting) without running `nginx -t`, shipping a broken config.
- Using `restart` for a routine change, dropping live connections.
- Overusing `if` inside `location`; many combinations behave unexpectedly — use `map`,
  `try_files`, or `return` instead.
- One giant `nginx.conf` that no one can review safely.

## Production Tips

- `nginx -T` prints the fully-resolved config with all includes — use it to debug
  "which value actually applied?" questions. See [debugging](24-debugging.md).
- Keep config in version control; every prod change is a reviewed commit.
- Test config in a container or staging host before reloading production.
- Set `worker_processes auto` and size `worker_connections` to your load, not defaults.

## AI Review Checklist

- Is every directive in a context where it is legal and takes effect?
- Does any nested block rely on inheritance that a sibling directive silently overrides?
- Is `nginx -t` run before every reload, in both deploy scripts and CI?
- Are changes applied with `reload`, not `restart`, unless upgrading the binary?
- Is the config split into reviewable includes rather than one monolith?
- Are `if`-in-`location` blocks replaced with `map`/`try_files`/`return` where possible?

## Related

- `knowledge/nginx/03-server-blocks.md`
- `knowledge/nginx/04-location-blocks.md`
- `knowledge/nginx/00-overview.md`
- `knowledge/nginx/24-debugging.md`
- `knowledge/nginx/26-best-practices.md`
