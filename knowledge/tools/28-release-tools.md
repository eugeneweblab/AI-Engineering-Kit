---
id: tools/28-release-tools
topic: tools
slug: release-tools
title: "Release Tools"
type: doc
order: 28
status: ready
tags: [tools, release-tools]
related: [tools/17-commit-conventions, tools/18-monorepo-tools, tools/27-dependency-management, tools/19-task-runners, tools/30-engineering-principles, cicd/00-overview]
when_to_use: "Read before automating versioning and publishing — choosing between Changesets and semantic-release, generating changelogs, or publishing packages from CI."
---
# Release Tools

## Purpose

This document defines how to automate releases: deriving version numbers, generating changelogs, and publishing from CI with credentials that never touch a developer's machine.

## Why It Matters

Manual releases fail in predictable ways: a version bumped in `package.json` but not tagged, a changelog written from memory a week later, a package published from a laptop with a stale build. Each is recoverable; together they mean nobody is confident about what is actually deployed.

Automation replaces judgment with a rule. The version follows from the changes, the changelog follows from the commits, and publishing follows from a merge.

## Core Principles

- **Version numbers are derived, not chosen.** They follow from the changes since the last release.
- **Changelogs are written when the change is made**, not assembled at release time from a diff.
- **Publish from CI.** A release built on a laptop is unreproducible, and a credential on a laptop is a credential that leaks.
- **Semantic versioning is a promise.** A major bump says "this breaks you" — honor it or the version number carries no information.

## Two Models

| | Changesets | semantic-release |
|---|---|---|
| Version derived from | Intent files an author writes | Commit messages |
| Best for | Monorepos, libraries, coordinated releases | Single packages, continuous delivery |
| Release cadence | Batched — a release PR accumulates changes | Every merge to main |
| Author effort | One file per user-facing change | Disciplined commit messages |
| Changelog quality | Higher — written for humans, at authoring time | Derived from commit subjects |

Changesets asks contributors to declare intent explicitly, which produces better changelogs and handles interdependent packages. semantic-release asks nothing beyond the commit convention, which suits a single package released continuously. Pick by whether you have multiple packages.

## Changesets

```bash
pnpm add -Dw @changesets/cli && pnpm changeset init
```

An author adds a changeset alongside the change:

```bash
pnpm changeset
# → select packages, select bump type, write the summary
```

```markdown
<!-- .changeset/lucky-pandas-shout.md -->
---
"@acme/ui": minor
"@acme/web": patch
---

Add `size` prop to `Button`, supporting `sm` and `lg` alongside the default.
`@acme/web` picks up the new prop on its checkout CTA.
```

That summary becomes the changelog entry verbatim, which is the point — it is written by the person who made the change, while the reasoning is fresh.

```json
// .changeset/config.json
{
  "$schema": "https://unpkg.com/@changesets/config/schema.json",
  "changelog": ["@changesets/changelog-github", { "repo": "acme/site" }],
  "commit": false,
  "access": "restricted",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": ["@acme/docs"]
}
```

CI turns accumulated changesets into a release PR, then publishes when it merges:

```yaml
# .github/workflows/release.yml
name: release
on:
  push:
    branches: [main]

concurrency: ${{ github.workflow }}-${{ github.ref }}

permissions:
  contents: write
  pull-requests: write
  id-token: write            # npm provenance

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version-file: '.nvmrc', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm verify

      - uses: changesets/action@v1
        with:
          version: pnpm changeset version    # opens/updates the release PR
          publish: pnpm changeset publish    # publishes when that PR merges
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_CONFIG_PROVENANCE: true
```

The release PR is the review surface: it shows the version bumps and the assembled changelog before anything is published.

## semantic-release

Version and changelog derive from Conventional Commits — see [Commit Conventions](17-commit-conventions.md), which is a hard prerequisite here.

```json
// .releaserc.json
{
  "branches": ["main", { "name": "beta", "prerelease": true }],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", { "changelogFile": "CHANGELOG.md" }],
    "@semantic-release/npm",
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]"
    }],
    "@semantic-release/github"
  ]
}
```

`fix` → patch, `feat` → minor, `BREAKING CHANGE:` → major. The consequence is that a mislabelled commit ships a wrong version number — which is why the commit-message hook matters more once this is in place.

## Publishing Safely

```json
// package.json — control what actually ships
{
  "name": "@acme/ui",
  "version": "0.0.0",
  "files": ["dist"],
  "exports": {
    ".": { "types": "./dist/index.d.ts", "import": "./dist/index.js" },
    "./styles.css": "./dist/styles.css"
  },
  "sideEffects": ["*.css"],
  "publishConfig": { "access": "public", "provenance": true },
  "scripts": { "prepublishOnly": "pnpm verify && pnpm build" }
}
```

Verify the artifact before trusting it:

```bash
npm pack --dry-run          # exactly what would be published
npx publint                 # packaging problems (exports, types, entry points)
npx @arethetypeswrong/cli   # whether consumers actually resolve your types
```

Missing type resolution and broken `exports` maps are the two defects that reach consumers most often, and both are invisible until someone installs the package.

**Use trusted publishing / OIDC where the registry supports it.** A short-lived token minted by CI is better than a long-lived npm token in repository secrets, and `provenance` gives consumers a verifiable link from package to source commit.

## Rollback

Publishing is close to irreversible. Unpublishing breaks anyone who already installed the version, so the recovery path is forward:

```bash
npm deprecate @acme/ui@1.4.2 "Broken exports map — use 1.4.3"
# then publish the fix as 1.4.3
```

For a package published by mistake with a secret in it, deprecation is not enough: rotate the secret first, then contact the registry. The secret is compromised the moment it is published, regardless of what happens to the package.

## Examples

**Good Example** — the changelog is a by-product of the commits

```bash
# Each change declares its own version impact, at the time it is written,
# by the person who knows.
pnpm changeset
# → which packages changed?  @acme/ui
# → what kind of change?     minor
# → summary:                 add `size` prop to Button
```

```yaml
# .github/workflows/release.yml — versioning and publishing are one reviewed PR.
- uses: changesets/action@v1
  with:
    version: pnpm changeset version   # bumps versions, writes CHANGELOG.md
    publish: pnpm changeset publish   # tags and publishes what the PR approved
  env:
    NPM_CONFIG_PROVENANCE: true       # signed provenance attestation
```

Interdependent packages are bumped together, the changelog is generated from the same
declarations, and the release is a diff someone approved.

**Bad Example** — versions edited by hand at release time

```bash
# The version bump, the tag, and the publish are three independent chances to
# be inconsistent — and this sequence publishes before the tag exists, so a
# failed push leaves a published version with no corresponding commit.
vim package.json          # 1.4.0 → 1.5.0
npm publish
git tag v1.5.0 && git push --tags
```

```markdown
<!-- CHANGELOG.md, written from memory after the fact -->
## 1.5.0
- Various improvements and bug fixes
```

A consumer cannot tell whether upgrading is safe. The one question a changelog exists to
answer is the one this does not answer.

---

## Common Mistakes

- Versions bumped by hand, drifting from tags and changelogs.
- Publishing from a developer machine with an unbuilt or stale `dist`.
- Long-lived registry tokens in CI secrets where OIDC is available.
- No `files` or `exports` field, shipping the entire repository.
- Changelogs generated from commit subjects when nobody follows the convention.
- Breaking changes released as minors because the commit was not marked.
- No `concurrency` guard, so two merges race and publish the same version.
- `npm unpublish` used as a rollback.
- Publishing without `publint` / `arethetypeswrong`, so consumers discover the packaging bug.

## Production Tips

- Release from `main` only, and require the full verify pipeline to pass first.
- Use prerelease channels (`beta`, `next`) for changes that need real-world validation before a stable tag.
- In a monorepo, let the tool handle interdependent bumps — hand-editing versions across packages is how mismatched releases happen. See [Monorepo Tools](18-monorepo-tools.md).
- Keep the changelog readable by humans: what changed and why it matters, not a list of commit hashes.
- Tag releases in git even when the registry is the source of truth; `git bisect` and incident triage both depend on it.

## AI Review Checklist

- Are version numbers derived by tooling rather than hand-edited?
- Is the changelog written at authoring time or generated from a convention that is actually enforced?
- Does publishing happen from CI, with short-lived credentials where available?
- Do `files` and `exports` limit and describe what ships?
- Is the artifact validated (`npm pack --dry-run`, `publint`) before release?
- Is there a `concurrency` guard on the release workflow?
- Is the rollback path forward — deprecate and re-release — rather than unpublish?

## Related

- `knowledge/tools/17-commit-conventions.md`
- `knowledge/tools/18-monorepo-tools.md`
- `knowledge/tools/27-dependency-management.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/cicd/00-overview.md`
