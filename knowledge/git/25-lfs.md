---
id: git/25-lfs
topic: git
slug: lfs
title: "LFS"
type: doc
order: 25
status: ready
tags: [git, lfs]
related: [git/24-monorepo, git/18-history, git/03-repository, git/28-security, git/13-remote-repositories]
when_to_use: "Read before adding large binaries, media, models, or datasets to a Git repository."
---
# LFS

## Purpose

This document defines how to use Git Large File Storage (LFS) to keep big binary files
out of the main Git object store while still versioning them. It covers when to adopt
LFS, how to configure tracking correctly, and the migration and hosting pitfalls that
break clones. It is written so an agent can add large assets without permanently bloating
a repository.

Git LFS replaces large files in the working tree with small text *pointer* files, and
stores the real bytes on a separate LFS server, fetched on demand. Regular Git stores a
full copy of every version of every file forever; LFS is how you avoid that for binaries.

## Why It Matters

Git is built for text: it diffs and compresses line-based content. A binary that changes
by one byte is stored as a whole new object, and every version stays in history for the
life of the repo — inflating every clone and fetch permanently. You cannot fix this by
deleting the file later; the bytes are still in old commits. LFS matters because the
decision is effectively irreversible: commit a 2 GB dataset directly and the only cure is
a coordinated [history rewrite](18-history.md) that invalidates everyone's clone. Getting
tracking right *before* the first commit is far cheaper than any cleanup.

## Core Principles

- **Track by pattern before committing, not after.** `git lfs track` must be in place and
  the `.gitattributes` committed *before* the binary lands, or the raw bytes enter
  history and LFS cannot retroactively remove them.
- **LFS versions binaries; it does not diff them.** You get history and dedup by object,
  but not meaningful line diffs. That is expected — binaries have no line semantics.
- **The pointer is the source of truth in Git.** What Git stores is a tiny text pointer;
  the real content lives on the LFS endpoint. A clone without LFS access gets pointers,
  not files.
- **Bandwidth and storage move, they do not vanish.** LFS keeps the Git history lean but
  the bytes still cost storage and transfer on the LFS server, often metered.
- **Prevention over cleanup.** A server-side size hook that blocks large non-LFS files is
  worth more than any migration tool.

## Best Practices

- Install once per machine (`git lfs install`) and track by extension, not by path, so new
  files of that type are captured automatically: `git lfs track "*.psd"`.
- Commit `.gitattributes` in the same or an earlier commit than the assets it governs, so
  every clone applies the same tracking rules.
- Verify what is actually in LFS with `git lfs ls-files` before pushing — a common failure
  is assuming a file is tracked when the pattern missed it.
- For repos that already contain big blobs, migrate history with
  `git lfs migrate import --include="*.zip"` in a coordinated, announced rewrite.
- Use `GIT_LFS_SKIP_SMUDGE=1` on clone for CI jobs that do not need the binaries, then
  `git lfs pull` only the paths a job actually uses.
- Confirm the host supports LFS and check quota. Mirrors and archive downloads
  (`git archive`, some CI caches) may not fetch LFS content — plan for it.

## Examples

**Good Example** — track before the first commit

```bash
git lfs install                      # one-time per machine

# Register the pattern and commit the rule FIRST.
git lfs track "*.psd" "*.mp4"
git add .gitattributes
git commit -m "chore: track design and video assets with LFS"

# Now the binary is stored as an LFS object; Git holds only a pointer.
git add hero.psd
git commit -m "assets: add hero mockup"
git lfs ls-files                     # verify: hero.psd shows as an LFS entry
```

**Bad Example** — commit first, "fix" later

```bash
# Binary committed straight into Git history — full bytes now permanent.
git add dataset.zip                  # 1.8 GB blob enters the object store
git commit -m "add dataset"

# Adding LFS tracking now does NOT remove the bytes already in history.
git lfs track "*.zip"                # every clone still downloads the 1.8 GB blob
git add .gitattributes && git commit -m "track zip"   # too late
```

## Common Mistakes

- Committing the binary before adding the `git lfs track` pattern, leaving raw bytes in
  history that tracking cannot reclaim.
- Forgetting to commit `.gitattributes`, so tracking works on your machine but nobody
  else's clone applies it.
- Assuming `git lfs migrate` on a shared repo is safe — it rewrites history and requires
  every collaborator to re-clone.
- Pushing to a host or mirror that does not support LFS, producing clones full of pointer
  files that resolve to nothing.
- Blowing through metered LFS bandwidth/storage because CI clones full binaries it never
  uses.
- Trying to `git diff` an LFS binary and expecting a line diff.

## Production Tips

- Add a pre-receive hook that rejects non-LFS files over a size threshold — the single
  most effective guard against repeated bloat.
- Prune old LFS objects the server no longer needs with `git lfs prune` to reclaim space.
- Cache LFS objects in CI to avoid re-downloading the same asset on every pipeline run.
- Store credentials for the LFS endpoint in the CI secrets store, never in the repo or
  `.lfsconfig`.

## AI Review Checklist

- Is `git lfs track` (and a committed `.gitattributes`) in place before any binary is
  committed?
- Does `git lfs ls-files` confirm the intended files are actually LFS-managed?
- Is `.gitattributes` committed so all clones share the tracking rules?
- Does the host support LFS, and is quota/bandwidth accounted for in CI?
- For pre-existing blobs, is migration done as a coordinated, announced history rewrite?
- Is there a server-side size guard to prevent future large non-LFS commits?

## Related

- `knowledge/git/24-monorepo.md`
- `knowledge/git/18-history.md`
- `knowledge/git/03-repository.md`
- `knowledge/git/28-security.md`
- `knowledge/git/13-remote-repositories.md`
