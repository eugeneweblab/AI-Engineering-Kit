---
id: github/19-organizations
topic: github
slug: organizations
title: "Organizations"
type: doc
order: 19
status: ready
tags: [github, organizations, none, GITHUB_TOKEN, write]
related: [github/20-teams, github/21-permissions, github/18-rulesets, github/28-enterprise, github/13-security]
when_to_use: "Read before configuring an organization's membership, base permissions, SSO, or security policy."
---
# Organizations

## Purpose

This document defines how to configure a GitHub **organization** — the shared account
that owns repositories, [teams](20-teams.md), and members — so access is least-privilege
by default and does not depend on any single person's account. It is written so an agent
can set up or review org settings without leaving the account open to takeover or
accidental over-sharing.

An organization is the security boundary: base permissions, [rulesets](18-rulesets.md),
SSO, and IP policy all apply org-wide. Get the org right and every repository inherits a
safe floor; get it wrong and every repository inherits the hole.

## Why It Matters

The organization owns your code, not the individuals in it — so its configuration
decides who can read every private repo, who can create or delete repositories, and who
keeps access after they leave the company. Two settings dominate the blast radius:
**base permissions** (what every member gets on every repo) and the **owner** role
(unrestricted control). Set base permissions too high and a new hire can read the entire
codebase on day one; leave a single human owner and losing that account can lock out or
compromise the whole org. These are quiet, standing risks, not runtime errors.

## Core Principles

- **Base permission is a floor applied to everyone.** Set it to `none` (or `read` only
  if genuinely everyone needs everything) and grant access through [teams](20-teams.md).
- **Owners are unrestricted — minimize them.** Owner can delete repos, change billing,
  and read all private code. Keep two or three, secured with MFA, ideally SSO-bound.
- **Identity should flow from your IdP.** With SAML SSO and SCIM, membership and
  deprovisioning are driven by the directory, so a departing employee loses access
  automatically instead of by a manual checklist.
- **Enforce controls at the org, not per repo.** MFA requirement, IP allow lists,
  default rulesets, and Actions policy belong at the org so new repos are covered on
  creation.
- **Outside collaborators are not members.** They get only the repos you name and never
  inherit base permissions — prefer them for contractors over full membership.

## Best Practices

- Set **organization base permissions to `none`**; grant every repository through a team
  with an explicit role. The cost is more up-front team setup; the payoff is that no
  access is implicit.
- **Require two-factor authentication** for all members and outside collaborators at the
  org level. Configure SAML SSO and **SCIM** so joins and leaves are automatic.
- Verify your **domains** so commits and org identity are trusted, and restrict member
  email visibility to the verified domain where compliance requires it.
- Restrict **repository creation** and **repository deletion** to owners or a named team;
  restrict who can change repo **visibility** (private → public is a data-exfil path).
- Set an org-wide **Actions policy**: allow only trusted actions (GitHub-authored plus a
  pinned allow-list), and default the `GITHUB_TOKEN` to read-only permissions.
- Configure an **IP allow list** if your compliance model requires it, and remember to
  include your CI/CD and integration egress ranges.
- Assign an org **security manager** team read access to security alerts across all repos
  without granting write access to code.

## Examples

**Good Example** — least-privilege org bootstrap via API

```bash
# Base permission is 'none': membership grants nothing until a team assigns a role.
gh api --method PATCH /orgs/ACME \
  -f default_repository_permission=none \
  -F members_can_create_repositories=false \       # only owners/named team create repos
  -F members_can_create_public_repositories=false \ # public repos require deliberate action
  -F two_factor_requirement_enabled=true \          # MFA enforced org-wide
  -f default_workflow_permissions=read              # GITHUB_TOKEN read-only by default
# Access is then granted per team, e.g. team 'payments' → repo 'billing' as 'write'.
```

**Bad Example** — permissive defaults, implicit access

```bash
gh api --method PATCH /orgs/ACME \
  -f default_repository_permission=write \  # every member can push to EVERY repo
  -F members_can_create_public_repositories=true \ # anyone can publish private code
  -F two_factor_requirement_enabled=false          # accounts protected by password alone
# No SSO/SCIM: a departing employee keeps org access until someone remembers to remove them.
```

## Common Mistakes

- Leaving base permission at `read` or `write`, so membership silently grants access to
  every repository including ones the person should never see.
- Keeping a single owner (bus factor and lockout risk) or, conversely, dozens of owners.
- Not enforcing MFA org-wide, so one phished password compromises the account.
- Skipping SCIM, so offboarding relies on humans and stale access accumulates.
- Allowing members to create public repositories, opening a private-to-public leak path.
- Adding contractors as full members instead of scoped outside collaborators.

## Production Tips

- Audit membership and owners quarterly; export via the API and diff against your HR
  directory to catch drift.
- Turn on the org **audit log streaming** to your SIEM so permission and settings changes
  are observable, not just visible in the UI.
- Use org-level default [rulesets](18-rulesets.md) so protection exists the moment a repo
  is created, not after review.

## AI Review Checklist

- Is the org base permission `none` (or the lowest that works), with access via teams?
- Is MFA required org-wide, and is SSO/SCIM wired to the IdP for auto-deprovisioning?
- Is the owner count small, MFA-protected, and documented?
- Are repository creation, deletion, and visibility changes restricted?
- Is the Actions policy locked to an allow-list with a read-only default token?
- Are contractors outside collaborators rather than members?
- Is the audit log streamed somewhere durable for review?

## Related

- `knowledge/github/20-teams.md`
- `knowledge/github/21-permissions.md`
- `knowledge/github/18-rulesets.md`
- `knowledge/github/28-enterprise.md`
- `knowledge/github/13-security.md`
