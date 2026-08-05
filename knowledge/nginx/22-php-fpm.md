---
id: nginx/22-php-fpm
topic: nginx
slug: php-fpm
title: "Php FPM"
type: doc
order: 22
status: ready
tags: [nginx, php-fpm, pm.max_children, fastcgi_read_timeout, SCRIPT_FILENAME, max_execution_time, index.php, try_files]
related: [nginx/21-fastcgi, nginx/19-proxying-applications, nginx/07-static-files, nginx/13-security, nginx/18-performance]
when_to_use: "Read before deploying nginx with PHP-FPM for WordPress, Laravel, Symfony, or any PHP app."
---
# Php FPM

## Purpose

This document defines how to run nginx in front of PHP-FPM correctly and safely. PHP-FPM
is the FastCGI process manager that executes PHP; nginx talks to it over the FastCGI
protocol described in [fastcgi](21-fastcgi.md). This doc is the concrete, PHP-specific
layer: the front-controller routing pattern that every modern framework expects, the
`cgi.fix_pathinfo` setting that governs whether upload-RCE is possible, and the FPM pool
sizing that keeps the site from falling over.

If you only read one rule here: match `\.php$` exactly, verify the file exists, and set
`SCRIPT_FILENAME` from the document root. Everything else tunes performance; that rule
prevents remote code execution.

## Why It Matters

PHP-FPM is the most-attacked FastCGI setup on the internet because PHP apps accept file
uploads and PHP executes any `.php` file it is handed. Two settings decide whether an
uploaded `avatar.jpg` can be run as code: nginx's location regex and PHP's
`cgi.fix_pathinfo`. Get either wrong and a user-uploaded file becomes remote code
execution. Separately, PHP-FPM has a fixed pool of worker processes; size it wrong and the
site either exhausts memory (too many workers) or queues every request behind a full pool
(too few). Both failures are common and both are configuration, not code.

## Core Principles

- **Front-controller routing.** Modern frameworks route every dynamic request through one
  `index.php`. Use `try_files $uri $uri/ /index.php?$query_string;` and execute only
  `index.php` — do not let arbitrary `.php` files be requested directly.
- **Match `\.php$` exactly and verify existence.** Same rule as FastCGI: anchored regex
  plus `try_files ... =404` so only real scripts run.
- **Set `cgi.fix_pathinfo=0` in PHP.** The default (`1`) makes PHP fall back to a partial
  path, which is the mechanism behind `x.jpg/hack.php` execution.
- **Never execute uploads or writable dirs.** `wp-content/uploads`, `storage`, `public/media` —
  serve as data, never as PHP.
- **Size the FPM pool to memory, not to hope.** `pm.max_children` × peak per-request memory
  must fit in RAM with headroom. This is capacity planning, not a magic number.

## Best Practices

- Use the standard front-controller block: a `location /` with `try_files` falling back to
  `/index.php`, and a `location ~ \.php$` that runs it.
- Add `try_files $uri =404;` inside the PHP location so a request for a missing script
  returns 404 instead of reaching FPM.
- Set `fastcgi_pass unix:/run/php/php8.3-fpm.sock;` (a Unix socket) for a co-located pool —
  faster and unreachable from the network. Use TCP only when nginx and FPM are on different hosts.
- Set `SCRIPT_FILENAME $realpath_root$fastcgi_script_name;` (`$realpath_root` resolves
  symlinks — important for atomic deploys) and `include fastcgi_params;`.
- Deny access to sensitive files: `location ~ /\.` and hidden config; block direct access
  to `.env`, `composer.json`, `.git`.
- Choose an FPM `pm` mode: `dynamic` for variable load, `static` for predictable high load;
  set `pm.max_children` from `available_RAM / avg_process_MB`.
- Set `fastcgi_read_timeout` to match PHP's `max_execution_time`; if nginx gives up first,
  PHP keeps running a request no one reads.

## Examples

**Good Example** — front controller, existence check, safe uploads

```nginx
server {
    root /var/www/app/public;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;   # everything routes to the front controller
    }

    location ~ \.php$ {
        try_files $uri =404;                             # only run scripts that exist
        include fastcgi_params;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;      # local socket, off the network
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;  # symlink-safe
        fastcgi_read_timeout 60s;                        # match PHP max_execution_time
    }

    location ~* /uploads/.*\.php$ { deny all; }          # uploaded PHP is never executed
    location ~ /\.        { deny all; }                  # hide .env, .git, dotfiles
}
```

```ini
; php.ini — the setting that closes the upload-RCE path
cgi.fix_pathinfo=0
```

**Bad Example** — direct script access, path-info RCE open

```nginx
server {
    root /var/www/app;

    location ~ \.php$ {
        fastcgi_pass 127.0.0.1:9000;   # FPM port exposed; anyone on the network can reach it
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        # no try_files, no front controller: every .php is directly callable
        # with default cgi.fix_pathinfo=1, /uploads/avatar.jpg/x.php runs avatar.jpg as PHP
    }
    # no upload guard, no dotfile guard → .env and uploaded scripts are reachable
}
```

## Common Mistakes

- Leaving `cgi.fix_pathinfo=1` (the default) combined with a loose location, enabling the
  classic upload-to-RCE chain.
- Pointing `root` at the project root instead of `public/`, exposing `.env`, `vendor/`, and
  framework internals to direct download.
- Missing the front-controller `try_files`, so pretty URLs 404 and every `.php` is directly hittable.
- Setting `pm.max_children` too high, so a traffic spike spawns more PHP than RAM allows and
  the OOM killer takes down the box.
- Setting it too low, so requests queue behind a full pool and latency spikes under normal load.
- `fastcgi_read_timeout` shorter than PHP's `max_execution_time`, producing 504s while PHP
  is still working.
- Exposing the FPM TCP port to the network instead of a local socket.

## Production Tips

- Watch FPM's own status page (`pm.status_path`) for `listen queue` and `active processes`;
  a growing listen queue means `pm.max_children` is too low.
- Enable OPcache in production (`opcache.enable=1`, `opcache.validate_timestamps=0` for
  immutable deploys) — it is the single biggest PHP performance win.
- Use `$realpath_root` with symlink-based atomic deploys so OPcache does not serve a stale
  path after a release.
- Add `fastcgi_cache` for cacheable pages (logged-out WordPress traffic, public pages); it
  serves without invoking PHP at all. See [fastcgi](21-fastcgi.md).
- Log slow PHP requests via FPM's `slowlog` + `request_slowlog_timeout` to find the actual
  bottleneck instead of guessing.

## AI Review Checklist

- Is `root` set to the framework's `public`/web directory, not the project root?
- Is there a front-controller `try_files ... /index.php?$query_string;`?
- Does the PHP location match `\.php$` exactly with `try_files $uri =404;`?
- Is `cgi.fix_pathinfo=0` set in php.ini?
- Is execution denied in upload and writable directories, and are dotfiles blocked?
- Is FPM reached over a Unix socket (or a firewalled port), not an open TCP port?
- Does `fastcgi_read_timeout` match PHP `max_execution_time`, and is `pm.max_children`
  sized to available RAM?

## Related

- `knowledge/nginx/21-fastcgi.md`
- `knowledge/nginx/19-proxying-applications.md`
- `knowledge/nginx/07-static-files.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/18-performance.md`
