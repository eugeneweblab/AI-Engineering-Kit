---
id: tools/20-local-environments
topic: tools
slug: local-environments
title: "Local Environments"
type: doc
order: 20
status: ready
tags: [tools, local-environments]
related: [tools/02-version-management, tools/19-task-runners, tools/24-database-tools, tools/21-debuggers, tools/30-engineering-principles, docker/00-overview]
when_to_use: "Read before setting up a local development environment — Docker Compose, WordPress-specific tooling, or making a project runnable with one command."
---
# Local Environments

## Purpose

This document defines how to make a project runnable locally in one step: containerized
services, environment configuration, seed data, and the WordPress-specific tooling that
handles a stack most generic setups get wrong.

## Why It Matters

The time between `git clone` and a running application is the clearest measure of a project's
tooling health. When that takes a day and a colleague's help, every new contributor pays it,
and the setup instructions are wrong within a month because nobody re-runs them.

The second cost is silent: an environment that differs from production produces bugs that
appear only after deploy — a different database version, a missing extension, a case-sensitive
filesystem.

## Core Principles

- **One command to start.** `make up` or `docker compose up` should produce a working
  application with data.
- **Match production's shape.** Same major versions of runtime, database, and cache. Exotic
  differences are where deploy-time surprises come from.
- **Configuration by environment, never by edited files.** A setup requiring someone to modify
  a tracked file will produce accidental commits.
- **Seed data is part of the environment.** An empty database is not a working application, and
  every developer inventing their own test data guarantees inconsistent bug reports.

## Best Practices

```yaml
# compose.yaml — services pinned to production's majors
services:
  app:
    build:
      context: .
      target: development
    ports: ['3000:3000']
    volumes:
      - .:/app
      - /app/node_modules          # keep the container's install, not the host's
    environment:
      DATABASE_URL: postgres://app:app@db:5432/app
      REDIS_URL: redis://cache:6379
    depends_on:
      db: { condition: service_healthy }
      cache: { condition: service_started }

  db:
    image: postgres:16.4-alpine    # same major as production
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    ports: ['5432:5432']           # exposed so GUI clients can connect
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U app']
      interval: 5s
      retries: 10

  cache:
    image: redis:7.4-alpine
    ports: ['6379:6379']

  mail:
    image: axllent/mailpit          # catches outgoing mail; nothing reaches real inboxes
    ports: ['1025:1025', '8025:8025']

volumes:
  db-data:
```

The healthcheck plus `depends_on: condition: service_healthy` removes the most common startup
race: the app connecting before Postgres finishes initializing.

Mail catching deserves emphasis — without it, a local password-reset test emails a real
customer address from seed data.

```bash
# Makefile — the documented entry point
up:
	docker compose up -d
	docker compose exec app pnpm db:migrate
	docker compose exec app pnpm db:seed
	@echo "App:  http://localhost:3000"
	@echo "Mail: http://localhost:8025"

down:
	docker compose down

reset:  ## Destroy data and rebuild from scratch
	docker compose down -v
	$(MAKE) up
```

## WordPress Environments

WordPress has purpose-built tooling that handles PHP, MySQL, WP-CLI, and the install step
together:

```json
// .wp-env.json — @wordpress/env, the standard for plugin and block development
{
  "core": "WordPress/WordPress#6.7",
  "phpVersion": "8.3",
  "plugins": [ ".", "https://downloads.wordpress.org/plugin/query-monitor.zip" ],
  "themes": [ "./themes/acme" ],
  "config": {
    "WP_DEBUG": true,
    "WP_DEBUG_LOG": true,
    "WP_DEBUG_DISPLAY": false,
    "SCRIPT_DEBUG": true
  },
  "mappings": {
    "wp-content/mu-plugins": "./mu-plugins"
  }
}
```

```bash
npx wp-env start                    # WordPress at localhost:8888, tests at :8889
npx wp-env run cli wp plugin list
npx wp-env clean all                # reset to a fresh install
```

`wp-env` provisions a second instance for integration tests, which is why it is preferable to
a hand-written Compose file for plugin work. DDEV and Lando are the fuller alternatives for
whole-site projects, adding HTTPS, mail catching, and Xdebug configuration out of the box.

## Examples

**Good Example** — environment configuration that fails loudly

```bash
# .env.example — committed, with every variable the app needs
DATABASE_URL=postgres://app:app@localhost:5432/app
REDIS_URL=redis://localhost:6379
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx        # test keys only; never a live key in an example file
```

```ts
// src/env.ts — validated once at startup
import { z } from 'zod';

const schema = z.object({
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
});

export const env = schema.parse(process.env);   // fails at boot with the missing name
```

**Bad Example** — a setup that cannot be reproduced

```
README:
1. Install PostgreSQL 14 (or 15, either works)
2. Create a database called `app_dev`
3. Ask Sergey for the .env file
4. Run the SQL in docs/schema.sql
5. If migrations fail, run them again
```

Every step is a divergence point, and "ask a colleague" means the environment cannot be
created without one.

## Common Mistakes

- No containerization on a project with several services.
- Container images tagged `latest`, so environments drift apart between rebuilds.
- Database versions differing from production by a major.
- Secrets shared over chat instead of a `.env.example` plus a secrets manager.
- No seed data, so every developer builds different test cases.
- No mail catcher, risking real emails from local runs.
- Host `node_modules` mounted into a Linux container, breaking native modules.
- No healthchecks, producing intermittent startup failures blamed on the application.
- `.env` committed to the repository.

## Production Tips

- Keep the development image a separate build target from production, so hot reload and dev
  dependencies never ship.
- Mount source code but exclude installed dependencies (`- /app/node_modules`) — bind-mounting
  them is the standard cause of "works outside Docker only".
- Provide `make reset` that destroys volumes and rebuilds; a fast way back to a known state is
  what keeps people from debugging their own environment.
- Seed with realistic volume, not three rows. Performance problems that only appear at 50,000
  rows should appear locally too.
- On Apple Silicon, pin platform explicitly (`platform: linux/amd64`) for images without ARM
  builds rather than letting emulation surprise people with slow startups.

## AI Review Checklist

- Can the project be started with one documented command?
- Are service versions pinned and aligned with production majors?
- Is there a committed `.env.example` covering every required variable?
- Are environment variables validated at startup?
- Does the environment include seed data and a mail catcher?
- Are healthchecks defined so services start in the right order?
- Is there a reset path that returns to a known-good state?
- For WordPress, is `wp-env` or an equivalent used rather than a bespoke stack?

## Related


- `knowledge/tools/02-version-management.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/24-database-tools.md`
- `knowledge/tools/21-debuggers.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/docker/00-overview.md`
