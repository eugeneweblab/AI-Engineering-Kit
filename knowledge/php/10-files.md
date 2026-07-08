---
id: php/10-files
topic: php
slug: files
title: "Files"
type: doc
order: 10
status: ready
tags: [php, files]
related: [php/08-error-handling, php/13-security, php/11-http, php/18-generators]
when_to_use: "Read before reading, writing, uploading, or building any path from user-influenced input."
---
# Files

## Purpose

This document defines how to work with the filesystem safely and efficiently in PHP:
reading and writing, streaming large files, handling uploads, and — most importantly —
building paths from untrusted input without opening a directory-traversal or overwrite
hole. Filesystem code sits directly on top of the OS, so mistakes here become security
bugs and data loss, not just wrong output.

## Why It Matters

The filesystem is a shared, mutable, attacker-reachable resource. A path assembled from
user input can escape its intended directory (`../../etc/passwd`), overwrite critical
files, or serve arbitrary content. Reading a large file into memory with
`file_get_contents` can exhaust the process. A missing `false` check on a write can lose
data silently. Every file operation must assume the path may be hostile, the disk may be
full, and the file may vanish between two calls.

## Core Principles

- **Never trust a path built from input.** Resolve it with `realpath()` and verify the
  result is still inside an allowlisted base directory before touching it. A filename from
  a request is data, not a path.
- **Check every return value.** `fopen`, `file_get_contents`, `file_put_contents`, and
  friends return `false` on failure. Treat `false` as an error you must handle, not ignore.
- **Stream large or unbounded data; never slurp it.** Use `fopen`/`fgets`/`SplFileObject`
  or generators for big files so memory stays constant regardless of file size.
- **Write atomically.** Write to a temp file, then `rename()` into place. `rename` is
  atomic on the same filesystem, so readers never see a half-written file.
- **Release resources deterministically.** Close handles and use `finally` so a throw
  mid-operation does not leak file descriptors or leave locks held.

## Best Practices

- Validate uploaded files by content and size, not by the client-supplied name or
  extension. Use `finfo` for the real MIME type, cap the size, and store under a generated
  name — never the original filename.
- Confirm an upload with `is_uploaded_file()` and move it with `move_uploaded_file()`;
  do not use `copy()`/`rename()` on `$_FILES['x']['tmp_name']` directly.
- Prefer relative-safe operations: canonicalize with `realpath()`, then check
  `str_starts_with($resolved, $baseDir)` to enforce the sandbox boundary.
- Use `LOCK_EX` with `file_put_contents` (or `flock`) when concurrent writers are
  possible, to avoid interleaved/corrupt writes.
- For serving files over [HTTP](11-http.md), stream with `readfile()`/`fpassthru()` and
  set correct headers; never `echo file_get_contents()` on a large asset.
- Keep upload/temp directories outside the web root, or block execution there, so an
  uploaded `.php` can never be run.

## Examples

**Good Example** — sandboxed path, streamed read, atomic write

```php
<?php
declare(strict_types=1);

function readUserFile(string $baseDir, string $userPath): string
{
    $base = realpath($baseDir);
    $full = realpath($baseDir . '/' . $userPath);   // canonicalize, resolving ../

    // Reject anything that escapes the sandbox (traversal) or does not exist.
    if ($base === false || $full === false || !str_starts_with($full, $base . DIRECTORY_SEPARATOR)) {
        throw new RuntimeException('Path outside allowed directory');
    }

    $data = file_get_contents($full);
    if ($data === false) {                            // never ignore the false return
        throw new RuntimeException("Unable to read {$full}");
    }
    return $data;
}

// Atomic write: reader sees either the old file or the fully-written new one, never half.
function writeAtomic(string $target, string $contents): void
{
    $tmp = $target . '.' . bin2hex(random_bytes(6)) . '.tmp';
    if (file_put_contents($tmp, $contents, LOCK_EX) === false || !rename($tmp, $target)) {
        @unlink($tmp);
        throw new RuntimeException("Failed writing {$target}");
    }
}
```

**Bad Example** — traversal, unchecked, memory blow-up

```php
<?php
// User controls the whole path -> ../../../../etc/passwd escapes the intended folder.
$path = '/var/app/files/' . $_GET['name'];
echo file_get_contents($path);          // no false check; disclosure + fatal on failure

// Trusts client filename & extension; stores executable content in the web root.
move_uploaded_file($_FILES['f']['tmp_name'], __DIR__ . '/uploads/' . $_FILES['f']['name']);

// Slurps an arbitrarily large file fully into memory -> OOM under load.
$all = file_get_contents('/var/log/huge.log');
```

## Common Mistakes

- Concatenating user input into a path without `realpath()` + base-directory check.
- Ignoring the `false` return of read/write calls, losing or corrupting data silently.
- Trusting `$_FILES['x']['name']` / `['type']` — both are attacker-controlled.
- Storing uploads under the web root with executable extensions.
- Loading huge files with `file_get_contents`/`file()` instead of streaming.
- Non-atomic writes that let readers observe a partially written file.
- Leaking file handles by not closing them on the error path.

## Production Tips

- Enforce size limits at both the web-server (`client_max_body_size`) and PHP
  (`upload_max_filesize`, `post_max_size`) layers; the app check is the last line, not
  the only one.
- Put user uploads on object storage (S3/GCS) rather than local disk when horizontally
  scaled, so files are not tied to one node.
- Monitor disk usage and handle `ENOSPC` (write returns `false`) gracefully instead of
  crashing mid-request.

## AI Review Checklist

- Is every path from input canonicalized with `realpath()` and confined to a base dir?
- Is the return value of every file read/write checked for `false`?
- Are uploads validated by real MIME/size and stored under generated names outside web root?
- Are large files streamed rather than read wholly into memory?
- Are writes atomic (temp file + `rename`) where partial reads would be harmful?
- Are file handles closed on both success and error paths (`finally`)?

## Related

- `knowledge/php/08-error-handling.md`
- `knowledge/php/13-security.md`
- `knowledge/php/11-http.md`
- `knowledge/php/18-generators.md`
