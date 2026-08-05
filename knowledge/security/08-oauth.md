---
id: security/08-oauth
topic: security
slug: oauth
title: "OAuth 2.0 and OpenID Connect"
type: doc
order: 8
status: ready
tags: [security, oauth]
related: [security/03-authentication, security/07-jwt, security/06-session-management, security/12-csrf]
when_to_use: "Read before integrating an OAuth 2.x / OIDC provider or building a 'Sign in with...' flow."
---
# OAuth 2.0 and OpenID Connect

## Purpose

This document defines how to use OAuth 2.x for *delegated authorization* and OpenID Connect
(OIDC) for *federated authentication* — the "Sign in with Google/GitHub" and third-party-API
flows. It is written so an agent can wire up a provider without opening a redirect, token, or
code-interception hole.

OAuth answers "may this app act on the user's behalf?". OIDC layers identity on top,
answering "who is this user?" via an `id_token`. Do not use a raw OAuth `access_token` as
proof of *who* the user is — that is a classic and dangerous mistake.

## Why It Matters

OAuth flows move credentials and authorization codes across redirects between three parties:
the user, your app, and the provider. Every hop is an opportunity for interception,
substitution, or replay. A single missing check — an unvalidated `redirect_uri`, a skipped
`state` parameter, an unverified token audience — turns "log in with one click" into account
takeover for every user. The protocol is safe only when implemented to spec; the dangerous
part is that a broken flow still logs users in perfectly, so the bug ships unnoticed.

## Core Principles

- **Use Authorization Code + PKCE for every client type.** Under OAuth 2.1, PKCE is
  mandatory for all clients, not just mobile. It binds the code to the client that started
  the flow, defeating code interception.
- **Never use the Implicit or Password grant.** Both are removed in OAuth 2.1: Implicit
  leaks tokens in the URL, Password hands your app the user's raw credentials.
- **`state` is not optional.** It ties the callback to the request you started and is your
  CSRF defense for the redirect (see [CSRF](12-csrf.md)).
- **Access token ≠ identity.** For "who is the user?", use OIDC's `id_token` and verify it.
  An `access_token` is opaque to you and may belong to a different app.
- **Validate the redirect target exactly.** Register exact `redirect_uri` values and match
  them literally — open redirects here become token theft.

## Best Practices

- Run **Authorization Code flow with PKCE**: generate a `code_verifier`, send its S256
  `code_challenge`, and present the verifier at token exchange.
- Generate `state` as a cryptographically random value, store it server-side (or in a
  signed cookie), and reject any callback whose `state` does not match.
- Exchange the code for tokens **server-side**, where the client secret lives; never expose
  the secret to a browser or mobile bundle.
- For OIDC, verify the `id_token`'s signature, `iss`, `aud` (must equal your client id),
  `exp`, and the `nonce` you sent. See [JWT](07-jwt.md) for verification rules.
- Request the **least scope** you need and show the user what you asked for. Broad scopes
  are a standing liability if the token leaks.
- Store the provider's `access`/`refresh` tokens encrypted at rest; treat refresh tokens
  as high-value secrets (see [secrets management](16-secrets-management.md)).
- Match your identity to the provider's **stable subject** (`sub`), not the email — emails
  are reassignable and can be spoofed by providers that do not verify them.

## Examples

**Good Example** — code flow with PKCE, state, and nonce

```ts
// 1. Start: bind the flow with PKCE + anti-CSRF state + OIDC nonce.
const verifier = randomUrlSafe(64);
const state = randomUrlSafe(32);
const nonce = randomUrlSafe(32);
await session.save({ verifier, state, nonce }); // server-side, one-time use
redirect(authorizeUrl({
  response_type: "code",
  code_challenge: sha256Base64Url(verifier), // binds code to this client
  code_challenge_method: "S256",
  state, nonce, scope: "openid email",         // minimal scope
}));

// 2. Callback: verify state BEFORE trusting the code.
if (query.state !== session.state) throw new Error("state mismatch"); // CSRF/replay defense
const tokens = await exchangeCode(query.code, session.verifier);     // server-side, holds secret
const claims = await verifyIdToken(tokens.id_token, {
  audience: CLIENT_ID, issuer: PROVIDER, nonce: session.nonce,       // proves identity
});
const user = await users.upsertBySubject(claims.iss, claims.sub);    // stable id, not email
```

**Bad Example** — implicit grant, no state, token treated as identity

```ts
// Implicit flow: token returned in the URL fragment, logged and cached everywhere.
redirect(`${authorizeUrl}?response_type=token&scope=email`); // no PKCE, no state

// Callback trusts whatever token appears — no state check → CSRF login / token injection.
const token = parseFragment(location.hash).access_token;
// Calls userinfo with an opaque access token and assumes the result is "the logged-in user".
// A token minted for a DIFFERENT app also works here → account takeover.
const me = await fetch("/userinfo", { headers: { authorization: `Bearer ${token}` } });
login(await me.json());
```

## Common Mistakes

- Using Implicit or Resource Owner Password grants (both removed in OAuth 2.1).
- Omitting PKCE, allowing an intercepted authorization code to be redeemed by an attacker.
- Skipping `state`, enabling login CSRF and code/token injection.
- Treating an `access_token` (or unverified `userinfo`) as proof of identity instead of a
  verified `id_token`.
- Loose or wildcard `redirect_uri` matching, turning an open redirect into token theft.
- Keying the local account off `email` rather than the provider's stable `sub`.
- Shipping the client secret in a browser or mobile app.

## Production Tips

- Prefer providers/libraries that support OIDC discovery (`.well-known`) and JWKS so key
  rotation and endpoints are automatic.
- Handle refresh-token rotation and revocation; detect reuse of a rotated refresh token as
  a compromise signal and invalidate the family.
- Log authorization *events* and token-exchange failures, never the codes or tokens.
- Test callbacks with a mismatched `state`, a replayed code, an `id_token` for the wrong
  `aud`, and an expired token.

## AI Review Checklist

- Is the flow Authorization Code **with PKCE** (never Implicit or Password)?
- Is `state` generated, stored, and verified on the callback?
- Is the code exchanged server-side, keeping the client secret off the client?
- For login, is a verified `id_token` used for identity rather than an access token?
- Are `iss`, `aud`, `exp`, and `nonce` all checked on the `id_token`?
- Is `redirect_uri` matched exactly against a registered value?
- Is the local account keyed on the provider's stable `sub`, not email?

## Related

- `knowledge/security/03-authentication.md`
- `knowledge/security/07-jwt.md`
- `knowledge/security/06-session-management.md`
- `knowledge/security/12-csrf.md`
