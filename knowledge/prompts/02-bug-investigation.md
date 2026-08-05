---
id: prompts/02-bug-investigation
topic: prompts
slug: bug-investigation
title: "Prompt — Bug Investigation"
type: prompt
order: 2
status: ready
tags: [prompts, bug-investigation, applyDiscount, TypeError]
related: [prompts/01-code-review, prompts/03-refactoring, workflows/02-fix-a-bug, engineering/03-debugging-methodology, workflows/06-investigate-production-bug]
when_to_use: "Copy when asking an assistant to find a root cause, and fill in the evidence you already have."
---
# Prompt — Bug Investigation

## Purpose

A prompt for finding a root cause rather than a plausible-looking patch. Most of its value is
in the evidence section: an assistant given a symptom guesses, while one given a reproduction
and the observed values reasons.

---

## The Prompt

```markdown
Find the root cause of this bug.

## Symptom
<what happens, and what should happen instead>

## Reproduction
<the exact steps, input, or request that triggers it>
Frequency: <every time / intermittently / only in production>

## Evidence
- Error or stack trace: <paste it, unabridged>
- Observed values: <what the data actually was at the point of failure>
- Started: <when, and what changed around then — deploy, migration, dependency, config>
- Environments: <where it reproduces and where it does not>

## What I have ruled out
<hypotheses already eliminated, and how — so we do not repeat them>

## What I want
The mechanism, not a patch. Explain what actually happens, step by step, from the trigger to
the symptom. Tell me which specific line or condition is wrong and why it produces this
result.

Then propose the fix — and tell me what test would fail on the current code and pass after it.

If the evidence is not sufficient to determine the cause, say what would be needed rather
than guessing.
```

---

## Why It Is Shaped This Way

**"The mechanism, not a patch" is the point.** Asked to fix a bug, an assistant produces a
change that makes the symptom disappear — which is often a mask over the real defect.
Requiring the causal chain first makes the difference visible.

**"What I have ruled out" prevents re-treading.** Without it, the first three suggestions are
usually the things you already checked.

**"Started, and what changed around then" is the highest-value line in the prompt.** Most
bugs are recent changes, and correlation narrows the search dramatically.

**The permission to say "insufficient evidence" matters.** Otherwise the model produces a
confident answer from whatever it has, and a confident wrong cause costs more time than no
answer at all.

**Asking for the failing test** forces the diagnosis to be concrete. A cause that cannot be
expressed as a test that fails on the old code is a hypothesis, not a finding — see
[Workflow — Fix a Bug](../workflows/02-fix-a-bug.md).

---

## Variants

**Intermittent failure** — when it does not reproduce reliably:

```markdown
This fails roughly <1 in N> times and I cannot reproduce it on demand.

Rather than guessing at a cause, list the mechanisms that produce this class of
intermittency here — race conditions, ordering assumptions, time or timezone dependence,
cache state, connection reuse, retries — and for each, tell me what evidence would confirm
or eliminate it and how to capture that evidence.
```

**Works locally, fails in production:**

```markdown
This works locally and fails in production. Same commit.

Enumerate what differs between the two environments that could produce this symptom —
runtime version, environment variables, data volume and shape, concurrency, caching layers,
filesystem case sensitivity, timezone, network egress — and rank them by how well each
explains the specific symptom above.
```

**Performance regression:**

```markdown
This got slower: <before> → <after>, measured at <p50/p95> on <endpoint or operation>.

Here is the profile / query log: <paste>.

Tell me where the time actually goes and what specifically changed to move it. Do not
suggest optimizations for code that is not in the hot path.
```

---

## Using the Output

- **Verify the mechanism against the code** before accepting the fix. The narrative can be
  coherent and wrong.
- **Write the failing test first**, then apply the fix. If the test passes before the fix, the
  diagnosis is wrong.
- **Ask what else shares the pattern.** A root cause usually has siblings — the same mistake
  elsewhere in the codebase.

---

## Examples

**Good Example** — evidence in the prompt, hypotheses out

```text
Investigate this failure. Do not propose a fix yet — I want the cause first.

Symptom
  POST /api/orders returns 500 for ~2% of requests since 14:10 UTC, 2026-08-04.
  Before 14:10: 0.01% baseline.

Evidence
  - Every failing request has plan:"legacy" in the structured log (attached).
  - Three deploys in the window: 7c1a9f2 (docs), 8f2c1a9 (pricing), 9a3b7c1 (css).
  - Stack trace: TypeError: Cannot read properties of null (reading 'toFixed')
    at applyDiscount (src/pricing/discount.ts:24)
  - Not reproducible with a standard plan locally.

Ask
  1. Rank the plausible causes by how well they explain ALL the evidence.
  2. For each, state the single cheapest check that would confirm or refute it.
  3. Say explicitly what the evidence does NOT tell us.
```

**Bad Example** — the symptom, and a request for the answer

```text
Our checkout is broken, it returns 500 sometimes. What's wrong and how do I fix it?
```

With no logs, no timestamps, and no deploy history, any answer is a guess dressed as a
diagnosis — and a confident guess is worse than none, because it directs the next hour of work
at the wrong subsystem.

---

## Related

- `knowledge/prompts/01-code-review.md`
- `knowledge/prompts/03-refactoring.md`
- `knowledge/workflows/02-fix-a-bug.md`
- `knowledge/engineering/03-debugging-methodology.md`
- `knowledge/workflows/06-investigate-production-bug.md`
