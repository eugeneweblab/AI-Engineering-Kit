---
id: linux/10-ssh
topic: linux
slug: ssh
title: "SSH"
type: doc
order: 10
status: ready
tags: [linux, ssh, sudo]
related: [linux/09-networking, linux/17-security, linux/21-firewall, linux/04-users-and-groups, linux/23-automation]
when_to_use: "Read before configuring SSH access, keys, or hardening a server's remote login."
---
# SSH

## Purpose

This document defines how to configure SSH — the standard for remote shell access and
secure file transfer on Linux — so that access is authenticated by keys, resistant to
brute force, and scoped to least privilege. It is written so an agent can set up or review
SSH access without leaving a server open to the internet's constant login attempts.

SSH is the primary remote entry point to almost every Linux host, which makes its
configuration a direct extension of the host's [security](17-security.md) posture and its
[networking](09-networking.md) exposure. Get it wrong and every other control is moot.

## Why It Matters

Every internet-facing SSH port is under continuous automated attack; bots try common
username/password pairs around the clock. Password authentication turns that pressure into
a real risk, while a single stolen or reused private key hands over a shell. The failures
are quiet — a permissive config works exactly like a hardened one until the day it is
breached — so SSH is held to the same "assume hostile input" bar as authentication code.
The good news is that a handful of settings (keys only, no root login, correct file modes)
eliminate the overwhelming majority of the risk.

## Core Principles

- **Keys, not passwords.** Disable password authentication entirely once keys are in place.
  A key cannot be guessed the way a password can be brute-forced.
- **Protect the private key like a password.** It stays on the client, never leaves it,
  and is encrypted with a passphrase. A leaked private key is a leaked account.
- **No direct root login.** Log in as an unprivileged user and escalate with `sudo`, so
  every action is attributable and root is not a single guessable target.
- **File permissions are load-bearing.** SSH *refuses* keys and configs with loose modes:
  `~/.ssh` is `700`, private keys `600`, `authorized_keys` `600`. This is a feature, not an
  obstacle.
- **The host key is the server's identity.** A changed host key means either a legitimate
  rebuild or a man-in-the-middle. Never blindly accept it; verify.

## Best Practices

- Generate modern keys: `ssh-keygen -t ed25519` (compact, fast, strong). Use RSA only at
  `-b 4096` where ed25519 is unsupported. Always set a passphrase.
- Harden `sshd_config`: `PasswordAuthentication no`, `PermitRootLogin no`,
  `PubkeyAuthentication yes`, `KbdInteractiveAuthentication no`. Reload sshd after editing.
- Keep a second working session open when changing `sshd_config` and test the new setting in
  a fresh connection before closing the first — a bad reload can lock you out otherwise.
- Use an `~/.ssh/config` with per-host `IdentityFile`, `User`, and `IdentitiesOnly yes` so
  the client offers exactly one intended key instead of spraying every key it holds.
- Use an SSH agent (and agent forwarding only when necessary, or better `ProxyJump`) to
  avoid retyping passphrases without copying keys onto intermediate hosts.
- Scope keys tightly: for automation and Git, use a dedicated key with `command=` and
  `restrict` options in `authorized_keys`, not a full-shell key.

## Examples

**Good Example** — hardened server config and a scoped client config

```bash
# /etc/ssh/sshd_config.d/10-hardening.conf  (drop-in; survives package upgrades)
PasswordAuthentication no        # kill brute-forceable passwords entirely
PermitRootLogin no               # force login as a user, escalate via sudo
PubkeyAuthentication yes         # keys are the only accepted credential
KbdInteractiveAuthentication no  # close the interactive-password side door
# apply: sudo sshd -t && sudo systemctl reload ssh   # -t validates BEFORE reload

# ~/.ssh/config on the client
Host prod
    HostName 10.0.3.11
    User deploy
    IdentityFile ~/.ssh/id_ed25519_prod
    IdentitiesOnly yes           # offer ONLY this key, not every key in the agent
```

**Bad Example** — passwords on, root allowed, world-readable key

```bash
# sshd_config
PasswordAuthentication yes   # bots brute-force this 24/7
PermitRootLogin yes          # root is a single known target with a guessable password

# on the client
chmod 644 ~/.ssh/id_ed25519  # world-readable private key -> ssh refuses it anyway,
                             # and anyone on the box can copy it
ssh -o StrictHostKeyChecking=no root@server   # blindly trusts any host key -> MITM
```

## Common Mistakes

- Leaving `PasswordAuthentication yes`, keeping the host under permanent brute-force risk.
- Allowing `PermitRootLogin yes`, making root a single guessable target.
- Loose permissions on `~/.ssh`, keys, or `authorized_keys`, which SSH then rejects.
- Editing `sshd_config` without `sshd -t` and without a backup session, risking lockout.
- `StrictHostKeyChecking=no` or blindly accepting changed host keys, enabling MITM.
- Reusing one private key everywhere, or committing a private key to a repo.

## Production Tips

- Put SSH behind a bastion/jump host and reach internal machines with `ProxyJump`, so only
  one hardened host is exposed and agent keys never land on intermediates.
- Manage `authorized_keys` centrally (config management or a CA with short-lived
  certificates) so revoking access is one action, not a hunt across every host.
- Rate-limit and monitor: fail2ban or firewall rules plus alerting on auth failures turn a
  brute-force flood into a non-event. See [firewall](21-firewall.md).

## AI Review Checklist

- Is `PasswordAuthentication` disabled and `PubkeyAuthentication` the only method?
- Is `PermitRootLogin` set to `no`?
- Are keys ed25519 (or RSA 4096), passphrase-protected, and never committed?
- Are `~/.ssh`, private keys, and `authorized_keys` at `700`/`600`?
- Is `sshd_config` validated with `sshd -t` before reload, with a fallback session?
- Is host-key checking left enabled (no blanket `StrictHostKeyChecking=no`)?

## Related

- `knowledge/linux/09-networking.md`
- `knowledge/linux/17-security.md`
- `knowledge/linux/21-firewall.md`
- `knowledge/linux/04-users-and-groups.md`
- `knowledge/linux/23-automation.md`
