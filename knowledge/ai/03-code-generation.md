---
id: ai/03-code-generation
topic: ai
slug: code-generation
title: "Code Generation"
type: doc
order: 3
status: ready
tags: [ai, code-generation]
related: [ai/02-task-planning, ai/04-code-modification, ai/06-self-verification]
when_to_use: "Read before generating new code so it integrates naturally with the existing project."
---
# Code Generation

## Purpose

This document defines how AI coding agents should generate code inside an existing software project.

The primary objective is not to generate code quickly.

The primary objective is to generate code that is indistinguishable from code written by an experienced engineer already familiar with the project.

Code generation should preserve architecture, reduce maintenance cost, and integrate naturally with the existing codebase.

---

## Core Principle

Generate code that belongs to the project.

Not code that demonstrates knowledge.

The generated implementation should feel as though it has always been part of the repository.

---

## Generation Priorities

Always prioritize:

1. Correctness
2. Consistency
3. Maintainability
4. Readability
5. Reusability
6. Performance
7. Brevity

Shorter code is not necessarily better code.

---

## Repository-First Generation

Before generating any code, inspect the repository.

Determine:

- folder structure;
- architectural patterns;
- naming conventions;
- file organization;
- dependency injection patterns;
- error handling;
- logging strategy;
- testing strategy.

Generate code that follows the existing project.

Never generate code based only on generic framework examples.

### Technique: mirror the nearest sibling

The most reliable way to generate code that belongs is not to write from a mental template — it is to open the closest existing file that solves the same *category* of problem and copy its skeleton, then swap the domain-specific parts. A sibling file answers, in one read, every convention question you would otherwise guess at: how classes are decorated, how dependencies arrive, where errors are thrown, what gets logged, and what the file exports.

Concretely, when asked to add a `findByEmail` method to a service, first read a sibling method in the same repo:

```ts
// EXISTING sibling in the repo — read this before writing anything.
@Injectable()
export class UsersService {
  constructor(private readonly prisma: PrismaService) {}

  async findById(id: string): Promise<User> {
    const user = await this.prisma.user.findUnique({ where: { id } });
    if (!user) {
      throw new NotFoundException(`User ${id} not found`);
    }
    return user;
  }
}
```

Now generate the new method as a structural clone of the sibling — same injected client, same lookup-then-guard shape, same exception type and message format:

```ts
async findByEmail(email: string): Promise<User> {
  const user = await this.prisma.user.findUnique({ where: { email } });
  if (!user) {
    throw new NotFoundException(`User ${email} not found`);
  }
  return user;
}
```

The new method requires no design decisions because the sibling already made them. This is the difference between generating code that *works* and generating code that *belongs*.

---

## Reuse Before Creation

Before creating any new implementation, search for an existing one. Duplicate logic is the last option, not the first.

Run the search before you write, and let the result decide whether you generate at all:

```bash
# About to write a slug/formatter/date helper? Prove it does not already exist.
rg -n "export (function|const) (slugify|formatDate|toCurrency)" src/ shared/ lib/

# About to add validation? Find the project's validation convention first.
rg -l "z\.object\(|class \w+Dto|@IsString\(" src/
```

If a helper already exists, import it. If a *convention* exists (for example, the repo validates every DTO with `zod`), generate the new code inside that convention rather than introducing a parallel one. State the outcome of the search explicitly:

> "`src/shared/text.ts` already exports `slugify`, so the new route imports it instead of defining a local copy."

Categories worth searching before generating: components, services, utilities, hooks, helpers, validation logic, middleware, API clients, constants, and types.

---

## Match Existing Style

Generated code should match the repository.

Respect:

- naming conventions;
- import order;
- formatting;
- file structure;
- folder hierarchy;
- abstraction level;
- comment style;
- error handling patterns.

The generated code should not reveal which AI model produced it.

### Worked example: generic output vs repository-matched output

The failure mode is generating a plausible framework tutorial answer instead of code shaped like the repository. Suppose the repo consistently uses constructor-injected dependencies, a `Logger` instance, typed returns, and domain exceptions. The generic answer ignores all of that.

Bad — reads like a copied framework snippet, not like the repo:

```ts
// Untyped, raw Error, console logging, default export — none of which the repo uses.
export default async function createOrder(data: any) {
  console.log("creating order", data);
  const order = await db.orders.insert(data);
  if (!order) throw new Error("failed");
  return order;
}
```

Good — matches the conventions an adjacent service already established:

```ts
@Injectable()
export class OrdersService {
  private readonly logger = new Logger(OrdersService.name);

  constructor(private readonly prisma: PrismaService) {}

  async create(input: CreateOrderDto): Promise<Order> {
    this.logger.log(`Creating order for customer ${input.customerId}`);
    const order = await this.prisma.order.create({ data: input });
    return order;
  }
}
```

The two blocks are functionally similar. Only the second one integrates: it is injectable, typed with the repo's DTO, logs through the repo's logger, and throws through the repo's exception layer (via Prisma/Nest, not a bare `Error`). Match the layer, not just the behavior.

---

## Generate the Smallest Correct Change

Modify only what is required.

Avoid:

- unnecessary refactoring;
- unrelated formatting;
- dependency updates;
- architecture changes;
- renaming unrelated symbols.

The safest implementation is usually the smallest implementation.

---

## Respect Existing Boundaries

Do not move responsibilities between modules unless explicitly required.

Examples:

Business logic should remain in services.

Presentation logic should remain in UI.

Validation should remain in validation layers.

Database access should remain in repositories or data services.

Avoid mixing responsibilities.

---

## Prefer Extension Over Replacement

When existing code can be extended safely:

Prefer extension.

Do not replace an entire implementation simply because a different solution appears cleaner.

Respect the engineering history of the project.

---

## Error Handling

Generated code should follow existing error handling patterns.

Do not invent new approaches.

Verify:

- validation;
- null handling;
- exceptions;
- logging;
- retries;
- fallback behavior.

Every failure path should be intentional.

---

## Dependency Management

Before introducing a dependency, verify:

- an existing dependency already solves the problem;
- framework functionality is sufficient;
- a shared utility already exists.

New dependencies should require clear engineering justification.

---

## Comments

Comments should explain intent.

Do not comment obvious code.

Prefer:

Why

Instead of:

What

Bad:

```ts
// Increment counter
counter++;
```

Good:

```ts
// Prevent duplicate submission attempts
submissionCount++;
```

---

## Generated Code Should Be Predictable

Future engineers should be able to predict where new code will be located.

New implementations should follow existing project organization.

Avoid surprising file locations.

Avoid inconsistent naming.

Avoid unique patterns for common problems.

---

## Hallucination Prevention

Never invent:

- APIs;
- configuration values;
- environment variables;
- project utilities;
- framework capabilities;
- database tables;
- services;
- business rules.

When information cannot be verified, state the uncertainty.

### Technique: verify every referenced symbol before you emit it

The highest-frequency hallucination is a reference to something that *sounds* right — a config key, a helper name, an env var, a column. Before generating a line that depends on such a symbol, confirm it exists in the repo:

```bash
# Before writing this.config.get('STRIPE_WEBHOOK_SECRET'), prove the key is defined.
rg -n "STRIPE_WEBHOOK_SECRET" .env.example src/config/

# Before calling formatMoney(...), prove it is exported somewhere.
rg -n "export .*formatMoney" src/ shared/ lib/

# Before referencing a Prisma column, prove it is in the schema.
rg -n "customerId" prisma/schema.prisma
```

If a search returns nothing, do not invent the symbol to make the code compile in your head. Either use the real name the search *does* reveal, or surface the gap:

> "I could not find a `STRIPE_WEBHOOK_SECRET` in `.env.example`; the webhook handler needs one added before this code runs."

---

## Large Tasks

Large implementations should be completed incrementally.

Preferred order:

Understand

↓

Plan

↓

Generate infrastructure

↓

Generate implementation

↓

Generate tests

↓

Verify

↓

Review

Avoid generating hundreds of lines of code before validation.

---

## AI Execution Checklist

## Before Generation

- Read every affected file completely.
- Search for similar implementations.
- Identify reusable code.
- Understand naming conventions.
- Understand architecture.
- Verify project configuration.
- Verify framework version.

---

## During Generation

- Modify the smallest possible area.
- Preserve architecture.
- Match repository style.
- Reuse existing abstractions.
- Avoid duplicate logic.
- Keep responsibilities separated.

---

## Before Completion

- Verify imports.
- Verify exports.
- Verify naming consistency.
- Remove temporary code.
- Remove debugging statements.
- Verify documentation.
- Verify tests.
- Review affected files.
- Review side effects.

---

## Anti-patterns

Avoid:

Generating code from memory.

Inventing project conventions.

Ignoring existing architecture.

Creating duplicate implementations.

Moving unrelated code.

Introducing unnecessary abstractions.

Using framework examples without adapting them.

Replacing working code unnecessarily.

Generating large changes without incremental verification.

---

## AI Responsibilities

AI should always explain:

What was changed.

Why it was changed.

Why this implementation was selected.

What existing code was reused.

What assumptions were made.

What risks remain.

What should be verified manually.

Transparency increases trust.

---

## Definition of Success

Generated code is successful when:

It follows project architecture.

It matches existing coding style.

It introduces no unnecessary complexity.

It minimizes regression risk.

It reuses existing implementations.

It is understandable without additional explanation.

It passes verification.

The best generated code is code that another engineer would naturally assume was written by a member of the project team.

---

## Summary

AI should not generate code that merely works.

AI should generate code that belongs.

Every generated line should respect the architecture, conventions, and engineering philosophy of the repository.

Successful AI-assisted development is measured not by the amount of generated code, but by how seamlessly that code integrates into the existing system.

## Related

- `knowledge/ai/02-task-planning.md`
- `knowledge/ai/04-code-modification.md`
- `knowledge/ai/06-self-verification.md`
