---
id: wordpress/27-deployment
topic: wordpress
slug: deployment
title: "WordPress Deployment"
type: doc
order: 27
status: ready
tags: [wordpress, deployment]
related: [wordpress/26-wp-cli, wordpress/29-maintenance, wordpress/02-project-structure, wordpress/06-security, wordpress/23-caching]
when_to_use: "Read before setting up or changing a WordPress deployment — choosing what belongs in version control, managing configuration per environment, or moving content between environments."
---
# WordPress Deployment

## Purpose

This document defines how to deploy WordPress reliably: what belongs in version control, how
configuration differs per environment, why the database moves in one direction only, and what
a deploy must do beyond copying files.

WordPress predates modern deployment practice, and its defaults — editing files in the admin,
installing plugins through the UI, storing configuration in the database — actively conflict
with it. A disciplined setup starts by turning those defaults off.

---

## Core Principle

**Code flows up; content flows down.**

```
local → staging → production      code, migrations, configuration
production → staging → local      database, uploads
```

Pushing a database from staging to production overwrites orders, comments, and posts created
since the last sync. That direction is a data-loss event, not a deploy step, and the pipeline
should make it impossible rather than discouraged.

---

## What Goes in Version Control

```gitignore
# .gitignore
wp-config.php
wp-content/uploads/
wp-content/cache/
wp-content/upgrade/
wp-content/debug.log
*.sql
.env
node_modules/
vendor/            # if built in CI; commit it if deploying without a build step
```

Two viable models:

**Whole-install repository** — WordPress core, themes, and plugins all committed. Simple,
works with any host, and makes every update an explicit, reviewable commit.

**Composer-managed** (Bedrock or equivalent) — core and plugins declared as dependencies:

```json
{
  "require": {
    "roots/wordpress": "^6.7",
    "wpackagist-plugin/wordpress-seo": "^23.0",
    "wpackagist-theme/twentytwentyfive": "^1.0"
  },
  "extra": {
    "wordpress-install-dir": "web/wp",
    "installer-paths": {
      "web/app/plugins/{$name}/": [ "type:wordpress-plugin" ],
      "web/app/themes/{$name}/": [ "type:wordpress-theme" ]
    }
  }
}
```

The Composer model gives real dependency resolution, a lock file, and reproducible builds. Its
cost: premium plugins need private repositories, and the directory layout differs from what
most WordPress documentation assumes.

Either way, **disable admin-side modification** so the deployed state stays authoritative:

```php
// wp-config.php
define( 'DISALLOW_FILE_EDIT', true );   // no plugin/theme editor
define( 'DISALLOW_FILE_MODS', true );   // no installs or updates from the admin
```

---

## Configuration Per Environment

Secrets belong in the environment, never in the repository:

```php
// wp-config.php — reads the environment, contains no secrets itself.
define( 'DB_NAME',     getenv( 'DB_NAME' ) );
define( 'DB_USER',     getenv( 'DB_USER' ) );
define( 'DB_PASSWORD', getenv( 'DB_PASSWORD' ) );
define( 'DB_HOST',     getenv( 'DB_HOST' ) ?: 'localhost' );

// WordPress 5.5+: 'local' | 'development' | 'staging' | 'production'
define( 'WP_ENVIRONMENT_TYPE', getenv( 'WP_ENV' ) ?: 'production' );

if ( 'production' === wp_get_environment_type() ) {
	define( 'WP_DEBUG', false );
	define( 'WP_DEBUG_DISPLAY', false );
	define( 'DISALLOW_FILE_MODS', true );
	define( 'FORCE_SSL_ADMIN', true );
} else {
	define( 'WP_DEBUG', true );
	define( 'WP_DEBUG_LOG', true );
	define( 'WP_DEBUG_DISPLAY', false );   // log, do not print — broken JSON breaks REST
	define( 'SCRIPT_DEBUG', true );
}
```

`wp_get_environment_type()` is readable from plugin code, which makes it the right way to gate
behavior:

```php
if ( 'production' !== wp_get_environment_type() ) {
	add_filter( 'wp_mail', 'acme_redirect_mail_to_catcher' );   // never email real customers
}
```

URLs are the other per-environment value. Define them rather than storing them in the
database, so a database copy cannot point staging at production:

```php
define( 'WP_HOME',    getenv( 'WP_HOME' ) );
define( 'WP_SITEURL', WP_HOME . '/wp' );
```

---

## The Deploy Itself

An atomic deploy switches a symlink so no request ever sees a half-copied tree:

```
/var/www/acme/
├── releases/
│   ├── 2026-07-14-093000/
│   └── 2026-07-14-141500/     ← new release
├── shared/
│   ├── uploads/               ← symlinked into each release
│   └── .env
└── current -> releases/2026-07-14-141500
```

```bash
#!/usr/bin/env bash
set -euo pipefail

RELEASE="/var/www/acme/releases/$(date +%Y-%m-%d-%H%M%S)"
SHARED="/var/www/acme/shared"

git clone --depth 1 --branch main git@github.com:acme/site.git "$RELEASE"
composer install --no-dev --optimize-autoloader --working-dir="$RELEASE"
npm ci --prefix "$RELEASE" && npm run build --prefix "$RELEASE"

ln -sfn "$SHARED/uploads" "$RELEASE/web/app/uploads"
ln -sfn "$SHARED/.env"    "$RELEASE/.env"

# Verify the release boots BEFORE it serves traffic.
wp core is-installed --path="$RELEASE/web/wp"

ln -sfn "$RELEASE" /var/www/acme/current

# Post-switch: schema, caches, and the compiled-code cache.
wp core update-db --path=/var/www/acme/current/web/wp
wp cache flush   --path=/var/www/acme/current/web/wp
sudo systemctl reload php8.3-fpm      # clears OPcache; stale bytecode outlives the symlink

# Keep the last five releases.
ls -1dt /var/www/acme/releases/* | tail -n +6 | xargs -r rm -rf
```

The OPcache step is the one most often missed: without it, PHP keeps executing the previous
release's compiled bytecode from the old path, and the deploy appears to have done nothing.

---

## Moving the Database Down

```bash
# On production
wp db export prod.sql --exclude_tables=wp_users,wp_usermeta   # optional: keep local accounts

# On staging/local
wp db import prod.sql
wp search-replace 'https://acme.example' 'https://staging.acme.example' --precise --skip-columns=guid
wp cache flush

# Make the environment safe to work in.
wp option update blog_public 0                    # discourage indexing
wp plugin deactivate woocommerce-payments some-live-integration
wp user update admin --user_pass="$(openssl rand -base64 24)"
```

Never change URLs with SQL — serialized data breaks. See [WP-CLI](26-wp-cli.md).

For the rare cases where content must move *up* (a page built on staging), move that content
specifically — export the posts, or rebuild them — rather than the whole database.

---

## Pre-Deploy Checks in CI

```yaml
# .github/workflows/ci.yml
name: ci
on: pull_request

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with: { php-version: '8.3', tools: composer, coverage: none }
      - run: composer install --prefer-dist --no-progress
      - run: vendor/bin/phpcs --standard=WordPress --extensions=php .
      - run: vendor/bin/phpunit
      - run: |
          # Fail if a translatable string was added without regenerating the template.
          wp i18n make-pot . languages/acme.pot --domain=acme
          git diff --exit-code languages/acme.pot
```

PHPCS with the WordPress standard catches the majority of review comments before review — see
[Code Style](04-code-style.md).

---

## Rollback

A rollback plan is part of the deploy, not a response to failure:

```bash
# Code: repoint the symlink at the previous release and clear bytecode.
ln -sfn /var/www/acme/releases/2026-07-14-093000 /var/www/acme/current
sudo systemctl reload php8.3-fpm
```

Code rolls back cleanly. **Database migrations usually do not** — which is why schema changes
should be additive: add a column, deploy code that writes both old and new, migrate, then
remove the old in a later release. A destructive migration removes the option to roll back at
all.

---

## Examples

**Good Example** — atomic release, shared state, one-way database flow

```bash
#!/usr/bin/env bash
set -euo pipefail

RELEASE="/var/www/app/releases/$(git rev-parse --short HEAD)"
SHARED="/var/www/app/shared"

git archive HEAD | (mkdir -p "$RELEASE" && tar -x -C "$RELEASE")
composer install --no-dev --optimize-autoloader --working-dir="$RELEASE"

# Uploads and configuration live outside the release and survive every deploy.
ln -sfn "$SHARED/uploads"    "$RELEASE/wp-content/uploads"
ln -sfn "$SHARED/.env"       "$RELEASE/.env"

# Fail before switching, not after.
wp --path="$RELEASE" core verify-checksums
wp --path="$RELEASE" db check

# The switch itself is one atomic symlink change.
ln -sfn "$RELEASE" /var/www/app/current
wp --path=/var/www/app/current cache flush
```

```bash
# Database moves DOWN only. Pulling production into staging is routine;
# the reverse is a data-loss event and no script should offer it.
wp @production db export - | wp @staging db import -
wp @staging search-replace 'https://example.com' 'https://staging.example.com' --all-tables-with-prefix
```

**Bad Example** — editing production in place

```bash
# In-place git pull: the site serves a half-updated tree while files land, and
# composer install runs against live traffic.
cd /var/www/app && git pull origin main && composer install

# Uploads inside the repository: either they are committed (a 4 GB repo) or the
# deploy deletes them.
rsync -a --delete ./wp-content/ user@prod:/var/www/app/wp-content/

# Pushing the local database up destroys every order and comment created since
# the developer last pulled.
wp @local db export - | wp @production db import -
```

There is no rollback here: the previous release no longer exists on disk, and the database it
matched has been overwritten.

---

## Common Mistakes

- **Pushing a database from staging to production**, destroying live content.
- **`wp-config.php` or `.env` committed** to the repository.
- **Secrets in the repository** rather than the environment.
- **Editing files on production** through the plugin editor or SFTP.
- **Site URL stored only in the database**, so a copied database points at the wrong host.
- **No OPcache reset after deploy**, so the old code keeps running.
- **`uploads/` inside the release directory**, wiped or duplicated on every deploy.
- **Updating plugins on production first**, with no staging test.
- **`WP_DEBUG_DISPLAY` left on in production**, printing errors into REST and AJAX responses.
- **Destructive migrations** that make rollback impossible.

---

## Verification Checklist

- Is all code in version control, with uploads, config, and secrets excluded?
- Is configuration environment-driven, with `WP_ENVIRONMENT_TYPE` set?
- Are `DISALLOW_FILE_EDIT` and `DISALLOW_FILE_MODS` enabled in production?
- Are `WP_HOME` / `WP_SITEURL` defined rather than read from the database?
- Is the deploy atomic, with uploads shared and OPcache cleared afterwards?
- Does the database move only downward, with `search-replace` and staging safety steps?
- Does CI run PHPCS and tests on every pull request?
- Are migrations additive, and is a rollback path documented?

---

## Summary

Put code in version control and configuration in the environment; deploy atomically and clear
the bytecode cache; let the database flow only from production down; and design migrations so
that rolling back the code is always possible.

## Related


- `knowledge/wordpress/26-wp-cli.md`
- `knowledge/wordpress/29-maintenance.md`
- `knowledge/wordpress/02-project-structure.md`
- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/23-caching.md`
