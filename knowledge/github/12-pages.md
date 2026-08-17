---
id: github/12-pages
topic: github
slug: pages
title: "Pages"
type: doc
order: 12
status: ready
tags: [github, pages, runs-on, base, localhost, id-token]
related: [github/09-workflows, github/08-actions, github/02-repositories, github/13-security, github/17-branch-protection]
when_to_use: "Read before publishing a site, docs, or SPA to GitHub Pages."
---
# Pages

## Purpose

This document defines how to publish a static site — documentation, a landing page, a
project SPA — to **GitHub Pages** correctly and safely. It covers the two build sources
(branch vs. GitHub Actions), custom domains and HTTPS, and the security boundary of a
publicly served artifact. It is written so an agent can stand up a Pages site without
leaking secrets, serving stale content, or breaking on a subpath.

GitHub Pages serves static files only. There is no server-side runtime — no PHP, no Node
process, no database. Anything dynamic must be a client-side call to an external API.

## Why It Matters

A Pages site is public by default and served on a GitHub-owned domain, so anything you
commit to the publish source is world-readable forever (git history included). The most
common Pages incident is not downtime — it is publishing a `.env`, an API key baked into
a bundle, or an internal draft. Pages also has sharp, silent failure modes: a site built
for a root domain breaks when served from `/repo-name/`, and a misconfigured custom
domain can be taken over by an attacker. Getting the build source and base path right the
first time avoids a class of "works locally, 404s in production" bugs.

## Core Principles

- **Static only, secrets never.** The published output is public. Never commit or bundle
  API keys, tokens, or `.env` files into what Pages serves.
- **Prefer the GitHub Actions source over the legacy branch source.** Actions gives you a
  reproducible build, dependency control, and a real deploy log; the branch source hides
  the build and invites committing generated artifacts.
- **The base path is not `/`.** A project site lives at `/<repo>/`. Configure your
  framework's base URL to match, or every absolute asset link 404s.
- **Enforce HTTPS.** Always enable "Enforce HTTPS"; serve nothing over plain HTTP.
- **A custom domain is a security boundary.** Verify the domain and remove the DNS record
  before you delete the site, or you invite a subdomain takeover.

## Best Practices

- Deploy with the official actions: `actions/upload-pages-artifact` +
  `actions/deploy-pages`, gated to the `github-pages` environment. This is the supported,
  auditable path and works with branch protection.
- Set the framework base path explicitly: Vite `base: '/repo/'`, Next.js `basePath`,
  Astro `base`, Jekyll `baseurl`. Test the built site from a subpath, not just `localhost`.
- Add a `.nojekyll` file if you publish a folder that starts with `_` (e.g. `_next`,
  `_astro`) — Jekyll silently drops underscore-prefixed paths otherwise.
- For an SPA that uses client-side routing, add a `404.html` fallback; Pages has no
  rewrite rules, so deep links otherwise 404.
- Give the `deploy-pages` job `permissions: { pages: write, id-token: write }` and nothing
  more. Do not grant `contents: write` to a deploy job.
- Use organization-level Pages visibility controls (Enterprise/Team) to keep internal
  docs from being served publicly.

## Examples

**Good Example** — build in Actions, deploy to the Pages environment, least privilege

```yaml
# .github/workflows/pages.yml — reproducible build, scoped permissions
permissions:
  contents: read          # only read the repo; deploy job gets its own scope
jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - run: npm ci && npm run build   # base path set in vite.config to '/repo/'
      - uses: actions/upload-pages-artifact@v3  # illustrative ref; pin the reviewed SHA in production
        with: { path: ./dist }
  deploy:
    needs: build
    permissions:
      pages: write        # narrowly scoped: only what deploy needs
      id-token: write      # OIDC proof that this run produced the artifact
    environment: github-pages
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/deploy-pages@v4  # illustrative ref; pin the reviewed SHA in production
```

**Bad Example** — committing built output and secrets to a branch source

```bash
# Anti-pattern: hand-built output pushed to gh-pages, config baked into the bundle
npm run build
echo "VITE_API_KEY=sk_live_9f3..." >> .env   # secret ends up in the bundle...
npm run build                                # ...and is now served publicly, forever
git add -f dist .env && git commit -m "deploy"
git push origin gh-pages   # no build log, base path untested, key leaked in git history
```

## Common Mistakes

- Bundling a "public" API key that is actually privileged — Pages serves it to everyone.
- Leaving the framework base path at `/`, so a project site 404s all its assets.
- Forgetting `.nojekyll`, so `_next`/`_astro` folders vanish from the deployed site.
- Deleting a repo/site without removing the custom-domain DNS record → subdomain takeover.
- Not enabling "Enforce HTTPS", leaving the site reachable over plain HTTP.
- Granting the deploy job `contents: write` when it only needs `pages: write`.

## Production Tips

- Pin the site to a specific environment (`github-pages`) and add environment protection
  rules so only approved workflows can deploy.
- Cache-bust with content-hashed filenames; Pages sets aggressive CDN caching and a
  stable filename can serve stale JS for hours.
- For docs, treat the deploy like any release: build in CI, block merge on build failure,
  and keep the source in the repo — never hand-edit the deployed artifact.

## AI Review Checklist

- Does the published output contain any secret, `.env`, or privileged key?
- Is the build done in GitHub Actions with an auditable log, not hand-pushed to a branch?
- Is the framework base path set to `/<repo>/` for a project site and tested from a subpath?
- Is "Enforce HTTPS" enabled and the custom domain verified?
- Does the deploy job use least-privilege `pages: write` / `id-token: write` only?
- Is there a `.nojekyll` file when serving underscore-prefixed folders?

## Related

- `knowledge/github/09-workflows.md`
- `knowledge/github/08-actions.md`
- `knowledge/github/02-repositories.md`
- `knowledge/github/13-security.md`
- `knowledge/github/17-branch-protection.md`
