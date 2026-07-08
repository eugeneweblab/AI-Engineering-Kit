---
id: nodejs/09-http
topic: nodejs
slug: http
title: "HTTP"
type: doc
order: 9
status: ready
tags: [nodejs, http]
related: [nodejs/06-streams, nodejs/16-error-handling, nodejs/18-security, nodejs/26-deployment, nodejs/08-events]
when_to_use: "Read before writing a Node HTTP server or making outbound HTTP requests from a service."
---
# HTTP

## Purpose

This document defines how to build HTTP servers and clients in Node.js safely: reading
requests without buffering unbounded data, always sending a response, setting timeouts,
reusing connections, and shutting down gracefully. It is written so an agent can build an
HTTP service that survives slow clients, malformed input, and deploys without dropping
requests.

It covers the core `node:http`/`node:https` primitives and the modern `fetch` client. The
principles apply whether you use raw `http`, a framework (Express, Fastify), or `undici`.

## Why It Matters

An HTTP server is exposed to the open internet, so every failure mode is adversarial.
Request bodies are streams: read them naively into a string and a single large or slow
request exhausts memory or ties up a connection indefinitely (Slowloris). Miss one code
path that never calls `res.end()` and that request hangs until timeout, holding a socket.
On the client side, a missing timeout means one stuck upstream cascades into your whole
service hanging. And a deploy that kills the process mid-request returns 502s to real
users. Correct HTTP is mostly about the un-happy paths: limits, timeouts, and cleanup.

## Core Principles

- **Always end the response, on every path.** Every request must reach exactly one
  `res.end()` (or framework equivalent), including error and early-return branches, or the
  connection hangs.
- **Treat the request body as a hostile stream.** Enforce a maximum size and reject when it
  is exceeded; never accumulate an unbounded body in memory.
- **Set timeouts on both sides.** Servers need `requestTimeout`/`headersTimeout`; clients
  need a request timeout / `AbortSignal`. A request without a deadline is a hang waiting to
  happen.
- **Reuse connections with a keep-alive agent.** Creating a new TCP+TLS connection per
  outbound request is slow and exhausts ports under load.
- **Shut down gracefully.** On `SIGTERM`, stop accepting new connections, let in-flight
  requests finish, then exit — so deploys do not drop traffic.

## Best Practices

- Prefer `undici`/global `fetch` for clients; it pools connections and supports
  `AbortSignal` timeouts natively. Pass `signal: AbortSignal.timeout(ms)`.
- Stream request and response bodies with `pipeline` rather than buffering; enforce a body
  cap (framework body-limit option, or count bytes and `destroy()` on overflow).
- Validate and normalize inputs (method, content-type, JSON shape) before acting; return
  `4xx` for bad input, `5xx` only for server faults.
- Set explicit status codes and never reflect untrusted input into headers (header
  injection / response splitting).
- Configure `server.requestTimeout`, `server.headersTimeout`, and `server.keepAliveTimeout`
  rather than relying on defaults for your traffic profile.
- Put an `'error'` handler on the server and on each request/response stream; a socket error
  must not crash the process.

## Examples

**Good Example** — bounded body, guaranteed response, client timeout

```js
import { createServer } from "node:http";

const MAX_BODY = 1_000_000; // 1 MB cap; reject anything larger

const server = createServer((req, res) => {
  let size = 0;
  const chunks = [];
  req.on("data", (c) => {
    size += c.length;
    if (size > MAX_BODY) {
      res.writeHead(413).end("Payload Too Large"); // always end the response
      req.destroy();                                // stop reading the hostile stream
      return;
    }
    chunks.push(c);
  });
  req.on("end", () => res.writeHead(200).end("ok"));
  req.on("error", () => res.writeHead(400).end()); // socket error → respond, don't crash
});
server.requestTimeout = 30_000; // no request may hang forever

async function callUpstream(url) {
  // AbortSignal.timeout guarantees the request cannot hang the caller indefinitely.
  return fetch(url, { signal: AbortSignal.timeout(5_000) });
}
```

**Bad Example** — unbounded body, no timeout, path that never responds

```js
import { createServer } from "node:http";

const server = createServer((req, res) => {
  let body = "";
  req.on("data", (c) => (body += c)); // unbounded: a big/slow client exhausts memory
  req.on("end", () => {
    if (!isValid(body)) return;       // early return never calls res.end() → hangs
    res.end("ok");
  });
  // No requestTimeout, no 'error' handler: Slowloris pins connections; one reset crashes.
});

async function callUpstream(url) {
  return fetch(url); // no timeout: a stuck upstream hangs this request forever
}
```

## Common Mistakes

- A branch (validation failure, early return, thrown error) that never calls `res.end()`,
  leaving the request hanging until timeout.
- Accumulating the request body into a string/array with no size limit, enabling memory
  exhaustion.
- Outbound requests with no timeout or `AbortSignal`, so a slow upstream hangs your service.
- Creating a fresh connection per outbound call instead of reusing a keep-alive pool,
  exhausting ephemeral ports under load.
- Reflecting untrusted input into response headers, enabling header injection.
- No graceful shutdown, so every deploy returns 502s for in-flight requests.

## Production Tips

- On `SIGTERM`: `server.close()` to stop new connections, track in-flight requests, force
  a hard exit after a grace deadline (e.g. 10s) so a stuck request cannot block the deploy.
- Put the Node service behind a reverse proxy/load balancer for TLS termination and a first
  layer of timeout and rate limiting, but do not rely on it alone — set Node's timeouts too.
- Emit structured access logs with method, path, status, duration, and a request id; alert
  on p99 latency and 5xx rate.

## AI Review Checklist

- Does every request path — including errors and early returns — end the response exactly
  once?
- Is the request body size-capped and streamed, never accumulated unbounded?
- Are server timeouts (`requestTimeout`, `headersTimeout`) and client timeouts
  (`AbortSignal`) set?
- Do outbound requests reuse a keep-alive/pooled connection?
- Is untrusted input kept out of response headers?
- Is there a `SIGTERM` graceful-shutdown path that drains in-flight requests?

## Related

- `knowledge/nodejs/06-streams.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/26-deployment.md`
- `knowledge/nodejs/08-events.md`
