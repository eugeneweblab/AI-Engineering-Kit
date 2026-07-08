---
id: backend/10-authentication
topic: backend
slug: authentication
title: "Authentication"
type: doc
order: 10
status: ready
tags: [backend, authentication]
related: [backend/11-authorization, backend/09-validation, backend/06-api-design, backend/21-security, backend/22-observability]
when_to_use: "Read before building or reviewing login, signup, session, token, or credential-handling code in a backend service."
---
# Authentication

## Purpose

This document defines how a backend verifies *who* the caller is: login, credential
storage, session and token issuance, and how identity is carried on every request. It is
written so an agent can implement or review an authentication flow in a service without
opening a security hole.

Authentication answers "are you who you claim to be?". It is distinct from
[authorization](11-authorization.md) ("are you allowed to do this?"). A correct system
gets both right, in that order — identity first, permission second.

## Why It Matters

Authentication is the front door of the service. A single mistake here — a weak hash, a
forgeable token, a timing leak — compromises every user at once, not just one request,
and it does so silently: the app keeps working while attackers walk in. Because the blast
radius is total and the failure is invisible, auth code is held to a higher bar than
ordinary application code. Assume every input is hostile.

## Core Principles

- **Never invent your own crypto or auth scheme.** Use vetted libraries and standard
  protocols (OAuth 2.1, OIDC, WebAuthn). Custom schemes fail in ways you cannot see.
- **Store proof, not secrets.** Never store passwords; store a slow one-way hash. Never
  log credentials, tokens, or session ids.
- **Fail closed.** If verification cannot complete, deny access. An error is not a pass.
- **Make responses uniform.** Behave identically whether an account exists or not — same
  message, same timing. Differences leak valid accounts.
- **Authenticate every request.** Identity is not established once at login; every request
  must carry and re-verify a session or token. Treat all inputs as untrusted. See
  [validation](09-validation.md).

## Best Practices

- Hash passwords with a memory-hard algorithm — **Argon2id** (preferred) or **bcrypt** —
  with a per-user salt. Never MD5, SHA-1, or plain SHA-256 for passwords.
- Compare secrets with **constant-time** comparison to avoid timing attacks.
- Rate-limit and lock out (with backoff) login, MFA, and password-reset endpoints. See
  [security](21-security.md).
- Return one generic error for bad credentials — *"Invalid email or password."* — never
  revealing which field was wrong or whether the account exists.
- Regenerate the session identifier on every privilege change (login, logout) to prevent
  session fixation.
- Store sessions in `HttpOnly`, `Secure`, `SameSite=Lax` cookies; keep tokens out of
  `localStorage`, which any XSS can read.
- If using JWTs, verify signature, algorithm (pin it — reject `alg: none`), issuer,
  audience, and expiry before trusting a single claim. Keep access tokens short-lived and
  use refresh tokens with rotation.
- Expire sessions with a short idle timeout plus an absolute maximum, and support
  server-side revocation so logout actually ends the session.
- Treat signup, password reset, and "remember me" as authentication surfaces with the
  same rigor.

## Examples

**Good Example** — slow hash, uniform error, session rotation

```ts
import argon2 from "argon2";

async function login(email: string, password: string) {
  const user = await users.findByEmail(email);

  // Always run a verify, even when the user is missing, so response time
  // does not reveal whether the account exists.
  const hash = user?.passwordHash ?? DUMMY_HASH;
  const ok = await argon2.verify(hash, password);

  if (!user || !ok) throw new AuthError("Invalid email or password."); // one message for both
  await session.regenerate(user.id);   // new session id on login -> no fixation
  return user;
}
```

**Bad Example** — leaks account existence, fast reversible hash

```ts
async function login(email: string, password: string) {
  const user = await users.findByEmail(email);
  if (!user) throw new Error("No account with that email");   // enumerates valid emails
  if (user.passwordHash !== sha256(password))                 // fast + reversible hash
    throw new Error("Wrong password");                        // confirms the email is valid
  return user;                                                // session id never rotated -> fixation
}
```

## Common Mistakes

- Using a fast or reversible hash (SHA-256, encryption) for passwords.
- Different error messages or response times for "unknown user" vs "wrong password".
- Storing session tokens or JWTs in `localStorage`, exposing them to XSS.
- Never rotating the session id, enabling session fixation.
- Trusting a JWT without verifying signature, algorithm, issuer, audience, and expiry.
- Accepting `alg: none` or letting the token header choose the verification algorithm.
- No rate limiting, so credential-stuffing and brute-force run unchecked.

## Production Tips

- Log authentication *events* (success, failure, lockout, MFA) with user id and IP —
  never the credentials — and alert on failure spikes. See [observability](22-observability.md).
- Support forced logout / session revocation for incident response.
- Keep signing keys in a secrets manager, rotate on a schedule, and support key overlap so
  rotation doesn't invalidate every live token at once.
- Test negative paths in CI: wrong password, unknown user, expired session, tampered and
  replayed token.

## AI Review Checklist

- Are passwords hashed with Argon2id or bcrypt using a per-user salt?
- Is the response identical (message and timing) for unknown-user and wrong-password?
- Are sessions regenerated on login and revocable on logout?
- Are tokens stored in `HttpOnly` cookies rather than `localStorage`?
- Are JWT signature, pinned algorithm, issuer, audience, and expiry all verified?
- Are login, MFA, and reset endpoints rate-limited and lockout-protected?
- Is authentication clearly separated from [authorization](11-authorization.md)?

## Related

- `knowledge/backend/11-authorization.md`
- `knowledge/backend/09-validation.md`
- `knowledge/backend/06-api-design.md`
- `knowledge/backend/21-security.md`
- `knowledge/backend/22-observability.md`
