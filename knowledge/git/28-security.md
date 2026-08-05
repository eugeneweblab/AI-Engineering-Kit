---
id: git/28-security
topic: git
slug: security
title: "Git Security"
type: doc
order: 28
status: ready
tags: [git, security]
related: [git/20-hooks, git/18-history, git/16-push, git/27-best-practices, git/13-remote-repositories]
when_to_use: "Read before committing anything sensitive, handling a leaked secret, or hardening a repository."
---
# Git Security

## Purpose

This document defines how to keep a Git repository secure: prevent secrets from entering
history, verify who authored and pushed commits, and respond correctly when something
sensitive leaks. It is written so an agent can commit and push without creating a security
incident, and can remediate one properly if it happens.

Git security has two faces: keeping bad data *out* (secrets, keys, PII) and proving the
*provenance* of what is in (signed commits, protected branches). Both matter because Git
history is permanent and widely copied.

## Why It Matters

A secret committed to Git is not "deleted" by a later commit — it lives in history, in
every clone, and in every fork and CI cache that ever pulled it. The moment it reaches a
shared remote you must treat it as compromised and rotate it, because you cannot know who
already cloned it. Provenance matters for the same permanence reason: an unsigned commit
can claim any author's name and email, so history alone does not prove who wrote a change.
In supply-chain terms, an attacker who can push an unsigned, unverified commit to your
default branch can ship malicious code under a trusted name.

## Core Principles

- **Secrets never enter Git.** Prevention is the only reliable control; removal after the
  fact is a [history rewrite](18-history.md) plus mandatory rotation.
- **A pushed secret is a compromised secret.** Rotate it immediately. Scrubbing history is
  necessary cleanup, not a substitute for rotation.
- **Author identity is a claim, not proof.** `user.name`/`user.email` are freely set. Only
  cryptographic signing (GPG, SSH, or Sigstore/gitsign) proves authorship.
- **The remote is the trust boundary.** Enforce protection server-side; anything a
  developer can bypass locally (`--no-verify`) is advisory, not a control.
- **Least privilege on access.** Deploy keys, tokens, and CI credentials get the narrowest
  scope and shortest life that works.

## Best Practices

- Keep secrets in a secrets manager or untracked `.env`, and list `.env`/`*.pem`/`*.key`
  in `.gitignore` so they cannot be staged by accident.
- Run a secret scanner (gitleaks, trufflehog) as a [pre-commit hook](20-hooks.md) *and* in
  CI, so a local bypass is still caught before merge.
- Sign commits and tags and require verification on the default branch. SSH signing
  (`gpg.format=ssh`) is the simplest to adopt in 2026.
- Authenticate to remotes over SSH keys or short-lived tokens, never a password or a
  long-lived PAT committed anywhere.
- Protect the default branch: require signed, reviewed commits and passing checks;
  disable force-push and deletion.
- If a secret leaks, rotate the credential first, then purge it from history with
  `git filter-repo` and force everyone to re-clone. Order matters — rotate before you
  clean.

## Examples

**Good Example** — block the secret before it is ever committed

```bash
# .gitignore keeps env and key material unstageable.
printf ".env\n*.pem\n*.key\n" >> .gitignore

# Pre-commit secret scan; refuses the commit if a key is detected.
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
gitleaks protect --staged --redact || {
  echo "Secret detected in staged changes — commit blocked."; exit 1; }
EOF
chmod +x .git/hooks/pre-commit

# Sign commits so authorship is provable.
git config gpg.format ssh
git config user.signingkey ~/.ssh/id_ed25519.pub
git config commit.gpgsign true
```

**Bad Example** — leak, then pretend a later commit fixed it

```bash
git add config/prod.env           # contains a live database password
git commit -m "add prod config"
git push origin main              # secret is now in the remote and every clone/fork

# "Fixing" it by deleting the file in a new commit.
git rm config/prod.env
git commit -m "remove secret" && git push
# The password is STILL in history at the earlier commit — and was never rotated.
```

## Common Mistakes

- Committing `.env`, private keys, or tokens because `.gitignore` was incomplete.
- Believing a follow-up commit that deletes a secret removes it — the old commit still
  holds it.
- Cleaning history but forgetting to rotate the leaked credential (or vice versa).
- Trusting `user.email` as identity without commit signing.
- Enforcing hooks only locally, where `git commit --no-verify` bypasses them.
- Long-lived personal access tokens with broad scope stored in CI config or dotfiles.

## Production Tips

- Enable the host's push protection / secret scanning (GitHub, GitLab) as a backstop to
  your own hooks.
- Rotate signing keys and deploy tokens on a schedule; keep them in a secrets manager.
- Audit access regularly: remove stale collaborators, deploy keys, and machine tokens.
- After a leak, assume exposure from the push timestamp forward and monitor the rotated
  credential for abuse.

## AI Review Checklist

- Are secrets kept out of Git via `.gitignore` and a secret scanner (local *and* CI)?
- If a secret was ever pushed, was the credential rotated *and* history purged?
- Are commits and tags signed, with verification required on the default branch?
- Are remotes authenticated with SSH keys or short-lived scoped tokens, not passwords?
- Is the default branch protected against force-push and unreviewed commits?
- Are access, deploy keys, and tokens scoped to least privilege and rotated?

## Related

- `knowledge/git/20-hooks.md`
- `knowledge/git/18-history.md`
- `knowledge/git/16-push.md`
- `knowledge/git/27-best-practices.md`
- `knowledge/git/13-remote-repositories.md`
