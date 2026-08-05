---
id: security/100-common-antipatterns
topic: security
slug: common-antipatterns
title: "Security Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [security, common-antipatterns, Forbidden, send, price, isAdmin, userId, unsafe-inline]
related: [security/13-sql-injection, security/04-authorization, security/16-secrets-management, security/11-xss, security/28-owasp-top10]
when_to_use: "Read when writing or reviewing security-sensitive code, to recognize a dangerous pattern before it ships."
---
# Security Common Antipatterns

## Purpose

This document catalogs the recurring security antipatterns that AI agents and humans
reach for by default. Each entry names the pattern, explains *why it is wrong* in terms of
the attack it enables, and gives *the fix*. Recognizing the shape is the goal: once you can
name it, you can refuse it. These are the concrete failures behind the abstract principles
in the sibling docs.

## Why It Matters

Insecure code rarely looks insecure — it looks like the shortest path that makes the
feature work. Antipatterns are the shortcuts that pass review and demos while quietly
handing attackers the keys. Learning the pattern (not just the one-off fix) lets you catch
the next instance you have never seen before. The trade-off is discipline now versus a
breach later; the breach is always more expensive.

## Core Principles

- **Fix the pattern, not the instance.** If concatenated SQL appears once, search for all of it.
- **Insecure-by-default is the enemy.** Prefer APIs where the safe path is the easy path.
- **Trust nothing from the client** — not IDs, roles, prices, redirects, or content types.

## The Antipatterns

### 1. String-concatenated SQL

**Why it is wrong:** Interpolating input into a query string lets an attacker alter the
query's structure (`' OR 1=1 --`), reading or destroying the whole table. This is the
oldest and still most common critical bug.
**The fix:** Use parameterized queries / prepared statements or an ORM. The database
treats parameters as data, never as SQL. See [sql-injection](13-sql-injection.md).

### 2. Building shell commands from input

**Why it is wrong:** `exec("convert " + userFile)` lets `; rm -rf /` run with the app's
privileges. The shell interprets metacharacters you did not anticipate.
**The fix:** Call the program directly with an argument array (`execFile("convert",
[userFile])`) and no shell. Avoid `shell: true`. Validate the input regardless.

### 3. Trusting client-supplied authorization data

**Why it is wrong:** Reading `role`, `isAdmin`, `userId`, or `price` from the request body,
a JWT claim the client can set, or a hidden field lets anyone escalate by editing it. IDOR
and privilege escalation both live here.
**The fix:** Derive identity from the authenticated session server-side, and check
authorization against server-held data for *this specific object*. See
[authorization](04-authorization.md).

### 4. Homegrown crypto and password hashing

**Why it is wrong:** Custom ciphers, `sha256(password)`, ECB mode, or reused/static IVs
fail in ways you cannot see; the code "works" while being trivially reversible.
**The fix:** Use vetted libraries. Hash passwords with Argon2id/bcrypt; encrypt with an
authenticated mode (AES-GCM) via a maintained library. See [encryption](17-encryption.md).

### 5. Secrets in source, config, or logs

**Why it is wrong:** A key in the repo is public the moment the repo leaks, forks, or is
cloned to a laptop; git history keeps it forever. Logged tokens end up in log aggregators
and screenshots.
**The fix:** Load secrets from a secrets manager or injected env vars, scrub them from
logs, and rotate any that were ever committed. See [secrets-management](16-secrets-management.md).

### 6. Reflecting input into HTML unescaped

**Why it is wrong:** Writing user content straight into the DOM or a template executes
attacker script in the victim's session (XSS), stealing tokens and performing actions as them.
**The fix:** Context-aware output encoding, a framework that escapes by default, and a
strict CSP as defense in depth. Never `innerHTML` untrusted data. See [xss](11-xss.md).

### 7. Leaking internals in error responses

**Why it is wrong:** Stack traces, SQL text, and file paths in a 500 response map the
system for an attacker and often reveal versions and secrets.
**The fix:** Return a generic message and an opaque error id to clients; log the detail
server-side. Disable debug mode and source maps in production.

### 8. Failing open

**Why it is wrong:** `try { checkAuth() } catch { /* continue */ }` grants access when the
check errors — an attacker just needs to make the check fail.
**The fix:** Default deny. On any exception in a security decision, deny and log. The safe
state is "no access."

### 9. Leaky, timing-variable auth responses

**Why it is wrong:** Different messages or response times for "unknown user" vs "wrong
password" let an attacker enumerate valid accounts and target them.
**The fix:** One generic message, and run the hash comparison even when the user is missing
so timing is uniform. See [authentication](03-authentication.md).

### 10. Disabling security to make it work

**Why it is wrong:** `verify: false` on TLS, `CORS: *` on authenticated APIs, `csp:
unsafe-inline`, or `NODE_TLS_REJECT_UNAUTHORIZED=0` silences a warning by removing the
protection, and the setting survives into production.
**The fix:** Fix the root cause (install the right cert, list the real origins). Never
disable verification as a shortcut.

### 11. Unvalidated redirects and SSRF

**Why it is wrong:** Redirecting to a client-supplied URL enables phishing; fetching a
client-supplied URL server-side (SSRF) reaches internal metadata endpoints and services.
**The fix:** Allowlist redirect targets and outbound hosts; block private/link-local ranges
for server-side fetches.

## Examples

**Good** — parameterized, fails closed, generic error

```ts
try {
  const row = await db.query("SELECT * FROM users WHERE id = $1", [userId]); // param
  if (!row || row.orgId !== session.orgId) throw new Forbidden();            // default deny
  return row;
} catch (e) {
  log.error(e);              // detail stays server-side
  throw new Forbidden();     // fail closed, generic to client
}
```

**Bad** — every antipattern above, and it "works" in the demo

```ts
// concatenated SQL, no authz, fails open, leaks internals
const row = await db.query(`SELECT * FROM users WHERE id = ${req.query.id}`);
try { checkAuth(req); } catch { /* let it through */ }   // fails open
res.send(row ?? err.stack);                              // leaks stack trace
```

## Common Mistakes

- Patching the single reported instance while identical patterns remain elsewhere.
- Assuming an ORM or framework makes you immune — raw-query escape hatches reintroduce injection.
- Copying a "quick fix" from the web that disables a protection (`verify: false`).
- Believing input from another internal service is trusted; validate across every boundary.

## AI Review Checklist

- Does any query, command, or template build a string from untrusted input?
- Is any authorization decision based on client-supplied data?
- Are secrets present in source, config, or logs anywhere in the diff?
- Does the code fail closed, with generic client errors and detail logged server-side?
- Is any security control disabled (`verify: false`, `CORS: *`, `unsafe-inline`) as a shortcut?

## Related

- `knowledge/security/13-sql-injection.md`
- `knowledge/security/04-authorization.md`
- `knowledge/security/16-secrets-management.md`
- `knowledge/security/11-xss.md`
- `knowledge/security/28-owasp-top10.md`
