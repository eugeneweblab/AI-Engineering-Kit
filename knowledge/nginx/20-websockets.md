---
id: nginx/20-websockets
topic: nginx
slug: websockets
title: "Websockets"
type: doc
order: 20
status: ready
tags: [nginx, websockets, proxy_read_timeout, Connection, ip_hash, proxy_send_timeout, Upgrade, close]
related: [nginx/19-proxying-applications, nginx/05-reverse-proxy, nginx/18-performance, nginx/06-load-balancing, nginx/17-monitoring]
when_to_use: "Read before proxying a WebSocket, Socket.IO, or SSE connection through nginx."
---
# Websockets

## Purpose

This document defines how to proxy WebSocket connections through nginx. A WebSocket
starts as an HTTP request and then *upgrades* to a long-lived, bidirectional TCP
connection. nginx does not proxy that upgrade unless you tell it to explicitly. This
doc covers the upgrade handshake, the timeouts that keep idle sockets alive, and the
buffering settings that must be off for real-time traffic.

The general rules of [proxying applications](19-proxying-applications.md) still apply —
forward headers, set timeouts, bound the backend. WebSockets add three requirements on
top: pass the `Upgrade` handshake, use HTTP/1.1, and stop nginx from timing out or
buffering a connection that stays open for hours.

## Why It Matters

The WebSocket handshake fails silently by default. Without the upgrade headers, nginx
treats the request as ordinary HTTP, the `Connection: Upgrade` never reaches the backend,
and the client sees the socket close immediately with a 400 or an instant disconnect.
Once connected, the second trap is `proxy_read_timeout`: its default is 60 seconds, so a
correctly-upgraded socket that sits idle (a chat waiting for a message, a dashboard between
ticks) is killed after a minute and the client reconnect-storms. Both failures look like
an application bug when they are nginx configuration.

## Core Principles

- **The upgrade must be explicit.** nginx only forwards the WebSocket handshake when you
  set `proxy_set_header Upgrade` and `Connection`, and `proxy_http_version 1.1`. There is
  no default that does this.
- **Long-lived means long timeouts.** `proxy_read_timeout` and `proxy_send_timeout` bound
  idle time on the socket. A real-time connection needs them well above the default 60s.
- **Do not buffer a stream.** Buffering defeats the point of a real-time connection; nginx
  should pass frames through as they arrive.
- **Map the Connection header, do not hardcode it.** Use a `map` so ordinary requests on
  the same server still get connection reuse while upgrade requests get `Connection: upgrade`.
- **Sticky routing for stateful sockets.** If the backend keeps per-connection state and
  you load-balance, the client must reach the same node — use `ip_hash` or a sticky method.

## Best Practices

- Define a `map` from `$http_upgrade` to `$connection_upgrade` once in the `http` block,
  and reference it in every WebSocket location. This keeps `Connection: close` for
  non-upgrade requests and `Connection: upgrade` for handshakes.
- Set `proxy_http_version 1.1;` — WebSocket upgrade requires HTTP/1.1; HTTP/1.0 cannot
  carry it.
- Raise `proxy_read_timeout` and `proxy_send_timeout` to cover the longest expected idle
  gap (e.g. `3600s`), or send application-level pings and keep a shorter timeout.
- Keep `proxy_buffering` off for the WebSocket location so frames are not held.
- For Socket.IO and similar, proxy the dedicated path (`/socket.io/`) with the upgrade
  headers, and route it to the same upstream as its HTTP polling fallback.
- When load-balancing stateful sockets, use `ip_hash` or an explicit sticky-session module
  so reconnects land on the node holding the state. See [load balancing](06-load-balancing.md).

## Examples

**Good Example** — mapped upgrade, HTTP/1.1, long idle timeout

```nginx
# http block: derive the Connection header from the client's Upgrade request
map $http_upgrade $connection_upgrade {
    default upgrade;   # a real WebSocket handshake → Connection: upgrade
    ''      close;     # ordinary request → Connection: close (no dangling upgrade)
}

upstream ws_app { server 127.0.0.1:3000; }

server {
    location /ws/ {
        proxy_pass http://ws_app;

        proxy_http_version 1.1;                       # required to carry the upgrade
        proxy_set_header Upgrade    $http_upgrade;    # pass the client's Upgrade token
        proxy_set_header Connection $connection_upgrade;  # mapped, not hardcoded

        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_read_timeout 3600s;   # idle socket stays open for up to an hour
        proxy_send_timeout 3600s;
        proxy_buffering off;        # stream frames through, don't hold them
    }
}
```

**Bad Example** — no upgrade, default timeout kills idle sockets

```nginx
server {
    location /ws/ {
        proxy_pass http://127.0.0.1:3000;
        # no proxy_http_version 1.1 → HTTP/1.0 → upgrade impossible
        # no Upgrade / Connection headers → handshake never reaches backend, client gets 400
        # proxy_read_timeout defaults to 60s → idle chat socket dropped every minute,
        #   client reconnect-storms and looks like an app bug
    }
}
```

## Common Mistakes

- Omitting `proxy_http_version 1.1` and the `Upgrade`/`Connection` headers, so the
  handshake fails and the client cannot connect at all.
- Hardcoding `Connection "upgrade"` on a shared server, breaking keepalive for the normal
  HTTP requests on the same block — use the `map` instead.
- Leaving `proxy_read_timeout` at 60s, so idle connections drop and clients reconnect in a loop.
- Leaving `proxy_buffering on`, adding latency and memory to a real-time stream.
- Load-balancing stateful sockets round-robin, so a reconnect hits a node that has never
  seen the connection.
- Forgetting the same rules apply to SSE (`text/event-stream`): disable buffering and
  raise the read timeout there too.

## Production Tips

- Prefer application-level ping/pong (most WebSocket libraries send them) over a giant
  nginx timeout — it detects dead connections and lets you keep the timeout tighter.
- Monitor active connection counts (`stub_status` Active connections) — WebSockets hold a
  connection each, so they change your capacity math. See [monitoring](17-monitoring.md).
- If you terminate TLS at nginx, the client uses `wss://` to nginx and nginx proxies plain
  `ws://` to the backend — no extra config beyond the standard proxy headers.
- Watch for `upstream timed out` in the error log: it almost always means the read timeout
  is shorter than the socket's idle period.

## AI Review Checklist

- Is `proxy_http_version 1.1;` set on the WebSocket location?
- Are `Upgrade` and `Connection` headers forwarded, with `Connection` driven by a `map`?
- Are `proxy_read_timeout`/`proxy_send_timeout` raised well above the default 60s?
- Is `proxy_buffering off;` for the WebSocket (and SSE) location?
- If load-balanced and stateful, is sticky routing (`ip_hash` or equivalent) configured?
- Are the standard `Host`/`X-Forwarded-*` headers still forwarded?

## Related

- `knowledge/nginx/19-proxying-applications.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/18-performance.md`
- `knowledge/nginx/06-load-balancing.md`
- `knowledge/nginx/17-monitoring.md`
