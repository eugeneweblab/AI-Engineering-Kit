---
id: prisma/100-common-antipatterns
topic: prisma
slug: common-antipatterns
title: "Common Antipatterns"
type: doc
order: 100
status: ready
tags: [prisma, common-antipatterns]
related: [prisma/30-engineering-principles, prisma/11-relations-loading, prisma/08-transactions, prisma/15-performance, prisma/17-raw-sql]
when_to_use: "Read before writing Prisma code, or when a query is slow, leaks connections, or corrupts data."
---
# Common Antipatterns

## Purpose

A catalogue of the Prisma mistakes that recur across codebases, each with why it is
wrong and the concrete fix. These are the patterns that pass tests on small data and
fail in production. An agent should recognize each one on sight and refuse to generate
it.

## Why It Matters

Every anti-pattern below has the same shape: it looks correct, works in dev, and degrades
or corrupts only under real load and data volume. Because they do not throw at authoring
time, they slip through review and surface as outages. Naming them makes them catchable.

## The Anti-Patterns

### 1. A new PrismaClient per request

**Why it is wrong:** Each `new PrismaClient()` opens its own connection pool. Creating one
per request exhausts the database's connection limit in minutes under load, and the
clients are rarely disconnected.

**The fix:** Instantiate once in a shared module; import it everywhere.

```ts
// Bad
function handler() { const prisma = new PrismaClient(); /* ... */ }
// Good — db.ts
export const prisma = globalThis.__prisma ?? (globalThis.__prisma = new PrismaClient());
```

### 2. Unbounded `findMany`

**Why it is wrong:** `findMany()` with no `take` returns the whole table. It is fine on 100
rows and fatal on 10 million — memory blows up and the query times out.

**The fix:** Always add a `take` and a deterministic `orderBy`; paginate large lists.

```ts
// Bad:  await prisma.user.findMany();
// Good:
await prisma.user.findMany({ orderBy: { id: "asc" }, take: 50 });
```

### 3. N+1 relation loading

**Why it is wrong:** Fetching a list then loading each row's relation in a loop issues one
query per row. A page of 200 rows becomes 201 round trips — latency scales with data.

**The fix:** Load the relation in the same query with `include` or a nested `select`.

```ts
// Bad
for (const p of posts) p.author = await prisma.user.findUnique({ where: { id: p.authorId } });
// Good
await prisma.post.findMany({ select: { id: true, author: { select: { name: true } } } });
```

### 4. `select: *` by default — returning full rows

**Why it is wrong:** Omitting `select` returns every column, including large or sensitive
fields (password hashes, blobs) you did not intend to load or expose, and wastes
bandwidth.

**The fix:** Select only the columns the caller needs.

```ts
// Bad:  prisma.user.findMany();                       // returns passwordHash too
// Good: prisma.user.findMany({ select: { id: true, email: true } });
```

### 5. `skip`/`offset` for deep pagination

**Why it is wrong:** `skip: 100000` still forces the database to scan and discard 100,000
rows. Latency grows linearly with page depth.

**The fix:** Use cursor pagination on an indexed, ordered column.

```ts
// Bad:  findMany({ skip: 100000, take: 20 })
// Good: findMany({ take: 20, cursor: { id: lastId }, skip: 1, orderBy: { id: "asc" } })
```

### 6. Dependent writes without a transaction

**Why it is wrong:** If two writes must both succeed (debit + credit, order + line items)
and the second fails, the first is already committed — leaving corrupt state that no retry
can repair.

**The fix:** Wrap them in `$transaction`.

```ts
// Good
await prisma.$transaction([
  prisma.account.update({ where: { id: from }, data: { balance: { decrement: amount } } }),
  prisma.account.update({ where: { id: to },   data: { balance: { increment: amount } } }),
]);
```

### 7. External I/O inside an interactive transaction

**Why it is wrong:** An HTTP call or queue publish inside a `$transaction` callback holds
database locks open for the duration of that I/O, causing lock contention, timeouts, and
deadlocks.

**The fix:** Do the I/O before or after the transaction; keep the callback pure database work.

### 8. Read-then-write instead of upsert

**Why it is wrong:** `findUnique` then conditionally `create` has a race: two requests both
read "missing" and both insert, causing a duplicate or a unique-constraint crash.

**The fix:** Use `upsert`, or `create` and handle `P2002`.

```ts
// Good
await prisma.profile.upsert({ where: { userId }, create: { userId, ... }, update: { ... } });
```

### 9. `$queryRawUnsafe` with interpolated input

**Why it is wrong:** Concatenating user input into raw SQL is a direct SQL-injection hole.

**The fix:** Use tagged `$queryRaw` templates so values are parameterized.

```ts
// Bad:  prisma.$queryRawUnsafe(`SELECT * FROM "User" WHERE email = '${email}'`);
// Good: prisma.$queryRaw`SELECT * FROM "User" WHERE email = ${email}`;
```

### 10. `db push` in production

**Why it is wrong:** `db push` mutates the schema with no migration history and no review.
The database drifts from the tracked migrations, and there is no reproducible or reversible
record of the change.

**The fix:** Use `prisma migrate dev` locally and `prisma migrate deploy` in CI/CD.

### 11. Parsing error messages instead of codes

**Why it is wrong:** Matching on `error.message` text is brittle — messages change between
Prisma versions and locales, silently breaking your error handling.

**The fix:** Branch on `PrismaClientKnownRequestError.code` (`P2002`, `P2025`, `P2034`).

### 12. Missing index on a hot filter column

**Why it is wrong:** Filtering or sorting on an unindexed column forces a full table scan;
it is invisible until the table grows and the query slows to seconds.

**The fix:** Add `@@index([column])` and verify usage with `EXPLAIN`.

## AI Review Checklist

- [ ] Is `PrismaClient` shared, not created per request?
- [ ] Does every `findMany` on a growing table have `take` + `orderBy`?
- [ ] Are relations loaded in one query, with no N+1 loops?
- [ ] Are dependent writes transactional, with no external I/O inside the callback?
- [ ] Is raw SQL parameterized via tagged templates, never `Unsafe` interpolation?
- [ ] Do schema changes go through migrations, never `db push` in production?
- [ ] Are hot filter/sort columns indexed and error codes matched by code, not message?

## Related

- `knowledge/prisma/30-engineering-principles.md`
- `knowledge/prisma/11-relations-loading.md`
- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/17-raw-sql.md`
