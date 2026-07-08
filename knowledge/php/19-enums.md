---
id: php/19-enums
topic: php
slug: enums
title: "Enums"
type: doc
order: 19
status: ready
tags: [php, enums]
related: [php/02-types, php/04-oop, php/22-clean-code, php/12-database]
when_to_use: "Read before modeling a fixed set of named values, replacing string/int constants, or storing a status in the database."
---
# Enums

## Purpose

This document defines how to model a closed set of named values with PHP enums
(available since PHP 8.1). It is written so an agent can replace ad-hoc string or integer
constants with a type-safe enum, attach behavior correctly, and persist enum values
without breaking on unknown input.

PHP has two kinds: **pure enums** (`enum Status { case Active; }`) whose cases have no
scalar value, and **backed enums** (`enum Status: string { case Active = 'active'; }`)
whose cases map to a `string` or `int` for serialization.

## Why It Matters

A "status" passed around as a raw string invites typos, invalid states, and scattered
`if ($s === 'activ')` bugs the compiler cannot catch. An enum makes the set of legal
values a type: an invalid value cannot exist, `match` can be checked for exhaustiveness by
static analysis, and every allowed case is discoverable from one place. Backed enums add
a safe boundary for I/O — you decide explicitly how a value crosses into and out of the
database or API. The trade-off is that changing an enum's cases is a code change, so
enums fit fixed vocabularies, not user-editable lists.

## Core Principles

- **Use an enum for a fixed, code-owned set of values.** Order statuses, roles, HTTP
  methods — yes. User-defined tags or catalog categories — no; those belong in data.
- **Back the enum only when it crosses a boundary.** Use a backed enum for DB columns,
  JSON, and configuration. Use a pure enum for purely in-memory state machines.
- **`from()` throws, `tryFrom()` returns null.** Choose based on whether an unknown
  value is a bug (`from`) or expected external input (`tryFrom`).
- **Enums are objects, not scalars.** They can implement interfaces, hold methods and
  constants, and are compared by identity (`===`), never by loose `==` to a string.
- **Prefer `match` over `switch` on enum cases.** `match` is strict, returns a value, and
  a static analyzer flags a missing case; `switch` silently falls through.

## Best Practices

- Attach behavior as methods on the enum (`->label()`, `->isFinal()`) instead of external
  helper functions keyed on the value — behavior stays next to the cases it describes.
- Use `tryFrom()` at every trust boundary (request payloads, DB reads from legacy data)
  and handle the `null` explicitly; use `from()` only when the value is already trusted.
- Implement an interface on the enum when several enums share a contract, so callers
  depend on the interface, not the concrete enum.
- Store the backing value (`$status->value`), never the case name, in the database; the
  name is source code, the value is your stable persisted contract.
- Iterate all cases with `Status::cases()` for validation lists, dropdowns, or seeding —
  never hand-maintain a parallel array of values.
- Keep backing values stable forever once persisted; changing `'active'` to `'a'` silently
  invalidates every stored row.

## Examples

**Good Example** — backed enum with behavior and a safe boundary

```php
enum OrderStatus: string
{
    case Pending  = 'pending';
    case Shipped  = 'shipped';
    case Delivered = 'delivered';
    case Cancelled = 'cancelled';

    // Behavior lives with the data it describes.
    public function isFinal(): bool
    {
        return match ($this) {
            self::Delivered, self::Cancelled => true,
            self::Pending, self::Shipped     => false,
            // No default: a new case added later forces this match to be updated.
        };
    }
}

// External input is untrusted, so tryFrom + explicit null handling.
$status = OrderStatus::tryFrom($request['status'] ?? '')
    ?? throw new InvalidArgumentException('Unknown order status');
```

**Bad Example** — stringly-typed status, no type safety

```php
class Order
{
    public string $status = 'pending'; // any string is accepted, including typos

    public function isFinal(): bool
    {
        // Loose, scattered, and a mistyped literal fails silently as "not final".
        return $this->status == 'deliverd' || $this->status == 'cancelled';
    }
}

$order->status = 'shpped'; // never rejected; corrupts data downstream
```

## Common Mistakes

- Using `from()` on user input, which throws a `ValueError` on any unknown value and
  crashes the request instead of returning a clean validation error.
- Comparing an enum with `==` against a string; an enum is an object and will not match.
- Persisting `$status->name` (the source-level identifier) instead of `$status->value`,
  coupling your database to your code's naming.
- Modeling an open, user-editable set as an enum, forcing a deploy for every new value.
- Adding a `default` arm to `match ($this)`, which defeats exhaustiveness checking when
  a new case is introduced.
- Trying to add cases dynamically or extend an enum — enums are final and closed by design.

## Production Tips

- Most ORMs (Doctrine, Eloquent) cast backed enums natively; declare the enum type on the
  column so reads and writes convert automatically and invalid DB values surface early.
- When migrating legacy string columns, backfill and validate every existing value against
  `tryFrom()` before flipping the column to an enum cast, or reads will explode.
- For API responses, serialize `->value`; never leak `->name`, and document the value set.

## AI Review Checklist

- Is the value set truly fixed and code-owned (enum) rather than user-editable (data)?
- Is `tryFrom()` used with explicit null handling at every untrusted boundary?
- Is the persisted/serialized form `->value`, and are backing values stable?
- Do `match ($this)` blocks list every case with no `default`, so new cases fail loudly?
- Is behavior attached as enum methods rather than external value-keyed helpers?
- Are enums compared with `===`/`match`, never loose `==` against scalars?

## Related

- `knowledge/php/02-types.md`
- `knowledge/php/04-oop.md`
- `knowledge/php/22-clean-code.md`
- `knowledge/php/12-database.md`
