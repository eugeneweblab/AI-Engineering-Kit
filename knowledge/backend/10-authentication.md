---
id: backend/10-authentication
topic: backend
slug: authentication
title: "Backend Authentication"
type: doc
order: 10
status: ready
tags: [backend, authentication, NotFoundError, createRemoteJWKSet, cancelOwnedBy, getStore, decode]
related: [security/03-authentication, backend/11-authorization, backend/09-validation, backend/06-api-design, backend/21-security, backend/22-observability, security/07-jwt]
defers_to: security/03-authentication
when_to_use: "Read before wiring authentication into a service — where identity is verified, how it is carried through the layers, and how it crosses a service boundary."
---
# Backend Authentication

## Purpose

This document defines the backend's half of authentication: **where** identity is verified in
a service, **how** it is carried on every request, and how it crosses a service boundary.

The policy half — password storage, constant-time comparison, uniform login errors, lockout,
MFA, cookie flags — belongs to
[Security Authentication](../security/03-authentication.md) and is deliberately not repeated
here. Read that document for the rules; read this one for where they attach in a service.

Authentication answers "are you who you claim to be?";
[authorization](11-authorization.md) answers "may you do this?". Identity first, permission
second.

## Why It Matters

A service fails at authentication in ways a single-process application never does. Sessions
kept in memory disappear on the next deploy and do not exist on the second instance. A
gateway sets `X-User-Id` and the service trusts it, so anyone who can reach the service
directly is anyone they choose to be. A token is verified in one handler and assumed in the
next, so the one route that forgot is the way in.

None of these are cryptography mistakes. They are placement mistakes, and no amount of
correct hashing prevents them.

## Core Principles

- **Verify once, at the boundary.** One middleware or guard establishes identity for every
  request. Verification scattered across handlers is verification that one handler will miss.
- **Never trust an upstream header.** `X-User-Id` from a gateway is a claim, not proof. It is
  trustworthy only if the network path is, and the network path usually is not.
- **Identity is request state.** Carry it in a request context, never in a module-level
  variable — under concurrency a global identity belongs to whichever request wrote it last.
- **Sessions live in a shared store.** Anything held in process memory is lost on deploy and
  invisible to the other instances behind the load balancer.
- **Service-to-service identity is its own problem.** A backend calling another backend needs
  its own credential; forwarding the user's token makes every service a confused deputy.

## Best Practices

- Resolve identity in one middleware, attach it to the request context, and have every
  downstream layer read it rather than re-derive it.
- Verify a JWT completely before trusting one claim: signature, **pinned** algorithm,
  `iss`, `aud`, `exp`, `nbf`, with a small clock-skew allowance. See
  [JWT](../security/07-jwt.md).
- Fetch verification keys from JWKS with a cached TTL, and refetch on an unrecognised `kid`
  so key rotation does not require a deploy.
- Keep access tokens short-lived and refresh with rotation plus reuse detection — a refresh
  token presented twice means it leaked.
- Store sessions in Redis or the database with an explicit revocation path, so logout ends
  the session everywhere and incident response can force one.
- Give internal calls their own credential — mTLS or a service token with a specific `aud` —
  and verify it on the receiving side too. An internal network is not an authentication
  mechanism.
- Return `401` when identity is missing or invalid and `403` when identity is fine but the
  action is not permitted. Collapsing the two hides which one failed.
- Test the negative paths in CI: absent token, expired token, wrong audience, tampered
  signature, replayed refresh token, session revoked mid-request.

## Examples

**Good Example** — one boundary resolves identity; everything downstream reads it

```ts
// auth.middleware.ts — the only place a token becomes an identity.
const jwks = createRemoteJWKSet(new URL(env.JWKS_URL), {
  cacheMaxAge: 10 * 60_000,   // cached, and refetched automatically on an unknown kid
});

export const requestContext = new AsyncLocalStorage<{ userId: string; scopes: string[] }>();

export async function authenticate(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.match(/^Bearer (.+)$/)?.[1];
  if (!token) {
    return res.status(401).json({ code: 'not_authenticated' });
  }

  try {
    // Every check together: a signature alone proves nothing about who issued it or for whom.
    const { payload } = await jwtVerify(token, jwks, {
      algorithms: ['RS256'],            // pinned: never let the header choose
      issuer: env.TOKEN_ISSUER,
      audience: env.SERVICE_AUDIENCE,   // a token minted for another service is not valid here
      clockTolerance: 5,
    });

    if (await sessions.isRevoked(payload.sid as string)) {
      return res.status(401).json({ code: 'session_revoked' });
    }

    // Request-scoped: concurrent requests cannot see each other's identity.
    requestContext.run({ userId: payload.sub!, scopes: (payload.scope as string).split(' ') }, next);
  } catch {
    return res.status(401).json({ code: 'not_authenticated' });   // fail closed
  }
}
```

```ts
// Downstream layers read the resolved identity. They never parse a token themselves.
export async function cancelOrder(orderId: string): Promise<void> {
  const { userId } = requestContext.getStore()!;
  const cancelled = await orders.cancelOwnedBy(orderId, userId);
  if (!cancelled) {
    throw new NotFoundError();
  }
}
```

```ts
// A call to another service carries the SERVICE's own credential, not the user's token.
const res = await fetch(`${env.BILLING_URL}/invoices`, {
  headers: {
    authorization: `Bearer ${await serviceToken({ audience: 'billing' })}`,
    'x-on-behalf-of': userId,   // context for logging, NOT a substitute for authorization
  },
});
```

**Bad Example** — identity re-derived everywhere, or taken on trust

```ts
// The gateway sets this header, so the service treats it as proof. Anyone who can
// reach the service directly — another pod, a misrouted ingress, a port-forward —
// picks their own user id.
app.use((req, _res, next) => {
  (req as any).userId = req.headers['x-user-id'];
  next();
});

// Each handler decodes the token itself, and this one only decodes it.
// jwt.decode does NOT verify: the signature, issuer, audience, and expiry are ignored.
app.get('/orders/:id', async (req, res) => {
  const claims = jwt.decode(req.headers.authorization!.slice(7)) as { sub: string };
  res.json(await orders.findForUser(req.params.id, claims.sub));
});

// The handler added next week forgets to do it at all, and nothing catches that.
app.delete('/orders/:id', async (req, res) => {
  res.json(await orders.remove(req.params.id));
});

// Identity in a module-level variable: under any concurrency this is whichever
// request wrote it last, so one user acts as another.
let currentUser: User | null = null;

// Sessions in process memory: gone on deploy, and invisible to the second instance.
const sessions = new Map<string, Session>();
```

## Common Mistakes

- Trusting a gateway-supplied identity header without verifying it at the service.
- `jwt.decode()` where `jwtVerify()` was meant — decoding is parsing, not verification.
- Accepting the algorithm from the token header instead of pinning it, which is how
  `alg: none` and RS256→HS256 confusion get in.
- Skipping `aud`, so a token minted for a different service is accepted by this one.
- Per-handler authentication, where the route added last is the route that forgot.
- Identity in a global or a module-level variable rather than request-scoped state.
- Sessions in process memory, so logout works on one instance and a deploy logs everyone out.
- Forwarding the end user's token to an internal service, which then cannot tell whether it
  is acting for the user or as itself.
- Returning `403` for a missing token — it is `401`, and the difference tells the client
  whether to re-authenticate or give up.

## Production Tips

- Log authentication *events* — success, failure, revocation, service-token issuance — with
  the user id, service, and IP, never the credential itself. Alert on failure spikes. See
  [observability](22-observability.md).
- Emit the same request id on the authentication decision and on the handler that follows it,
  so a rejected request can be traced end to end.
- Keep signing keys in a secrets manager with overlapping validity, so rotation does not
  invalidate every live token at once.
- Make revocation reachable in an incident: an operator must be able to end one session, one
  user's sessions, or every session, without a deploy.
- Put a token-expiry clock-skew allowance in configuration, not in code — the value changes
  when the fleet's time source does.

## AI Review Checklist

- Is identity established in exactly one place, before any handler runs?
- Is every JWT claim verified — signature, pinned algorithm, issuer, audience, expiry?
- Is an upstream identity header treated as a claim rather than as proof?
- Is identity request-scoped rather than stored in a module-level variable?
- Are sessions in a shared store, with a revocation path that logout actually uses?
- Do internal calls carry their own service credential instead of the user's token?
- Are `401` and `403` used for their own meanings?
- Does the policy side follow [Security Authentication](../security/03-authentication.md)?

## Related

- `knowledge/security/03-authentication.md`
- `knowledge/backend/11-authorization.md`
- `knowledge/backend/09-validation.md`
- `knowledge/backend/06-api-design.md`
- `knowledge/backend/21-security.md`
- `knowledge/backend/22-observability.md`
- `knowledge/security/07-jwt.md`
