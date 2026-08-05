---
id: github/14-codeql
topic: github
slug: codeql
title: "CodeQL"
type: doc
order: 14
status: ready
tags: [github, codeql, pull_request, runs-on, schedule, write-all]
related: [github/13-security, github/09-workflows, github/17-branch-protection, github/07-code-review, github/15-dependabot]
when_to_use: "Read before enabling code scanning or writing a CodeQL workflow for a repository."
---
# CodeQL

## Purpose

This document defines how to run **CodeQL**, GitHub's static analysis engine, as the
"detect" layer for vulnerabilities in your own source code — SQL injection, XSS, path
traversal, unsafe deserialization, and similar. It covers the two setup modes (default vs.
advanced), tuning query suites, handling results in the Security tab, and — critically —
turning findings into a merge gate rather than a dashboard nobody reads.

CodeQL analyzes *your code*. It is complementary to [Dependabot](15-dependabot.md) (which
covers *dependencies*) and [secret scanning](16-secret-scanning.md) (which covers *leaked
credentials*). All three together are "code scanning + supply chain + secrets."

## Why It Matters

Most exploitable bugs are introduced during normal feature work by developers who are not
thinking about the attacker's path — a string concatenated into a query, user input echoed
into HTML. Human review misses these consistently because the dangerous data flow spans
several functions and files. CodeQL models the code as a queryable database and traces
tainted data from source to sink automatically, catching the flows a reviewer's eye skips.
Run on every PR, it stops whole vulnerability classes before they merge — but only if it
actually blocks the merge.

## Core Principles

- **Analyze on every pull request, not just a nightly scan.** The value is catching the
  vulnerability before it lands, while the author still has context to fix it.
- **A finding must gate the merge.** Configure code scanning as a required status check;
  an advisory-only alert list is noise that trains people to ignore it.
- **Tune to the highest severity you will act on.** Start with the `security-extended`
  suite for real coverage; dismiss with a documented reason, never by muting the tool.
- **Triage every alert to a terminal state.** Fix, or dismiss as false-positive / won't-fix
  with justification. An unbounded open-alert backlog is the same as no scanning.
- **Scanning is detection, not prevention.** It finds bugs; it does not stop you from
  writing them. Pair it with secure defaults and review.

## Best Practices

- Use **default setup** for standard repos — GitHub picks languages, queries, and schedule
  automatically and keeps the workflow updated. Switch to **advanced setup** (a committed
  `codeql-analysis.yml`) only when you need custom build steps, query packs, or matrices.
- Trigger on `pull_request` to the protected branch plus a weekly `schedule`, so new
  queries re-scan old code as CodeQL's query database improves.
- Give the analysis job `security-events: write` (to upload results) and `contents: read`
  — nothing more.
- Select the `security-extended` query suite for meaningful coverage; add
  `security-and-quality` only if the team will triage the extra maintainability alerts.
- For compiled languages, ensure the build actually compiles the code you want analyzed —
  CodeQL only sees code that is built.
- Make "Code scanning results / CodeQL" a required check in
  [branch protection](17-branch-protection.md).

## Examples

**Good Example** — PR-triggered analysis, extended queries, least privilege

```yaml
# .github/workflows/codeql.yml
on:
  pull_request: { branches: [main] }
  schedule: [{ cron: '0 3 * * 1' }]   # weekly re-scan with the latest queries
permissions:
  contents: read
  security-events: write              # scoped to uploading scan results only
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript-typescript
          queries: security-extended   # deeper coverage than the default suite
      - uses: github/codeql-action/analyze@v3
```

**Bad Example** — cron-only, default queries, results ignored

```yaml
on:
  schedule: [{ cron: '0 0 1 * *' }]   # monthly scan — vulnerabilities merge for weeks first
permissions: write-all                # over-broad; analysis needs only security-events: write
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: github/codeql-action/init@v3   # default 'security' suite: shallower coverage
      - uses: github/codeql-action/analyze@v3
      # not a required check → alerts pile up in the Security tab, no one triages them
```

## Common Mistakes

- Running CodeQL only on a schedule, so vulnerabilities merge and ship before the scan.
- Not making the result a required check, leaving findings as an ignored dashboard.
- Suppressing alerts by muting the tool instead of dismissing each with a reason.
- For compiled languages, a build step that skips code — unbuilt code is invisible to CodeQL.
- Leaving the default query suite when `security-extended` would catch the real bugs.
- Granting `write-all` to a job that only needs `security-events: write`.

## Production Tips

- Enable default setup org-wide via a security configuration so new repos scan from day one.
- Use `paths-ignore` to skip vendored/generated code and cut noise, but never skip the app.
- Track alert age in the security overview; set an SLA (e.g. fix critical within 7 days).
- Write custom CodeQL queries or import query packs for framework-specific sinks your
  stack uses that the standard suites don't model.

## AI Review Checklist

- Does CodeQL run on `pull_request` to the protected branch, not only on a schedule?
- Is "CodeQL" a required status check that blocks merge on new findings?
- Is the `security-extended` (or stricter) query suite selected?
- Does the analysis job use least-privilege `security-events: write` + `contents: read`?
- For compiled languages, does the build actually compile the analyzed code?
- Are open alerts triaged to a terminal state with documented dismissals?

## Related

- `knowledge/github/13-security.md`
- `knowledge/github/09-workflows.md`
- `knowledge/github/17-branch-protection.md`
- `knowledge/github/07-code-review.md`
- `knowledge/github/15-dependabot.md`
