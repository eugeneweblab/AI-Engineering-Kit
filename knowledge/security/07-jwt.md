---
id: security/07-jwt
topic: security
slug: jwt
title: "JWT"
type: doc
order: 7
status: ready
tags: [security, jwt, verifyAccessToken, localStorage]
related: [security/03-authentication, security/06-session-management, security/08-oauth, security/16-secrets-management]
when_to_use: "Read before issuing, verifying, or storing JSON Web Tokens for auth or API access."
---
# JWT

## Purpose

This document defines how to issue, verify, and store JSON Web Tokens (JWTs) safely.
A JWT is a signed, base64url-encoded claim set — it proves *who* issued a statement and
that it was not tampered with. It is a token format, not an authentication system. Use it
to carry identity across requests once a user has already authenticated
(see [authentication](03-authentication.md)).

The core risk is simple: a JWT is only as trustworthy as your verification code. Most JWT
vulnerabilities are verification bugs, not weaknesses in the format itself.

## Why It Matters

A JWT is a bearer token: whoever holds it *is* the user, for as long as it is valid. There
is no built-in revocation. That makes two mistakes catastrophic. First, a verification hole
(accepting `alg: none`, skipping signature checks, trusting the wrong key) lets an attacker
forge any identity. Second, a leaked token cannot be un-issued — if it is long-lived and
sits in `localStorage`, one XSS gives an attacker durable, un-killable access. Because the
token is self-contained and offline-verifiable, the failure is silent: the server never
sees the theft, only valid-looking requests.

## Core Principles

- **A JWT is a claim, not a session.** It says "the issuer asserts X." It does not track
  state or revocation. If you need instant logout, you need a session or a denylist.
- **Verify everything, every time.** Signature, algorithm, issuer (`iss`), audience
  (`aud`), and expiry (`exp`) must all be checked before you trust a single claim.
- **Pin the algorithm.** Decide server-side which algorithm is allowed; never let the
  token's own header choose it. This is the root cause of `alg` confusion attacks.
- **Keep them short-lived.** Access tokens should live minutes, not days, because they
  cannot be revoked. Use a refresh token (stored server-side and revocable) for longevity.
- **Never put secrets in the payload.** JWTs are signed, not encrypted — anyone can read
  the claims. Put only non-sensitive identity data there.

## Best Practices

- Use a maintained library (e.g. `jose`) and call its verify function; never hand-parse
  or hand-split the token. The cost of DIY is `alg: none` and signature-skip bugs.
- Pin `algorithms: ["EdDSA"]` (or `RS256`, or `HS256`) in the verify options. Reject any
  token whose header names a different algorithm.
- Prefer asymmetric signing (EdDSA/RS256) when multiple services verify tokens: they hold
  only the public key, so a compromised verifier cannot mint tokens.
- Always set and check `exp`; keep access-token lifetime short (5–15 min). Set `iss` and
  `aud` and verify both — a token minted for another audience must be rejected.
- Store tokens in `HttpOnly`, `Secure`, `SameSite` cookies, not `localStorage`, so XSS
  cannot read them. Pair cookies with CSRF defenses (see [CSRF](12-csrf.md)).
- Maintain a short-lived denylist (by `jti`) for logout and compromise, so a stolen token
  can be killed before it expires.
- Rotate signing keys on a schedule; expose them via JWKS and include a `kid` header so
  verifiers pick the right key during rotation.

## Examples

**Good Example** — pinned algorithm, full claim verification

```ts
import { jwtVerify } from "jose";

async function verifyAccessToken(token: string) {
  const { payload } = await jwtVerify(token, publicKey, {
    algorithms: ["EdDSA"], // pin the alg server-side; ignore the token's header choice
    issuer: "https://auth.example.com", // reject tokens from any other issuer
    audience: "api.example.com",         // reject tokens minted for another service
  });
  // exp is validated automatically by jwtVerify; a stale token throws here.
  if (await denylist.has(payload.jti as string)) {
    throw new Error("token revoked"); // supports logout despite JWT being stateless
  }
  return payload;
}
```

**Bad Example** — trusts the token to describe itself

```ts
import jwt from "jsonwebtoken";

function verifyAccessToken(token: string) {
  // No `algorithms` option → library honors the token's `alg` header.
  // An attacker sets alg:"none" or swaps RS256→HS256 and forges any identity.
  const payload = jwt.verify(token, publicKey);
  // No issuer/audience check → a token from any system we trust is accepted.
  // No expiry policy beyond the default and no revocation → stolen token works for days.
  return payload;
}
```

## Common Mistakes

- Omitting the `algorithms` allowlist, enabling `alg: none` and RS256→HS256 confusion.
- Decoding the payload without verifying the signature (`decode` is not `verify`).
- Not checking `iss`/`aud`, so a token meant for another service is accepted.
- Long-lived access tokens with no refresh flow and no way to revoke.
- Storing tokens in `localStorage`, exposing them to any XSS.
- Putting sensitive data (PII, roles that must stay secret) in the readable payload.
- Treating a valid signature as proof of authorization — it only proves the claim's origin.

## Production Tips

- Publish public keys via a JWKS endpoint and cache them with the `kid` for rotation
  without downtime.
- Log token *issuance* and *verification failures* (with `jti` and `iss`), never the raw
  token. Alert on spikes in signature failures — they signal forgery attempts.
- Keep clock skew tolerance small (30–60 s) so expired tokens are not honored long.
- Test negative paths in CI: `alg:none`, wrong key, expired, wrong audience, tampered
  payload, replayed after logout.

## AI Review Checklist

- Is the verify call passed an explicit `algorithms` allowlist?
- Are signature, `exp`, `iss`, and `aud` all verified before any claim is trusted?
- Are access tokens short-lived, with a revocable refresh token for longevity?
- Is there a revocation/denylist path for logout and compromise?
- Are tokens stored in `HttpOnly` cookies rather than `localStorage`?
- Is the payload free of secrets, since it is readable by anyone?
- Is signing-key material sourced from a secrets manager and rotatable?

## Related

- `knowledge/security/03-authentication.md`
- `knowledge/security/06-session-management.md`
- `knowledge/security/08-oauth.md`
- `knowledge/security/16-secrets-management.md`
