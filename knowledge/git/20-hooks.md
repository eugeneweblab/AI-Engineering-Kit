---
id: git/20-hooks
topic: git
slug: hooks
title: "Git Hooks"
type: doc
order: 20
status: ready
tags: [git, hooks, pre-commit, pre-push, commit-msg, commit, install]
related: [git/04-commits, git/16-push, git/28-security, git/29-tooling, git/27-best-practices]
when_to_use: "Read before adding pre-commit, commit-msg, or pre-push automation, or reviewing a repo's hook setup."
---
# Git Hooks

## Purpose

This document defines how to use Git hooks — scripts Git runs automatically at points
in its lifecycle (`pre-commit`, `commit-msg`, `pre-push`, `post-merge`, server-side
`pre-receive`) — to enforce quality gates and automate checks. It covers where hooks
live, how to share them across a team, and what belongs in a hook versus in CI.

Hooks are the earliest, cheapest place to catch a problem: they run on the developer's
machine before code ever leaves it. Used well they stop broken commits at the source;
used poorly they slow everyone down or lull the team into trusting checks that can be
bypassed.

## Why It Matters

The cost of catching a defect rises at every stage: a lint error caught by a
`pre-commit` hook costs seconds; the same error caught in CI costs a red pipeline and a
context switch; caught in review it costs a human's time; caught in production it costs
an incident. Hooks push feedback as far left as possible. But hooks run on machines you
do not control and can be skipped with `--no-verify`, so they are a *convenience* layer,
never the *only* enforcement. The security boundary must be server-side.

## Core Principles

- **Client hooks are advisory, not enforcement.** Any developer can bypass them with
  `--no-verify` or by not installing them. Duplicate every must-pass check in CI.
- **Hooks are not versioned by default.** `.git/hooks` is local and never committed.
  Share hooks through a tracked directory and a manager, or they will not exist on
  teammates' machines.
- **Fast or nothing.** A `pre-commit` hook that takes 30 seconds trains people to use
  `--no-verify`. Keep client hooks under a couple of seconds; defer slow work to CI.
- **Fail loud, exit non-zero.** A hook enforces by returning a non-zero exit code with
  a clear message. A hook that only warns changes nothing.
- **Server-side hooks are the real gate.** `pre-receive`/`update` on the server (or
  branch protection rules) cannot be bypassed by the client.

## Best Practices

- Manage client hooks with a tool (Husky, pre-commit, Lefthook) that installs them from
  a committed config, so every clone gets the same hooks. Do not hand-edit
  `.git/hooks`.
- Scope `pre-commit` checks to *staged* files (e.g. `lint-staged`), not the whole repo,
  so the hook stays fast as the codebase grows.
- Use `commit-msg` to validate message format (e.g. Conventional Commits) and
  `pre-push` for quick test/lint gates that should run before sharing.
- Keep the same checks runnable manually and in CI (`npm run lint`, `pre-commit run
  --all-files`) so the hook is not the only path.
- Make hooks deterministic and side-effect-free where possible; never have a hook
  auto-push, auto-commit, or contact the network on the critical path.
- On the server, enforce protected-branch policy (signed commits, required status,
  no force-push) with platform rules or `pre-receive` hooks — the parts that must
  never be bypassed.

## Examples

**Good Example** — fast, shared, staged-only pre-commit via a manager

```bash
# .husky/pre-commit  (committed to the repo, installed on every clone)
#!/bin/sh
npx lint-staged   # lints/formats ONLY staged files → stays fast, fixes in place
```

```json
// package.json — the check is also runnable in CI, so the hook is not the only gate
{
  "lint-staged": { "*.{ts,tsx}": ["eslint --fix", "prettier --write"] },
  "scripts": { "ci:lint": "eslint . && prettier --check ." }
}
```

**Bad Example** — local-only, slow, and treated as the sole enforcement

```bash
# Edited directly in .git/hooks/pre-commit — never committed, so ONLY exists on
# this one machine. Teammates and CI have no such check.
#!/bin/sh
npm run test:e2e   # full end-to-end suite on every commit → 90s → people run
                   # `git commit --no-verify` and the "gate" protects nothing
# No server-side rule backs this up, so unchecked code merges freely.
```

## Common Mistakes

- Putting hooks in `.git/hooks` and assuming teammates have them — that directory is
  never cloned.
- Treating a client hook as a security or compliance control; it is bypassable by
  design.
- Running slow suites (full tests, e2e) in `pre-commit`, training everyone to use
  `--no-verify`.
- Linting the whole repo instead of staged files, so hook time grows with the codebase.
- Hooks that mutate state (auto-commit, auto-push) or require network, causing
  surprising failures.
- Not mirroring the check in CI, so bypassing the hook silently disables the check.

## Production Tips

- Pin the hook manager and its config in the repo so a fresh clone plus `install` is
  the only setup step; document it in the README.
- Provide an escape hatch policy: `--no-verify` is fine for WIP commits *because* CI
  re-runs the same checks — state this explicitly so people do not fear or abuse it.
- For monorepos, run hooks only against changed packages to keep them fast.
- Require commit signing at the server (branch protection), not the client hook, when
  provenance matters (see [security](28-security.md)).

## AI Review Checklist

- Are client hooks installed from a committed config (Husky/pre-commit/Lefthook), not
  hand-edited in `.git/hooks`?
- Is every must-pass hook check also enforced in CI or server-side rules?
- Do `pre-commit` checks run on staged files only and finish in a second or two?
- Do hooks exit non-zero with a clear message on failure, rather than only warning?
- Are hooks free of network calls and state-mutating side effects on the critical path?
- Is the real enforcement (signing, required status, no force-push) on the server, not
  the client?

## Related

- `knowledge/git/04-commits.md`
- `knowledge/git/16-push.md`
- `knowledge/git/28-security.md`
- `knowledge/git/29-tooling.md`
- `knowledge/git/27-best-practices.md`
