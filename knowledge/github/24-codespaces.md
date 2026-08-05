---
id: github/24-codespaces
topic: github
slug: codespaces
title: "Codespaces"
type: doc
order: 24
status: ready
tags: [github, codespaces, GITHUB_TOKEN, DATABASE_URL, features, Dockerfile]
related: [github/16-secret-scanning, github/21-permissions, github/23-cli, github/02-repositories, github/27-best-practices]
when_to_use: "Read before defining a devcontainer, adding Codespaces secrets, or reviewing a cloud dev-environment setup."
---
# Codespaces

## Purpose

This document defines how to configure and secure **GitHub Codespaces** — cloud
development environments defined by a `devcontainer.json` and run on GitHub-hosted
machines. It covers the container definition, secret handling, the codespace's `GITHUB_TOKEN`
scope, prebuilds, and cost controls. It does not cover CI ([actions](08-actions.md)); a
Codespace is an *interactive developer environment*, not a build runner, and the security
model differs — a human is inside it with a live token.

A Codespace is a full machine with your source, your dependencies, and a token that can
talk to GitHub. Configure it so a new contributor gets a working, reproducible environment
in one click, and so a leaked secret or malicious `postCreateCommand` cannot escalate.

## Why It Matters

The `devcontainer.json` is executable configuration: its lifecycle hooks
(`postCreateCommand`, `postStartCommand`) run arbitrary shell on every codespace creation.
If that file — or a dependency it installs — is malicious, it runs with the developer's
codespace token and access to any secrets you injected. Codespaces also bill by the
compute-minute and by storage, so an unbounded machine type or a missing idle timeout
quietly burns spend. Because the environment is disposable and often trusted implicitly,
mistakes here leak credentials and money at the same time.

## Core Principles

- **Pin the environment, don't drift it.** Base the container on a specific image tag or
  `Dockerfile`, not `latest`, so every developer gets the same toolchain. The cost is
  manual bumps; the benefit is "works on my machine" stops being a class of bug.
- **Never commit secrets into the devcontainer.** Secrets belong in Codespaces secrets
  (encrypted, injected as env vars), never in `devcontainer.json`, `.env` files, or
  lifecycle scripts. The repo is world-readable to collaborators.
- **Scope the codespace token to least privilege.** The built-in `GITHUB_TOKEN` permissions
  are declarable in `devcontainer.json`; grant only the repos and scopes the work needs.
- **Treat lifecycle hooks as code you run with your credentials.** Audit any command that
  `curl | bash` or installs from an unpinned source — it executes before you review it.
- **Design for disposability.** A codespace should be reproducible from the repo alone.
  Anything that only exists inside a running codespace is lost and should not be relied on.

## Best Practices

- Define a `devcontainer.json` checked into the repo so the environment is versioned and
  reviewable; pin the base image by digest or explicit tag (`mcr.microsoft.com/devcontainers/
  typescript-node:1-20`, not `:latest`).
- Store per-user secrets as **Codespaces secrets** (user or org level) and reference them as
  environment variables; scope org secrets to specific repositories.
- Set `hostRequirements` and choose the smallest machine type that works; enable an
  organization **idle timeout** and **retention period** to stop paying for stopped machines.
- Use **prebuilds** for large repos so `postCreateCommand` (install, build) is cached — new
  codespaces start in seconds instead of minutes.
- Declare `customizations.vscode.extensions` and pinned tool versions in `features` so tooling
  is consistent, not whatever the developer happens to have installed.
- Restrict which base images and which repos can open codespaces at the org level; set a
  **spending limit** so a runaway cannot exceed budget.
- Keep dotfiles opt-in and audited — a personal dotfiles repo runs its install script inside
  every codespace with your token.

## Examples

**Good Example** — pinned image, secrets as env vars, least-privilege token

```jsonc
// .devcontainer/devcontainer.json
{
  "name": "api",
  "image": "mcr.microsoft.com/devcontainers/typescript-node:1-20", // pinned tag, not :latest
  "features": {
    "ghcr.io/devcontainers/features/aws-cli:1": {}                 // versioned feature
  },
  "postCreateCommand": "npm ci",     // reproducible install from lockfile, no network scripts
  "secrets": {
    "DATABASE_URL": { "description": "Injected from Codespaces secret, never committed" }
  },
  "customizations": {
    "codespaces": {
      // Token can only read this repo; it cannot push to others or read org secrets.
      "repositories": { "acme/api": { "permissions": { "contents": "read" } } }
    }
  }
}
```

**Bad Example** — mutable image, secret in the repo, broad token

```jsonc
{
  "name": "api",
  "image": "node:latest",                     // drifts; today's build ≠ tomorrow's
  // Secret committed in plaintext — readable by every collaborator and in git history.
  "containerEnv": { "DATABASE_URL": "postgres://admin:hunter2@db.internal/prod" },
  "postCreateCommand": "curl https://get.example.com/setup.sh | bash", // unpinned RCE
  "customizations": {
    "codespaces": { "repositories": { "*": { "permissions": "write" } } } // token can write everything
  }
}
```

## Common Mistakes

- Basing the container on `latest` or an untagged image, so environments silently drift.
- Committing connection strings, tokens, or `.env` files instead of using Codespaces secrets.
- `curl | bash` in a lifecycle hook from an unpinned URL, running unreviewed code with the token.
- Granting the codespace token write access to all repos when it needs read on one.
- No idle timeout or spending limit, so stopped machines and storage accrue cost indefinitely.
- Relying on manual setup steps a developer runs by hand instead of encoding them in the container.
- Pointing production databases and secrets at a developer's interactive environment.

## Production Tips

- Enable **prebuilds** on the default branch and the branches contributors fork from; monitor
  prebuild failures, because a broken prebuild silently falls back to a slow cold start.
- Set org-level policies: allowed machine types, idle timeout, retention days, and a spending
  limit — defaults are permissive and bill by the minute.
- Point codespaces at seeded/synthetic data or short-lived least-privilege credentials, never
  production secrets.
- Turn on **secret scanning** for the repo so a credential accidentally written into the
  devcontainer or a script is caught. See [secret-scanning](16-secret-scanning.md).

## AI Review Checklist

- Is the base image pinned to a specific tag or digest rather than `latest`?
- Are all secrets injected via Codespaces secrets, with none committed to the repo?
- Do lifecycle hooks avoid piping unpinned remote scripts into a shell?
- Is the codespace `GITHUB_TOKEN` scoped to the minimum repos and permissions?
- Are an idle timeout, retention period, and spending limit configured at the org level?
- Are prebuilds used for large repos to keep startup fast and deterministic?
- Does the environment point at synthetic data, not production credentials?

## Related

- `knowledge/github/16-secret-scanning.md`
- `knowledge/github/21-permissions.md`
- `knowledge/github/23-cli.md`
- `knowledge/github/02-repositories.md`
- `knowledge/github/27-best-practices.md`
