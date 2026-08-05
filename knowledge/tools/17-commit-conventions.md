---
id: tools/17-commit-conventions
topic: tools
slug: commit-conventions
title: "Commit Conventions"
type: doc
order: 17
status: ready
tags: [tools, commit-conventions]
related: [tools/16-git-hooks, tools/28-release-tools, tools/27-dependency-management, tools/19-task-runners, tools/30-engineering-principles, git/04-commits, git/27-best-practices]
when_to_use: "Read before adopting a commit message convention — configuring commitlint, choosing types and scopes, or wiring commits to automated versioning."
---
# Commit Conventions

## Purpose

This document defines how to structure commit messages so they can be read by humans and
parsed by tools: the Conventional Commits format, how to enforce it, and what it enables
downstream.

## Why It Matters

Commit messages are the only documentation guaranteed to exist at the moment of the
change. Six months later, `git log` is often the sole record of *why* something is the way it
is — and "fix stuff" answers nothing.

A machine-readable convention adds a second benefit: version numbers, changelogs, and release
notes can be derived from history instead of maintained by hand, and each of those is a task
people skip under pressure.

## Core Principles

- **The subject says what changed; the body says why.** The diff already shows the how.
- **A type and scope make history filterable.** `git log --grep '^fix(auth)'` is only possible
  if the convention holds.
- **Enforce with a hook, not a review comment.** Format is not worth a reviewer's attention.
- **Breaking changes must be explicit.** A `!` or a `BREAKING CHANGE:` footer is what drives
  a major version bump.

## The Format

```
<type>(<optional scope>): <subject>

<optional body>

<optional footer>
```

```
feat(checkout): support saved payment methods

Customers can now select a stored card at checkout instead of re-entering
details. Cards are tokenized by the payment provider; no card data reaches
our servers.

Closes #482
```

| Type | Meaning | Version effect |
|---|---|---|
| `feat` | New capability | minor |
| `fix` | Bug fix | patch |
| `perf` | Performance improvement | patch |
| `refactor` | Behavior-preserving change | none |
| `docs` | Documentation only | none |
| `test` | Tests only | none |
| `build` | Build system, dependencies | none |
| `ci` | CI configuration | none |
| `chore` | Maintenance | none |
| `style` | Formatting only | none |

Breaking changes are marked in either of two ways:

```
feat(api)!: remove the deprecated v1 endpoints

BREAKING CHANGE: /api/v1/* now returns 410. Clients must migrate to /api/v2/*.
The migration guide is in docs/migrations/v2.md.
```

## Enforcing It

```js
// commitlint.config.js
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [2, 'always', [
      'auth', 'checkout', 'catalog', 'admin', 'api', 'ui', 'deps', 'ci',
    ]],
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
    'body-max-line-length': [2, 'always', 100],
  },
};
```

```bash
# .husky/commit-msg
npx --no -- commitlint --edit "$1"
```

A fixed `scope-enum` is what makes scopes useful. Without it, the same area accumulates three
spellings and filtering stops working.

## Examples

**Good Example** — messages that answer a question later

```
fix(auth): refresh the session before it expires mid-request

Long-running exports failed with 401 because the token expired while the job
was streaming. The client now refreshes at 80% of the token lifetime rather
than on the first failure.

Fixes #1204
```

```
perf(catalog): prime term cache before rendering the grid

The category grid issued one query per product to read its terms — 240
queries on a full page. Priming the cache in one query reduces page time from
1.8s to 210ms at p95.
```

Both explain the cause and the effect. Neither requires reading the diff to understand.

**Bad Example** — history that documents nothing

```
fix
update
wip
final fix
address review comments
asdf
```

Six months later, none of these can be reasoned about, and `git bisect` output naming one of
them tells you nothing.

**Bad Example** — a breaking change hidden as a patch

```
fix(api): clean up response format
```

If a field was renamed, this silently ships a breaking change as a patch release, and every
consumer breaks on an automatic upgrade.

## Common Mistakes

- No convention, so history is unfilterable and changelogs are manual.
- A convention documented but not enforced, holding for a month and then decaying.
- Breaking changes not marked, producing incorrect version bumps.
- Free-form scopes with no enum, giving `auth`, `Auth`, and `authentication`.
- The body used to restate the diff instead of explaining the reason.
- Issue references only in the pull request, so the commit alone lacks context.
- Squash-merge titles that ignore the convention, which is what actually lands on main.
- `chore:` used for everything, defeating the classification entirely.

## Production Tips

- Configure the platform to derive the squash-merge title from the pull request title, and
  lint the PR title with the same commitlint config — the merge commit is what history keeps.
- Pair with automated releases so version and changelog follow from the commits — see
  [Release Tools](28-release-tools.md).
- Use `commitizen` or an editor template if adoption is slow; the friction is real and a
  prompt removes it.
- Keep the type list short. Ten types is already more than most teams distinguish reliably.
- Reference the issue in a footer (`Closes #482`), not the subject — subjects should read as
  sentences.

## AI Review Checklist

- Is a convention defined, configured, and enforced by a `commit-msg` hook?
- Is `scope-enum` fixed to a known list?
- Are breaking changes marked with `!` or a `BREAKING CHANGE:` footer?
- Do bodies explain the reason rather than restate the diff?
- Is the squash-merge title linted with the same rules?
- Are issue references in footers?

## Related

- `knowledge/tools/16-git-hooks.md`
- `knowledge/tools/28-release-tools.md`
- `knowledge/tools/27-dependency-management.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/27-best-practices.md`
