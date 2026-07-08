---
id: redis/15-session-storage
topic: redis
slug: session-storage
title: "Session Storage"
type: doc
order: 15
status: ready
tags: [redis, session-storage]
related: [redis/12-expiration, redis/07-hashes, redis/20-persistence, redis/21-security, redis/13-caching]
when_to_use: "Read before storing web/app session state or auth tokens in Redis."
---
# Session Storage

## Purpose

This document defines how to store server-side session state in Redis: key
design, TTLs, atomic idle-timeout renewal, and the security requirements for
holding authentication material. It is written so an agent can build a session
store that scales across app instances without leaking data or enabling session
attacks.

Redis is the default session store for horizontally-scaled apps because sessions
are small, per-user, latency-sensitive, and expiring — exactly Redis's sweet
spot. This doc is about the store; the auth semantics live in
[security/session-management](../security/06-session-management.md).

## Why It Matters

The session is the token that proves a user is logged in. If the store leaks,
mishandles TTLs, or lets one user read another's session, you have an
account-takeover vulnerability, not a performance bug.

Sessions also have a specific correctness requirement most caches don't: a
**sliding idle timeout**. Every authenticated request must extend the session's
life, but reading and re-writing the expiry non-atomically opens a window where a
session either dies mid-request or lives too long. And because sessions can hold
sensitive data, the durability and access-control posture of the Redis instance
matters directly.

## Core Principles

- **Every session key has a TTL — always.** The TTL *is* the session timeout. A
  session without expiry never logs the user out and leaks memory.
- **The session ID must be unguessable and server-generated.** Use a
  cryptographically random 128-bit+ id. Never let the client supply or influence
  the key.
- **Renew the idle timeout atomically.** Use `EXPIRE`/`GETEX` or a command that
  reads and re-arms the TTL in one step; never `GET` then `SET` (which also wipes
  the TTL — see [expiration](12-expiration.md)).
- **Regenerate the session ID on privilege change.** On login, logout, and role
  change, mint a new id and delete the old key to prevent session fixation.
- **Redis holds the session; the app owns the policy.** Absolute lifetime, idle
  timeout, and revocation rules are application decisions enforced via TTL and
  explicit `DEL`.

## Best Practices

- Store the session as a **hash** (`HSET session:<id> ...`) so individual fields
  update without rewriting the whole blob; set the TTL on the key.
- Use both an **idle timeout** (sliding, renewed per request) and an **absolute
  maximum lifetime** (never extended). Store the absolute deadline as a field and
  check it in app code.
- Renew with `GETEX session:<id> EX 1800` — reads the value and re-arms the TTL
  atomically in one round trip.
- On logout, `DEL` (or `UNLINK`) the key so revocation is immediate and
  server-side. Do not rely on the cookie expiring client-side.
- Keep only what you need in the session; store user *ids*, not full profiles or
  secrets. Never store passwords or raw tokens.
- Enable AOF persistence (`appendonly yes`) if a restart must not log everyone
  out; accept pure in-memory if a mass re-login is acceptable.
- Lock down the instance: `requirepass`/ACLs, TLS in transit, and network
  isolation — a session store is a high-value target (see
  [security](21-security.md)).

## Examples

**Good Example** — hash session, atomic sliding renewal, absolute cap

```ts
const IDLE = 1800;                 // 30 min sliding
const ABSOLUTE = 12 * 3600;        // 12 h hard cap

async function createSession(userId: string) {
  const sid = crypto.randomBytes(32).toString("hex");   // unguessable, server-side
  const key = `session:${sid}`;
  await redis.hset(key, {
    userId,
    createdAt: Date.now(),
    absExpiresAt: Date.now() + ABSOLUTE * 1000,          // absolute cap in a field
  });
  await redis.expire(key, IDLE);                         // idle TTL on the key
  return sid;
}

async function touch(sid: string) {
  const key = `session:${sid}`;
  // GETEX reads AND re-arms the idle TTL atomically: no check-then-act gap.
  const data = await redis.hgetall(key);                // (or GETEX on a string blob)
  if (!data.userId) return null;                         // expired/absent -> logged out
  if (Date.now() > Number(data.absExpiresAt)) {
    await redis.del(key);                                // absolute cap reached
    return null;
  }
  await redis.expire(key, IDLE);                         // slide the idle window
  return data;
}
```

**Bad Example** — client-controlled id, non-atomic renew, no expiry

```ts
async function touch(sid: string) {
  const key = `session:${sid}`;               // sid taken straight from a user field
  const raw = await redis.get(key);
  if (!raw) return null;
  // BUG: read then write is not atomic, and plain SET WIPES the TTL, so the
  // session's idle timeout silently disappears -> the session never expires.
  await redis.set(key, raw);
  return JSON.parse(raw);                       // no absolute cap, no revocation path
}
```

## Common Mistakes

- No TTL on the session key, so sessions never time out and memory grows forever.
- Renewing the timeout with `GET`+`SET`, which both races and clears the TTL
  instead of extending it — use `GETEX`/`EXPIRE`.
- Predictable or client-supplied session IDs, enabling guessing and fixation.
- Not regenerating the ID on login, leaving the app open to session fixation.
- Relying on cookie expiry for logout instead of deleting the server-side key, so
  a stolen session stays valid.
- Storing secrets, tokens, or full user records in the session, widening the blast
  radius if Redis is compromised.
- Only an idle timeout with no absolute cap, letting an active attacker keep a
  hijacked session alive indefinitely.

## Production Tips

- Size for the working set: `active_users x avg_session_bytes`, plus headroom;
  set `maxmemory` and a `volatile-*` eviction policy so only TTL'd keys can be
  evicted under pressure — never let session eviction be random.
- For forced logout / incident response, maintain a per-user index
  (`user:<id>:sessions` set) so you can revoke every session for a compromised
  account in one pass.
- Watch expired-key metrics to confirm sessions are actually timing out as
  intended.

## AI Review Checklist

- Does every session key have a TTL that equals the intended idle timeout?
- Is the session ID cryptographically random and server-generated (never client
  input)?
- Is the idle-timeout renewal atomic (`GETEX`/`EXPIRE`), never `GET` then `SET`?
- Is the session ID regenerated on login/logout, and the old key deleted?
- Is there an absolute maximum lifetime in addition to the idle timeout?
- Is logout implemented as a server-side `DEL`, not just a cookie expiry?
- Is the instance secured (auth, TLS, isolation) given it holds auth material?

## Related

- `knowledge/redis/12-expiration.md`
- `knowledge/redis/07-hashes.md`
- `knowledge/redis/20-persistence.md`
- `knowledge/redis/21-security.md`
- `knowledge/redis/13-caching.md`
