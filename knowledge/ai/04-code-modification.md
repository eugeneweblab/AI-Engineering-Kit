---
id: ai/04-code-modification
topic: ai
slug: code-modification
title: "Code Modification"
type: doc
order: 4
status: ready
tags: [ai, code-modification]
related: []
when_to_use: "Read before modifying existing code to make the smallest safe change without breaking behavior."
---
# Code Modification

## Purpose

This document defines how AI coding agents should modify existing code safely.

Most engineering work is not creating new software.

It is modifying existing software without breaking existing behavior.

The objective is to make the smallest correct change while preserving the integrity of the project.

---

## Core Principle

Respect the existing codebase.

Every line of existing code exists for a reason.

Before changing it, understand:

- why it exists;
- what depends on it;
- what assumptions it makes;
- what problems it solves.

Changing code without understanding its role increases technical debt.

---

## Modification Strategy

Always follow this sequence.

```
Understand
      ↓
Inspect
      ↓
Analyze Impact
      ↓
Plan
      ↓
Modify
      ↓
Verify
      ↓
Self Review
```

Never begin editing immediately.

---

## Rule 1 — Read Before Editing

Read the entire file.

Do not edit after reading only the relevant function.

Review:

- imports;
- exports;
- interfaces;
- helper functions;
- surrounding logic;
- comments;
- TODOs.

Local changes often have file-level implications.

---

## Rule 2 — Understand Why

Before changing existing logic determine:

- why it was written;
- whether it solves multiple problems;
- whether other modules depend on it;
- whether it exists for backward compatibility.

Never assume existing code is incorrect simply because it looks unfamiliar.

---

## Rule 3 — Minimize the Change Surface

Modify only what is necessary.

Prefer:

- changing one function;
- extending one class;
- adding one condition;
- updating one interface.

Avoid rewriting entire modules unless explicitly required.

Small changes reduce risk.

---

## Rule 4 — Preserve Public Contracts

When modifying:

- APIs;
- public functions;
- exported types;
- reusable components;
- services;

assume external code depends on them.

Changing public behavior requires careful verification.

Backward compatibility should be preserved whenever practical.

---

## Rule 5 — Preserve Existing Patterns

Match:

- naming;
- architecture;
- folder organization;
- abstraction level;
- dependency flow;
- testing style.

Avoid introducing a new pattern inside an established project.

---

## Rule 6 — Avoid Hidden Side Effects

Before modifying code determine:

What calls this?

What imports this?

Who depends on this?

What assumptions may change?

Every modification should consider downstream consumers.

### Worked example — impact analysis before editing

Suppose you are asked to change `formatPrice`. Do not open the file and edit
it. First build the full caller set, because the type checker will not catch
dynamic or string-based usage.

```bash
# 1. Every direct reference to the symbol (word-boundary anchored)
#    ripgrep's built-in `ts` type already covers .ts, .tsx, .mts, .cts
rg -n '\bformatPrice\b' --type ts

# 2. Re-exports that hide callers behind a barrel file
rg -n "export .*formatPrice" --type ts

# 3. Dynamic / string usage the compiler cannot follow
#    (template rendering, event names, feature-flag lookups)
rg -n "formatPrice" --type html --type vue --glob '*.stories.*'
```

When the language server is available, prefer semantic references over text
search — they resolve aliases and imports correctly:

```
find_referencing_symbols(name_path="formatPrice", relative_path="src/lib/pricing.ts")
```

Only after the caller set is known can you judge whether a change is local or a
public-contract change (Rule 4). An empty search result is itself a signal:
either the symbol is dead code, or your query missed a usage pattern —
investigate before assuming it is safe to change freely.

---

## Rule 7 — Separate Refactoring From Functional Changes

Do not combine:

- formatting;
- renaming;
- optimization;
- feature development;
- dependency upgrades.

One pull request should solve one engineering problem.

Mixed changes increase review complexity.

---

## Rule 8 — Preserve Existing Behavior

If behavior is not intentionally changing:

It should remain identical.

Regression prevention is a primary engineering responsibility.

### Worked example — lock behavior before refactoring

Before refactoring code you do not fully understand, pin its current output in
a *characterization test*. It asserts what the code does today — not what it
should do — so any behavioral drift during the refactor surfaces immediately.

```ts
// characterization test: written BEFORE touching legacy discount logic.
// The expected values are captured from the current implementation's output,
// including any quirks. If a "cleanup" changes any row, the diff is now visible.
describe('applyDiscount (characterization)', () => {
  it.each([
    [100, 'GOLD', 80],
    [100, 'SILVER', 90],
    [100, 'NONE', 100],
    [0, 'GOLD', 0],
    [-50, 'GOLD', -50], // yes, it currently allows negatives — preserve until proven wrong
  ])('applyDiscount(%i, %s) === %i', (price, tier, expected) => {
    expect(applyDiscount(price, tier)).toBe(expected);
  });
});
```

Run this suite green, refactor, then run it again. If a row flips, you have
either found the intended change or an unintended regression — both are now
explicit rather than silent. Never delete a surprising row (like the negative
case) as part of a refactor; that is a functional change and belongs in a
separate task (Rule 7).

---

## Rule 9 — Extend Before Replacing

If existing code can safely support the new requirement:

Extend it.

Avoid replacing mature implementations simply because a new approach appears cleaner.

Engineering history has value.

### Worked example — extend a contract instead of breaking it

Requirement: `formatPrice` must support currencies other than USD. The tempting
move is to add a required parameter. That silently breaks every caller found in
the Rule 6 impact analysis.

Bad — a required parameter turns a local change into a breaking change:

```ts
// Every existing call site — formatPrice(amount) — now fails to compile,
// or worse, passes undefined at runtime in loosely-typed callers.
export function formatPrice(amount: number, currency: string): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
}
```

Good — an optional parameter with a default preserves the existing contract:

```ts
// formatPrice(9.99) keeps working unchanged; formatPrice(9.99, 'EUR') is the
// new capability. No caller in the impact set needs to be touched.
export function formatPrice(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
}
```

The extension adds behavior at the edge without disturbing the center. Reserve
a true signature change for when the impact analysis shows every caller must
change anyway — and when it does, that is a separate, clearly-scoped task.

---

## Rule 10 — Remove Temporary Changes

Before completion remove:

- console logs;
- debug output;
- temporary variables;
- commented-out code;
- experimental logic;
- unused imports.

Only intentional code should remain.

---

## Safe Modification Checklist

Before editing verify:

- I understand the file.
- I understand the module.
- I understand the architecture.
- I understand why this implementation exists.

---

Before saving verify:

- Only required code changed.
- Existing behavior is preserved.
- Public interfaces remain compatible.
- Existing conventions were followed.
- No duplicate logic was introduced.

---

Before completing verify:

- Imports are correct.
- Types are correct.
- Documentation remains valid.
- Tests still pass.
- No debugging code remains.
- Side effects were reviewed.

---

## Modification Risk Assessment

Before modifying code estimate the risk.

## Low Risk

- UI text
- Styling
- Documentation
- Small isolated utility

---

## Medium Risk

- Component logic
- Business rules
- API validation
- Shared utilities

---

## High Risk

- Authentication
- Authorization
- Database schema
- Payment logic
- Framework configuration
- Public APIs
- Shared infrastructure

Higher-risk changes require more investigation and verification.

---

## AI Execution Checklist

## Investigation

☐ Read the complete file.

☐ Read related files.

☐ Search similar implementations.

☐ Identify reusable code.

☐ Understand dependencies.

☐ Understand architecture.

---

## Modification

☐ Modify the smallest possible area.

☐ Preserve existing naming.

☐ Preserve architecture.

☐ Preserve public contracts.

☐ Avoid duplicate logic.

☐ Avoid unnecessary refactoring.

---

## Verification

☐ Review changed files.

☐ Review imports.

☐ Review exports.

☐ Review side effects.

☐ Review edge cases.

☐ Remove temporary code.

☐ Verify documentation.

☐ Verify tests.

---

## Common Anti-patterns

## Rewrite Instead of Extend

Replacing large sections of code when a small extension would solve the problem.

---

## Cascade Editing

Changing multiple unrelated files because they appear similar.

---

## Architecture Drift

Introducing a new pattern into a project that already has an established architecture.

---

## Silent Breaking Change

Changing public behavior without updating documentation or dependent code.

---

## Accidental Cleanup

Removing code simply because its purpose is unclear.

Unclear code should be investigated—not deleted.

---

## AI Responsibilities

Before proposing modifications AI should explain:

- what will change;
- why the change is necessary;
- what existing code will remain unchanged;
- possible side effects;
- rollback strategy if the change fails.

Transparency improves engineering confidence.

---

## Definition of Success

A successful modification:

- solves the intended problem;
- preserves existing behavior where expected;
- introduces the smallest reasonable change;
- follows repository conventions;
- minimizes regression risk;
- improves maintainability rather than reducing it.

The best modification is often the one that future engineers barely notice because it integrates naturally into the existing codebase.

---

## Summary

Professional software engineering is primarily the discipline of changing existing systems safely.

AI coding agents should optimize for confidence, predictability, and maintainability—not for the amount of generated code.

Safe modifications build trust.

Trust enables effective AI-assisted engineering.