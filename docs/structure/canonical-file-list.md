# Canonical File List

Companion to [`frozen-structure-v1.md`](frozen-structure-v1.md), which defines the layout.
This document names every file that layout produces, topic by topic.

**How to use it.** Before adding, renaming, or removing a document under `knowledge/`, find
its topic below. The filename and its numeric prefix come from this list — the prefix is the
document's `order`, and `order` must be unique within a topic.

**Scope.** Parts 2–29 were written first and cover 28 topics; parts 30–50 were added later
and cover the remaining 21, including the ten topics that use a custom structure. Numbering
starts at Part 2 and is left as it is so existing references keep working — there is no
Part 1 in this file.

**Beyond 30.** The standard layout runs `01`–`30`. A topic may extend past it when the
subject genuinely needs another document; `aws/31-high-availability.md` is the only case
today. Reusing an `order` that is already taken is not an option — see
`scripts/check-knowledge.py`, which fails the build on a duplicate.

**Keeping it true.** `python3 scripts/check-knowledge.py knowledge` verifies that every
standard topic has `README`, `00`, `98`, `99`, `100` and no gap in `01`–`30`, and that each
document's frontmatter `order` matches its filename prefix.

---

# Part 2 — TypeScript

Directory:

knowledge/typescript/

---

README.md

00-overview.md

01-language-fundamentals.md
02-type-system.md
03-type-inference.md
04-functions.md
05-objects.md
06-interfaces.md
07-type-aliases.md
08-generics.md
09-utility-types.md
10-enums-and-literals.md
11-unions-and-intersections.md
12-type-guards.md
13-advanced-types.md
14-modules.md
15-decorators.md
16-configuration.md
17-error-handling.md
18-asynchronous-programming.md
19-collections.md
20-immutability.md
21-functional-programming.md
22-design-patterns.md
23-clean-code.md
24-testing.md
25-performance.md
26-security.md
27-library-design.md
28-best-practices.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 3 — JavaScript

Directory:

knowledge/javascript/

---

README.md

00-overview.md

01-language-fundamentals.md
02-execution-context.md
03-scope-and-closures.md
04-functions.md
05-objects-and-prototypes.md
06-classes.md
07-modules.md
08-asynchronous-javascript.md
09-promises.md
10-event-loop.md
11-browser-api.md
12-dom.md
13-fetch-api.md
14-error-handling.md
15-memory-management.md
16-this-keyword.md
17-es6-features.md
18-iterators-and-generators.md
19-symbols.md
20-proxies-and-reflect.md
21-functional-programming.md
22-design-patterns.md
23-clean-code.md
24-testing.md
25-performance.md
26-security.md
27-browser-performance.md
28-best-practices.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 4 — HTML

Directory:

knowledge/html/

---

README.md

00-overview.md

01-document-structure.md
02-semantic-html.md
03-text-elements.md
04-links.md
05-images.md
06-lists.md
07-tables.md
08-forms.md
09-media.md
10-metadata.md
11-accessibility.md
12-seo.md
13-structured-data.md
14-custom-data-attributes.md
15-iframes.md
16-svg.md
17-canvas.md
18-performance.md
19-security.md
20-browser-rendering.md
21-best-practices.md
22-validation.md
23-progressive-enhancement.md
24-html-email.md
25-web-components.md
26-microdata.md
27-html-apis.md
28-common-patterns.md
29-debugging.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 5 — CSS

Directory:

knowledge/css/

---

README.md

00-overview.md

01-css-fundamentals.md
02-selectors.md
03-specificity.md
04-box-model.md
05-positioning.md
06-flexbox.md
07-grid.md
08-sizing.md
09-spacing.md
10-typography.md
11-colors.md
12-backgrounds.md
13-borders.md
14-transforms.md
15-transitions.md
16-animations.md
17-responsive-design.md
18-media-queries.md
19-container-queries.md
20-css-variables.md
21-architecture.md
22-performance.md
23-accessibility.md
24-print-styles.md
25-modern-css.md
26-browser-compatibility.md
27-debugging.md
28-best-practices.md
29-css-methodologies.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md


# Part 6 — React

Directory:

knowledge/react/

---

README.md

00-overview.md

01-react-philosophy.md
02-component-architecture.md
03-jsx.md
04-components.md
05-props.md
06-state.md
07-lifecycle.md
08-hooks.md
09-custom-hooks.md
10-context-api.md
11-rendering.md
12-performance.md
13-component-composition.md
14-patterns.md
15-forms.md
16-data-fetching.md
17-routing.md
18-state-management.md
19-error-handling.md
20-accessibility.md
21-testing.md
22-folder-structure.md
23-code-style.md
24-design-patterns.md
25-security.md
26-best-practices.md
27-debugging.md
28-production.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 7 — Next.js

Directory:

knowledge/nextjs/

---

README.md

00-overview.md

01-architecture.md
02-project-structure.md
03-app-router.md
04-routing.md
05-layouts.md
06-server-components.md
07-client-components.md
08-rendering-strategies.md
09-data-fetching.md
10-caching.md
11-server-actions.md
12-api-routes.md
13-proxy.md
14-authentication.md
15-authorization.md
16-images.md
17-fonts.md
18-metadata.md
19-seo.md
20-performance.md
21-environment-variables.md
22-testing.md
23-observability.md
24-security.md
25-accessibility.md
26-deployment.md
27-folder-structure.md
28-best-practices.md
29-engineering-principles.md
30-migration-guide.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 8 — Node.js

Directory:

knowledge/nodejs/

---

README.md

00-overview.md

01-nodejs-runtime.md
02-event-loop.md
03-modules.md
04-package-management.md
05-file-system.md
06-streams.md
07-buffers.md
08-events.md
09-http.md
10-process.md
11-child-process.md
12-worker-threads.md
13-cluster.md
14-environment.md
15-configuration.md
16-error-handling.md
17-logging.md
18-security.md
19-performance.md
20-memory-management.md
21-testing.md
22-debugging.md
23-cli-development.md
24-background-jobs.md
25-microservices.md
26-deployment.md
27-monitoring.md
28-best-practices.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 9 — PHP

Directory:

knowledge/php/

---

README.md

00-overview.md

01-language-fundamentals.md
02-types.md
03-functions.md
04-oop.md
05-namespaces.md
06-autoloading.md
07-composer.md
08-error-handling.md
09-exceptions.md
10-files.md
11-http.md
12-database.md
13-security.md
14-performance.md
15-testing.md
16-cli.md
17-attributes.md
18-generators.md
19-enums.md
20-dependency-injection.md
21-design-patterns.md
22-clean-code.md
23-modern-php.md
24-psr-standards.md
25-debugging.md
26-best-practices.md
27-production.md
28-tooling.md
29-architecture.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 10 — Databases

Directory:

knowledge/databases/

---

README.md

00-overview.md

01-database-fundamentals.md
02-relational-vs-nosql.md
03-data-modeling.md
04-normalization.md
05-denormalization.md
06-schema-design.md
07-indexing.md
08-query-optimization.md
09-transactions.md
10-concurrency.md
11-locking.md
12-acid.md
13-eventual-consistency.md
14-replication.md
15-sharding.md
16-partitioning.md
17-migrations.md
18-backup-and-recovery.md
19-security.md
20-performance.md
21-monitoring.md
22-high-availability.md
23-data-integrity.md
24-soft-delete.md
25-multi-tenancy.md
26-auditing.md
27-testing.md
28-best-practices.md
29-architecture.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md




# Part 11 — SQL

Directory:

knowledge/sql/

---

README.md

00-overview.md

01-select.md
02-filtering.md
03-sorting.md
04-grouping.md
05-joins.md
06-subqueries.md
07-common-table-expressions.md
08-window-functions.md
09-aggregate-functions.md
10-functions.md
11-data-types.md
12-ddl.md
13-dml.md
14-transactions.md
15-indexes.md
16-query-planning.md
17-query-optimization.md
18-views.md
19-materialized-views.md
20-stored-procedures.md
21-triggers.md
22-security.md
23-performance.md
24-testing.md
25-debugging.md
26-best-practices.md
27-portability.md
28-architecture.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 12 — PostgreSQL

Directory:

knowledge/postgresql/

---

README.md

00-overview.md

01-installation.md
02-configuration.md
03-data-types.md
04-indexes.md
05-query-planner.md
06-transactions.md
07-locking.md
08-jsonb.md
09-arrays.md
10-full-text-search.md
11-partitioning.md
12-replication.md
13-high-availability.md
14-backups.md
15-extensions.md
16-performance.md
17-monitoring.md
18-security.md
19-roles-and-permissions.md
20-vacuum.md
21-analyze.md
22-migrations.md
23-testing.md
24-debugging.md
25-best-practices.md
26-production.md
27-tuning.md
28-architecture.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 13 — MySQL

Directory:

knowledge/mysql/

---

README.md

00-overview.md

01-installation.md
02-configuration.md
03-data-types.md
04-indexes.md
05-query-optimization.md
06-transactions.md
07-locking.md
08-storage-engines.md
09-replication.md
10-clustering.md
11-backups.md
12-security.md
13-users-and-roles.md
14-performance.md
15-monitoring.md
16-migrations.md
17-testing.md
18-debugging.md
19-best-practices.md
20-production.md
21-high-availability.md
22-partitioning.md
23-full-text-search.md
24-json.md
25-events.md
26-triggers.md
27-procedures.md
28-architecture.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 14 — Prisma

Directory:

knowledge/prisma/

---

README.md

00-overview.md

01-installation.md
02-schema.md
03-models.md
04-relations.md
05-migrations.md
06-client.md
07-crud.md
08-transactions.md
09-filtering.md
10-pagination.md
11-relations-loading.md
12-seeding.md
13-middleware.md
14-extensions.md
15-performance.md
16-indexes.md
17-raw-sql.md
18-error-handling.md
19-testing.md
20-debugging.md
21-security.md
22-multi-tenancy.md
23-soft-delete.md
24-best-practices.md
25-production.md
26-observability.md
27-tooling.md
28-patterns.md
29-architecture.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 15 — Redis

Directory:

knowledge/redis/

---

README.md

00-overview.md

01-installation.md
02-data-types.md
03-strings.md
04-lists.md
05-sets.md
06-sorted-sets.md
07-hashes.md
08-streams.md
09-pub-sub.md
10-transactions.md
11-lua-scripting.md
12-expiration.md
13-caching.md
14-rate-limiting.md
15-session-storage.md
16-message-queues.md
17-distributed-locks.md
18-replication.md
19-clustering.md
20-persistence.md
21-security.md
22-monitoring.md
23-performance.md
24-testing.md
25-debugging.md
26-best-practices.md
27-production.md
28-observability.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 16 — Docker

Directory:

knowledge/docker/

---

README.md

00-overview.md

01-installation.md
02-docker-architecture.md
03-images.md
04-containers.md
05-volumes.md
06-bind-mounts.md
07-networks.md
08-dockerfile.md
09-image-optimization.md
10-buildkit.md
11-multi-stage-builds.md
12-docker-compose.md
13-environment-variables.md
14-secrets.md
15-healthchecks.md
16-logging.md
17-resource-limits.md
18-security.md
19-registry.md
20-container-debugging.md
21-development-workflow.md
22-production.md
23-orchestration.md
24-monitoring.md
25-performance.md
26-best-practices.md
27-troubleshooting.md
28-tooling.md
29-ci-integration.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md


# Part 17 — Kubernetes

Directory:

knowledge/kubernetes/

---

README.md

00-overview.md

01-architecture.md
02-cluster.md
03-nodes.md
04-pods.md
05-deployments.md
06-replicasets.md
07-services.md
08-ingress.md
09-configmaps.md
10-secrets.md
11-volumes.md
12-persistent-volumes.md
13-statefulsets.md
14-daemonsets.md
15-jobs.md
16-cronjobs.md
17-network-policies.md
18-rbac.md
19-resource-management.md
20-autoscaling.md
21-observability.md
22-security.md
23-monitoring.md
24-debugging.md
25-upgrades.md
26-production.md
27-best-practices.md
28-disaster-recovery.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 18 — Nginx

Directory:

knowledge/nginx/

---

README.md

00-overview.md

01-installation.md
02-configuration.md
03-server-blocks.md
04-location-blocks.md
05-reverse-proxy.md
06-load-balancing.md
07-static-files.md
08-caching.md
09-compression.md
10-http2.md
11-http3.md
12-ssl-tls.md
13-security.md
14-rate-limiting.md
15-authentication.md
16-logging.md
17-monitoring.md
18-performance.md
19-proxying-applications.md
20-websockets.md
21-fastcgi.md
22-php-fpm.md
23-docker.md
24-debugging.md
25-production.md
26-best-practices.md
27-high-availability.md
28-tooling.md
29-troubleshooting.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 19 — Linux

Directory:

knowledge/linux/

---

README.md

00-overview.md

01-filesystem.md
02-shell.md
03-bash.md
04-users-and-groups.md
05-permissions.md
06-processes.md
07-services.md
08-systemd.md
09-networking.md
10-ssh.md
11-storage.md
12-package-management.md
13-environment.md
14-cron.md
15-logging.md
16-monitoring.md
17-security.md
18-performance.md
19-debugging.md
20-backups.md
21-firewall.md
22-containers.md
23-automation.md
24-scripting.md
25-production.md
26-best-practices.md
27-troubleshooting.md
28-tooling.md
29-system-administration.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 20 — DevOps

Directory:

knowledge/devops/

---

README.md

00-overview.md

01-devops-culture.md
02-development-lifecycle.md
03-git-workflow.md
04-branching-strategies.md
05-build-pipelines.md
06-release-management.md
07-deployment-strategies.md
08-infrastructure-as-code.md
09-configuration-management.md
10-containerization.md
11-orchestration.md
12-monitoring.md
13-observability.md
14-logging.md
15-alerting.md
16-security.md
17-secrets-management.md
18-disaster-recovery.md
19-high-availability.md
20-scalability.md
21-performance.md
22-testing.md
23-quality-gates.md
24-change-management.md
25-incident-management.md
26-postmortems.md
27-sre-principles.md
28-best-practices.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 21 — CI/CD

Directory:

knowledge/cicd/

---

README.md

00-overview.md

01-ci-cd-fundamentals.md
02-pipeline-design.md
03-build-stage.md
04-test-stage.md
05-quality-gates.md
06-security-scanning.md
07-artifacts.md
08-versioning.md
09-release-management.md
10-deployment.md
11-blue-green-deployment.md
12-canary-deployment.md
13-feature-flags.md
14-rollbacks.md
15-secrets.md
16-environments.md
17-github-actions.md
18-gitlab-ci.md
19-bitbucket-pipelines.md
20-jenkins.md
21-docker-integration.md
22-kubernetes-integration.md
23-monitoring.md
24-notifications.md
25-debugging.md
26-performance.md
27-best-practices.md
28-production.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md


# Part 22 — AWS

Directory:

knowledge/aws/

---

README.md

00-overview.md

01-global-infrastructure.md
02-iam.md
03-ec2.md
04-s3.md
05-rds.md
06-vpc.md
07-route53.md
08-cloudfront.md
09-acm.md
10-elastic-load-balancer.md
11-auto-scaling.md
12-lambda.md
13-api-gateway.md
14-cloudwatch.md
15-cloudtrail.md
16-secrets-manager.md
17-parameter-store.md
18-ecs.md
19-eks.md
20-ecr.md
21-sqs.md
22-sns.md
23-eventbridge.md
24-cost-optimization.md
25-security.md
26-monitoring.md
27-production.md
28-best-practices.md
29-well-architected-framework.md
30-engineering-principles.md
31-high-availability.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 23 — Git

Directory:

knowledge/git/

---

README.md

00-overview.md

01-version-control.md
02-installation.md
03-repository.md
04-commits.md
05-branches.md
06-merging.md
07-rebasing.md
08-cherry-pick.md
09-reset.md
10-revert.md
11-stash.md
12-tags.md
13-remote-repositories.md
14-fetch.md
15-pull.md
16-push.md
17-conflict-resolution.md
18-history.md
19-reflog.md
20-hooks.md
21-submodules.md
22-git-flow.md
23-trunk-based-development.md
24-monorepo.md
25-lfs.md
26-debugging.md
27-best-practices.md
28-security.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md


# Part 24 — GitHub

Directory:

knowledge/github/

---

README.md

00-overview.md

01-github-platform.md
02-repositories.md
03-issues.md
04-projects.md
05-discussions.md
06-pull-requests.md
07-code-review.md
08-actions.md
09-workflows.md
10-packages.md
11-releases.md
12-pages.md
13-security.md
14-codeql.md
15-dependabot.md
16-secret-scanning.md
17-branch-protection.md
18-rulesets.md
19-organizations.md
20-teams.md
21-permissions.md
22-api.md
23-cli.md
24-codespaces.md
25-copilot.md
26-automation.md
27-best-practices.md
28-enterprise.md
29-integrations.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 25 — REST API

Directory:

knowledge/rest-api/

---

README.md

00-overview.md

01-http.md
02-rest-principles.md
03-resource-design.md
04-endpoints.md
05-routing.md
06-request-response.md
07-status-codes.md
08-validation.md
09-error-handling.md
10-pagination.md
11-filtering.md
12-sorting.md
13-search.md
14-versioning.md
15-authentication.md
16-authorization.md
17-rate-limiting.md
18-idempotency.md
19-caching.md
20-file-upload.md
21-openapi.md
22-swagger.md
23-testing.md
24-security.md
25-performance.md
26-monitoring.md
27-best-practices.md
28-production.md
29-api-design-review.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 26 — GraphQL

Directory:

knowledge/graphql/

---

README.md

00-overview.md

01-graphql-fundamentals.md
02-schema.md
03-types.md
04-queries.md
05-mutations.md
06-subscriptions.md
07-resolvers.md
08-context.md
09-scalars.md
10-input-types.md
11-directives.md
12-fragments.md
13-pagination.md
14-filtering.md
15-n1-problem.md
16-dataloader.md
17-security.md
18-authentication.md
19-authorization.md
20-error-handling.md
21-caching.md
22-performance.md
23-federation.md
24-testing.md
25-monitoring.md
26-best-practices.md
27-production.md
28-tooling.md
29-schema-evolution.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 27 — Backend

Directory:

knowledge/backend/

---

README.md

00-overview.md

01-backend-architecture.md
02-layered-architecture.md
03-clean-architecture.md
04-hexagonal-architecture.md
05-ddd.md
06-api-design.md
07-business-logic.md
08-domain-modeling.md
09-validation.md
10-authentication.md
11-authorization.md
12-error-handling.md
13-caching.md
14-events.md
15-message-brokers.md
16-background-jobs.md
17-transactions.md
18-database-design.md
19-performance.md
20-scalability.md
21-security.md
22-observability.md
23-testing.md
24-documentation.md
25-code-organization.md
26-deployment.md
27-production.md
28-best-practices.md
29-architecture-review.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 28 — Frontend

Directory:

knowledge/frontend/

---

README.md

00-overview.md

01-frontend-architecture.md
02-component-driven-development.md
03-design-systems.md
04-state-management.md
05-routing.md
06-data-fetching.md
07-rendering.md
08-performance.md
09-accessibility.md
10-responsive-design.md
11-seo.md
12-forms.md
13-error-handling.md
14-security.md
15-styling.md
16-css-architecture.md
17-animations.md
18-assets.md
19-build-tools.md
20-bundling.md
21-code-splitting.md
22-testing.md
23-monitoring.md
24-documentation.md
25-folder-structure.md
26-production.md
27-best-practices.md
28-ui-patterns.md
29-design-review.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 29 — Architecture

Directory:

knowledge/architecture/

---

README.md

00-overview.md

01-software-architecture.md
02-system-design.md
03-clean-architecture.md
04-hexagonal-architecture.md
05-layered-architecture.md
06-domain-driven-design.md
07-cqrs.md
08-event-driven-architecture.md
09-microservices.md
10-modular-monolith.md
11-api-first.md
12-integration-patterns.md
13-scalability.md
14-performance.md
15-security.md
16-high-availability.md
17-fault-tolerance.md
18-observability.md
19-caching-strategies.md
20-message-brokers.md
21-distributed-systems.md
22-cloud-architecture.md
23-infrastructure.md
24-deployment.md
25-documentation.md
26-architecture-decision-records.md
27-architecture-review.md
28-best-practices.md
29-real-world-patterns.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 30 — AI

Directory:

knowledge/ai/

---

Custom structure — see `frozen-structure-v1.md`. This topic does not follow the standard
`01`–`30` plus `98`/`99`/`100` layout; the list below is the complete set.

README.md

00-ai-engineering-principles.md

01-context-gathering.md
02-task-planning.md
03-code-generation.md
04-code-modification.md
05-bug-fixing.md
06-self-verification.md



# Part 31 — Engineering

Directory:

knowledge/engineering/

---

Custom structure — see `frozen-structure-v1.md`. This topic does not follow the standard
`01`–`30` plus `98`/`99`/`100` layout; the list below is the complete set.

README.md

00-engineering-principles.md

01-decision-framework.md
02-code-review.md
03-debugging-methodology.md
04-task-execution.md
05-context-first-development.md

WRITING_STANDARD.md



# Part 32 — Workflows

Directory:

knowledge/workflows/

---

Custom structure — see `frozen-structure-v1.md`. This topic does not follow the standard
`01`–`30` plus `98`/`99`/`100` layout; the list below is the complete set.

README.md

01-implement-figma-design.md
02-fix-a-bug.md
03-create-new-feature.md
04-refactor-existing-code.md
05-review-pull-request.md
06-investigate-production-bug.md
07-add-api-endpoint.md
08-build-react-component.md
09-build-wordpress-feature.md
10-build-divi-module.md
11-build-gutenberg-block.md



# Part 33 — Figma

Directory:

knowledge/figma/

---

Custom structure — see `frozen-structure-v1.md`. This topic does not follow the standard
`01`–`30` plus `98`/`99`/`100` layout; the list below is the complete set.

README.md

01-figma-analysis.md
02-layout-analysis.md
03-design-token-extraction.md
04-auto-layout.md
05-responsive-analysis.md
06-component-detection.md
07-figma-to-html.md
08-figma-to-wordpress.md
09-figma-to-divi.md
10-design-qa.md
11-ai-design-review.md
12-ai-prompts.md
13-visual-regression.md
14-figma-inspection-checklist.md
15-screenshot-comparison.md
16-accessibility-from-figma.md
17-animation-analysis.md
18-image-assets.md
19-design-handoff.md
20-implementation-definition-of-done.md



# Part 34 — NestJS

Directory:

knowledge/nestjs/

---

README.md

00-overview.md

01-architecture.md
02-modules.md
03-dependency-injection.md
04-controllers.md
05-services.md
06-repositories.md
07-dto.md
08-validation.md
09-guards.md
10-interceptors.md
11-exception-filters.md
12-pipes.md
13-middleware.md
14-configuration.md
15-authentication.md
16-authorization.md
17-database.md
18-transactions.md
19-caching.md
20-queues.md
21-events.md
22-cqrs.md
23-distributed-systems.md
24-observability.md
25-testing.md
26-security.md
27-performance.md
28-deployment.md
29-maintenance.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 35 — WordPress

Directory:

knowledge/wordpress/

---

README.md

00-overview.md

01-wordpress-architecture.md
02-project-structure.md
03-best-practices.md
04-code-style.md
05-performance.md
06-security.md
07-testing.md
08-hooks.md
09-custom-post-types.md
10-taxonomies.md
11-metadata.md
12-queries.md
13-template-hierarchy.md
14-theme-development.md
15-plugin-development.md
16-block-editor.md
17-block-themes.md
18-rest-api.md
19-database.md
20-users-and-capabilities.md
21-media-and-uploads.md
22-cron-and-background-tasks.md
23-caching.md
24-internationalization.md
25-multisite.md
26-wp-cli.md
27-deployment.md
28-debugging.md
29-maintenance.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 36 — WooCommerce

Directory:

knowledge/woocommerce/

---

README.md

00-overview.md

01-architecture.md
02-installation.md
03-product-types.md
04-product-management.md
05-orders.md
06-customers.md
07-checkout.md
08-payments.md
09-shipping.md
10-taxes.md
11-coupons.md
12-hooks.md
13-rest-api.md
14-headless.md
15-performance.md
16-security.md
17-customization.md
18-emails.md
19-subscriptions.md
20-multisite.md
21-testing.md
22-deployment.md
23-monitoring.md
24-scaling.md
25-best-practices.md
26-debugging.md
27-production.md
28-real-world-patterns.md
29-ai-review.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 37 — Divi

Directory:

knowledge/divi/

---

README.md

00-overview.md

01-architecture.md
02-theme-builder.md
03-modules.md
04-custom-modules.md
05-layouts.md
06-global-elements.md
07-dynamic-content.md
08-templates.md
09-custom-css.md
10-performance.md
11-responsive-design.md
12-accessibility.md
13-seo.md
14-woocommerce.md
15-custom-fields.md
16-wordpress-hooks.md
17-rest-api.md
18-headless.md
19-security.md
20-debugging.md
21-testing.md
22-deployment.md
23-maintenance.md
24-best-practices.md
25-production.md
26-real-world-patterns.md
27-client-projects.md
28-ai-workflow.md
29-review.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 38 — Testing

Directory:

knowledge/testing/

---

README.md

00-overview.md

01-testing-fundamentals.md
02-unit-testing.md
03-integration-testing.md
04-e2e-testing.md
05-test-doubles.md
06-mocking.md
07-test-data.md
08-test-organization.md
09-assertions.md
10-fixtures.md
11-contract-testing.md
12-api-testing.md
13-ui-testing.md
14-visual-regression.md
15-performance-testing.md
16-load-testing.md
17-security-testing.md
18-accessibility-testing.md
19-test-coverage.md
20-test-maintenance.md
21-cicd.md
22-flaky-tests.md
23-debugging-tests.md
24-best-practices.md
25-production-testing.md
26-observability.md
27-quality-gates.md
28-testing-strategy.md
29-test-review.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 39 — Security

Directory:

knowledge/security/

---

README.md

00-overview.md

01-security-fundamentals.md
02-threat-modeling.md
03-authentication.md
04-authorization.md
05-password-security.md
06-session-management.md
07-jwt.md
08-oauth.md
09-input-validation.md
10-output-encoding.md
11-xss.md
12-csrf.md
13-sql-injection.md
14-command-injection.md
15-file-upload-security.md
16-secrets-management.md
17-encryption.md
18-https.md
19-cors.md
20-csp.md
21-rate-limiting.md
22-security-headers.md
23-dependency-security.md
24-supply-chain-security.md
25-monitoring.md
26-incident-response.md
27-best-practices.md
28-owasp-top10.md
29-security-review.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 40 — Performance

Directory:

knowledge/performance/

---

README.md

00-overview.md

01-performance-fundamentals.md
02-metrics.md
03-cpu.md
04-memory.md
05-network.md
06-rendering.md
07-loading.md
08-caching.md
09-lazy-loading.md
10-code-splitting.md
11-images.md
12-fonts.md
13-database-performance.md
14-api-performance.md
15-query-optimization.md
16-profiling.md
17-monitoring.md
18-web-vitals.md
19-benchmarking.md
20-capacity-planning.md
21-scalability.md
22-load-testing.md
23-performance-budget.md
24-optimization-workflow.md
25-production-monitoring.md
26-debugging.md
27-best-practices.md
28-real-world-patterns.md
29-performance-review.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 41 — Accessibility

Directory:

knowledge/accessibility/

---

README.md

00-overview.md

01-accessibility-fundamentals.md
02-pour-principles.md
03-semantic-html.md
04-keyboard-navigation.md
05-focus-management.md
06-screen-readers.md
07-aria.md
08-forms.md
09-images.md
10-color-and-contrast.md
11-typography.md
12-layout.md
13-responsive-accessibility.md
14-motion-and-animation.md
15-media.md
16-dialogs.md
17-tables.md
18-error-messages.md
19-live-regions.md
20-testing-tools.md
21-axe.md
22-lighthouse.md
23-wcag.md
24-accessibility-testing.md
25-remediation.md
26-legal-requirements.md
27-best-practices.md
28-real-world-patterns.md
29-documentation.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 42 — SEO

Directory:

knowledge/seo/

---

README.md

00-overview.md

01-seo-fundamentals.md
02-crawling.md
03-indexing.md
04-rendering.md
05-metadata.md
06-canonicalization.md
07-sitemaps.md
08-robots-txt.md
09-structured-data.md
10-open-graph.md
11-twitter-cards.md
12-performance.md
13-core-web-vitals.md
14-international-seo.md
15-local-seo.md
16-images.md
17-links.md
18-pagination.md
19-javascript-seo.md
20-headless-seo.md
21-analytics.md
22-search-console.md
23-audits.md
24-monitoring.md
25-content-quality.md
26-best-practices.md
27-production-checks.md
28-real-world-patterns.md
29-seo-review.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 43 — Tailwind CSS

Directory:

knowledge/tailwind/

---

README.md

00-overview.md

01-installation.md
02-core-concepts.md
03-utility-first.md
04-layout.md
05-flexbox.md
06-grid.md
07-spacing.md
08-sizing.md
09-typography.md
10-colors.md
11-responsive-design.md
12-dark-mode.md
13-state-variants.md
14-pseudo-classes.md
15-customization.md
16-theme.md
17-components.md
18-plugins.md
19-performance.md
20-optimization.md
21-design-system.md
22-accessibility.md
23-nextjs.md
24-react.md
25-debugging.md
26-best-practices.md
27-production.md
28-patterns.md
29-tooling.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 44 — Tools

Directory:

knowledge/tools/

---

README.md

00-overview.md

01-package-managers.md
02-version-management.md
03-typescript-compiler.md
04-eslint.md
05-prettier.md
06-stylelint.md
07-php-code-standards.md
08-static-analysis.md
09-vite.md
10-webpack.md
11-esbuild-and-swc.md
12-babel.md
13-test-runners.md
14-playwright.md
15-storybook.md
16-git-hooks.md
17-commit-conventions.md
18-monorepo-tools.md
19-task-runners.md
20-local-environments.md
21-debuggers.md
22-profilers.md
23-api-clients.md
24-database-tools.md
25-editor-setup.md
26-ai-coding-tools.md
27-dependency-management.md
28-release-tools.md
29-observability-tools.md
30-engineering-principles.md

98-production-checklist.md
99-ai-review-checklist.md
100-common-antipatterns.md



# Part 45 — Examples

Directory:

knowledge/examples/

---

Custom structure — see `frozen-structure-v1.md`. This topic does not follow the standard
`01`–`30` plus `98`/`99`/`100` layout; the list below is the complete set.

README.md

01-rest-endpoint.md
02-react-component.md
03-wordpress-feature.md



# Part 46 — Templates

Directory:

knowledge/templates/

---

Custom structure — see `frozen-structure-v1.md`. This topic does not follow the standard
`01`–`30` plus `98`/`99`/`100` layout; the list below is the complete set.

README.md

01-pull-request.md
02-architecture-decision-record.md
03-incident-report.md



# Part 47 — Checklists

Directory:

knowledge/checklists/

---

Custom structure — see `frozen-structure-v1.md`. This topic does not follow the standard
`01`–`30` plus `98`/`99`/`100` layout; the list below is the complete set.

README.md

01-pre-launch.md
02-pull-request-author.md
03-new-project-setup.md



# Part 48 — Playbooks

Directory:

knowledge/playbooks/

---

Custom structure — see `frozen-structure-v1.md`. This topic does not follow the standard
`01`–`30` plus `98`/`99`/`100` layout; the list below is the complete set.

README.md

01-site-down.md
02-failed-deployment.md
03-security-incident.md



# Part 49 — Prompts

Directory:

knowledge/prompts/

---

Custom structure — see `frozen-structure-v1.md`. This topic does not follow the standard
`01`–`30` plus `98`/`99`/`100` layout; the list below is the complete set.

README.md

01-code-review.md
02-bug-investigation.md
03-refactoring.md



# Part 50 — Snippets

Directory:

knowledge/snippets/

---

Custom structure — see `frozen-structure-v1.md`. This topic does not follow the standard
`01`–`30` plus `98`/`99`/`100` layout; the list below is the complete set.

README.md

01-typescript-utilities.md
02-php-wordpress.md
03-shell-scripts.md
