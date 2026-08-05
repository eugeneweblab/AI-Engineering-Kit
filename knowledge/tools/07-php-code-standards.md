---
id: tools/07-php-code-standards
topic: tools
slug: php-code-standards
title: "PHP Code Standards"
type: doc
order: 7
status: ready
tags: [tools, php-code-standards]
related: [tools/08-static-analysis, tools/16-git-hooks, tools/01-package-managers, tools/19-task-runners, tools/30-engineering-principles, php/24-psr-standards, wordpress/04-code-style]
when_to_use: "Read before setting up PHP linting — configuring PHP_CodeSniffer or PHP-CS-Fixer, applying the WordPress standard, or automating fixes."
---
# PHP Code Standards

## Purpose

This document defines how to enforce coding standards in PHP projects: PHP_CodeSniffer for
checking, PHP-CS-Fixer for formatting, and the WordPress standard for WordPress work — plus
which violations are worth failing a build over.

## Why It Matters

In PHP the linter carries more weight than in most languages, because PHP's own runtime
tolerates so much. Undefined variables, loose comparisons, and unescaped output all execute
without complaint. The WordPress Coding Standards ruleset in particular encodes real security
rules — escaping, sanitization, prepared statements — so a PHPCS failure there is frequently a
vulnerability rather than a style preference.

## Core Principles

- **Checking and fixing are separate tools.** PHPCS reports; `phpcbf` and PHP-CS-Fixer
  rewrite. Only one of them should own formatting.
- **Security sniffs are not style.** In WordPress projects, `WordPress.Security.*` failures
  are defects and must not be excluded to make the build pass.
- **Configuration lives in the repository** as `phpcs.xml.dist`, so every developer and CI run
  uses the same ruleset.
- **Zero violations, or a baseline.** A backlog of "known" errors makes the report unreadable.

## Best Practices

```xml
<?xml version="1.0"?>
<ruleset name="Acme">
	<description>Coding standards for the Acme plugin.</description>

	<file>src</file>
	<file>acme-events.php</file>
	<exclude-pattern>*/vendor/*</exclude-pattern>
	<exclude-pattern>*/node_modules/*</exclude-pattern>

	<!-- p: progress, s: show sniff codes so violations can be looked up -->
	<arg value="ps"/>
	<arg name="extensions" value="php"/>
	<arg name="parallel" value="8"/>

	<config name="testVersion" value="8.1-"/>
	<config name="minimum_wp_version" value="6.4"/>

	<rule ref="WordPress">
		<!-- Formatting handled by PHP-CS-Fixer; keep one owner. -->
		<exclude name="Generic.WhiteSpace.DisallowSpaceIndent"/>
		<exclude name="WordPress.Files.FileName"/>
	</rule>

	<!-- Naming rules need the project's prefixes to be useful. -->
	<rule ref="WordPress.NamingConventions.PrefixAllGlobals">
		<properties>
			<property name="prefixes" type="array">
				<element value="acme"/>
				<element value="Acme\Events"/>
			</property>
		</properties>
	</rule>

	<rule ref="WordPress.WP.I18n">
		<properties>
			<property name="text_domain" type="array">
				<element value="acme-events"/>
			</property>
		</properties>
	</rule>
</ruleset>
```

Install the standards as dev dependencies rather than globally:

```json
{
  "require-dev": {
    "squizlabs/php_codesniffer": "^3.10",
    "wp-coding-standards/wpcs": "^3.1",
    "phpcompatibility/phpcompatibility-wp": "^2.1",
    "dealerdirect/phpcodesniffer-composer-installer": "^1.0"
  },
  "scripts": {
    "lint": "phpcs",
    "lint:fix": "phpcbf",
    "check": ["@lint", "@analyse", "@test"]
  },
  "config": { "allow-plugins": { "dealerdirect/phpcodesniffer-composer-installer": true } }
}
```

The `dealerdirect` plugin registers installed standards automatically — without it,
`phpcs` reports that the `WordPress` standard does not exist.

## Examples

**Good Example** — what the security sniffs catch

```php
// PHPCS: WordPress.Security.EscapeOutput.OutputNotEscaped
echo $user_input;

// PHPCS: WordPress.DB.PreparedSQL.NotPrepared
$wpdb->get_results( "SELECT * FROM {$table} WHERE id = {$id}" );

// PHPCS: WordPress.Security.NonceVerification.Missing
if ( isset( $_POST['acme_action'] ) ) {
	acme_do_thing();
}
```

Each of these is a real vulnerability, reported before review. That is the argument for
running WPCS on WordPress projects even when the team dislikes the brace style.

**Bad Example** — silencing the sniff instead of fixing the defect

```php
// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
echo $user_input;
```

A `phpcs:ignore` on a security sniff needs a justification explaining why the value is already
safe, and ideally proof — for example, that it came from `wp_kses_post()` one line earlier.
Without that, this comment converts a caught bug into a shipped one.

**Good Example** — a justified, narrow suppression

```php
// The value was escaped in acme_render_card(); escaping again would double-encode entities.
echo $prepared_html; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
```

## Common Mistakes

- Excluding `WordPress.Security.*` to get a green build.
- Blanket `phpcs:disable` at the top of a file.
- PHPCS and PHP-CS-Fixer both enforcing formatting, so each undoes the other.
- Standards installed globally, so CI and developers use different versions.
- No `phpcs.xml.dist` in the repository, leaving the ruleset to the command line.
- `phpcbf` run across the codebase in the same commit as a feature change.
- Running the linter over `vendor/`.
- Prefix and text-domain properties left unset, disabling the naming and i18n rules that would
  otherwise be the most useful ones.

## Production Tips

- Add `--cache` and `--parallel` for local runs; PHPCS is slow on large codebases without them.
- On pre-commit, check staged files only:
  `git diff --cached --name-only --diff-filter=ACM -- '*.php' | xargs -r vendor/bin/phpcs`.
- When adopting standards on an existing codebase, run `phpcbf` in an isolated commit, add it
  to `.git-blame-ignore-revs`, then fix the remaining manual violations in batches by sniff.
- Add `PHPCompatibilityWP` and set `testVersion` so the linter also reports syntax that will
  break on the PHP version production runs.
- Pair PHPCS with PHPStan — they catch different classes of problem, and neither substitutes
  for the other. See [Static Analysis](08-static-analysis.md).

## AI Review Checklist

- Is there a committed `phpcs.xml.dist`, with standards installed as dev dependencies?
- Are security sniffs enabled, with no blanket exclusions?
- Is every `phpcs:ignore` narrow and accompanied by a justification?
- Do prefix and text-domain properties match the project?
- Is `testVersion` set to the production PHP version?
- Is formatting owned by exactly one tool?
- Does CI run the linter with a non-zero exit on violations?

## Related


- `knowledge/tools/08-static-analysis.md`
- `knowledge/tools/16-git-hooks.md`
- `knowledge/tools/01-package-managers.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/php/24-psr-standards.md`
- `knowledge/wordpress/04-code-style.md`
