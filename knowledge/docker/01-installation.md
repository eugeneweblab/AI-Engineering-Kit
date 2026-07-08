---
id: docker/01-installation
topic: docker
slug: installation
title: "Installation"
type: doc
order: 1
status: ready
tags: [docker, installation]
related: [docker/00-overview, docker/02-docker-architecture, docker/04-containers, docker/18-security, docker/21-development-workflow]
when_to_use: "Read before installing Docker on a new machine, CI runner, or server, or when diagnosing a broken install."
---
# Installation

## Purpose

This document defines how to install the Docker Engine correctly and verify it
works, on a developer machine, a CI runner, and a Linux server. It covers the choice
between Docker Desktop and the standalone Engine, post-install hardening, and the
one-command smoke test that proves the install is functional.

## Why It Matters

The install is where security posture and licensing are decided, often silently. On
Linux, the default socket grants root-equivalent access to anyone in the `docker`
group — an install detail with production consequences. Docker Desktop is a paid
product for larger organizations, so choosing it on a CI fleet can create a
compliance problem. Getting the install right once prevents a class of "permission
denied" and "unexpected billing" issues that are painful to unwind later.

## Core Principles

- **Match the install to the environment.** Docker Desktop for interactive dev on
  macOS/Windows; the standalone Engine (`docker-ce`) for Linux servers and CI.
- **Pin to a known version in automation.** Never `curl | sh` an unpinned installer
  into a reproducible pipeline; you cannot reason about what you deployed.
- **Verify before you build.** A `docker run hello-world` is the contract that the
  daemon, networking, and image pull all work end to end.
- **Adding a user to the `docker` group is granting root.** Treat it as a privileged
  decision, not a convenience toggle.

## Best Practices

- On Linux servers, install the official `docker-ce` package from Docker's apt/yum
  repository, not the distro's older `docker.io` package, so you get current,
  supported releases.
- Install the **Compose v2 plugin** (`docker compose`, a subcommand) rather than the
  legacy standalone `docker-compose` binary, which is end-of-life.
- Enable and start the daemon as a service (`systemctl enable --now docker`) so it
  survives reboots.
- In CI, prefer a base image or runner that ships Docker preinstalled, or install a
  pinned version; cache nothing security-sensitive in the runner image.
- Confirm the client and daemon versions with `docker version` — a mismatch (old
  client, new daemon) is a common source of confusing API errors.
- Understand Docker Desktop licensing: it requires a paid subscription for companies
  above Docker's size threshold. For rootless or license-free Linux dev, consider
  the standalone Engine or a compatible alternative.

## Examples

**Good Example** — pinned, verified Engine install on Debian/Ubuntu

```bash
# Install prerequisites and Docker's official GPG key + repo (details abbreviated).
# Then install a PINNED version so the build is reproducible across machines.
VERSION_STRING=5:27.3.1-1~ubuntu.24.04~noble
sudo apt-get install -y \
  docker-ce=$VERSION_STRING \
  docker-ce-cli=$VERSION_STRING \
  containerd.io \
  docker-compose-plugin        # gives us `docker compose`, the maintained v2

sudo systemctl enable --now docker   # start now AND on every boot

# The smoke test: proves daemon, registry pull, and container run all work.
docker run --rm hello-world
```

**Bad Example** — unpinned, unverified, silently grants root

```bash
# Pulls whatever the script decides today — not reproducible, can't audit it.
curl -fsSL https://get.docker.com | sudo sh

# Adds the CI user to the docker group with no acknowledgement that this is
# equivalent to passwordless root on the host. No version pin, no smoke test.
sudo usermod -aG docker "$USER"
# ...build proceeds assuming it "just works"; a broken pull surfaces mid-build.
```

## Common Mistakes

- Installing the distro's stale `docker.io` package and hitting bugs fixed years ago
  upstream.
- Using the deprecated `docker-compose` (hyphen) binary instead of the `docker
  compose` plugin, then finding features and fixes missing.
- Running `sudo docker ...` everywhere to dodge permissions, masking the fact that
  the daemon socket is misconfigured.
- Adding users to the `docker` group on a shared server without recognizing it as a
  root grant — see [18-security](18-security.md).
- Shipping Docker Desktop across an org's machines without checking the license.
- Skipping the `hello-world` smoke test, so networking or storage-driver failures
  first appear inside a real build.

## Production Tips

- On servers, prefer **rootless mode** or a hardened daemon config so a container
  escape does not equal host root; document the trade-offs with your platform team.
- Configure the daemon via `/etc/docker/daemon.json` (log driver, storage driver,
  registry mirrors, `live-restore`) rather than ad-hoc flags, so config is
  reviewable and versioned.
- Enable `live-restore` on single-node hosts so containers keep running during a
  daemon upgrade or restart.

## AI Review Checklist

- Is the install method appropriate for the environment (Desktop vs Engine)?
- Is the Docker version pinned in any automated/CI install?
- Is the maintained `docker compose` plugin used, not the legacy binary?
- Is `docker group` membership treated as a root-level privilege decision?
- Is there a `docker run hello-world` (or equivalent) verification step?
- Is Docker Desktop licensing considered for organizational use?

## Related

- `knowledge/docker/00-overview.md`
- `knowledge/docker/02-docker-architecture.md`
- `knowledge/docker/04-containers.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/21-development-workflow.md`
