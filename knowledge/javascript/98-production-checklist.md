---
id: javascript/98-production-checklist
topic: javascript
slug: production-checklist
title: "JavaScript Production Checklist"
type: doc
order: 98
status: ready
tags: [javascript, production-checklist]
related: [javascript/14-error-handling, javascript/26-security, javascript/25-performance, javascript/29-tooling, javascript/24-testing]
when_to_use: "Read before shipping JavaScript to production or approving a release."
---
# JavaScript Production Checklist

## Purpose

This is the go/no-go checklist for shipping JavaScript to production. Every item is a
verifiable yes/no an agent can confirm by reading the code, the config, or the build
output — not an opinion. If any box in the blocking groups is unchecked, the change is
not ready to ship. Use it as the final gate after the code is written and reviewed.

## Why It Matters

Most JavaScript production incidents are not exotic — they are a missing `res.ok` check,
a secret committed to the bundle, an unhandled rejection, or a dependency with a known
CVE. These are all catchable before release with a mechanical pass. The cost of checking
is minutes; the cost of skipping is a rollback, a leaked key, or a user-facing outage.
A checklist turns "we were careful" into "we verified."

## Error Handling and Resilience

- [ ] Every `fetch` / network call checks `res.ok` (or equivalent) before using the body.
- [ ] No empty or log-only `catch` blocks — every caught error is handled or rethrown.
- [ ] A global handler exists for `unhandledrejection` (browser) / `unhandledRejection`
      and `uncaughtException` (Node), reporting to an error tracker.
- [ ] Errors are thrown as `Error` objects (or subclasses), never strings.
- [ ] User-facing failures degrade gracefully; internal error details are not shown to
      end users.
- [ ] Timeouts and retry limits exist on all outbound calls so nothing hangs forever.

## Security

- [ ] No secrets, API keys, or tokens are present in client-side bundles or committed
      files (grep the built output, not just the source).
- [ ] User-controlled strings are never passed to `innerHTML`, `eval`, `new Function`, or
      `document.write`; DOM is built with `textContent` / safe templating.
- [ ] Dependencies pass `npm audit` (or equivalent) with no unresolved high/critical CVEs.
- [ ] Auth tokens are stored in `HttpOnly` cookies, not `localStorage`.
- [ ] Environment-specific config comes from environment variables, not hardcoded values.

## Performance

- [ ] The production bundle is minified, tree-shaken, and served with compression
      (gzip/brotli).
- [ ] Independent async work runs concurrently (`Promise.all`), not in serial `await`
      loops.
- [ ] Large or rarely used modules are code-split / lazily imported.
- [ ] No obvious memory leaks: event listeners, timers, and observers are cleaned up; no
      unbounded caches or arrays. See [memory management](15-memory-management.md).
- [ ] Expensive work is measured against a real profile, not assumed.

## Build and Configuration

- [ ] `NODE_ENV=production` (or the framework equivalent) is set so dev-only code and
      warnings are stripped.
- [ ] Source maps are generated and uploaded to the error tracker but not publicly
      served (or served access-controlled).
- [ ] Dependency versions are locked (`package-lock.json` / `pnpm-lock.yaml` committed).
- [ ] The build is reproducible in CI from a clean checkout — no reliance on local state.
- [ ] Linting and type checks pass with zero errors as a required CI gate.

## Observability

- [ ] Errors and unhandled rejections report to a monitoring service with stack traces.
- [ ] Logs are structured and contain no credentials, tokens, or PII.
- [ ] Key user flows emit metrics or events so regressions are detectable post-deploy.
- [ ] A rollback path exists and has been verified (previous build is deployable).

## Testing

- [ ] Unit tests cover the core logic including failure paths, not just the happy path.
- [ ] Async code is tested for both resolution and rejection.
- [ ] Tests run in CI and block merge on failure.
- [ ] Critical user journeys have at least one end-to-end or integration test.

## AI Review Checklist

- Is every network response checked before its body is used?
- Are all secrets absent from the shipped bundle and sourced from the environment?
- Do global handlers catch unhandled rejections and report them?
- Is the bundle minified, split where appropriate, and free of dev-only code?
- Are lint, type, and test gates green in CI before merge?
- Does a verified rollback path exist?

## Related

- `knowledge/javascript/14-error-handling.md`
- `knowledge/javascript/26-security.md`
- `knowledge/javascript/25-performance.md`
- `knowledge/javascript/29-tooling.md`
- `knowledge/javascript/24-testing.md`
