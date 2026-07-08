---
id: php/13-security
topic: php
slug: security
title: "Security"
type: doc
order: 13
status: ready
tags: [php, security]
related: [php/12-database, php/11-http, php/08-error-handling, php/27-production]
when_to_use: "Read before writing or reviewing PHP that handles user input, passwords, output rendering, file uploads, or secrets."
---
# Security

## Purpose

This document defines the security rules specific to writing PHP: how to neutralize
injection, escape output, hash passwords, protect sessions, guard against CSRF, and
handle secrets and uploads. It is scoped to *language- and runtime-level* mistakes an
agent can make in PHP code. Cross-cutting topics like authentication protocols and
authorization models live in the `security` topic and are referenced where relevant.

## Why It Matters

PHP powers a large share of the public web, which makes its applications the most
attacked. The language makes insecure code easy to write: strings concatenate into SQL
and HTML without complaint, `extract()` and dynamic includes turn input into control
flow, and a forgotten escape renders attacker markup verbatim. Every one of these
compiles, runs, and passes a happy-path test. The gap between "works" and "safe" is
exactly the input you did not try, and an attacker's entire job is to find it.

## Core Principles

- **Treat all input as hostile.** Query strings, headers, cookies, JSON bodies, uploaded
  filenames, and environment values are attacker-controlled until validated.
- **Escape at the boundary, for the destination.** SQL, HTML, shell, and URLs each need
  their own encoding. Escaping once, generically, is wrong for every specific context.
- **Never build code or queries from input.** No `eval`, no variable-variable dispatch,
  no `include $_GET[...]`, no shell string built from user data.
- **Hash passwords; never encrypt or store them.** Use PHP's password API, which chooses
  and versions a slow algorithm for you.
- **Fail closed and stay quiet.** On error, deny the action and return a generic message;
  detailed errors belong in server logs, not in responses.

## Best Practices

- Prevent SQL injection with bound PDO parameters (see database doc); never interpolate.
- Escape HTML output with `htmlspecialchars($v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')`,
  or use a template engine (Twig, Blade) that auto-escapes. Escape at render, per field.
- Hash passwords with `password_hash($pw, PASSWORD_DEFAULT)` and verify with
  `password_verify()`. Re-hash on login when `password_needs_rehash()` returns true.
- Validate and normalize input with `filter_var()` (e.g. `FILTER_VALIDATE_EMAIL`,
  `FILTER_VALIDATE_INT`) or a schema; reject rather than sanitize where you can.
- Send a strict `Content-Security-Policy`, plus `X-Content-Type-Options: nosniff` and a
  `Referrer-Policy`. CSP is the backstop when an escape is missed.
- Protect state-changing requests with a per-session CSRF token; compare it with
  `hash_equals()` (constant-time), never `==`.
- Set session cookies with `session.cookie_httponly`, `session.cookie_secure`, and
  `session.cookie_samesite=Lax`; call `session_regenerate_id(true)` on privilege change.
- For file uploads, validate the real MIME type, generate your own filename, store
  outside the web root, and never trust the client-supplied name or extension.
- Compare secrets, tokens, and MACs with `hash_equals()` to avoid timing side channels.
- Keep secrets in environment variables or a secrets manager; never commit them, never
  echo them, and disable `display_errors` in production.

## Examples

**Good Example** — hashing, escaping, and constant-time token check

```php
// Store a password: slow, salted, and self-upgrading over time.
$hash = password_hash($plain, PASSWORD_DEFAULT); // Argon2id/bcrypt, PHP picks + versions

// Verify a login and transparently upgrade weak legacy hashes.
if (password_verify($plain, $hash)) {
    if (password_needs_rehash($hash, PASSWORD_DEFAULT)) {
        $hash = password_hash($plain, PASSWORD_DEFAULT); // persist the stronger hash
    }
}

// Render user data into HTML, escaped for exactly this context.
echo htmlspecialchars($comment, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');

// Validate a CSRF token in constant time — length and content never leak via timing.
if (!hash_equals($_SESSION['csrf'], $request->post('csrf', ''))) {
    http_response_code(403);
    exit; // fail closed
}
```

**Bad Example** — reversible hash, raw output, forgeable check

```php
$hash = md5($plain);                 // fast, unsalted, reversible via rainbow tables
$_SESSION['pw'] = $hash;

echo "<p>$comment</p>";              // unescaped → stored/reflected XSS

if ($_SESSION['csrf'] == $_POST['csrf']) { // loose ==, timing-leaky, "0e..." collisions
    process();                             // and no check for a missing token at all
}
```

## Common Mistakes

- Hashing passwords with `md5`/`sha1`, or "encrypting" them with a reversible cipher.
- Echoing user input into HTML without `htmlspecialchars`, causing XSS.
- Comparing tokens or hashes with `==` — loose comparison treats `"0e123"` strings as
  equal and leaks length via timing. Always `hash_equals()`.
- `include`/`require` on a path derived from input, enabling local/remote file inclusion.
- Passing user data to `exec`/`shell_exec`/`system` without `escapeshellarg()`.
- Trusting `$_FILES['x']['type']` or the uploaded filename instead of inspecting content.
- Leaving `display_errors = On` in production, leaking paths, queries, and stack traces.
- Storing secrets in the repository or logging them "just for debugging".

## Production Tips

- Set `expose_php = Off`, `display_errors = Off`, and log to a file or aggregator.
- Add security headers at the edge/framework layer so no route can forget them.
- Keep PHP and every Composer dependency patched; run `composer audit` in CI to catch
  known-vulnerable packages before deploy.
- Rate-limit authentication and other abuse-prone endpoints; log security events
  (login failure, CSRF reject, upload reject) without logging the sensitive payload.

## AI Review Checklist

- Is every SQL value a bound parameter, with no string interpolation?
- Is all dynamic HTML output escaped with `htmlspecialchars` (or an auto-escaping engine)?
- Are passwords stored via `password_hash` and checked with `password_verify`?
- Are tokens, MACs, and secrets compared with `hash_equals`, never `==`?
- Are state-changing routes protected by a CSRF token and correct cookie flags?
- Are file uploads renamed, content-checked, and stored outside the web root?
- Is any `include`/`eval`/`exec` path free of unvalidated user input?
- Is `display_errors` off and are secrets sourced from the environment?

## Related

- `knowledge/php/12-database.md`
- `knowledge/php/11-http.md`
- `knowledge/php/08-error-handling.md`
- `knowledge/php/27-production.md`
