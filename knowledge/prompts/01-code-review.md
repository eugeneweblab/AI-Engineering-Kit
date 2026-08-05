---
id: prompts/01-code-review
topic: prompts
slug: code-review
title: "Prompt — Code Review"
type: doc
order: 1
status: ready
tags: [prompts, code-review]
related: [prompts/02-bug-investigation, engineering/02-code-review, workflows/05-review-pull-request, checklists/02-pull-request-author, tools/26-ai-coding-tools]
when_to_use: "Copy when asking an assistant to review a diff, and adapt the context section to the project."
---
# Prompt — Code Review

## Purpose

A prompt for reviewing a change before merge. The goal is coverage of real defects with
enough context attached that a human can triage the output quickly.

---

## The Prompt

```markdown
Review this change for defects.

## Context
- Stack: <framework, language, versions>
- This code runs: <in a request handler / as a background job / at build time>
- It handles: <untrusted input? money? personal data? none of these>

## What to look for
Correctness first: logic errors, unhandled edge cases (empty, null, zero, one, many,
concurrent), incorrect assumptions about data. Then security where untrusted input reaches
output, a query, or a filesystem path. Then performance where the change adds queries,
loops over I/O, or unbounded result sets.

## How to report
Report every issue you find, including ones you are uncertain about or consider
low-severity. Do not filter for importance at this stage — I will triage. For each finding
give: the file and line, what breaks, a concrete input or state that triggers it, your
confidence, and a suggested fix.

If you find nothing in a category, say so rather than padding the list.

## Out of scope
Formatting and import order — the formatter owns those. Style preferences where the code
matches its surroundings.
```

---

## Why It Is Shaped This Way

**"Report everything, I will triage" is the load-bearing instruction.** Told to report only
important issues, a model follows that literally: it finds the bugs, judges some below the
bar, and does not mention them. Precision rises and measured recall falls — the defects were
found and then discarded. Move the filtering to a second pass, or to you.

**Naming the runtime context changes what gets flagged.** "Runs in a request handler,
handles untrusted input" produces a different review from "runs at build time on our own
config" — and without it the model guesses.

**Asking for a triggering input separates real findings from plausible ones.** A finding that
cannot be given a concrete failing case is usually a guess dressed as a defect. This one line
removes most false positives.

**Excluding formatting** stops the output filling with noise your tooling already handles.

---

## Follow-Up: Verification Pass

For a large or high-stakes review, a second pass on the findings costs little and removes
most of the remaining noise:

```markdown
Here are the findings from the review. For each one, try to refute it: construct the
argument that it is not a real defect in this codebase. Then state whether it survives.

Default to "not a real defect" when you are uncertain — a finding that cannot be
demonstrated with a concrete input is not actionable.
```

Adversarial framing works better than "double-check these", which tends to confirm.

---

## Variants

**Security-focused** — replace the "what to look for" section:

```markdown
Review for security defects only. Trace every path from untrusted input to a sink: rendered
output, a database query, a filesystem path, a shell command, a redirect, a deserializer.
For each, state whether the value is validated on the way in and encoded for the context it
lands in. Check authorization on every state-changing path — permission on the specific
object, not just an authenticated session.
```

**Migration or refactor review** — when behavior should not have changed:

```markdown
This change is meant to be behavior-preserving. Identify anywhere behavior actually differs:
changed defaults, different error handling, altered ordering, timing changes, or edge cases
handled differently than before. List them even where the new behavior looks better.
```

---

## Using the Output

Treat the findings as a reviewer's notes, not a verdict:

- **Verify before acting.** A confident description of a defect that does not exist reads
  exactly like one that does.
- **Check the fix, not just the finding.** A correct diagnosis with a wrong remedy is common.
- **Findings are not a substitute for reading the diff.** They are a second pass over code
  you have already read — see [Workflow — Review a Pull Request](../workflows/05-review-pull-request.md).

---

## Related

- `knowledge/engineering/02-code-review.md`
- `knowledge/workflows/05-review-pull-request.md`
- `knowledge/checklists/02-pull-request-author.md`
- `knowledge/prompts/02-bug-investigation.md`
