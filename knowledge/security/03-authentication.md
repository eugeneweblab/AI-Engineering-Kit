---
id: security/03-authentication
topic: security
slug: authentication
title: "Security Authentication"
type: doc
order: 3
status: ready
tags: [security, authentication]
related: [backend/10-authentication, security/04-authorization, security/05-password-security, security/06-session-management, security/07-jwt, security/21-rate-limiting]
when_to_use: "Read before building or reviewing any login, signup, session, or credential-handling code."
---
# Security Authentication

## Purpose

This document defines how to verify *who* a user is: login, credential storage,
sessions, tokens, and multi-factor authentication. It is written so an agent can
implement or review an authentication flow without introducing a security hole.

Authentication answers "are you who you claim to be?". It is distinct from
[authorization](04-authorization.md) ("are you allowed to do this?"). Do not conflate
them — a correct auth system gets both right, in that order.

This document owns the **policy**: what is stored, what is compared, what a response may
reveal. Where those rules attach inside a service — which middleware verifies the token, how
identity travels through the layers, what happens at a service boundary — is
[Backend Authentication](../backend/10-authentication.md).

## Why It Matters

Authentication is the front door of the system. A single mistake here — a timing leak,
a weak hash, a forgeable token — compromises every user at once, not just one request.
These bugs are silent: the app keeps working perfectly while attackers walk in. Because
the blast radius is total and the failure is invisible, authentication code is held to a
higher bar than ordinary application code. Assume every input is hostile.

## Core Principles

- **Never invent your own crypto or auth scheme.** Use vetted libraries and standard
  protocols (OAuth 2.1, OIDC, WebAuthn). Custom schemes fail in ways you cannot see.
- **Store proof, not secrets.** Never store passwords; store a slow one-way hash. Never
  log credentials, tokens, or session IDs.
- **Fail closed.** If verification cannot complete, deny access. An error is not a pass.
- **Make responses uniform.** The system must behave identically whether an account
  exists or not — same message, same timing. Differences leak valid accounts.
- **Bind identity to a session, re-check it every request.** Authentication is not a
  one-time event; every request must carry provable identity.

## Best Practices

- Hash passwords with a memory-hard algorithm — **Argon2id** (preferred) or **bcrypt** —
  with per-user salt. Never use MD5, SHA-1, or plain SHA-256 for passwords.
- Compare secrets with **constant-time** comparison to avoid timing attacks.
- Enforce rate limiting and account lockout (with backoff) on login and MFA endpoints.
- Return one generic error for bad credentials: *"Invalid email or password."* Never
  reveal which field was wrong.
- Regenerate the session identifier on every privilege change (login, logout, role
  change) to prevent session fixation.
- Set session cookies `HttpOnly`, `Secure`, and `SameSite=Lax` (or `Strict`). Keep
  tokens out of `localStorage` — it is readable by any XSS.
- Offer MFA (TOTP or WebAuthn) and require it for administrative accounts.
- Expire sessions: short idle timeout plus an absolute maximum lifetime. Support
  server-side revocation (logout must actually end the session).
- Treat signup, password reset, and "remember me" as authentication surfaces — same
  rigor applies.

## Examples

**Good Example** — slow hash, generic error, constant-time path

```ts
import argon2 from "argon2";

async function verifyLogin(email: string, password: string) {
  const user = await users.findByEmail(email);

  // Always run a hash comparison, even when the user is missing, so response
  // time does not reveal whether the account exists.
  const hash = user?.passwordHash ?? DUMMY_HASH;
  const ok = await argon2.verify(hash, password);

  if (!user || !ok) {
    throw new AuthError("Invalid email or password."); // one message for both cases
  }
  await session.regenerate(user.id); // new session id on login
  return user;
}
```

**Bad Example** — leaks account existence, fast reversible hash

```ts
async function verifyLogin(email: string, password: string) {
  const user = await users.findByEmail(email);
  if (!user) throw new Error("No account with that email"); // leaks valid emails
  if (user.passwordHash !== sha256(password)) {             // fast + reversible
    throw new Error("Wrong password");                      // confirms email is valid
  }
  return user; // session id never rotated → fixation
}
```

## Common Mistakes

- Using a fast or reversible hash (SHA-256, encryption) for passwords.
- Different error messages or response times for "unknown user" vs "wrong password".
- Storing session tokens or JWTs in `localStorage`, exposing them to XSS.
- Never rotating the session ID, enabling session fixation.
- Trusting a JWT without verifying its signature, algorithm, issuer, and expiry.
- No rate limiting, so credential-stuffing and brute-force run unchecked.
- Building a bespoke SSO/OAuth flow instead of using a compliant library.

## Production Tips

- Log authentication *events* (success, failure, lockout, MFA) with user id and IP —
  never the credentials themselves. Alert on spikes in failures.
- Support forced logout / session revocation for incident response.
- Rotate signing keys on a schedule and keep them in a secrets manager, not in code.
- Test the negative paths in CI: wrong password, unknown user, expired session,
  tampered token, replayed token.

## AI Review Checklist

- Are passwords hashed with Argon2id or bcrypt, with a per-user salt?
- Is the response identical (message and timing) for unknown-user and wrong-password?
- Are sessions regenerated on login and revocable on logout?
- Are tokens stored in `HttpOnly` cookies, not `localStorage`?
- Are login and MFA endpoints rate-limited and lockout-protected?
- Are JWT signature, algorithm, issuer, and expiry all verified before trust?
- Is authentication clearly separated from [authorization](04-authorization.md)?

## Related

- `knowledge/backend/10-authentication.md`
- `knowledge/security/04-authorization.md`
- `knowledge/security/05-password-security.md`
- `knowledge/security/06-session-management.md`
- `knowledge/security/07-jwt.md`
- `knowledge/security/21-rate-limiting.md`
