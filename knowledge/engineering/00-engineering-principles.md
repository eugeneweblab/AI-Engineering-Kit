---
id: engineering/00-engineering-principles
topic: engineering
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 0
status: ready
tags: [engineering, engineering-principles]
related: [engineering/01-decision-framework, engineering/04-task-execution, engineering/05-context-first-development, architecture/30-engineering-principles]
when_to_use: "Read before making any engineering decision to apply the kit's foundational principles."
---
# Engineering Principles

## Purpose

This document defines the engineering principles that guide every recommendation in the AI Engineering Kit.

These principles apply to every technology, framework, programming language, and AI coding agent.

When documentation appears to conflict, these principles take precedence.

---

## Principle 1 — Understand Before Changing

Never modify code before understanding its purpose.

Before making changes:

- identify the problem;
- understand the surrounding architecture;
- determine why the current implementation exists;
- identify potential side effects.

Making changes without understanding the existing system often introduces unnecessary complexity and regressions.

**Bad Example**

> You see a `setTimeout(fn, 0)` that looks pointless and delete it to "clean up." It was deferring work until after the current render. Removing it reintroduces a layout bug the original author fixed months ago, and the regression ships because nobody knew why the line existed.

**Good Example**

> Before touching the line, you trace its history and find the commit and linked issue that explain the render-timing fix. You keep the line and add a comment recording *why* it exists.

```bash
# Find the commit and reasoning behind a specific line before changing it
git log -L 42,42:src/profile/render.ts     # history of just that line
git blame -L 42,42 src/profile/render.ts   # author and commit for the line
```

---

## Principle 2 — Solve the Root Cause

Do not optimize symptoms.

Do not patch consequences.

Identify and solve the underlying cause of the problem whenever practical.

Temporary workarounds should be explicitly documented.

A missing value that surfaces in the UI is usually a symptom. Guarding at the point of display hides broken data everywhere else it flows.

**Bad Example**

```ts
// Bad — patch the symptom where it happens to surface
function renderProfile(user: User): string {
  // user.name is "sometimes" undefined, so default it here
  return `<h1>${user.name ?? "Unknown"}</h1>`;
}
```

The same missing `name` will now silently appear as `"Unknown"` in emails, invoices, and search results — each needing its own patch.

**Good Example**

```ts
// Good — enforce the invariant at the source, so no downstream code has to guess
function toUser(row: UserRow): User {
  if (!row.name) {
    throw new Error(`User ${row.id} loaded without a name — fix the import, not the view`);
  }
  return { id: row.id, name: row.name };
}
```

If a workaround is genuinely temporary, mark it so it can be found and removed:

```ts
// TODO(#4821): remove once upstream billing API stops returning null totals (target: Q3)
const total = response.total ?? 0;
```

---

## Principle 3 — Prefer Simplicity

Choose the simplest solution that fully satisfies the requirements.

Simple solutions are easier to:

- understand;
- review;
- test;
- maintain;
- extend.

Simplicity should never sacrifice correctness.

Reach for a pattern (factory, strategy, event bus) only when the problem has the variability the pattern manages. Two fixed cases do not.

**Bad Example**

```ts
// Bad — a factory and a strategy interface for two hard-coded rules
interface DiscountStrategy { apply(total: number): number; }
class MemberDiscount implements DiscountStrategy {
  apply(total: number) { return total * 0.9; }
}
class GuestDiscount implements DiscountStrategy {
  apply(total: number) { return total; }
}
class DiscountFactory {
  create(isMember: boolean): DiscountStrategy {
    return isMember ? new MemberDiscount() : new GuestDiscount();
  }
}
```

**Good Example**

```ts
// Good — the requirement is two cases; a pure function covers it
function priceAfterDiscount(total: number, isMember: boolean): number {
  return isMember ? total * 0.9 : total;
}
```

The function is easier to read, test, and change. Introduce the strategy pattern later — *when* a third or fourth discount rule actually appears.

---

## Principle 4 — Preserve Consistency

Consistency is more valuable than personal preference.

Follow the conventions already established within the project unless there is a clear engineering reason to improve them.

Consistency reduces cognitive load and improves long-term maintainability.

**Bad Example**

> The codebase returns errors as `{ error: { code, message } }`. Your new endpoint returns `{ success: false, msg: "..." }` because you prefer it. Every client now needs a special case for one route.

**Good Example**

> You match the existing error shape even though you would have designed it differently. If the shape is genuinely worse, you raise it separately and change it everywhere at once — not one endpoint at a time.

---

## Principle 5 — Reuse Before Creating

Before introducing new code, determine whether an existing implementation can be reused.

Always:

- search for similar components;
- inspect existing utilities;
- evaluate extension points;
- compare responsibilities.

Create new abstractions only when reuse would increase complexity.

Duplicated logic does not stay identical. Each copy drifts, and bugs get fixed in one place but not the other.

**Bad Example**

```ts
// Bad — reimplementing slug logic that already lives in utils/slug.ts
function toSlug(title: string): string {
  return title.toLowerCase().split(" ").join("-");
  // silently diverges: keeps punctuation, breaks on multiple spaces
}
```

**Good Example**

```ts
// Good — reuse the shared, tested implementation
import { slugify } from "../utils/slug";

const slug = slugify(title); // one definition, fixed in one place
```

Before writing a helper, search first (`grep`, `git grep`, or your editor's symbol search) for an existing one. Create a new abstraction only when reuse would force unrelated call sites to share code they do not really have in common.

---

## Principle 6 — Minimize Change Surface

Modify as little code as necessary.

Smaller changes are:

- easier to review;
- easier to test;
- easier to revert;
- less likely to introduce regressions.

Avoid unrelated refactoring during feature implementation or bug fixes.

**Bad Example**

> A one-line off-by-one fix arrives as a 400-line diff because the editor reformatted the whole file on save. The real change is invisible, and the reformatting quietly hides a behavior regression the reviewer cannot spot.

**Good Example**

> The same fix touches one function and adds one test that reproduces the bug — a 6-line diff a reviewer can confirm in under a minute. Wanted reformatting goes in a separate, formatting-only commit.

---

## Principle 7 — Make Intent Obvious

Code should communicate intent before implementation details.

Prioritize:

- meaningful names;
- clear structure;
- predictable behavior;
- explicit logic.

Future maintainers should understand *why* the code exists before reading *how* it works.

**Bad Example**

```ts
// Bad — magic numbers, single-letter names, buried meaning
if (u.s === 2 && Date.now() - u.t > 2592000000) {
  suspend(u);
}
```

A reader cannot tell what `2`, `t`, or `2592000000` mean without hunting through other files.

**Good Example**

```ts
enum MemberStatus { Inactive = 0, Pending = 1, Active = 2 }

const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000;

function isDormantMember(user: { status: MemberStatus; lastSeenAt: number }): boolean {
  return (
    user.status === MemberStatus.Active &&
    Date.now() - user.lastSeenAt > THIRTY_DAYS_MS
  );
}

if (isDormantMember(user)) {
  suspend(user);
}
```

The named function and constant carry the intent. The condition now reads like the rule it enforces.

---

## Principle 8 — Optimize for Maintainability

Software is read significantly more often than it is written.

Favor solutions that improve long-term maintenance over short-term implementation speed.

Maintainability includes:

- readability;
- modularity;
- testability;
- consistency;
- documentation.

---

## Principle 9 — Verify Assumptions

Never assume.

Whenever possible:

- inspect existing code;
- inspect project configuration;
- inspect documentation;
- inspect APIs;
- inspect design assets.

Assumptions should be replaced with evidence.

---

## Principle 10 — Respect Existing Architecture

Every project has architectural decisions.

Understand them before introducing new ones.

Avoid creating competing patterns inside the same codebase.

When improvements are necessary, evolve the architecture incrementally instead of replacing it entirely.

---

## Principle 11 — Separate Problems

Solve one problem at a time.

Do not combine:

- feature development;
- refactoring;
- dependency upgrades;
- formatting changes;
- architectural redesign.

Independent changes produce clearer reviews and safer deployments.

---

## Principle 12 — Design for Future Readers

Write every line of code as if the next person maintaining it has no prior context.

Future readers may include:

- teammates;
- open-source contributors;
- future versions of yourself;
- AI coding agents.

Readable code reduces engineering cost.

---

## Principle 13 — Performance Requires Evidence

Do not optimize based on assumptions.

Measure first.

Optimize only after identifying a measurable bottleneck.

Avoid sacrificing readability for hypothetical performance improvements.

**Bad Example**

```ts
// Bad — "feels slow", so bolt on a cache without measuring
const cache = new Map<string, User>();

async function getUser(id: string): Promise<User | undefined> {
  if (cache.has(id)) return cache.get(id);
  const { rows } = await pool.query("SELECT * FROM users WHERE id = $1", [id]);
  cache.set(id, rows[0]); // never invalidated → users now see stale data
  return rows[0];
}
```

The cache adds a correctness bug (stale reads) and never addresses the real cost.

**Good Example**

```ts
// Good — profiling showed one query per order row (an N+1). Fix the actual cause.
async function usersForOrders(orders: Order[]): Promise<User[]> {
  const ids = orders.map((o) => o.userId);
  const { rows } = await pool.query(
    "SELECT * FROM users WHERE id = ANY($1)", // one round trip instead of N
    [ids],
  );
  return rows;
}
```

Measure before and after (query count, p95 latency, a benchmark) so you can prove the change helped rather than assuming it did.

---

## Principle 14 — Security Is a Requirement

Security is never an optional enhancement.

Every implementation should consider:

- input validation;
- output escaping;
- authentication;
- authorization;
- secret management;
- dependency trust.

Secure defaults are preferable to configurable security.

**Bad Example**

```ts
// Bad — string interpolation into SQL (injectable) and a secret in source
const email = req.query.email as string;
const query = `SELECT * FROM users WHERE email = '${email}'`;
const { rows } = await pool.query(query);

const apiKey = "sk_live_9f8a2c...";  // committed to the repository forever
```

An attacker can pass `' OR '1'='1` to dump the table, and the leaked key cannot be rotated without a code change.

**Good Example**

```ts
// Good — parameterized query and secret loaded from the environment
const email = req.query.email as string;
const { rows } = await pool.query(
  "SELECT * FROM users WHERE email = $1", // driver escapes the value
  [email],
);

const apiKey = process.env.PAYMENT_API_KEY;
if (!apiKey) {
  throw new Error("PAYMENT_API_KEY is not set"); // fail fast, never fall back to insecure defaults
}
```

---

## Principle 15 — Quality Before Speed

Fast delivery has value.

Reliable delivery has greater value.

Engineering decisions should balance:

- delivery speed;
- correctness;
- maintainability;
- operational risk.

Shipping quickly should never justify knowingly introducing avoidable technical debt.

---

## Summary

Every document in AI Engineering Kit builds upon these principles.

Technology-specific recommendations should never contradict them.

When uncertainty exists, these principles should guide the final engineering decision.

## Related

- `knowledge/engineering/01-decision-framework.md`
- `knowledge/engineering/04-task-execution.md`
- `knowledge/engineering/05-context-first-development.md`
- `knowledge/architecture/30-engineering-principles.md`
