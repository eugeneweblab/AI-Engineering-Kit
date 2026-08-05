---
id: tools/100-common-antipatterns
topic: tools
slug: common-antipatterns
title: "Tools Common Antipatterns"
type: doc
order: 100
status: ready
tags: [tools, common-antipatterns]
related: [tools/30-engineering-principles, tools/99-ai-review-checklist, tools/01-package-managers, tools/16-git-hooks, tools/19-task-runners, tools/98-production-checklist]
when_to_use: "Read when setting up or reviewing project tooling, to recognize the recurring failure modes and their fixes."
---
# Tools Common Antipatterns

## Purpose

This document catalogs the tooling mistakes that recur across almost every project. Each entry names the antipattern, explains **why it is wrong** — the concrete failure it causes — and gives **the fix**.

## Why It Matters

These antipatterns share one trait: they all work. The build succeeds, the tests pass, the feature ships — which is why they survive. Their cost arrives later and elsewhere: a colleague who cannot reproduce a bug, a deploy that behaves differently from staging, a security check everyone learned to ignore. Recognizing the pattern early is the cheapest possible fix.

---

## Antipatterns

### 1. Floating versions

**What it looks like:** `node-version: '20'` in CI, `FROM node:latest` in a Dockerfile, no `.nvmrc`, no `packageManager`.

**Why it is wrong:** "Works on my machine" is almost always an unpinned runtime. Two developers and CI resolve three different patch versions, and a build that succeeded yesterday fails today because a base image moved.

**The fix:** Pin the runtime in a committed file, read it everywhere, and enforce it with `engines` + `engine-strict`. Pin Docker images to a patch tag.

---

### 2. `npm install` in CI

**What it looks like:** The developer install command in a workflow, silently rewriting the lockfile.

**Why it is wrong:** CI tests a dependency tree nobody reviewed. When it differs from the committed lockfile, the artifact you ship was never validated against the tree you approved.

**The fix:** `npm ci` / `pnpm install --frozen-lockfile`. It fails loudly when the lockfile is stale, which is the correct behavior.

---

### 3. Two tools for one job

**What it looks like:** ESLint enforcing `semi` while Prettier formats; PHPCS and PHP-CS-Fixer both owning style; two lockfiles from two package managers.

**Why it is wrong:** They disagree, and every save or commit flips the file back and forth. Developers learn to ignore one tool's output, which usually means ignoring both.

**The fix:** One owner per job. `eslint-config-prettier` last in the config; one package manager, pinned.

---

### 4. The permanent warning backlog

**What it looks like:** `eslint .` with hundreds of warnings, a static-analysis baseline that only grows, "we'll fix those later".

**Why it is wrong:** Nobody reads output that is always noisy, so a genuine new error scrolls past unseen. The tool now costs CI minutes and delivers nothing.

**The fix:** Zero tolerance — `--max-warnings 0`. Freeze existing debt in an explicit baseline and gate only new code, then shrink the baseline deliberately.

---

### 5. Checks that only exist in CI

**What it looks like:** A workflow invoking `npx eslint src --ext .ts --format junit` and `tsc --project tsconfig.ci.json`, with nothing equivalent in `package.json`.

**Why it is wrong:** A developer cannot reproduce the failure. Debugging becomes push-and-wait, and the feedback loop stretches from seconds to minutes.

**The fix:** Every gate is a project script; CI calls the script. One `verify` command runs them all.

---

### 6. The hook everyone bypasses

**What it looks like:** Pre-commit running the full test suite, a production build, and a repo-wide lint — four minutes per commit.

**Why it is wrong:** `--no-verify` becomes muscle memory within a week. The hook now protects nobody while still costing everybody.

**The fix:** Pre-commit on staged files only, under a few seconds. Type checks and unit tests at pre-push; everything else in CI.

---

### 7. Formatting mixed into a feature commit

**What it looks like:** A pull request with 4,000 changed lines, of which 30 are the actual change.

**Why it is wrong:** The real change is unreviewable, and `git blame` now attributes every line to whoever ran the formatter.

**The fix:** Format in an isolated commit, record it in `.git-blame-ignore-revs`, then make the functional change.

---

### 8. Trusting a fast transpiler to check types

**What it looks like:** A Vite or esbuild build with no `tsc --noEmit` anywhere in the pipeline.

**Why it is wrong:** esbuild and SWC strip types without validating them. The project looks fully typed in the editor and has no type safety in CI at all.

**The fix:** `tsc --noEmit` as a separate required step, plus `isolatedModules: true`.

---

### 9. Setup documented instead of automated

**What it looks like:** A README section listing eight steps, one of which is "ask a teammate for the `.env` file".

**Why it is wrong:** Every step is a divergence point, and the instructions are stale within a month because nobody re-runs them. Onboarding becomes a person, not a command.

**The fix:** One command that installs, migrates, seeds, and starts. A committed `.env.example` with a secrets manager for real values.

---

### 10. Production credentials in a desktop tool

**What it looks like:** A read-write production database connection saved in a GUI client with auto-commit on; an MCP server pointed at the live database.

**Why it is wrong:** One mistyped statement in the wrong tab, and there is nothing to roll back. This is the most common cause of avoidable data loss.

**The fix:** A read-only role for production, colour-coded connections, auto-commit off, and access through an SSH tunnel.

---

### 11. Secrets in configuration and prompts

**What it looks like:** An API key in a committed Postman collection, a `VITE_`-prefixed secret in `.env`, credentials pasted into an assistant's context.

**Why it is wrong:** Anything prefixed for the client is inlined into the shipped bundle. Anything committed is in every clone and every fork. Deleting it does not un-leak it.

**The fix:** Secrets from the environment, never from a committed file, never client-side. On exposure, rotate first and clean up second.

---

### 12. Auto-merging runtime dependency updates

**What it looks like:** A bot configured to merge any update once CI is green.

**Why it is wrong:** CI verifies the behavior you thought to test. A silently changed default in a minor release passes every test and breaks production.

**The fix:** Auto-merge dev tooling patches only. Runtime dependencies get a human; majors get a plan.

---

### 13. Deferring updates until forced

**What it looks like:** A dependency backlog untouched for a year, then a rushed upgrade because an advisory landed.

**Why it is wrong:** Small updates are individually reviewable; two years of updates applied at once is an unreviewable migration undertaken under pressure.

**The fix:** Scheduled, grouped, automated updates. Advisories bypass the schedule.

---

### 14. Hand-edited version numbers

**What it looks like:** A version bumped in `package.json`, sometimes tagged, with a changelog written from memory later.

**Why it is wrong:** Version, tag, and changelog drift apart until nobody can say what a published version contains.

**The fix:** Derive versions from changesets or commit conventions; publish from CI; write changelog entries at authoring time.

---

### 15. Instrumentation nobody reads

**What it looks like:** Error tracking installed without sourcemaps, prose log lines, alerts that fire nightly and are always dismissed.

**Why it is wrong:** Minified stack traces are unreadable, prose logs cannot be aggregated, and an always-firing alert has trained everyone to ignore the channel — including the night it matters.

**The fix:** Upload sourcemaps keyed to a release, log structured JSON with a request ID, and delete alerts nobody acts on.

---

### 16. Tools accumulated, never removed

**What it looks like:** Config files for a bundler the project no longer uses, a second test runner from a half-finished migration, plugins nobody can explain.

**Why it is wrong:** Each is an upgrade obligation, a supply-chain surface, and a source of confusion about which tool actually runs.

**The fix:** Audit quarterly with `depcheck` / `knip`. Removing a tool is as valuable as adding one.

---

## AI Review Checklist

- Are any versions floating — runtime, package manager, Docker base image, CI action?
- Does CI install with a frozen lockfile and call project scripts?
- Is exactly one tool responsible for each job?
- Are warnings treated as failures, with legacy debt in an explicit baseline?
- Can every CI gate be run locally?
- Is the pre-commit hook fast enough to survive?
- Is type checking a separate step from bundling?
- Is setup automated rather than documented?
- Are production credentials absent from desktop tools and assistant contexts?
- Are secrets sourced from the environment and kept out of client bundles?
- Are dependency updates scheduled, grouped, and human-reviewed where they ship?
- Has anything been removed recently?

## Related


- `knowledge/tools/30-engineering-principles.md`
- `knowledge/tools/99-ai-review-checklist.md`
- `knowledge/tools/01-package-managers.md`
- `knowledge/tools/16-git-hooks.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/98-production-checklist.md`
