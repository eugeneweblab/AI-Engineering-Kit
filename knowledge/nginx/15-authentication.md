---
id: nginx/15-authentication
topic: nginx
slug: authentication
title: "Authentication"
type: doc
order: 15
status: ready
tags: [nginx, authentication]
related: [nginx/12-ssl-tls, nginx/13-security, nginx/05-reverse-proxy, nginx/14-rate-limiting]
when_to_use: "Read before adding basic auth, client-certificate, or forward/subrequest auth in nginx."
---
# Authentication

## Purpose

This document defines the authentication mechanisms nginx itself can enforce: HTTP
Basic auth, mutual TLS (client certificates), and delegated auth via `auth_request`
to an external identity service. It is written so an agent knows which mechanism fits
which job and how to wire each one without leaving a bypass.

nginx authenticates the *transport and the edge*, not the application's users. It is
excellent for protecting internal tools, staging sites, metrics endpoints, and mTLS
between services — and it should *delegate*, never reimplement, real user login.

## Why It Matters

Edge authentication is where teams most often build a false sense of safety. Basic auth
over plain HTTP sends the password in base64 on every request — readable by anyone on
the path. An `auth_request` wired to the wrong location protects the front door while
the API sits open beside it. A client-cert config with `optional` instead of `on`
accepts unauthenticated clients silently. Each mistake looks secured — the login prompt
appears, the config parses — while the resource is effectively public. Because nginx is
the gate, a gap here bypasses everything behind it.

## Core Principles

- **Never send credentials over plain HTTP.** Basic auth and mTLS require TLS first;
  otherwise the credential is on the wire in the clear. See [ssl-tls](12-ssl-tls.md).
- **nginx guards the edge; the app owns user identity.** Use nginx auth for operators,
  services, and internal endpoints — delegate real user login to an auth service.
- **Delegate with `auth_request`, do not reinvent.** Forward the credential to an
  identity service and let nginx allow/deny on its verdict. Do not parse JWTs by hand
  in config.
- **Require, do not merely request.** `ssl_verify_client on` rejects missing certs;
  `optional` lets them through. Verify the mode matches the intent.
- **Rate-limit and protect every auth surface.** An unthrottled Basic-auth endpoint is
  brute-forceable; pair auth with [rate-limiting](14-rate-limiting.md).

## Best Practices

- Put Basic auth behind HTTPS only; generate the file with `htpasswd` using bcrypt
  (`htpasswd -B`), never plain or crypt hashes, and keep it `root:nginx 0640`.
- Prefer `auth_request` to a dedicated auth service for anything user-facing — it
  centralizes logic, supports SSO/OIDC, and returns real identity headers to the app.
- For service-to-service traffic, use **mTLS** with `ssl_verify_client on` and a pinned
  `ssl_client_certificate` CA; pass the verified subject to the backend.
- Apply auth to the whole protected tree, including error and API subpaths — audit that
  no sibling `location` escapes it.
- Scrub inbound copies of your identity headers (e.g. `X-Auth-User`) so a client cannot
  forge them; set them only from nginx after verification.
- Return `401` with an appropriate `WWW-Authenticate` challenge for Basic; `403` when a
  presented credential is valid but not permitted.

## Examples

**Good Example** — delegated auth over TLS, forged headers stripped

```nginx
server {
    listen 443 ssl;                              # auth only over TLS
    server_name internal.example.com;

    # Verify each request against an auth service; it returns 200 (allow) or 401 (deny).
    location = /_auth {
        internal;                                # not reachable directly by clients
        proxy_pass http://authsvc/verify;
        proxy_pass_request_body off;             # only headers/cookies needed
        proxy_set_header Content-Length "";
        proxy_set_header X-Original-URI $request_uri;
    }

    location /admin/ {
        auth_request /_auth;                     # deny unless /_auth returns 2xx
        # Capture the verified identity and pass it on; never trust the client's copy.
        auth_request_set $user $upstream_http_x_user;
        proxy_set_header X-Auth-User $user;      # set by us, after verification
        proxy_pass http://app;
    }
}
```

**Bad Example** — Basic auth over HTTP, forgeable identity, optional certs

```nginx
server {
    listen 80;                                   # no TLS → password sent in the clear
    server_name internal.example.com;

    location /admin/ {
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;   # base64 creds on every plain request
        # Passes the client's own X-Auth-User straight through → trivially forged.
        proxy_set_header X-Auth-User $http_x_auth_user;
        proxy_pass http://app;
    }

    location /admin/api/ {
        # Sibling path with NO auth_basic → the "protected" API is wide open.
        proxy_pass http://app;
    }
}
```

## Common Mistakes

- Enabling Basic auth or mTLS on a `listen 80` server, exposing credentials in the clear.
- Storing `htpasswd` entries with weak (crypt/MD5) hashes instead of bcrypt.
- Protecting one `location` but leaving a sibling API/error path unauthenticated.
- Passing the client's identity header (`X-Auth-User`) through instead of setting it
  after verification — the client forges whoever it wants.
- `ssl_verify_client optional` where `on` was intended, silently admitting anonymous clients.
- Reimplementing token/JWT validation in nginx config instead of delegating to a service.
- No rate limiting on the auth endpoint, leaving it brute-forceable.

## Production Tips

- Return the verified user/roles from the auth service as headers and log them, so every
  request is attributable.
- Cache `auth_request` verdicts briefly when the auth service is a bottleneck, but keep
  the TTL short so revocation is fast.
- For mTLS, monitor client-cert expiry the same way you monitor server certs — an expired
  client cert is a silent service outage.
- Keep the `htpasswd`/CA files out of the image and repo; mount them as secrets.

## AI Review Checklist

- Is every auth mechanism served only over HTTPS (never `listen 80`)?
- Are identity headers set by nginx after verification and stripped from client input?
- Does the protected tree cover all subpaths, with no unauthenticated sibling `location`?
- For mTLS, is `ssl_verify_client on` (not `optional`) with a pinned client CA?
- Is user-facing auth delegated via `auth_request`, not hand-rolled in config?
- Are `htpasswd` hashes bcrypt, and the file access-restricted and out of the repo?
- Is the auth endpoint rate-limited?

## Related

- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/14-rate-limiting.md`
