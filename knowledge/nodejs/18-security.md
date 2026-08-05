---
id: nodejs/18-security
topic: nodejs
slug: security
title: "Node.js Security"
type: doc
order: 18
status: ready
tags: [nodejs, security]
related: [nodejs/16-error-handling, nodejs/14-environment, nodejs/09-http, nodejs/04-package-management, nodejs/17-logging]
when_to_use: "Read before shipping any Node.js service that handles user input, secrets, dependencies, or network traffic."
---
# Node.js Security

## Purpose

This document defines how to harden a Node.js process against the attacks that
specifically target the runtime: dependency supply-chain compromise, unsafe
deserialization, command and path injection, secret leakage through the
environment, and unbounded resource consumption. It is scoped to Node-specific
mechanics — application-layer concerns like authentication and authorization live
under the `security` topic and are referenced, not repeated here.

## Why It Matters

A Node process runs with full OS privileges: it can spawn shells, read the
filesystem, and open sockets. A single injectable `child_process.exec`, one
prototype-pollution sink, or one malicious transitive dependency gives an attacker
those same privileges. Because Node apps pull in hundreds of npm packages, most of
your attack surface is code you never wrote and never read. The failure mode is
remote code execution, not a broken page — treat every external byte as hostile.

## Core Principles

- **Never pass untrusted input to a shell.** Use `execFile`/`spawn` with an argument
  array, never `exec` with an interpolated string. The shell is a code interpreter.
- **Validate and normalize at the boundary.** Parse input against a schema (Zod,
  Ajv) before it reaches business logic. Reject, do not sanitize-and-hope.
- **Pin and audit dependencies.** A lockfile plus `npm audit` and provenance checks
  is your supply-chain defense. Unpinned deps are unreviewed code with `require`.
- **Keep secrets out of code and logs.** Secrets come from the environment or a
  secrets manager, never a committed file, and are never logged or serialized.
- **Fail closed and bound everything.** Every request gets a size limit, a timeout,
  and a rate limit. Unbounded input is a denial-of-service primitive.

## Best Practices

- Run with `node --disable-proto=delete` and freeze `Object.prototype` where feasible
  to blunt prototype pollution; validate object keys before merging user data.
- Set the `NODE_OPTIONS` allowlist and run as a non-root user in the container.
  Drop Linux capabilities; a compromised process should not be able to bind port 80.
- Add security headers with `helmet`, enforce a strict body-size limit
  (`express.json({ limit: "100kb" })`), and rate-limit public endpoints.
- Use `crypto.timingSafeEqual` for comparing tokens and HMACs, and
  `crypto.randomBytes`/`randomUUID` for anything that must be unguessable. Never
  use `Math.random()` for security tokens.
- Resolve and confine filesystem paths: `path.resolve` the input, then verify it
  stays under an allowed root before opening. This blocks `../` traversal.
- Keep Node on an active LTS line and patch promptly; subscribe to Node security
  releases. EOL runtimes receive no CVE fixes.
- Enable `npm ci` in CI (not `npm install`) so the lockfile is authoritative, and
  fail the build on high-severity `npm audit` findings.

## Examples

**Good Example** — no shell, validated input, bounded path

```js
import { execFile } from "node:child_process";
import { resolve, sep } from "node:path";

const ROOT = resolve("/srv/uploads");

async function convert(userFilename) {
  // resolve then confine: reject anything that escapes ROOT via ../ or symlinks
  const abs = resolve(ROOT, userFilename);
  if (!abs.startsWith(ROOT + sep)) throw new Error("path traversal");

  // execFile takes an argv array — the filename can never become shell syntax
  return new Promise((res, rej) =>
    execFile("convert", [abs, "-resize", "800x", `${abs}.out`], (e) =>
      e ? rej(e) : res(),
    ),
  );
}
```

**Bad Example** — shell injection and path traversal in three lines

```js
import { exec } from "node:child_process";

function convert(userFilename) {
  // userFilename = "x.png; rm -rf / #" runs as a shell command → RCE
  // and "../../etc/passwd" is read directly → no path confinement
  exec(`convert /srv/uploads/${userFilename} -resize 800x out.png`);
}
```

## Common Mistakes

- Building shell commands with template strings and `child_process.exec`.
- Merging untrusted JSON into config objects, enabling prototype pollution via
  `__proto__` / `constructor` keys.
- Storing secrets in a committed `.env` or hardcoding API keys in source.
- Comparing tokens with `===`, leaking length and content through timing.
- Running `npm install` (not `npm ci`) in CI, so a drifted lockfile ships.
- Trusting `req.body` size — a 2GB JSON payload OOMs the process before any handler runs.
- Running the container as root, so any RCE becomes host compromise.

## Production Tips

- Generate an SBOM and enable dependency review / Dependabot; treat a new
  transitive dependency as a code review event.
- Set `process.env` allowlisting at boot: read the secrets you need into typed
  config once, then delete them from `process.env` so accidental logs cannot leak them.
- Run SAST (CodeQL, Semgrep) and secret scanning in CI on every PR.
- Ship structured audit logs of security events (auth failures, rate-limit hits)
  without the secret payloads themselves — see `nodejs/17-logging`.

## AI Review Checklist

- Is every `child_process` call using `execFile`/`spawn` with an argv array, never a shell string?
- Is all external input validated against a schema at the boundary?
- Are user-supplied paths resolved and confined under an allowed root?
- Are secrets read from the environment/secrets manager and kept out of code and logs?
- Is CI using `npm ci` with a committed lockfile and failing on high-severity audits?
- Are token/HMAC comparisons using `crypto.timingSafeEqual`?
- Are request bodies size-limited, timed out, and rate-limited?

## Related

- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/14-environment.md`
- `knowledge/nodejs/09-http.md`
- `knowledge/nodejs/04-package-management.md`
- `knowledge/nodejs/17-logging.md`
