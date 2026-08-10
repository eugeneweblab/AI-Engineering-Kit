---
id: prisma/23-soft-delete
topic: prisma
slug: soft-delete
title: "Prisma Soft Delete"
type: doc
order: 23
status: ready
tags: [prisma, soft-delete, findMany, Date, deleteMany, PrismaClient, listUsers, deleteUser, deleted, removing, marking]
related: [prisma/14-extensions, prisma/09-filtering, prisma/16-indexes, prisma/22-multi-tenancy]
when_to_use: "Read before implementing or reviewing soft delete (marking rows deleted instead of removing them) in Prisma."
---
# Prisma Soft Delete

## Purpose

This document defines how to implement soft delete in Prisma — flagging a row as deleted
instead of removing it — without the classic bugs it invites: rows that "come back",
unique constraints that block re-creation, and cascades that no longer fire. It covers
the schema, how to filter deleted rows automatically, and when soft delete is the wrong
tool.

## Why It Matters

Soft delete looks trivial — add a `deletedAt` column, set it instead of deleting — and
that naïve version is a trap. Every existing query still returns the "deleted" rows
because nothing filters them, so a `delete` that appears to work leaves the record
visible everywhere. Then unique constraints fight you: a user who deletes account
`a@x.com` and signs up again hits a duplicate-email error, because the old row still
occupies the unique index. And database foreign-key cascades stop meaning anything,
because you are no longer deleting. Soft delete changes the semantics of your whole data
layer; implementing it half-way is worse than not having it.

## Core Principles

- **Filter deleted rows by default, everywhere.** The instant a row can be soft-deleted,
  every read must exclude it unless it explicitly opts in. Enforce this structurally, not
  per query.
- **Soft "delete" is an update.** Model it as setting `deletedAt`; a real `delete`
  becomes a deliberate, rare "purge" operation.
- **Uniqueness must account for deletion.** A unique column shared with deleted rows
  blocks re-creation. Use a partial unique index over live rows only.
- **You own the cascade now.** Database FK cascades do not run on an update, so
  cascading a soft delete to children is your responsibility.
- **Know when not to.** Legal/GDPR erasure and unbounded growth mean soft delete is not
  a substitute for real deletion and retention policies.

## Best Practices

- Add `deletedAt DateTime?` (nullable = live, non-null = deleted) rather than a boolean;
  it records *when*, which you almost always need. Index it, often as
  `@@index([deletedAt])` or composite with tenant/status columns.
- Enforce the default filter with a **Prisma Client extension** that rewrites `findMany`/
  `findFirst`/`findUnique` to add `where: { deletedAt: null }`, and rewrites `delete`/
  `deleteMany` into an `update` setting `deletedAt`. This is the modern replacement for
  the removed `$use` middleware.
- Provide an explicit escape hatch (e.g. a separate unscoped client or a `withDeleted`
  flag) for admin, restore, and audit paths that legitimately need deleted rows.
- Replace plain unique constraints with **partial unique indexes** on live rows so
  re-creation works after a soft delete:
  `CREATE UNIQUE INDEX ... ON "User"(email) WHERE "deletedAt" IS NULL`.
- Implement restore as clearing `deletedAt`, and cascade soft deletes to children
  explicitly inside a `$transaction`.
- Schedule a hard-delete/purge job for rows past their retention window so the table does
  not grow forever.

## Examples

**Good Example** — extension filters reads and intercepts deletes

```ts
const prisma = new PrismaClient().$extends({
  query: {
    $allModels: {
      // Exclude soft-deleted rows from every read unless caller opts in.
      async findMany({ args, query }) {
        args.where = { deletedAt: null, ...args.where };
        return query(args);
      },
      // Turn delete into an update so the row is retained and stays hidden.
      async delete({ args, query, model }) {
        return (prisma as any)[model].update({
          where: args.where,
          data: { deletedAt: new Date() },
        });
      },
    },
  },
});
// Partial unique index (in a migration) lets email be reused after soft delete:
//   CREATE UNIQUE INDEX user_email_live ON "User"(email) WHERE "deletedAt" IS NULL;
```

**Bad Example** — flag with no default filter, plain unique

```ts
// Schema: email String @unique   // blocks re-signup after "deletion"
async function deleteUser(id: number) {
  await prisma.user.update({ where: { id }, data: { deletedAt: new Date() } });
}

async function listUsers() {
  // No deletedAt filter: "deleted" users still appear in every list, dropdown,
  // and count. The delete silently did nothing visible.
  return prisma.user.findMany();
}
// Re-registering a soft-deleted email throws P2002 because the old row still
// owns the unique index — a bug users hit immediately.
```

## Common Mistakes

- Adding `deletedAt` but leaving reads unfiltered, so deleted rows stay visible.
- A boolean `isDeleted` instead of a timestamp, losing the deletion time you later need.
- Keeping a plain `@unique`, so users cannot re-create a soft-deleted record.
- Forgetting to cascade the soft delete to child rows, orphaning them as visible.
- No purge policy, letting soft-deleted rows accumulate and bloat indexes forever.
- Using soft delete for data that law requires be truly erased (GDPR right to erasure).
- Building on `$use` middleware instead of a client extension — it was removed in
  Prisma 7 and no longer compiles. See [migrating off middleware](13-middleware.md).

## Production Tips

- Add an admin/audit client without the soft-delete filter so support can inspect and
  restore rows.
- Run a scheduled purge that hard-deletes rows older than the retention window, in
  batches, to reclaim space and honor retention policy.
- When soft delete meets multi-tenancy, combine both filters (`deletedAt: null` and
  `tenantId`) in the same extension so neither can be forgotten.

## AI Review Checklist

- Is `deletedAt: null` applied to every read by default, structurally (extension), not
  per query?
- Are `delete`/`deleteMany` intercepted and turned into updates?
- Are unique constraints implemented as partial indexes over live rows so re-creation works?
- Are soft deletes cascaded to children explicitly, inside a transaction?
- Is there an explicit escape hatch for admin/restore/audit to see deleted rows?
- Is there a purge/retention job, and is soft delete not used where true erasure is required?

## Related

- `knowledge/prisma/14-extensions.md`
- `knowledge/prisma/09-filtering.md`
- `knowledge/prisma/16-indexes.md`
- `knowledge/prisma/22-multi-tenancy.md`
