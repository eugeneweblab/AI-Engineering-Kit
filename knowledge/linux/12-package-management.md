---
id: linux/12-package-management
topic: linux
slug: package-management
title: "Linux Package Management"
type: doc
order: 12
status: ready
tags: [linux, package-management]
related: [linux/17-security, linux/25-production, linux/23-automation, linux/22-containers]
when_to_use: "Read before installing software, writing a Dockerfile, or scripting provisioning on a Linux host."
---
# Linux Package Management

## Purpose

This document defines how to install, update, and remove software on Linux in a way
that is reproducible, secure, and safe to run unattended. It covers the system package
managers (`apt`, `dnf`, `apk`), package pinning, and the boundary between OS packages
and language-level packages. It is written so an agent can provision a host or write a
Dockerfile without introducing drift, breakage, or a supply-chain hole.

## Why It Matters

A package manager mutates the running system. A careless command can silently upgrade a
kernel, replace a config file, or pull an unverified binary that runs as root. Because
installs are often scripted into images and provisioning, one bad line is reproduced
across every host and every build. The failures are also delayed: `apt upgrade` today
breaks a service three deploys from now. Treat every install command as production code.

## Core Principles

- **Never install interactively in automation.** Scripts and Dockerfiles must pass
  non-interactive flags so a prompt cannot hang a build forever.
- **Update the index in the same layer you install.** A stale package index installs
  stale, possibly vulnerable versions.
- **Pin what must be reproducible, float what must be patched.** Application dependencies
  should be pinned; security-critical base packages should track patches.
- **Verify provenance.** Only add repositories and keys you trust, over HTTPS, with the
  signing key verified — a repo you add can run code as root on every update.
- **Clean up in the same step.** Leftover caches and index files bloat images and leak
  the exact package set to anyone who reads the layer.

## Best Practices

- On Debian/Ubuntu use `apt-get` (stable CLI) in scripts, not `apt` (human-facing UI
  that prints warnings about its unstable interface).
- Always combine index update and install: `apt-get update && apt-get install -y ...`.
  A separate cached `update` layer defeats the point.
- Use `DEBIAN_FRONTEND=noninteractive` and `--no-install-recommends` to keep installs
  deterministic and minimal.
- Pin exact versions for reproducibility (`nginx=1.26.*`) where drift would break you;
  document why. Unpinned installs make two builds a week apart non-identical.
- Do not mix package managers for the same software (e.g. distro `nodejs` plus a
  Nodesource repo) — you get two versions and undefined `PATH` resolution.
- Keep OS packages and language packages separate: use `apt`/`dnf` for system libraries,
  and `pip`/`npm`/`cargo` for application code. Never `pip install --user` as root into
  the system Python.
- Run `unattended-upgrades` (Debian) or `dnf-automatic` for security patches on
  long-lived hosts; reboot when the kernel or glibc changes.

## Examples

**Good Example** — deterministic, minimal, cleaned up in one layer

```dockerfile
# Single RUN: index update and install share a layer, so the index is never stale.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates=* \
        curl=7.88.* && \
    rm -rf /var/lib/apt/lists/*   # drop the index so the image stays small
```

**Bad Example** — interactive, stale, and bloated

```dockerfile
RUN apt-get update                 # cached in its own layer — goes stale
RUN apt-get install curl           # no -y: hangs waiting for a prompt in CI
                                   # no version pin: two builds differ silently
                                   # cache left in /var/lib/apt/lists: image is fat
```

## Common Mistakes

- Splitting `apt-get update` and `apt-get install` into separate Docker layers, so a
  cached update installs outdated packages.
- Omitting `-y`/`--yes`, causing scripted installs to hang on a confirmation prompt.
- Piping a remote script straight into a root shell (`curl … | sudo bash`) without
  reading it or verifying a checksum — arbitrary code execution as root.
- Adding a third-party repo without importing and verifying its GPG key.
- Running `apt-get upgrade` blindly in a Dockerfile, making the image non-reproducible.
- Using `pip`/`npm` as root to write into system directories, then fighting permission
  and version conflicts later.

## Production Tips

- Cache and mirror packages internally (`apt-cacher-ng`, a private registry) so a
  deploy does not depend on an upstream mirror being up.
- Track installed versions in your image manifest and scan images for known CVEs
  (`trivy`, `grype`) in CI; fail the build on critical findings.
- Schedule and stage security updates; never let `unattended-upgrades` restart a
  database mid-transaction. Coordinate reboots with your orchestration.
- Prefer minimal base images (`-slim`, `distroless`) so there is less to patch.

## AI Review Checklist

- Do install commands pass `-y`/non-interactive flags so they cannot hang?
- Is `apt-get update` in the same `RUN`/step as the install it feeds?
- Are third-party repos added over HTTPS with a verified signing key?
- Are versions pinned where reproducibility matters, and is the reason documented?
- Is the package cache removed in the same layer to keep images small?
- Are OS packages and language packages kept in their own managers?
- Is there a patch strategy (`unattended-upgrades`/scanning) for long-lived hosts?

## Related

- `knowledge/linux/17-security.md`
- `knowledge/linux/25-production.md`
- `knowledge/linux/23-automation.md`
- `knowledge/linux/22-containers.md`
