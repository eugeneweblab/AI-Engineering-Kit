---
id: github/25-copilot
topic: github
slug: copilot
title: "Copilot"
type: doc
order: 25
status: ready
tags: [github, copilot]
related: [github/07-code-review, github/14-codeql, github/16-secret-scanning, github/24-codespaces, github/27-best-practices]
when_to_use: "Read before enabling GitHub Copilot for an org, or when reviewing code produced with AI assistance."
---
# Copilot

## Purpose

This document defines how to use **GitHub Copilot** — AI code completion, Copilot Chat, and
Copilot coding agents — safely inside a real engineering workflow. It covers reviewing
generated code, content exclusion, secret and license risk, and org-level policy. It does not
teach prompting; the concern here is that Copilot output is *untrusted input authored by a
model*, and it lands in your codebase with your name on the commit.

Copilot accelerates typing, not judgment. Every suggestion it emits must clear the same bar
as code written by a new contributor: reviewed, tested, and understood before merge. The
person who accepts a suggestion owns it.

## Why It Matters

Copilot generates plausible code, which is exactly the danger — it can be subtly wrong,
insecure, or licensed in a way you cannot ship, while looking correct. It may reproduce a
hardcoded secret pattern, an outdated API, an off-by-one, or a SQL string built by
concatenation. Because the output reads fluently, reviewers relax, and bugs that a human
would have hesitated to write sail through. On top of correctness, generated code can echo
public code (a licensing exposure) and prompts can send proprietary source to the service if
content exclusion is not configured. The failure mode is a codebase that looks fine and is
quietly full of unreviewed, unattributed, sometimes-vulnerable code.

## Core Principles

- **AI output is a draft, not an authority.** Read, understand, and test every suggestion
  before accepting. If you cannot explain why it is correct, do not merge it. The cost is
  time; the benefit is you do not ship code you do not understand.
- **Never accept secrets or credentials from a suggestion.** If Copilot completes an API key,
  connection string, or token, that value is wrong or leaked — delete it, never commit it.
- **Configure content exclusion before enabling org-wide.** Exclude paths holding secrets,
  proprietary algorithms, or regulated data so their content is not sent as context.
- **Enable the duplication filter to reduce license risk.** Blocking suggestions that match
  public code lowers the chance of importing incompatibly licensed snippets.
- **Keep the human review gate.** Copilot-authored PRs and agent changes still require human
  code review, CI, and branch protection — automation does not remove the reviewer.

## Best Practices

- Turn on **content exclusion** (repo and org level) for files matching secrets, `.env`,
  infra credentials, and any code you are contractually barred from sharing.
- Enable the **matching public code / duplication filter** so suggestions that reproduce
  public code verbatim are blocked, reducing licensing exposure.
- Treat Copilot PRs and **Copilot coding agent** changes as PRs: they must pass required
  status checks and human review under [branch protection](17-branch-protection.md).
- Use **Copilot Autofix** for code scanning alerts to draft fixes, but review each fix — an
  autofix is a suggestion, not a verified patch. See [codeql](14-codeql.md).
- Prefer a small, well-tested change you understand over a large generated block you skim;
  scope prompts narrowly and verify each piece.
- Choose the right plan tier (Business/Enterprise) for org policy control, audit, and the
  guarantee that prompts are not used to train the public model.
- Run secret scanning and CI on every branch so anything Copilot introduces is caught by the
  same gates as hand-written code.

## Examples

**Good Example** — generated code reviewed, parameterized, tested

```ts
// Copilot suggested a query; the author rewrote it to parameterize and added a test
// before accepting, because the raw suggestion concatenated user input.
async function findUser(email: string) {
  return db.query("SELECT id, name FROM users WHERE email = $1", [email]); // bound param
}

test("findUser escapes input", async () => {
  await expect(findUser("a'; DROP TABLE users;--")).resolves.toBeDefined(); // no injection
});
```

**Bad Example** — accepted verbatim, injectable, secret committed

```ts
// Accepted the raw suggestion without reading it: string-built SQL + a "helpful" default key.
async function findUser(email: string) {
  // Injectable: attacker-controlled email is concatenated straight into the query.
  return db.query(`SELECT * FROM users WHERE email = '${email}'`);
}
const OPENAI_KEY = "sk-proj-abc123..."; // Copilot completed a key pattern; committed as-is
```

## Common Mistakes

- Accepting suggestions without reading them, so unreviewed code enters the codebase.
- Committing a secret Copilot autocompleted instead of deleting it.
- Enabling Copilot org-wide without configuring content exclusion for sensitive paths.
- Leaving the duplication/public-code filter off, importing snippets with unclear licenses.
- Treating a Copilot coding-agent PR as pre-approved and skipping human review.
- Merging an Autofix suggestion without verifying it actually fixes the alert and breaks nothing.
- Using generated code the author cannot explain, then being unable to debug it later.

## Production Tips

- Set org policies on a Business/Enterprise plan: enforce content exclusion, the duplication
  filter, and disable features (e.g., agent) you do not want, so individual users cannot opt out.
- Review the Copilot **audit log** for policy changes and usage; confirm your plan excludes
  prompts from training and check the data-handling terms for regulated data.
- Keep required status checks and reviews on protected branches so AI-authored changes cannot
  bypass the gate.

## AI Review Checklist

- Was every accepted suggestion read, understood, and covered by a test?
- Is content exclusion configured for secrets and proprietary/regulated paths?
- Is the public-code duplication filter enabled to limit licensing risk?
- Do Copilot and agent PRs pass required checks and human review like any other PR?
- Are Autofix suggestions verified to resolve the alert without side effects?
- Are no secrets or credentials present in any accepted suggestion?
- Does the author understand the generated code well enough to maintain it?

## Related

- `knowledge/github/07-code-review.md`
- `knowledge/github/14-codeql.md`
- `knowledge/github/16-secret-scanning.md`
- `knowledge/github/24-codespaces.md`
- `knowledge/github/27-best-practices.md`
