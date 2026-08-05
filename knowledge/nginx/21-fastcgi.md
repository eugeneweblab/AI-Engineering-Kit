---
id: nginx/21-fastcgi
topic: nginx
slug: fastcgi
title: "FastCGI"
type: doc
order: 21
status: ready
tags: [nginx, fastcgi, SCRIPT_FILENAME, fastcgi_cache, fastcgi_read_timeout, proxy_pass, proxy_set_header, try_files]
related: [nginx/22-php-fpm, nginx/19-proxying-applications, nginx/07-static-files, nginx/13-security, nginx/04-location-blocks]
when_to_use: "Read before wiring nginx to any FastCGI backend (PHP-FPM, Python flup, Perl) with fastcgi_pass."
---
# FastCGI

## Purpose

This document defines how to connect nginx to a FastCGI application server. FastCGI is a
binary protocol — distinct from HTTP `proxy_pass` — that nginx speaks to long-running
backends like PHP-FPM. Instead of forwarding an HTTP request, nginx builds a set of
FastCGI *parameters* (the CGI environment) and hands them to the backend. Getting those
parameters right, and only routing real scripts, is what this doc is about.

The most common FastCGI backend, PHP-FPM, has its own document
([php-fpm](22-php-fpm.md)) covering socket, pool, and security specifics. This doc is the
protocol layer: how `fastcgi_pass`, `fastcgi_param`, and `SCRIPT_FILENAME` fit together,
and the path-handling mistake that turns FastCGI into remote code execution.

## Why It Matters

FastCGI executes code. Unlike a reverse proxy that just relays bytes, a FastCGI backend
runs the file that nginx names in `SCRIPT_FILENAME`. If nginx computes that path from
untrusted request data — or passes a request for `evil.jpg` to the interpreter — an
attacker can make the backend execute a file they uploaded. The classic PHP RCE
(`/uploads/avatar.jpg/x.php`) is a FastCGI misconfiguration, not a PHP bug. Because the
blast radius is arbitrary code execution, the routing rules here are security-critical,
not stylistic.

## Core Principles

- **Only pass real script files to the interpreter.** Match an exact extension at the end
  of the URI (`\.php$`), never a substring. A file that merely contains `.php` in its path
  must never reach `fastcgi_pass`.
- **Set `SCRIPT_FILENAME` from the resolved document root, not raw request data.** The
  backend runs whatever this points at; compute it deterministically.
- **Guard against path traversal with `try_files`.** Confirm the script exists on disk
  before handing it to FastCGI, so requests for nonexistent scripts get a 404, not an
  interpreter probe.
- **Include the standard params, then override intentionally.** `include fastcgi_params;`
  provides the CGI environment; add `SCRIPT_FILENAME` explicitly — do not rely on it being
  set for you.
- **FastCGI is not HTTP.** Use `fastcgi_pass`, `fastcgi_param`, `fastcgi_cache` — the
  `proxy_*` directives do not apply to a FastCGI upstream.

## Best Practices

- Route scripts with a regex `location ~ \.php$` and immediately re-validate with
  `try_files $uri =404;` so only files that exist are executed.
- Set `SCRIPT_FILENAME` as `$document_root$fastcgi_script_name` and `include fastcgi_params;`.
- Set `fastcgi_split_path_info` and pass `PATH_INFO` only if the app needs it; otherwise
  leave it off — path info is the vector for the `.jpg/x.php` attack.
- Disable execution in upload directories entirely (a `location` that returns 403 or omits
  the FastCGI handler) so uploaded files can never be interpreted.
- Bound the backend with `fastcgi_connect_timeout` and `fastcgi_read_timeout`, same
  reasoning as proxy timeouts — a hung interpreter should not pin nginx forever.
- Size `fastcgi_buffers` for typical responses; cache cacheable responses with
  `fastcgi_cache` for a large win on read-heavy apps.
- Pass a Unix socket (`unix:/run/php/php-fpm.sock`) for a co-located backend rather than a
  TCP port, so the interpreter is unreachable from the network.

## Examples

**Good Example** — exact match, existence check, deterministic script path

```nginx
server {
    root /var/www/app/public;

    location ~ \.php$ {
        try_files $uri =404;                 # 404 if the script doesn't exist — blocks probes

        include fastcgi_params;              # standard CGI environment
        fastcgi_pass unix:/run/php/php-fpm.sock;  # local socket, off the network
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;  # resolved, not raw

        fastcgi_read_timeout 60s;            # bound a stuck interpreter
    }

    # Uploaded files can never be executed, only served as data
    location /uploads/ {
        location ~ \.php$ { return 403; }    # defense in depth against upload RCE
    }
}
```

**Bad Example** — loose match enables remote code execution

```nginx
server {
    root /var/www/app/public;

    location ~ \.php {                       # no end anchor: matches /uploads/x.jpg/hack.php too
        fastcgi_pass unix:/run/php/php-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        # no try_files: nonexistent scripts still hit the interpreter
        # with default cgi.fix_pathinfo, /uploads/avatar.jpg/x.php executes avatar.jpg as PHP
    }
}
```

## Common Mistakes

- Using `location ~ \.php` (or `\.php.*`) without the `$` end anchor, so paths containing
  `.php` anywhere match and reach the interpreter.
- Omitting `try_files $uri =404;`, letting requests for nonexistent scripts probe the backend.
- Allowing script execution inside upload/writable directories, turning a file upload into
  code execution.
- Forgetting `include fastcgi_params;` or `SCRIPT_FILENAME`, so the backend gets an empty
  or wrong environment and returns "No input file specified" or "Primary script unknown".
- Reaching for `proxy_pass`/`proxy_set_header` on a FastCGI backend — wrong protocol.
- Exposing the FastCGI port (`9000`) to the network instead of a local socket.

## Production Tips

- Set `fastcgi_cache` with a sensible key and `fastcgi_cache_valid` for cacheable pages;
  measure the hit ratio — it can offload the interpreter dramatically.
- Log `$upstream_status` and `$upstream_response_time` for the FastCGI location so you can
  distinguish nginx errors from interpreter errors.
- Keep `SCRIPT_FILENAME` construction identical across all server blocks — a single
  divergent block is where the RCE hides.
- When adding a new file type (e.g. `.phtml`) to execution, audit every upload path first;
  a new executable extension re-opens the upload-RCE question.

## AI Review Checklist

- Does the FastCGI location match an exact anchored extension (`~ \.php$`), not a substring?
- Is `try_files $uri =404;` present before `fastcgi_pass`?
- Is `SCRIPT_FILENAME` built from `$document_root$fastcgi_script_name`, not request data?
- Is script execution disabled in upload/writable directories?
- Is `include fastcgi_params;` present, with explicit overrides after it?
- Is the backend reached over a local socket rather than an exposed TCP port?
- Are `fastcgi_connect_timeout`/`fastcgi_read_timeout` set?

## Related

- `knowledge/nginx/22-php-fpm.md`
- `knowledge/nginx/19-proxying-applications.md`
- `knowledge/nginx/07-static-files.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/04-location-blocks.md`
