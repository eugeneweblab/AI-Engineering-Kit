---
id: php/24-psr-standards
topic: php
slug: psr-standards
title: "PSR Standards"
type: doc
order: 24
status: ready
tags: [php, psr-standards, __construct, autoload.psr-4, LoggerInterface, issue, Redis]
related: [php/07-composer, php/06-autoloading, php/28-tooling, php/22-clean-code, php/20-dependency-injection]
when_to_use: "Read before naming files, wiring interfaces between libraries, or configuring a formatter/autoloader."
---
# PSR Standards

## Purpose

PSRs (PHP Standards Recommendations) are the interoperability contracts published by
the PHP-FIG group. They define how autoloading finds classes, how code is formatted,
and what shared interfaces (logging, caching, HTTP messages, containers) look like so
that libraries from different vendors compose without glue code. This document tells an
agent which PSRs are load-bearing, which are superseded, and how to apply them.

A PSR is not a style opinion — it is a published interface or convention that other
code depends on. Follow the active ones and cite them by number, not by memory.

## Why It Matters

PHP's ecosystem is built on Composer packages from thousands of vendors. That only works
because they agree on contracts: PSR-4 lets any autoloader find any class, PSR-3 lets any
framework accept any logger, PSR-7/15/17 let middleware from one library run in another's
pipeline. Ignore the standards and you get duplicate adapters, broken autoloading, and
interfaces that cannot be swapped. Following PSRs is the cheapest way to keep code
replaceable and reviewable — every PHP developer already knows what PSR-12 code looks like.

## Core Principles

- **Prefer the interface PSR, not a concrete class.** Type-hint `Psr\Log\LoggerInterface`,
  not `Monolog\Logger`, so implementations stay swappable.
- **Know what is active vs. superseded.** PSR-0 and PSR-2 are deprecated. Use **PSR-4**
  for autoloading and **PSR-12** (the extension of the retired PSR-2) for style, now
  itself extended by the evolving **PER Coding Style** the FIG maintains.
- **Standards are contracts, not suggestions.** A PSR-4 namespace must map exactly to a
  directory; a one-character mismatch breaks autoloading silently under optimized dumps.
- **Depend on abstractions the FIG defines.** PSR-3 (Log), PSR-6/16 (Cache), PSR-11
  (Container), PSR-7/15/17/18 (HTTP) exist so you never invent your own version.

## Best Practices

- Configure Composer `autoload.psr-4` to map each namespace prefix to one base directory;
  keep file names identical to class names (case-sensitive) so it works on Linux.
- Format with a tool (PHP-CS-Fixer or PHP_CodeSniffer) pinned to the PSR-12 / PER ruleset
  in CI — do not hand-format, because reviewers should never argue about braces.
- Accept `Psr\Log\LoggerInterface`, `Psr\SimpleCache\CacheInterface`, and
  `Psr\Container\ContainerInterface` in constructors; let the framework inject a concrete.
- For HTTP, build on PSR-7 messages and PSR-15 middleware so handlers are portable across
  Slim, Laminas, Mezzio, and Symfony's PSR bridge.
- Use PSR-17 factories to *create* PSR-7 objects rather than `new` on a concrete class —
  the concrete implementation then stays a dependency you can replace.
- Reference PSRs by number in code comments and ADRs so the contract is discoverable.

## Examples

**Good Example** — depend on the PSR interface, autoload by PSR-4

```php
<?php
// composer.json: "autoload": { "psr-4": { "App\\": "src/" } }
// So App\Service\Invoicer lives at src/Service/Invoicer.php — exact case, one mapping.

namespace App\Service;

use Psr\Log\LoggerInterface; // PSR-3: any logger, not a specific vendor

final class Invoicer
{
    public function __construct(private LoggerInterface $logger) {}

    public function issue(Invoice $invoice): void
    {
        // Swappable: Monolog in prod, a test spy in CI — same interface.
        $this->logger->info('invoice.issued', ['id' => $invoice->id]);
    }
}
```

**Bad Example** — concrete coupling and a broken PSR-4 mapping

```php
<?php
namespace App\Service;

use Monolog\Logger; // ties this class to one logger vendor forever

final class Invoicer
{
    // File saved as src/Service/invoicer.php (lowercase) — autoload fails on Linux
    // even though it "works" on a case-insensitive macOS dev machine.
    public function __construct(private Logger $logger) {}
}
```

## Common Mistakes

- Type-hinting a concrete `Monolog\Logger` or `Redis` instead of the PSR interface,
  making the dependency impossible to mock or replace.
- File name case not matching the class name — passes locally, 500s in production.
- Multiple PSR-4 prefixes pointing at the same directory, causing ambiguous resolution.
- Still following PSR-0 or PSR-2 in new code; both are deprecated.
- Hand-formatting to "roughly PSR-12" instead of enforcing it with a tool in CI.
- Reinventing a logger, cache, or container interface the FIG already standardized.

## Production Tips

- Run `composer dump-autoload --optimize --classmap-authoritative` for release builds;
  it turns PSR-4 lookups into a static map but *requires* the case to be exactly right.
- Pin the coding-standard ruleset version so a tool upgrade cannot silently reformat the
  whole repo in one PR.

## AI Review Checklist

- Do constructors depend on PSR interfaces (Log, Cache, Container) instead of concretes?
- Does every namespace prefix map to exactly one directory via `autoload.psr-4`?
- Do file names match class names in case, so autoloading survives on Linux?
- Is PSR-12 / PER style enforced by a formatter in CI, not by hand?
- Are HTTP components built on PSR-7/15/17 rather than framework-specific classes?
- Is any deprecated PSR-0 or PSR-2 usage removed from new code?

## Related

- `knowledge/php/07-composer.md`
- `knowledge/php/06-autoloading.md`
- `knowledge/php/28-tooling.md`
- `knowledge/php/22-clean-code.md`
- `knowledge/php/20-dependency-injection.md`
