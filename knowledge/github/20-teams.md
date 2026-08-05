---
id: github/20-teams
topic: github
slug: teams
title: "Teams"
type: doc
order: 20
status: ready
tags: [github, teams, CODEOWNERS, payments, platform, security, write]
related: [github/19-organizations, github/21-permissions, github/07-code-review, github/17-branch-protection, github/18-rulesets]
when_to_use: "Read before designing an organization's team hierarchy, code-owner routing, or IdP team sync."
---
# Teams

## Purpose

This document defines how to structure GitHub **teams** — the groups through which an
[organization](19-organizations.md) grants repository access and routes review. It is
written so an agent can design a team hierarchy that maps to how the company actually
works, without creating orphaned access or noisy review requests.

Teams are the *unit of access management*: you grant a team a role on a repository, and
membership follows people as they change roles. Done well, access is a byproduct of who
is on which team; done poorly, it is a pile of one-off grants nobody can audit.

## Why It Matters

Access granted to individuals rots — people move teams, projects end, and direct grants
are forgotten. Access granted to *teams* stays correct because it is tied to a role, not
a name: add someone to the `payments` team and they get exactly the repos that team owns;
remove them and it all goes away at once. Teams also drive **code review routing** via
`CODEOWNERS` and **required reviews** in [rulesets](18-rulesets.md). Get the hierarchy
wrong and you either over-grant (a child team inherits parent access it should not have)
or drown owners in review requests they cannot action.

## Core Principles

- **Grant to teams, not people.** Direct collaborator grants bypass your access model and
  become invisible standing access. Route every grant through a team.
- **Nesting inherits access downward.** A child team receives all repository access of its
  parents. Structure the tree so inheritance matches intent, never as a shortcut.
- **Sync membership from the IdP where possible.** Team sync (via SAML groups / SCIM)
  keeps membership authoritative in one place and removes people automatically.
- **Maintainers manage the team, not the code.** The team **maintainer** role controls
  membership and settings; it is independent of the repo role the team holds.
- **CODEOWNERS must reference teams that actually have write access.** A code-owner team
  without write on the repo cannot be a required reviewer and silently fails.

## Best Practices

- Model teams on **durable functions** (`platform`, `payments`, `security`) rather than
  transient projects, so the tree survives reorganizations.
- Use **nesting for inheritance you actually want**: a parent `engineering` team for
  broad read, child teams for write on their services. The cost of misuse is a child
  quietly inheriting parent write.
- Drive membership through **team sync** with your IdP; reserve manual membership for
  cases the directory cannot express, and document them.
- Put teams (not usernames) in **`CODEOWNERS`** so review routing survives staffing
  changes, and confirm each owner team has at least `write` on that path.
- Give each team one or two **maintainers** to keep membership current; do not make
  everyone a maintainer.
- Prefer **child teams** over duplicating access: if two teams need the same repos, a
  shared parent expresses it once.

## Examples

**Good Example** — team-based access and code-owner routing

```bash
# Create a team synced from the IdP group, then grant it access to a repo by role.
gh api --method POST /orgs/ACME/teams \
  -f name='payments' -f privacy='closed'          # 'closed' = visible to org, sync-eligible
gh api --method PUT /orgs/ACME/teams/payments/repos/ACME/billing \
  -f permission='push'                            # team gets write; members follow the team
```

```text
# .github/CODEOWNERS — route review to a team that HAS write on these paths
/services/billing/  @ACME/payments   # required reviewers resolve to current team members
*.tf                @ACME/platform   # infra changes need the platform team
```

**Bad Example** — individual grants and a broken owner

```bash
# Direct collaborator grant: invisible to the team model, forgotten when she moves teams.
gh api --method PUT /repos/ACME/billing/collaborators/alice -f permission='push'
```

```text
# CODEOWNERS points at a team with only READ access → it can never be a required reviewer,
# so "require review from code owners" passes with zero real review.
/services/billing/  @ACME/auditors
```

## Common Mistakes

- Adding individual collaborators to repos instead of granting through teams, creating
  standing access nobody audits.
- Using nesting as a shortcut and accidentally giving a child team its parent's write
  access to sensitive repos.
- Listing a team in `CODEOWNERS` that lacks write access, so required code-owner review
  is silently satisfied by nobody.
- Naming teams after temporary projects, so the tree is stale within a quarter.
- Managing membership by hand while an IdP group already exists, causing the two to drift.
- Making every member a maintainer, so membership changes go unreviewed.

## Production Tips

- Reconcile team membership against IdP groups on a schedule and alert on manual overrides.
- Audit `CODEOWNERS` in CI: fail the build if any owner reference is a team without write
  access or a nonexistent user.
- Use **secret/child teams** sparingly and document why each exists; visibility aids audit.

## AI Review Checklist

- Is every repository grant made to a team, with no ad-hoc individual collaborators?
- Does the nesting tree grant only the inheritance you intend (no accidental child write)?
- Is membership synced from the IdP, with manual exceptions documented?
- Does every `CODEOWNERS` team have at least write access on the paths it owns?
- Are teams named for durable functions rather than transient projects?
- Does each team have a named, limited set of maintainers?

## Related

- `knowledge/github/19-organizations.md`
- `knowledge/github/21-permissions.md`
- `knowledge/github/07-code-review.md`
- `knowledge/github/17-branch-protection.md`
- `knowledge/github/18-rulesets.md`
