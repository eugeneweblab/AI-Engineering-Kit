---
id: prisma/04-relations
topic: prisma
slug: relations
title: "Relations"
type: doc
order: 4
status: ready
tags: [prisma, relations, cuid, "@default", onDelete, onUpdate]
related: [prisma/03-models, prisma/02-schema, prisma/11-relations-loading, prisma/05-migrations]
when_to_use: "Read before modeling foreign keys, one-to-many, many-to-many, or one-to-one links between models."
---
# Relations

## Purpose

This document defines how to model relationships between Prisma models: one-to-many,
many-to-many, and one-to-one. It covers the relation scalar (the foreign-key field), the
`@relation` attribute, referential actions (`onDelete`/`onUpdate`), and implicit vs.
explicit join tables. Loading related data at query time is covered in
[11-relations-loading](11-relations-loading.md); this doc is about the schema.

## Why It Matters

Relations are where data integrity lives or dies. A missing or wrong referential action
leaves orphaned rows or blocks deletes; a foreign key on the wrong side produces a schema
that models the inverse of reality. These mistakes are expensive because they are baked
into the database structure — fixing them later means a migration plus a data backfill,
not a code edit. Modeling the relation correctly the first time is far cheaper than
untangling orphaned rows in production.

## Core Principles

- **The foreign key lives on the "many" side.** In one-to-many, the child holds the
  relation scalar (`authorId`) and the `@relation(fields:…, references:…)`; the parent
  holds only the list field. Putting it on the wrong side inverts the model.
- **Referential actions are a deliberate choice.** Decide `onDelete` explicitly:
  `Cascade` (delete children with the parent), `Restrict`/`NoAction` (block the delete),
  or `SetNull` (orphan them intentionally). The default is not always what you want.
- **Prefer explicit join tables for many-to-many.** They let you attach data to the
  relationship (role, joined-at) and evolve it; implicit tables cannot carry attributes.
- **A relation is enforced by a real foreign key** (on relational databases), so the
  database — not the application — guarantees referential integrity.

## Best Practices

- For one-to-many, put the relation scalar and `@relation` on the child; index it —
  Prisma indexes single-column FKs automatically, but confirm for composite keys.
- Set `onDelete` explicitly on every relation. Use `Cascade` for owned children (a
  post's comments), `Restrict` for shared references you must not silently destroy.
- Model many-to-many **explicitly** with a join model when the link has attributes or
  will grow; use the implicit `A[] … B[]` form only for pure tag-style links.
- For one-to-one, put the FK with `@unique` on the side that logically "owns" the other
  (e.g. `Profile.userId @unique`).
- Name relations with `@relation("Name")` when two relations connect the same pair of
  models, so Prisma can tell them apart.

## Examples

**Good Example** — FK on the many side, explicit delete behavior, rich join table

```prisma
model User {
  id    String @id @default(cuid())
  posts Post[]                    // back-relation only; no FK here
  memberships Membership[]
}

model Post {
  id       String @id @default(cuid())
  authorId String                                        // relation scalar lives on the child
  author   User   @relation(fields: [authorId], references: [id], onDelete: Cascade)
  // onDelete: Cascade — deleting a user removes their posts, which are owned by that user
}

model Organization {
  id          String       @id @default(cuid())
  memberships Membership[]
}

// Explicit join table: carries `role` and `joinedAt`, which an implicit m-n cannot.
model Membership {
  userId String
  orgId  String
  role   String
  user   User         @relation(fields: [userId], references: [id], onDelete: Cascade)
  org    Organization @relation(fields: [orgId],  references: [id], onDelete: Cascade)
  @@id([userId, orgId]) // one membership per user per org
}
```

**Bad Example** — FK on the wrong side, delete behavior left to chance

```prisma
model User {
  id     String @id @default(cuid())
  postId String                                     // FK on the parent — inverts the model
  post   Post   @relation(fields: [postId], references: [id]) // a user now has ONE post
}

model Post {
  id   String @id @default(cuid())
  user User?
  // No onDelete specified: deleting a referenced Post is silently RESTRICTed,
  // so user deletes start failing in prod with a foreign-key error nobody expected.
}
```

## Common Mistakes

- Placing the foreign key on the "one" side, so a one-to-many is modeled as one-to-one.
- Leaving `onDelete` implicit and being surprised when deletes cascade — or refuse to.
- Using an implicit many-to-many when the relationship needs attributes, then having to
  migrate to an explicit join table under load.
- Forgetting `@unique` on the FK for a one-to-one, silently allowing one-to-many.
- Omitting relation names when two relations link the same two models, so the schema
  fails to validate.

## Production Tips

- Cascading deletes can remove far more than intended; on high-value tables prefer
  `Restrict` plus an explicit, reviewed cleanup path, or a soft delete
  (see [23-soft-delete](23-soft-delete.md)).
- Changing a referential action is a migration — plan it, and check for existing rows
  that would violate the new constraint.

## AI Review Checklist

- Is the foreign key (relation scalar + `@relation`) on the "many"/owning side?
- Does every relation set `onDelete` explicitly and correctly for ownership?
- Are many-to-many links with attributes modeled as explicit join tables?
- Do one-to-one relations carry `@unique` on the foreign key?
- Are relations connecting the same two models disambiguated with `@relation("Name")`?

## Related

- `knowledge/prisma/03-models.md`
- `knowledge/prisma/02-schema.md`
- `knowledge/prisma/11-relations-loading.md`
- `knowledge/prisma/05-migrations.md`
