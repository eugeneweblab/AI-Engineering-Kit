---
id: git/12-tags
topic: git
slug: tags
title: "Tags"
type: doc
order: 12
status: ready
tags: [git, tags, vMAJOR.MINOR.PATCH, v2.4.0, point, cutting, marking]
related: [git/16-push, git/13-remote-repositories, git/04-commits, git/22-git-flow, git/27-best-practices]
when_to_use: "Read before cutting a release or marking any commit as a permanent, referenceable point."
---
# Tags

## Purpose

This document defines how to mark a specific commit as a named, permanent reference —
a *tag* — most often to identify a release. It is written so an agent can create,
sign, and publish tags correctly, and never mutate one after it is public.

A tag names a commit; a [branch](05-branches.md) tracks a moving line of work. The
critical difference: a branch pointer advances with every commit, a tag pointer does
not. Treat a published tag as immutable — downstreams, CI, and package managers pin to
it and will silently break if it moves.

## Why It Matters

Tags are the anchors a release process, changelog, and rollback depend on. `v2.4.0`
must mean the same commit today, next year, and on every clone. If a tag is moved or
deleted after publication, every consumer that fetched it now has a different notion
of what that version is — reproducible builds break, `git describe` lies, and a
security patch may quietly point at unpatched code. The failure is silent and shows up
far from the change, so tag discipline is not optional for anything shipped.

## Core Principles

- **A published tag is immutable.** Once pushed, never move or delete it. If you got it
  wrong, cut a new version instead. Consumers pin to tags; moving one rewrites history
  they already trust.
- **Prefer annotated tags for releases.** An annotated tag is a real object with a
  tagger, date, message, and (optionally) a signature. A lightweight tag is just a
  bare pointer with no metadata — fine for a personal bookmark, wrong for a release.
- **Tags are not pushed by default.** `git push` sends commits, not tags. A tag only
  reaches the remote when you push it explicitly.
- **Sign release tags.** A GPG/SSH signature proves the tag came from an authorized
  releaser and was not forged or altered.
- **Follow one version scheme.** Adopt [Semantic Versioning](https://semver.org)
  (`vMAJOR.MINOR.PATCH`) and keep the prefix consistent so tooling can sort and match.

## Best Practices

- Create release tags annotated and signed: `git tag -s v1.4.0 -m "Release 1.4.0"`.
- Tag the exact commit that was built and tested, not "latest main" — pass the SHA
  explicitly when tagging after the fact: `git tag -s v1.4.0 <sha>`.
- Push the specific tag you meant to publish: `git push origin v1.4.0`. Avoid
  `--tags`, which dumps every local tag, including experiments.
- Verify signatures in CI before releasing: `git tag -v v1.4.0` must succeed.
- Keep tag names sortable and machine-parseable; do not mix `v1.2` and `release-1.2`.
- Delete a *local* mistake before it is pushed; once public, supersede it instead.
- Use `git describe --tags` to derive human-readable build versions from the nearest tag.

## Examples

**Good Example** — annotated, signed, pinned to a reviewed commit, pushed explicitly

```bash
# Tag the exact tested commit, not whatever HEAD happens to be now.
git tag -s v1.4.0 3f9a2c1 -m "Release 1.4.0"

# Verify the signature locally before it goes anywhere downstream.
git tag -v v1.4.0

# Publish only this tag — commits do not carry tags automatically.
git push origin v1.4.0
```

**Bad Example** — lightweight, unsigned, and mutated after publication

```bash
git tag v1.4.0                 # lightweight: no tagger, no message, no signature
git push origin v1.4.0         # published…

# …then "fix" the release by moving the tag:
git tag -f v1.4.0 HEAD         # -f rewrites the pointer
git push -f origin v1.4.0      # every consumer's v1.4.0 now means a different commit
```

## Common Mistakes

- Using a lightweight tag for a release, so there is no author, date, or signature.
- Forgetting to push the tag — the release exists locally but no one else can fetch it.
- Force-moving or deleting a published tag instead of cutting a new version.
- Tagging `main` after new commits landed, so the tag points past the tested commit.
- Pushing every local tag with `--tags`, leaking throwaway or internal tags.
- Inconsistent naming (`v1.2` vs `1.2.0` vs `rel_1.2`) that breaks sort and matching.

## Production Tips

- Automate tagging in the release pipeline from a reviewed commit, and let CI verify
  the signature before publishing artifacts.
- Protect tag namespaces on the host (branch/tag protection rules) so only the release
  pipeline or maintainers can push `v*` tags.
- Store the signing key in the CI secrets manager, not in a developer's shell profile.
- Generate changelogs from the commit range between two tags (`git log v1.3.0..v1.4.0`).

## AI Review Checklist

- Is the release tag **annotated and signed**, not lightweight?
- Does the tag point at the **exact commit that was built and tested**?
- Was the tag **pushed explicitly** (not left local, not dumped via `--tags`)?
- Is the version name **consistent** with the project's scheme (e.g. `vX.Y.Z`)?
- Is there **no force-move or delete** of an already-published tag?
- Does CI **verify the signature** before releasing artifacts?

## Related

- `knowledge/git/16-push.md`
- `knowledge/git/13-remote-repositories.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/22-git-flow.md`
- `knowledge/git/27-best-practices.md`
