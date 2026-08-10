---
id: divi/19-security
topic: divi
slug: security
title: "Divi Security"
type: doc
order: 19
status: ready
tags: [divi, security, unfiltered_html, wp_kses, update_post_meta, current_user_can, add_action, esc_html, ajax, builder, handler]
related: [divi/04-custom-modules, divi/16-wordpress-hooks, divi/17-rest-api, divi/23-maintenance, divi/99-ai-review-checklist]
when_to_use: "Read before writing any Divi custom module, AJAX handler, code module, or granting builder access."
---
# Divi Security

## Purpose

This document defines how to keep a Divi + WordPress site secure: safe custom-module and
[hook](16-wordpress-hooks.md) code, correct capability and nonce checks, disciplined use
of Divi's raw-code features, and least-privilege access to the builder. It is written so
an agent can add functionality to a Divi site without opening an injection or privilege
hole.

## Why It Matters

A Divi site is a full WordPress install with a large plugin surface, and Divi itself has
shipped critical CVEs (privilege escalation, arbitrary uploads) that were only closed by
updates. On top of that, Divi hands editors raw-HTML/JS features (the Code module, the
`unfiltered_html` capability) and custom modules run arbitrary PHP. One unescaped output
or one missing capability check is a stored-XSS or RCE that affects every visitor. Because
the same install serves the public and hosts the admin, the blast radius of a mistake is
the whole site.

## Core Principles

- **Sanitize input, escape output, verify intent.** Every request value is hostile: sanitize
  on the way in, escape on the way out (`esc_html`, `esc_attr`, `esc_url`, `wp_kses`), and
  gate state changes with a nonce **and** a capability check. See [custom-modules](04-custom-modules.md).
- **Least privilege for the builder.** The Divi Builder and `unfiltered_html` let a user
  inject scripts. Only trusted roles get them; Authors/Editors should not run raw HTML/JS.
- **Keep Divi and WordPress current.** Most Divi exploits are patched vulnerabilities. An
  outdated Divi or WP core is the single most common way these sites are compromised. See
  [maintenance](23-maintenance.md).
- **Never trust imported layouts.** Divi Library JSON and third-party child themes can carry
  malicious Code modules or PHP. Review before importing.

## Best Practices

- In custom modules and AJAX handlers: `check_ajax_referer()` / `wp_verify_nonce()`, then
  `current_user_can()`, **before** any write. Escape every dynamic value at output.
- Treat the **Code module** as a privilege: restrict who can add pages using it, and never
  paste third-party `<script>` snippets you have not read.
- Add `define('DISALLOW_FILE_EDIT', true);` so a compromised admin cannot edit theme/plugin
  files from the dashboard.
- Store the Divi Updates username/API key and any integration secrets in `wp-config.php` or
  a secrets manager — never in a Code module, post content, or the repo.
- Lock down the [REST API](17-rest-api.md): authenticate write endpoints, and do not expose
  custom fields containing PII via unauthenticated routes.
- Enforce HTTPS, strong admin passwords + 2FA, and limit login attempts; the builder is
  admin-only, so protecting `wp-admin` protects the builder.
- Put all PHP in a child theme so security patches to the Divi parent theme apply cleanly.

## Examples

**Good Example** — nonce, capability, sanitize, escape

```php
add_action( 'wp_ajax_save_cta', function () {
    // Verify intent (CSRF) and permission BEFORE doing anything.
    check_ajax_referer( 'cta_save', 'nonce' );
    if ( ! current_user_can( 'edit_posts' ) ) {
        wp_send_json_error( 'forbidden', 403 );
    }

    $label = sanitize_text_field( wp_unslash( $_POST['label'] ?? '' ) ); // sanitize in
    update_post_meta( absint( $_POST['post_id'] ), 'cta_label', $label );

    wp_send_json_success( array( 'label' => esc_html( $label ) ) ); // escape out
} );
```

**Bad Example** — no checks, echoes raw input

```php
add_action( 'wp_ajax_nopriv_save_cta', function () {   // nopriv: anyone, unauthenticated
    // No nonce, no capability check -> CSRF + privilege escalation
    update_post_meta( $_POST['post_id'], 'cta_label', $_POST['label'] ); // unsanitized
    echo $_POST['label'];   // reflected XSS: attacker-controlled HTML echoed verbatim
    wp_die();
} );
```

## Common Mistakes

- Registering `wp_ajax_nopriv_*` handlers that perform writes with no auth.
- Echoing shortcode attributes or field values without `esc_*` / `wp_kses`, enabling XSS.
- Handing Editors/Authors the Code module or `unfiltered_html`, letting them inject scripts.
- Running an outdated Divi with a known, publicly-documented CVE.
- Putting API keys in Code modules or post content, where they leak via export/REST.
- Importing third-party Divi layouts or child themes without reviewing embedded code.
- Editing the parent theme, so a security update overwrites your patch.

## Production Tips

- Subscribe to Divi/WordPress security advisories and patch high-severity CVEs the same day.
- Run a WAF/firewall plugin or edge WAF; log and alert on admin logins and failed logins.
- Keep off-site backups so a compromise is recoverable, not catastrophic — see
  [maintenance](23-maintenance.md).

## AI Review Checklist

- Does every state-changing handler verify a nonce **and** `current_user_can` before writing?
- Is all dynamic output escaped with the correct `esc_*` / `wp_kses` function?
- Are there any `wp_ajax_nopriv_*` handlers doing privileged work?
- Are Code-module / `unfiltered_html` privileges limited to trusted roles?
- Are Divi, WordPress core, and plugins on patched versions?
- Are secrets kept out of post content, Code modules, and the repo?
- Is all custom PHP in a child theme, not the parent?

## Related

- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/16-wordpress-hooks.md`
- `knowledge/divi/17-rest-api.md`
- `knowledge/divi/23-maintenance.md`
- `knowledge/divi/99-ai-review-checklist.md`
