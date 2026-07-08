---
id: nginx/01-installation
topic: nginx
slug: installation
title: "Installation"
type: doc
order: 1
status: ready
tags: [nginx, installation]
related: [nginx/00-overview, nginx/02-configuration, nginx/23-docker, nginx/12-ssl-tls, nginx/25-production]
when_to_use: "Read before installing, upgrading, or containerizing nginx on a server."
---
# Installation

## Purpose

This document defines how to install nginx correctly for production: which package
source to use, how to verify what you got, and how to keep it current. The goal is a
supported, up-to-date build whose version and modules you can reason about — not
whatever an image happened to bundle three years ago.

## Why It Matters

The nginx binary is your TLS termination point and the process that parses every
untrusted byte from the internet. An outdated build carries unpatched CVEs in exactly
the code path attackers reach first. Distro-default packages also lag upstream by
months and sometimes omit modules you need (`http_v2`, `http_v3`, `stream`). Choosing
the wrong source once means every server you provision inherits the gap.

## Core Principles

- **Prefer the official nginx repository over distro defaults** for current versions
  and predictable module availability; the cost is one extra repo to trust and manage.
- **Pin and record the version.** Reproducible infrastructure requires knowing exactly
  which build runs where, so upgrades are deliberate, not accidental.
- **Verify what you installed.** Check the version and compiled-in modules before you
  rely on a feature; a config using an absent module fails only at reload time.
- **Keep it patched.** Track upstream stable releases and apply security updates on a
  schedule, because edge software is the highest-value target in your stack.

## Best Practices

- Use the **official nginx.org repository** (mainline for latest features, stable for
  conservative environments). Mainline is production-safe and gets fixes first.
- Confirm the build with `nginx -V` (capital V) — it prints version, OpenSSL version,
  and every `--with-*` module. Grep this before assuming a module exists.
- On containers, pin a specific tag (`nginx:1.27.3`) rather than `latest`, so image
  rebuilds are reproducible. See [Docker](23-docker.md).
- Run nginx as an unprivileged worker user (the default `nginx`/`www-data`); only the
  master process needs root, and only to bind ports below 1024.
- After install, immediately run `nginx -t` to validate the shipped default config,
  then enable and start the service.
- Automate installation with your provisioning tool; never hand-install production hosts.

## Examples

**Good Example** — official repo, version verified, pinned

```bash
# Add the official nginx stable repository (Debian/Ubuntu), keyring verified
curl -fsSL https://nginx.org/keys/nginx_signing.key \
  | gpg --dearmor -o /usr/share/keyrings/nginx-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] \
http://nginx.org/packages/debian $(lsb_release -cs) nginx" \
  > /etc/apt/sources.list.d/nginx.list

apt-get update && apt-get install -y nginx=1.27.3-1~$(lsb_release -cs)  # pin exact version
nginx -V           # verify version + compiled modules BEFORE relying on them
nginx -t           # validate config before first start
systemctl enable --now nginx
```

**Bad Example** — stale distro package, unverified, unpinned

```bash
apt-get install -y nginx   # whatever the distro shipped — often months behind upstream
systemctl start nginx      # no `nginx -t`; a broken default config fails silently at runtime
# never checked `nginx -V`, so a config using http_v2 may reference a module that isn't built
```

## Common Mistakes

- Installing the distro default and later discovering it lacks `http_v3` or `stream`.
- Skipping `nginx -V`, then writing config for a module that was never compiled in.
- Using the `latest` container tag, so a rebuild silently changes the nginx version.
- Running workers as root instead of the dedicated unprivileged user.
- Treating install as one-time; never applying upstream security patches afterward.

## Production Tips

- Track nginx security advisories and subscribe to the nginx-announce list.
- Keep the compiled module list in your infra docs so config reviewers know what exists.
- Test upgrades in staging; a new mainline release can change default behavior.
- For custom modules, prefer dynamic modules (`load_module`) over recompiling the core.

## AI Review Checklist

- Is nginx installed from the official repository (or a pinned, current image)?
- Is the exact version pinned and recorded in provisioning code?
- Was `nginx -V` used to confirm required modules are compiled in?
- Do workers run as an unprivileged user, with root only on the master?
- Is there a patching process for upstream security releases?

## Related

- `knowledge/nginx/00-overview.md`
- `knowledge/nginx/02-configuration.md`
- `knowledge/nginx/23-docker.md`
- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/25-production.md`
