---
id: php/06-autoloading
topic: php
slug: autoloading
title: "Autoloading"
type: doc
order: 6
status: ready
tags: [php, autoloading, UserService, files, composer.json, autoload, declare, autoload.psr-4]
related: [php/05-namespaces, php/07-composer, php/24-psr-standards, php/04-oop]
when_to_use: "Read before wiring up class loading, adding a package, or touching composer.json autoload config."
---
# Autoloading

## Purpose

This document defines how PHP finds and loads class, interface, trait, and enum
definitions on demand. Modern PHP does not `require` files by hand — it registers an
*autoloader* that maps a fully-qualified class name to a file path and includes it the
first time the class is referenced. The de facto standard is **PSR-4**, driven by
[Composer](07-composer.md). This doc is written so an agent can configure autoloading
correctly and never reintroduce manual `require` chains.

## Why It Matters

Autoloading is the backbone of every namespaced PHP codebase. Get the class-to-path
mapping wrong and nothing loads: you get a fatal `Class "App\Foo" not found` at runtime,
often only on a code path that CI missed. Manual `require` lists rot silently — a moved
file, a renamed class, a wrong include order, and the app breaks in production. A correct
PSR-4 setup makes the mapping mechanical and total: any class in the right namespace and
directory is found automatically, forever, with zero maintenance.

## Core Principles

- **One class per file, named exactly after the class.** PSR-4 requires the file
  basename to match the class name, case-sensitive. `class UserService` lives in
  `UserService.php` — not `user-service.php`, not two classes in one file.
- **Namespace prefix maps to a base directory.** A PSR-4 rule says "namespace prefix
  `App\` maps to directory `src/`". The remaining namespace segments become
  subdirectories: `App\Http\Controller` resolves to `src/Http/Controller.php`.
- **Never `require` a class file yourself.** Registering the autoloader once (via
  `vendor/autoload.php`) is the only include a modern app needs for classes.
- **Autoloaders may only load; they must not have side effects.** An autoloaded file
  must contain only a definition — no echo, no top-level function calls, no state.
- **Regenerate the map after moving files.** Composer caches the classmap; a stale
  cache is a common "why isn't my new class found" bug.

## Best Practices

- Define autoloading in `composer.json` under `autoload.psr-4`, keying the namespace
  prefix (with trailing `\`) to its directory. Run `composer dump-autoload` after edits.
- Keep test and dev-only classes under `autoload-dev` so they never ship to production.
- For production, run `composer dump-autoload --optimize --classmap-authoritative` (or
  install with `--no-dev -o`). This builds a static classmap so the loader never hits
  the filesystem to guess paths — a measurable request-time win.
- Prefer PSR-4 over PSR-0 (deprecated) and over `classmap`/`files` autoloading. Reserve
  `files` autoload strictly for non-class globals like helper functions.
- Match directory case to namespace case exactly. It works on case-insensitive macOS
  and breaks on the Linux production box — the classic "works on my machine" outage.
- Do not commit the generated `vendor/` directory; commit `composer.json` and
  `composer.lock` and let CI/CD run `composer install`.

## Examples

**Good Example** — PSR-4 config plus a matching class

```json
// composer.json — namespace prefix "App\" resolves to the src/ directory
{
    "autoload": {
        "psr-4": { "App\\": "src/" }
    },
    "autoload-dev": {
        "psr-4": { "App\\Tests\\": "tests/" }
    }
}
```

```php
<?php
// src/Service/UserService.php  — path mirrors the FQCN exactly
declare(strict_types=1);

namespace App\Service;            // App\ -> src/, so Service\ -> src/Service/

final class UserService {}         // file basename == class name (case-sensitive)
```

```php
<?php
require __DIR__ . '/vendor/autoload.php'; // the ONLY include an app needs
$svc = new App\Service\UserService();      // autoloaded on first use, no require
```

**Bad Example** — manual requires and a mismatched map

```php
<?php
// Hand-maintained include list: rots the moment a file moves or is added.
require __DIR__ . '/src/Service/user_service.php'; // wrong case + wrong name vs class
require __DIR__ . '/src/Service/OrderService.php'; // order-sensitive, easy to break

$svc = new App\Service\UserService();
// Fatal on Linux: filename casing doesn't match the class -> "Class not found".
// Every new class means another require here; miss one and it fails at runtime.
```

## Common Mistakes

- Filename or directory case that does not match the class/namespace exactly — passes on
  macOS/Windows, fatals on Linux.
- Forgetting `composer dump-autoload` after adding a class or editing autoload rules.
- Putting side-effect code (output, bootstrapping) in an autoloaded class file.
- Declaring multiple classes in one file, so autoloading finds only the first.
- Using `files` autoload for classes instead of PSR-4, defeating lazy loading.
- Shipping dev/test namespaces to production because they were under `autoload` instead
  of `autoload-dev`.

## Production Tips

- Build the optimized authoritative classmap in your Docker/CI image:
  `composer install --no-dev --optimize-autoloader --classmap-authoritative`.
- With `--classmap-authoritative`, a class missing from the map is treated as
  non-existent (no filesystem fallback), so verify the build includes every namespace.
- If you use a preloading setup (`opcache.preload`), feed it the generated classmap so
  hot classes are compiled once at server start.

## AI Review Checklist

- Does every class file contain exactly one class, named identically to the file?
- Do namespace prefixes in `composer.json` map to real directories with matching case?
- Is `vendor/autoload.php` the only class include, with no hand-written `require` lists?
- Are test-only namespaces under `autoload-dev`, not `autoload`?
- Does the production build run `--optimize-autoloader` (and ideally authoritative)?
- Are autoloaded files free of side effects (output, top-level calls)?

## Related

- `knowledge/php/05-namespaces.md`
- `knowledge/php/07-composer.md`
- `knowledge/php/24-psr-standards.md`
- `knowledge/php/04-oop.md`
