---
id: php/05-namespaces
topic: php
slug: namespaces
title: "Namespaces"
type: doc
order: 5
status: ready
tags: [php, namespaces, array_sum, InvoiceService, total, LoggerInterface, declare, composer.json]
related: [php/04-oop, php/06-autoloading, php/07-composer, php/24-psr-standards, php/00-overview]
when_to_use: "Read before creating a new class file, choosing a namespace, or wiring PSR-4 autoloading."
---
# Namespaces

## Purpose

This document defines how to organize PHP code into namespaces and map them to files. It
covers namespace declaration, the `use` import rules, fully-qualified vs. relative names,
the leading-backslash convention, and how namespaces align with PSR-4 autoloading so a
class name resolves to exactly one file.

## Why It Matters

Namespaces are how PHP avoids name collisions between your code, libraries, and the global
runtime. Combined with PSR-4, the namespace *is* the file path: `App\Billing\Invoice` lives
at `src/Billing/Invoice.php`, and Composer's autoloader finds it with no manual `require`.
Get the mapping wrong and autoloading fails with a "class not found" that is tedious to
debug; get global-function resolution wrong and you silently pay a performance and clarity
cost on every call.

## Core Principles

- **One class per file, namespace mirrors directory (PSR-4).** The file's namespace plus
  class name must match its path under the Composer `autoload` root. This is what makes the
  class loadable. See [autoloading](06-autoloading.md).
- **`namespace` must be the first statement.** Only `declare(strict_types=1);` and comments
  may precede it. Everything after belongs to that namespace.
- **Import symbols with `use`; reference them short.** Put `use App\Billing\Invoice;` at the
  top, then write `Invoice` in the body. This keeps the code readable and the dependencies
  visible in one place.
- **Prefix global functions/constants with `\` in namespaced code.** Inside a namespace,
  an unqualified `strlen()` triggers a fallback lookup (namespace first, then global).
  `\strlen()` resolves directly — clearer and marginally faster.
- **Match your vendor namespace to Composer.** The top-level namespace (`App\`, `Acme\`)
  is declared in `composer.json`'s PSR-4 map; keep them in sync. See [composer](07-composer.md).

## Best Practices

- Group `use` statements at the top, one symbol per line; PSR-12 orders them and tooling
  (Pint/PHP-CS-Fixer) can sort and dedupe them automatically. See [psr-standards](24-psr-standards.md).
- Use `use ... as Alias` only to resolve a genuine name clash between two imported classes,
  not to shorten already-short names — aliases obscure origin.
- Import functions and constants explicitly with `use function` / `use const` when you use
  them repeatedly, rather than fully-qualifying at every call.
- Keep namespace depth shallow and meaningful (`App\Domain\Billing`), reflecting bounded
  contexts, not arbitrary layers.
- Never rely on the global namespace for your own code; everything you write should be
  namespaced so it is autoloadable and collision-free.

## Examples

**Good Example** — PSR-4 mapping, explicit imports, `\` on globals

```php
<?php
// File: src/Billing/InvoiceService.php   Composer: {"autoload":{"psr-4":{"App\\":"src/"}}}

declare(strict_types=1);

namespace App\Billing;              // first statement; mirrors the directory path

use App\Billing\Invoice;           // imported once, referenced short below
use Psr\Log\LoggerInterface;       // third-party class from its own vendor namespace

final class InvoiceService
{
    public function __construct(private LoggerInterface $logger) {}

    public function total(Invoice $invoice): int
    {
        // \array_sum resolves straight to the global function, no namespace fallback
        return \array_sum($invoice->lineTotals());
    }
}
```

**Bad Example** — mismatched path, fully-qualified everywhere, fallback lookups

```php
<?php
// File: src/services/invoice_service.php  ← path does not match namespace → PSR-4 miss

namespace app\billing; // wrong case ('app' vs 'App'): autoloader will not find this class

class InvoiceService {
    public function total($invoice) {
        // Fully-qualifying a class inline instead of importing hides the dependency
        $lines = \App\Billing\Invoice::linesFrom($invoice);
        // Unqualified global call triggers a namespace-first fallback lookup each time
        return array_sum($lines);
    }
}
```

## Common Mistakes

- Namespace or file case not matching the path, so PSR-4 autoloading fails with "class not
  found".
- Putting code or `use` before the `namespace` declaration (must be first).
- Fully-qualifying class names inline instead of importing them with `use`, hiding
  dependencies and cluttering the body.
- Calling global functions unqualified in namespaced code, incurring the fallback lookup.
- Aliasing everything, making it unclear which package a class comes from.
- Editing the PSR-4 map in `composer.json` and forgetting to run `composer dump-autoload`.

## Production Tips

- After changing namespaces or the autoload map, run `composer dump-autoload -o` so the
  optimized classmap reflects the new layout.
- A linter rule (PHP-CS-Fixer `global_namespace_import` / `native_function_invocation`) can
  enforce the `\`-prefix and import conventions automatically.

## AI Review Checklist

- Does each file's namespace + class name match its path under the PSR-4 root, including
  case?
- Is `namespace` the first statement (after only `declare` and comments)?
- Are external classes imported with `use` and referenced by short name?
- Are global functions/constants called with a leading `\` in namespaced code?
- Is the top-level namespace consistent with the Composer autoload map?
- Are aliases used only to resolve real name collisions?

## Related

- `knowledge/php/04-oop.md`
- `knowledge/php/06-autoloading.md`
- `knowledge/php/07-composer.md`
- `knowledge/php/24-psr-standards.md`
- `knowledge/php/00-overview.md`
