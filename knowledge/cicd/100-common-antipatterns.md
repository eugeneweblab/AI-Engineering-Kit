---
id: cicd/100-common-antipatterns
topic: cicd
slug: common-antipatterns
title: "CI/CD Common Antipatterns"
type: doc
order: 100
status: ready
tags: [cicd, common-antipatterns]
related: [cicd/04-test-stage, cicd/05-quality-gates, cicd/14-rollbacks, cicd/15-secrets, cicd/30-engineering-principles]
when_to_use: "Read when a pipeline is slow, flaky, or untrusted, or before reviewing CI/CD changes for known traps."
---
# CI/CD Common Antipatterns

## Purpose

A catalog of recurring CI/CD failures, each with why it is wrong and the fix. These are
the patterns that quietly degrade a pipeline until engineers stop trusting it and start
working around it. An agent can use this list to spot the trap in a diff and correct it
before it becomes an incident.

## Why It Matters

Every anti-pattern here trades a real guarantee for short-term convenience: a bypassed
gate, a rebuilt artifact, a retried flaky test. The cost is invisible until the moment it
matters — a rollback that does not roll back, a "tested" build that was never the build
that shipped. Naming these patterns makes them reviewable.

## Anti-Patterns

### 1. Rebuilding the artifact per environment

**Why it is wrong:** Compiling separately for staging and production re-resolves
dependencies and can produce different bytes, so production runs code that was never
tested. "It passed in staging" becomes meaningless.
**The fix:** Build once, produce an immutable digest-addressed artifact, and promote that
exact artifact through every environment. See [engineering principles](30-engineering-principles.md).

### 2. Depending on floating tags (`latest`, unpinned actions)

**Why it is wrong:** `image:latest` or `uses: some/action@main` resolves to whatever
exists at build time. A green build today can break tomorrow with no code change, and the
failure is unreproducible.
**The fix:** Pin base images by digest, actions/plugins by SHA or exact tag, and
dependencies by lockfile. Update pins deliberately through review.

### 3. Retrying flaky tests until they pass

**Why it is wrong:** Blanket retries and `continue-on-error` mask real, intermittent bugs
and train the team to ignore red. A test that passes on the third try proves nothing.
**The fix:** Quarantine flaky tests to a non-blocking lane, track them, and fix or delete
them on a deadline. Keep the blocking suite deterministic. See [test stage](04-test-stage.md).

### 4. Slow tests before fast ones

**Why it is wrong:** Running a 30-minute e2e suite before a 20-second lint step delays
every failure signal, so developers context-switch away and merges pile up.
**The fix:** Order stages cheapest-and-most-likely-to-fail first: lint, then unit, then
integration, then e2e. Fail fast and parallelize.

### 5. Secrets hardcoded or printed in logs

**Why it is wrong:** A token committed to a workflow file or echoed by a debug step lives
forever in git history and log storage, readable by anyone with repo or CI access.
**The fix:** Inject secrets at runtime from a secrets manager, mark them masked, and never
`echo` or `set -x` around them. See [secrets](15-secrets.md).

### 6. Editing pipelines live in the CI web UI

**Why it is wrong:** UI edits bypass code review and leave no history. Nobody can see who
changed the deploy step or why, and the change cannot be reverted with the code.
**The fix:** Keep pipeline definitions in the repo and change them through pull requests,
reviewed like any other code.

### 7. Deploying with no rollback path

**Why it is wrong:** If the only way back is "roll forward with a hotfix", every bad
deploy becomes an outage that lasts as long as it takes to write and ship a fix.
**The fix:** Design the rollback before the rollout — a one-step revert to the previous
artifact — and actually exercise it. See [rollbacks](14-rollbacks.md).

### 8. Coupling schema migrations to code deploys

**Why it is wrong:** A migration that drops or renames a column in the same release as the
code makes rollback impossible — reverting the code leaves the schema ahead of it.
**The fix:** Use backward-compatible, expand-then-contract migrations run separately from
the code deploy, so code and schema can move independently.

### 9. Gates that can be bypassed

**Why it is wrong:** A "required" check that admins can click past, or a coverage
threshold set to advisory, is not a gate — it is a suggestion that erodes under deadline
pressure.
**The fix:** Make checks genuinely block merge and deploy via branch/environment
protection. Bypasses should be rare, logged, and reviewed. See [quality gates](05-quality-gates.md).

### 10. Running untrusted PR code with production secrets

**Why it is wrong:** Fork pull requests can run arbitrary code. If that job has access to
production credentials, a malicious PR can exfiltrate them.
**The fix:** Run untrusted PR builds in an isolated context with no production secrets;
require approval before privileged workflows run on external contributions.

### 11. One giant monolithic pipeline job

**Why it is wrong:** A single job that builds, tests, and deploys cannot cache, parallelize,
or retry independently. One failure re-runs everything and feedback is slow.
**The fix:** Split into focused, dependency-linked stages so they cache and parallelize,
and a re-run only repeats the failed unit.

## AI Review Checklist

- Is the artifact built once and promoted, not rebuilt per environment?
- Are all inputs pinned, with no floating tags?
- Are flaky tests quarantined rather than blindly retried?
- Are secrets sourced from a manager and absent from logs?
- Does every deploy have a tested one-step rollback and decoupled migrations?
- Are required gates genuinely blocking and unbypassable?

## Related

- `knowledge/cicd/04-test-stage.md`
- `knowledge/cicd/05-quality-gates.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/15-secrets.md`
- `knowledge/cicd/30-engineering-principles.md`
