---
id: security/05-password-security
topic: security
slug: password-security
title: "Password Security"
type: doc
order: 5
status: ready
tags: [security, password-security, hashPassword, verifyPassword, hash, createHash, digest]
related: [security/03-authentication, security/06-session-management, security/16-secrets-management, security/21-rate-limiting, security/17-encryption]
when_to_use: "Read before building or reviewing signup, login, password reset, or any credential-storage code."
---
# Password Security

## Purpose

This document defines how to store, verify, and manage passwords safely: which hashing
algorithm to use, how to handle resets, and what policies to enforce. It is a focused
companion to [Authentication](03-authentication.md) — that doc covers the login flow;
this one covers the credential itself.

## Why It Matters

Password databases get stolen. Assume yours eventually will be — via a SQL injection, a
backup leak, or a misconfigured bucket. When it happens, the *only* thing standing
between the dump and every user's account is how the passwords were stored. A fast hash
falls to a GPU in hours; a proper memory-hard hash buys years. Because users reuse
passwords, a weak store also compromises their accounts on *other* systems. This is one
of the few places where getting the algorithm choice right, once, prevents a mass
compromise.

## Core Principles

- **Never store the password, store a slow one-way hash.** Not the plaintext, not
  encryption (reversible), not a fast digest. Only a memory-hard hash designed for
  passwords.
- **Salt every hash, uniquely and automatically.** A per-password random salt defeats
  rainbow tables and stops identical passwords hashing alike. Modern password hashers
  generate and store the salt for you — do not roll your own.
- **Make verification constant-time.** Use the library's `verify`, which compares in
  constant time; never compare hashes with `==`, which can leak via timing.
- **Cost must be tunable and current.** Hardware gets faster; the work factor must be
  raised over time and re-applied on next login.
- **Length beats complexity.** A long passphrase has more entropy than a short string of
  mandated symbols. Favor length minimums over composition rules.

## Best Practices

- Hash with **Argon2id** (preferred) or **bcrypt**. Argon2id parameters as of 2026: at
  least 19 MiB memory, 2 iterations, parallelism 1, tuned up to your latency budget.
  For bcrypt use cost ≥ 12 and note its 72-byte input limit.
- Never use MD5, SHA-1, SHA-256, or any general-purpose/fast hash for passwords — they
  are built to be fast, which is exactly wrong here.
- Enforce a **minimum length of 12+**; do not cap length low or strip characters.
  Support the full Unicode range and paste (password managers depend on it).
- Reject known-breached passwords by checking against a breach corpus (e.g. the
  k-anonymity Have I Been Pwned range API) rather than imposing arcane composition rules.
- Rehash on login when the stored parameters are below current policy, transparently
  upgrading users.
- Rate-limit and lock out (with backoff) on login and reset endpoints to blunt
  brute-force and credential stuffing. See [Rate Limiting](21-rate-limiting.md).
- For password reset, email a single-use, expiring, high-entropy token; never email the
  password, and invalidate all sessions on a successful reset.

## Examples

**Good Example** — Argon2id with tuned cost, library verify, transparent rehash

```ts
import argon2 from "argon2";

const OPTS = { type: argon2.argon2id, memoryCost: 19456, timeCost: 2, parallelism: 1 };

async function hashPassword(pw: string): Promise<string> {
  // Salt is generated and embedded automatically; never manage it by hand.
  return argon2.hash(pw, OPTS);
}

async function verifyPassword(stored: string, pw: string): Promise<boolean> {
  const ok = await argon2.verify(stored, pw); // constant-time comparison
  if (ok && argon2.needsRehash(stored, OPTS)) {
    await users.updateHash(await argon2.hash(pw, OPTS)); // upgrade cost on login
  }
  return ok;
}
```

**Bad Example** — fast hash, hand-rolled salt, timing-leaky compare

```ts
import crypto from "crypto";

function hashPassword(pw: string): string {
  // SHA-256 is fast and reversible under brute force; a static salt is useless.
  return crypto.createHash("sha256").update("staticSalt" + pw).digest("hex");
}

function verifyPassword(stored: string, pw: string): boolean {
  return stored === hashPassword(pw); // "===" leaks via timing; no cost, no per-user salt
}
```

## Common Mistakes

- Using MD5/SHA-1/SHA-256 or encryption instead of a password hash.
- A single application-wide salt, or no salt, instead of a per-password one.
- Comparing hashes with `==`/`===` instead of a constant-time verify.
- Capping password length or stripping characters, breaking password managers.
- Composition rules (must have a symbol) instead of length + breach checks.
- Emailing the password, or a reset link that does not expire or is reusable.
- No rate limiting, leaving login open to credential stuffing.
- Logging the plaintext password or the hash anywhere.

## Production Tips

- Store the algorithm and parameters *inside* the hash string (Argon2/bcrypt formats do
  this), so you can migrate algorithms without a schema change.
- Alert on spikes in failed logins and reset requests — signals of stuffing or takeover.
- Re-benchmark hash cost yearly against current hardware and raise it.
- On any suspected breach, force a global reset and invalidate all sessions and tokens.

## AI Review Checklist

- Is the password hashed with Argon2id or bcrypt (never a fast/general hash)?
- Is a unique per-password salt used, generated by the library?
- Is verification constant-time (library `verify`, not `==`)?
- Are hashes transparently rehashed when cost policy increases?
- Is there a minimum length (12+) with no low cap and no character stripping?
- Are breached passwords rejected, and login/reset rate-limited?
- Are reset tokens single-use, expiring, and do they invalidate existing sessions?
- Are plaintext passwords and hashes kept out of logs?

## Related

- `knowledge/security/03-authentication.md`
- `knowledge/security/06-session-management.md`
- `knowledge/security/16-secrets-management.md`
- `knowledge/security/21-rate-limiting.md`
- `knowledge/security/17-encryption.md`
