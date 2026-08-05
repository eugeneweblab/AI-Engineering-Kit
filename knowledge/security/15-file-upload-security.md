---
id: security/15-file-upload-security
topic: security
slug: file-upload-security
title: "File Upload Security"
type: doc
order: 15
status: ready
tags: [security, file-upload-security, ValueError, Content-Type, nosniff, save]
related: [security/09-input-validation, security/11-xss, security/14-command-injection, security/28-owasp-top10]
when_to_use: "Read before building or reviewing any endpoint that accepts files from users — avatars, documents, imports, or media."
---
# File Upload Security

## Purpose

This document defines how to accept files from untrusted users without letting an
upload become code execution, storage abuse, or a delivery vector for malware. A
file is just attacker-controlled bytes plus attacker-controlled metadata (name,
extension, declared type). Treat every part of it as hostile and decide, on the
server, exactly what you will accept and where it will live.

The danger is not storing a file — it is what the *server* or a *later viewer* does
with it. Uploads intersect with [command injection](14-command-injection.md) (files
fed to shell tools), [XSS](11-xss.md) (HTML/SVG served inline), and path traversal.

## Why It Matters

An uploaded web shell placed inside the document root and then requested by URL is
a classic path to full server compromise. An SVG or HTML file served from your
domain runs JavaScript in your users' sessions. A crafted filename like
`../../etc/cron.d/x` overwrites system files. And unbounded uploads exhaust disk
or bandwidth. Uploads combine three attacker-controlled surfaces — bytes, name,
and type — so they need layered defenses, not a single extension check.

## Core Principles

- **Validate content, not just the claimed type.** The `Content-Type` header and
  file extension are attacker-supplied; verify the actual bytes (magic number /
  content sniffing) against an allowlist of permitted formats.
- **Never trust the filename.** Generate your own storage name; never use the
  client's name to build a path. This defeats path traversal and overwrite attacks.
- **Store outside the web root, serve deliberately.** Uploaded files must not be
  executable or directly reachable as URLs under an interpreter.
- **Constrain size and count.** Enforce hard limits before and during the read so a
  single request cannot exhaust memory, disk, or bandwidth.
- **Assume the file is malicious until proven otherwise.** Scan, sandbox
  processing, and serve back in a form that cannot execute.

## Best Practices

- Enforce a **type allowlist** by inspecting file content (magic bytes), not the
  extension or `Content-Type`. Reject anything not on the list — never use a
  blocklist, which always misses a format.
- Generate a random or hashed storage key (e.g. a UUID) and store the original name
  only as a display string. Build paths with a safe join and reject `..`, absolute
  paths, and null bytes.
- Store uploads outside the document root, or in object storage (S3/GCS) with
  execution disabled; serve them through a handler that sets `Content-Type` and
  `Content-Disposition: attachment` and an `X-Content-Type-Options: nosniff` header.
- Set and enforce a maximum file size at the proxy/framework *and* in code; cap the
  number of files per request and per user.
- Re-encode or transform where possible: decode and re-emit images through a trusted
  library, rasterize SVGs, or render documents to PDF, stripping active content.
- Run uploads through a malware scanner and process untrusted files in an isolated,
  least-privilege worker (container/sandbox) rather than the main app process.
- Serve user files from a separate, cookieless domain so a malicious file cannot
  script your primary origin or read its cookies.

## Examples

**Good Example** — content-checked type, generated name, non-executable storage

```python
import uuid, magic  # python-magic reads real content type from bytes

ALLOWED = {"image/png", "image/jpeg"}  # allowlist by verified content type
MAX_BYTES = 5 * 1024 * 1024

def store_upload(data: bytes, db):
    if len(data) > MAX_BYTES:
        raise ValueError("file too large")            # bounded before any processing
    kind = magic.from_buffer(data, mime=True)         # inspect bytes, not the header
    if kind not in ALLOWED:
        raise ValueError("unsupported file type")     # reject anything off the allowlist
    key = f"{uuid.uuid4()}.bin"                        # our name, never the client's
    object_store.put(key, data, content_type=kind, executable=False)  # outside web root
    return key
```

**Bad Example** — trusts extension and client name, serves from web root

```python
def store_upload(file):
    # Extension check only: "shell.php" renamed to "shell.php.png" or a polyglot
    # slips through, and the declared name drives the path.
    if file.filename.endswith((".png", ".jpg")):
        path = "/var/www/html/uploads/" + file.filename  # path traversal + executable dir
        file.save(path)                                  # served as code by the web server
        return path
```

## Common Mistakes

- Checking only the file extension or the `Content-Type` header, both of which the
  client controls.
- Saving with the user-supplied filename, enabling `../` traversal and overwriting
  existing files.
- Storing uploads inside the web/document root where the server will execute them.
- Serving user files inline (`Content-Disposition: inline`) so SVG/HTML runs script.
- Using a blocklist of "dangerous" extensions instead of an allowlist of permitted
  types.
- Enforcing the size limit only in the browser, or reading the whole file into
  memory before checking its size.

## Production Tips

- Put uploads behind antivirus/YARA scanning and quarantine on match; log the
  detected type, size, and storage key (never the raw bytes).
- Set object-storage bucket policies to deny public listing and disable code
  execution; use pre-signed, short-lived URLs for downloads.
- Rate-limit upload endpoints and enforce per-user storage quotas to bound abuse.

## AI Review Checklist

- Is the file type validated by inspecting content (magic bytes) against an allowlist?
- Is a server-generated name used, with the client filename never in a filesystem path?
- Are files stored outside the web root or in non-executable object storage?
- Are size and count limits enforced server-side, before full read into memory?
- Are downloads served with `nosniff` and `Content-Disposition: attachment`?
- Are risky formats (SVG/HTML) re-encoded, sandboxed, or blocked, and files scanned?

## Related

- `knowledge/security/09-input-validation.md`
- `knowledge/security/11-xss.md`
- `knowledge/security/14-command-injection.md`
- `knowledge/security/28-owasp-top10.md`
