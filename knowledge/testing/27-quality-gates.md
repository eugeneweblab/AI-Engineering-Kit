---
id: testing/27-quality-gates
topic: testing
slug: quality-gates
title: "Testing Quality Gates"
type: doc
order: 27
status: ready
tags: [testing, quality-gates]
related: [testing/21-cicd, testing/19-test-coverage, testing/22-flaky-tests, testing/29-test-review, testing/25-production-testing]
when_to_use: "Read before configuring what CI blocks a merge on, or when tuning coverage and check thresholds."
---
# Testing Quality Gates

## Purpose

A quality gate is an automated, pass/fail check that must succeed before code can merge or
deploy. This document defines which gates are worth blocking on, how to set thresholds
that catch regressions without becoming busywork, and how to keep gates from being routed
around. Gates are how a team's standards become enforced instead of aspirational.

A gate is a decision encoded in [CI](21-cicd.md): "this property must hold, and if it
doesn't, the change stops here." The art is choosing properties that are objective,
fast, and meaningful.

## Why It Matters

Standards that rely on humans remembering them decay under deadline pressure. A gate does
not get tired, rushed, or overruled in a hallway. But a badly chosen gate is corrosive: if
it is slow, flaky, or blocks on subjective style, engineers learn to bypass it — with
admin merge, with `--no-verify`, with a rubber-stamp override — and once bypassing is
normal, *every* gate loses authority. The goal is a small set of gates that are fast,
deterministic, and clearly tied to correctness, so that red genuinely means "do not ship."

## Core Principles

- **Gate objective properties only.** Tests pass, build compiles, types check, no known
  vulnerabilities, coverage on new code. Never gate on subjective taste — that belongs in
  [review](29-test-review.md), not a blocking check.
- **Fast enough to respect.** A gate that takes 40 minutes gets bypassed. Keep the
  blocking path lean; push slow suites to a non-blocking or post-merge lane.
- **Deterministic or it can't block.** A flaky gate that fails randomly trains everyone to
  hit "re-run." A blocking gate must be trustworthy (see [flaky tests](22-flaky-tests.md)).
- **Ratchet, don't slam.** Introduce a new threshold at the current level and tighten it
  over time. A gate set far above reality just gets disabled.
- **No silent bypass.** Overrides must be rare, logged, and reviewed. If people route
  around a gate routinely, the gate is wrong — fix or remove it.

## Best Practices

- Make these **required, blocking** checks: unit + integration tests pass, build succeeds,
  type check clean, linter clean, dependency/vuln scan clean, secrets scan clean.
- Gate **coverage on changed lines**, not whole-repo coverage. "New code ≥ 80% covered"
  drives the right behavior; a global number is gamed and demoralizing (see
  [test coverage](19-test-coverage.md)).
- Set thresholds as a **ratchet**: coverage may not drop below the current baseline, and
  the baseline only moves up. This blocks regressions without a flag day.
- Keep the **blocking suite fast** (target under ~10 minutes); run long e2e, load, and
  visual suites in a parallel non-blocking lane or nightly.
- Enforce gates on the **merge**, not just locally — use branch protection / required
  status checks so a green button is impossible while a gate is red.
- Track and **alarm on flaky gates**; auto-quarantine a check that flaps rather than
  leaving the whole team to re-run it.
- Make every gate **explain its failure** with an actionable message and a link, so the
  fix is obvious.

## Examples

**Good Example** — blocking on objective checks, coverage ratchet on new code

```yaml
# Branch protection: these must be green to merge; thresholds match reality and ratchet up.
required_checks:
  - unit-tests            # deterministic, ~3 min
  - type-check
  - lint
  - vuln-scan
coverage:
  scope: changed-lines    # gate new code, not the whole repo
  minimum: 80
  ratchet: true           # baseline can only increase, blocking regressions
e2e:
  blocking: false         # slow suite runs in parallel, reported not enforced
```

**Bad Example** — slow, subjective, easily bypassed

```yaml
required_checks:
  - full-e2e-suite        # 45 min and flaky → everyone hits re-run or admin-merges
coverage:
  scope: whole-repo
  minimum: 95             # unreachable → team disables the gate next sprint
gate: "reviewer feels the code is clean"  # subjective, unverifiable, not a gate at all
allow_admin_bypass: true  # silent override → the gate has no real authority
```

## Common Mistakes

- Gating on whole-repo coverage, which punishes new work for old gaps and invites gaming.
- Blocking on a 40-minute flaky suite, training the team to bypass all gates.
- Setting a threshold far above current reality, so it gets disabled instead of met.
- Encoding subjective style as a hard gate instead of an advisory linter/review comment.
- Allowing routine admin merges, quietly nullifying every required check.
- Gates whose failure message doesn't say what broke or how to fix it.
- Adding gates but not enforcing them at the branch-protection level, so they're optional.

## Production Tips

- Review your gate set quarterly: remove gates that never catch anything and gates people
  routinely override — both are noise.
- Report override/bypass usage as a metric; a rising trend means a gate is miscalibrated.
- Cache dependencies and parallelize the blocking suite before you loosen a threshold —
  speed problems are usually fixable without dropping the bar.

## AI Review Checklist

- Do blocking gates cover tests, build, types, lint, and vulnerability/secret scans?
- Is coverage gated on changed lines with a ratchet, not a global number?
- Is the blocking suite fast enough (~10 min) that bypassing isn't tempting?
- Are all blocking checks deterministic, with flaky ones quarantined not tolerated?
- Are gates enforced via branch protection, not merely reported?
- Are overrides rare, logged, and reviewed rather than silent?
- Does each gate failure give an actionable, linked explanation?

## Related

- `knowledge/testing/21-cicd.md`
- `knowledge/testing/19-test-coverage.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/29-test-review.md`
- `knowledge/testing/25-production-testing.md`
