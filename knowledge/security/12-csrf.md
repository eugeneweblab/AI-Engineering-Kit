---
id: security/12-csrf
topic: security
slug: csrf
title: "CSRF"
type: doc
order: 12
status: ready
tags: [security, csrf]
related: [security/06-session-management, security/11-xss, security/03-authentication, security/19-cors]
when_to_use: "Read before building state-changing endpoints that rely on cookies, or any form/POST handler."
---
# CSRF (Cross-Site Request Forgery)

## Purpose

This document defines how to prevent Cross-Site Request Forgery: tricking a logged-in user's
browser into sending a state-changing request the user never intended. Because the browser
attaches the user's cookies automatically, the forged request arrives fully authenticated.

CSRF exists only because of *ambient* credentials — cookies (and HTTP Basic/NTLM) that the
browser sends on every request to an origin, regardless of who initiated it. The defense is to
require a proof of intent that an attacker's site cannot supply.

## Why It Matters

If your app authenticates requests with a session cookie and nothing else, any other website
the victim visits can silently submit forms or fire requests to your app *as that victim* —
change their email, transfer money, delete data, escalate privileges. The victim only had to
be logged in and load a malicious (or ad-laden) page. There is no theft of credentials and no
alert; the request looks legitimate because, from the server's view, it is. CSRF turns every
authenticated cookie-based endpoint into a target that any external page can trigger.

## Core Principles

- **CSRF targets cookie/ambient auth.** If a request is authenticated by something the browser
  does *not* attach automatically — a bearer token in an `Authorization` header set by JS — it
  is not CSRF-able in the same way. Cookie-authenticated endpoints need explicit protection.
- **Require a proof the attacker cannot forge.** A per-session CSRF token or the browser's
  `SameSite` cookie behavior provides evidence the request came from your own site.
- **`SameSite` is the baseline, tokens are the belt-and-suspenders.** Set `SameSite=Lax` (or
  `Strict`) on session cookies; add synchronizer/double-submit tokens for defense in depth,
  especially for cross-site POSTs you deliberately allow.
- **Safe methods must be safe.** `GET`/`HEAD` must never change state. If a `GET` mutates data,
  it can be triggered by an `<img>` tag and no token protects it.
- **CORS is not CSRF protection.** CORS governs whether JS can *read* a cross-origin response;
  the forged request is still *sent* and its side effects still happen.

## Best Practices

- Set session cookies `SameSite=Lax` (default) or `Strict`, plus `HttpOnly` and `Secure`. Lax
  blocks cross-site POSTs and most forged requests while allowing top-level navigations.
- Add a **synchronizer token**: server issues a per-session random token, the form/JS sends it
  back in a header or hidden field, and the server compares it. Use your framework's built-in
  CSRF middleware rather than rolling your own.
- For SPAs, use the **double-submit cookie** pattern: a non-`HttpOnly` CSRF cookie mirrored in
  a custom request header; the server checks they match. Same-origin policy stops other sites
  from setting that header.
- Keep all mutations on `POST`/`PUT`/`PATCH`/`DELETE`; never mutate on `GET`.
- Validate `Origin`/`Referer` on state-changing requests as an additional signal, rejecting
  requests from unexpected origins.
- Require re-authentication or a fresh token for high-value actions (password/email change,
  payments) so a stale forged request cannot complete them.
- Prefer a custom request header for JSON APIs; a cross-site HTML form cannot set custom
  headers, so requiring one blocks simple form-based CSRF.

## Examples

**Good Example** — SameSite cookie plus verified CSRF token

```ts
// Session cookie is not sent on cross-site POSTs, and a per-session token is required.
app.use(session({
  cookie: { httpOnly: true, secure: true, sameSite: "lax" }, // blocks most cross-site sends
}));
app.use(csrf()); // framework middleware issues + verifies a per-session token

app.post("/account/email", (req, res) => {
  // Middleware already rejected the request if the CSRF token was missing/wrong.
  // A GET is never used for this mutation, so <img> tricks cannot trigger it.
  updateEmail(req.session.userId, req.body.email);
  res.sendStatus(204);
});
```

**Bad Example** — cookie-only auth on a state-changing GET

```ts
// GET that mutates state + no token + cookie auth = trivially forgeable.
// <img src="https://bank.example/transfer?to=attacker&amt=1000"> on any page fires this
// with the victim's session cookie attached automatically.
app.get("/transfer", (req, res) => {
  transfer(req.session.userId, req.query.to, req.query.amt); // no intent proof, wrong method
  res.sendStatus(200);
});
```

## Common Mistakes

- Authenticating with cookies but shipping no CSRF token and no `SameSite` restriction.
- Performing state changes on `GET`, which no CSRF token can protect.
- Believing CORS prevents CSRF — it governs *reading* responses, not *sending* requests.
- Rolling a custom token scheme instead of using the framework's tested middleware.
- Using a static or predictable token, or not tying it to the session.
- Forgetting that stored [XSS](11-xss.md) defeats CSRF tokens entirely — the script reads the
  token; fix XSS too.
- Applying CSRF protection to login/logout forms only, leaving other mutations open.

## Production Tips

- Default every route to protected and explicitly opt specific endpoints out (e.g. a webhook
  authenticated by signature), rather than opting routes in.
- For cross-service webhooks and non-browser clients, use signed requests or bearer tokens
  instead of cookies, so CSRF does not apply.
- Log and alert on `Origin`/`Referer` mismatches on mutating endpoints — a signal of active
  CSRF attempts.
- Test that mutating endpoints reject requests with a missing/invalid token and with a
  foreign `Origin`.

## AI Review Checklist

- Are session cookies set `SameSite=Lax`/`Strict`, `HttpOnly`, and `Secure`?
- Do all state-changing endpoints require a per-session CSRF token (or double-submit header)?
- Are all mutations on `POST`/`PUT`/`PATCH`/`DELETE`, never `GET`?
- Is the token verification the framework's tested middleware, not a custom scheme?
- Is `Origin`/`Referer` validated on state-changing requests?
- Is it understood that CORS does not stop CSRF and that XSS defeats CSRF tokens?
- Are non-browser clients using bearer/signature auth rather than ambient cookies?

## Related

- `knowledge/security/06-session-management.md`
- `knowledge/security/11-xss.md`
- `knowledge/security/03-authentication.md`
- `knowledge/security/19-cors.md`
