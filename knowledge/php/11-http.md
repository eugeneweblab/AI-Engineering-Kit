---
id: php/11-http
topic: php
slug: http
title: "PHP HTTP"
type: doc
order: 11
status: ready
tags: [php, http]
related: [php/13-security, php/08-error-handling, php/24-psr-standards, php/10-files]
when_to_use: "Read before handling a request, building a response, or making an outbound HTTP call."
---
# PHP HTTP

## Purpose

This document defines how to handle inbound HTTP requests and produce responses in PHP,
and how to make safe outbound HTTP calls. It covers reading input, setting status codes
and headers, content types, and the PSR-7/PSR-15 abstractions that modern frameworks use.
Because every request is attacker-reachable, correct HTTP handling is inseparable from
[security](13-security.md); this doc focuses on the mechanics that make responses correct
and inputs safe.

## Why It Matters

HTTP is the boundary between your application and the internet. Everything in `$_GET`,
`$_POST`, `$_COOKIE`, `$_SERVER`, and the request body is untrusted and must be validated
before use. On the way out, a wrong status code misleads clients and monitoring, a missing
security header leaves a hole, and an unescaped value in the response body becomes XSS.
Getting HTTP right means treating input as hostile, output as needing correct headers and
status, and never sending headers after body content has started.

## Core Principles

- **All request data is untrusted.** Superglobals are raw attacker input. Validate type,
  range, and format; cast explicitly; never interpolate directly into SQL, HTML, shell,
  or file paths.
- **Set the status code deliberately.** The status line is the primary machine-readable
  outcome. Return 400 for bad input, 401/403 for auth, 404 for missing, 422 for
  unprocessable, 500 for unexpected — never 200 with an error body.
- **Headers before body, always.** `header()` and `http_response_code()` must be called
  before any output. A stray `echo`/whitespace before them causes "headers already sent".
- **Declare the content type and charset.** Send `Content-Type: application/json` or
  `text/html; charset=utf-8` so clients interpret the body correctly and safely.
- **Escape output for its context; never for HTML only.** JSON via `json_encode` with
  the right flags, HTML via `htmlspecialchars`. The response's safety depends on matching
  the encoding to the sink.

## Best Practices

- Prefer a PSR-7 request/response and PSR-15 middleware (via a framework or
  `nyholm/psr7` + a runner) over raw superglobals — immutable messages are testable and
  composable. Reserve raw `$_GET`/`header()` for tiny scripts.
- Validate and normalize input with `filter_input`/`filter_var` or a validation library;
  reject rather than sanitize-and-hope when input is malformed.
- Encode JSON with `json_encode($data, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE)` so
  encoding failures throw instead of silently returning `false`.
- Send baseline security headers: `Content-Security-Policy`, `X-Content-Type-Options:
  nosniff`, `Referrer-Policy`, and `Strict-Transport-Security` on HTTPS.
- For outbound calls use Guzzle or the PSR-18 client with an explicit timeout, TLS
  verification **on**, and no automatic following of redirects to internal hosts (SSRF).
- Read the raw body from `php://input` for JSON/APIs; do not rely on `$_POST`, which only
  populates for form encodings.

## Examples

**Good Example** — validated input, correct status, safe JSON

```php
<?php
declare(strict_types=1);

// Validate and coerce; a missing/invalid id is a client error, not a 500.
$id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);
if ($id === false || $id === null) {
    http_response_code(400);                                   // status set before output
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['error' => 'id must be an integer'], JSON_THROW_ON_ERROR);
    return;
}

$user = $repo->find($id);                                       // may throw -> handled globally

http_response_code(200);
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');                     // block MIME sniffing
echo json_encode($user, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE);
```

**Bad Example** — trusted input, wrong status, XSS

```php
<?php
$name = $_GET['name'];                     // raw, untrusted, unvalidated
echo "<h1>Hello $name</h1>";               // reflected XSS: <script> runs in the browser

$id = $_GET['id'];
$user = $repo->query("SELECT * WHERE id = $id"); // untrusted input into SQL (injection)
if (!$user) {
    echo 'not found';                      // HTTP 200 for a missing resource -> misleads
}
header('Content-Type: application/json');  // sent AFTER echo -> "headers already sent"
```

## Common Mistakes

- Using `$_GET`/`$_POST`/`$_SERVER` values directly in SQL, HTML, shell, or paths.
- Returning HTTP 200 for errors, so clients and monitoring cannot detect failure.
- Calling `header()`/`http_response_code()` after output has started.
- Echoing user input into HTML without `htmlspecialchars` (reflected XSS).
- Using `json_encode` without `JSON_THROW_ON_ERROR`, silently emitting `false`.
- Outbound requests with TLS verification disabled or unbounded timeouts.
- Trusting `Host`, `X-Forwarded-For`, or `Content-Type` headers as if they were verified.

## Production Tips

- Terminate TLS at the edge and set `Strict-Transport-Security`; redirect HTTP to HTTPS.
- Behind a proxy, only trust `X-Forwarded-*` from known proxy IPs — otherwise clients can
  spoof their address and defeat rate limiting.
- Add a correlation/request id header, propagate it to logs and downstream calls, and
  return it so support can trace a specific request.
- Set sane timeouts (`max_execution_time`, client timeouts) so a slow dependency cannot
  pin all workers.

## AI Review Checklist

- Is every value from a superglobal or the body validated/typed before use?
- Does each response set an explicit, correct status code (no 200-on-error)?
- Are status and headers set before any output is produced?
- Is HTML output escaped with `htmlspecialchars` and JSON encoded with `JSON_THROW_ON_ERROR`?
- Are baseline security headers (`nosniff`, CSP, HSTS) present?
- Do outbound calls have timeouts, TLS verification on, and SSRF protection?
- Are proxy headers (`X-Forwarded-*`, `Host`) trusted only from known sources?

## Related

- `knowledge/php/13-security.md`
- `knowledge/php/08-error-handling.md`
- `knowledge/php/24-psr-standards.md`
- `knowledge/php/10-files.md`
