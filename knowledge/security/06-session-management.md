---
id: security/06-session-management
topic: security
slug: session-management
title: "Session Management"
type: doc
order: 6
status: ready
tags: [security, session-management, HttpOnly, login, SameSite, Secure, localStorage, clearCookie]
related: [security/03-authentication, security/04-authorization, security/07-jwt, security/12-csrf, security/11-xss]
when_to_use: "Read before building or reviewing how a login is remembered across requests — cookies, tokens, or server sessions."
---
# Session Management

## Purpose

This document defines how to keep a user authenticated across requests after login:
issuing a session, storing it safely in the browser, expiring it, and revoking it.
[Authentication](03-authentication.md) proves identity once; session management is what
carries that proof to every subsequent request without asking for the password again.

## Why It Matters

The session identifier *is* the user for the life of the session. Whoever holds it is
logged in — no password required. That makes the session token a bearer credential as
sensitive as the password itself, but one that travels on every request and lives in
the browser where XSS can reach it. Steal it (via XSS, a network sniff, or a fixation
trick) and you have the account. Sessions also outlive the moment of login, so
revocation and expiry are what limit the damage when a device is lost or a token leaks.

## Core Principles

- **Session tokens are unguessable secrets.** Generate them from a CSPRNG with ≥128 bits
  of entropy. Never derive them from the user id, a counter, or a timestamp.
- **Rotate the identifier on every privilege change.** Issue a fresh session id at login
  and on role elevation, and discard the old one — this defeats session fixation, where
  an attacker plants a known id before you log in.
- **Bind the token to a secure transport and keep it off script.** Deliver it in a
  cookie that is `HttpOnly` (JS cannot read it → XSS cannot steal it), `Secure` (HTTPS
  only), and `SameSite` (blunts CSRF).
- **Sessions must be revocable and expiring.** Support server-side invalidation so
  logout actually ends the session, plus an idle timeout and an absolute maximum
  lifetime. A session that cannot be revoked is a permanent key.
- **Fail closed on any doubt.** A missing, expired, malformed, or unknown session is
  unauthenticated — never a fallback to "guest with elevated rights".

## Best Practices

- Prefer **opaque server-side session ids** (a random id keyed to server state) for
  browser apps: they are trivially revocable and carry no data to tamper with. If you
  use stateless [JWTs](07-jwt.md) instead, add a revocation list or keep lifetimes very
  short — you cannot un-issue a JWT.
- Set cookies: `HttpOnly; Secure; SameSite=Lax` (use `Strict` for high-value apps),
  `Path=/`, and a `__Host-` prefix to lock them to the exact host. Do **not** store
  session tokens in `localStorage` — any XSS reads it.
- Enforce two timeouts: a short **idle** timeout (e.g. 15–30 min) that slides on
  activity, and an **absolute** timeout (e.g. 8–24 h) that does not, capping token
  lifetime even for active sessions.
- On logout, delete the server-side session *and* clear the cookie — do not merely
  redirect. Provide "log out all devices" for account recovery.
- Pair sessions with CSRF defense (SameSite plus a synchronizer/double-submit token) —
  cookies are sent automatically, so the session alone does not prove intent. See
  [CSRF](12-csrf.md).
- Regenerate the session and re-prompt for step-up auth before sensitive actions
  (changing email, password, or payment details).

## Examples

**Good Example** — CSPRNG id, hardened cookie, rotate on login, real logout

```ts
import crypto from "crypto";

async function login(res, user) {
  const sid = crypto.randomBytes(32).toString("base64url"); // 256 bits, unguessable
  await sessions.destroyFor(user.id);                       // rotate: drop old sessions
  await sessions.create({ sid, userId: user.id, absExpiry: hours(12), idleExpiry: mins(30) });

  res.cookie("__Host-sid", sid, {
    httpOnly: true,   // XSS cannot read it
    secure: true,     // HTTPS only
    sameSite: "lax",  // blunts CSRF
    path: "/",
  });
}

async function logout(req, res) {
  await sessions.destroy(req.sid); // server-side invalidation, not just a redirect
  res.clearCookie("__Host-sid");
}
```

**Bad Example** — guessable token in localStorage, never expires or rotates

```ts
function login(user) {
  // Predictable, forgeable "token"; no entropy, no server record to revoke.
  const token = btoa(`${user.id}:${Date.now()}`);
  // Readable by any XSS; sent to no HttpOnly cookie; lives forever.
  localStorage.setItem("session", token);
  // No rotation on login → fixation; no expiry → a leak is permanent.
}
```

## Common Mistakes

- Storing the session token in `localStorage`/`sessionStorage`, exposing it to XSS.
- Predictable or low-entropy session ids (user id, counter, timestamp).
- Never rotating the id at login → session fixation.
- Cookies missing `HttpOnly`, `Secure`, or `SameSite`.
- No idle or absolute timeout, so tokens live indefinitely.
- "Logout" that only redirects and leaves the session valid server-side.
- Stateless JWT sessions with no revocation path and long lifetimes.
- No CSRF protection on cookie-based sessions.

## Production Tips

- Store sessions where you can revoke fast (Redis/DB) and expire keys with a TTL that
  matches the absolute timeout.
- Record device/IP with each session and surface active sessions to users, with a
  "revoke" control — essential for account-takeover recovery.
- Invalidate all sessions on password reset, email change, or suspected compromise.
- Alert on many sessions from one account across distant IPs (possible token theft).

## AI Review Checklist

- Are session ids generated from a CSPRNG with ≥128 bits of entropy?
- Is the id rotated on login and privilege change (no fixation)?
- Are session cookies `HttpOnly`, `Secure`, and `SameSite`, and kept out of `localStorage`?
- Are both idle and absolute timeouts enforced?
- Does logout invalidate the session server-side, not just clear the client?
- Are cookie-based sessions protected against CSRF?
- If JWTs are used, is there a revocation strategy or a short lifetime?

## Related

- `knowledge/security/03-authentication.md`
- `knowledge/security/04-authorization.md`
- `knowledge/security/07-jwt.md`
- `knowledge/security/12-csrf.md`
- `knowledge/security/11-xss.md`
