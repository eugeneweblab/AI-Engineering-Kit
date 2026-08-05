---
id: wordpress/22-cron-and-background-tasks
topic: wordpress
slug: cron-and-background-tasks
title: "Cron and Background Tasks"
type: doc
order: 22
status: ready
tags: [wordpress, cron-and-background-tasks]
related: [wordpress/15-plugin-development, wordpress/26-wp-cli, wordpress/27-deployment, wordpress/28-debugging, wordpress/05-performance, wordpress/29-maintenance]
when_to_use: "Read before scheduling recurring work — using WP-Cron, replacing it with a system cron, or processing a large job in batches."
---
# Cron and Background Tasks

## Purpose

This document defines how scheduled work runs in WordPress: what WP-Cron actually is, why it
is unreliable by default, how to schedule and cancel events correctly, and how to process
large jobs without hitting a timeout.

The recurring theme: WP-Cron is not cron, and treating it as if it were produces jobs that run
late, run twice, or never run at all.

---

## Core Principle

**WP-Cron is triggered by traffic.** On each page load, WordPress checks whether a scheduled
event is due and, if so, fires an internal request to run it. Consequences:

- A site with no visitors runs no scheduled tasks.
- A site behind full-page caching may serve most requests without booting PHP, so the check
  never happens.
- Two simultaneous visitors can trigger the same event twice.
- The "run at 03:00" you scheduled means "at the first request after 03:00".

For anything that must actually happen on time, replace the trigger with the operating
system's:

```php
// wp-config.php — stop traffic from triggering cron.
define( 'DISABLE_WP_CRON', true );
```

```cron
# Real cron, every five minutes. WP-Cron still manages the schedule;
# only the trigger changes.
*/5 * * * * cd /var/www/site && wp cron event run --due-now --quiet
```

This is the recommended production configuration for any site where scheduled work matters.

---

## Scheduling

The hook must be registered on **every request** — otherwise the callback does not exist when
cron fires. Scheduling happens once; hooking happens always.

```php
// Always: register the callback.
add_action( 'acme_daily_cleanup', 'acme_run_daily_cleanup' );

// Once: create the schedule, on activation.
register_activation_hook( ACME_EVENTS_FILE, function () {
	if ( ! wp_next_scheduled( 'acme_daily_cleanup' ) ) {
		wp_schedule_event( time() + HOUR_IN_SECONDS, 'daily', 'acme_daily_cleanup' );
	}
} );

// And clean up on deactivation, or the event outlives the plugin.
register_deactivation_hook( ACME_EVENTS_FILE, function () {
	wp_clear_scheduled_hook( 'acme_daily_cleanup' );
} );
```

A one-off task:

```php
wp_schedule_single_event( time() + 5 * MINUTE_IN_SECONDS, 'acme_send_reminder', array( $signup_id ) );
add_action( 'acme_send_reminder', 'acme_send_reminder_email' );   // receives $signup_id
```

**Arguments are part of the event's identity.** To unschedule, pass exactly the same array:

```php
$timestamp = wp_next_scheduled( 'acme_send_reminder', array( $signup_id ) );
if ( $timestamp ) {
	wp_unschedule_event( $timestamp, 'acme_send_reminder', array( $signup_id ) );
}
```

Passing different arguments — or none — silently fails to cancel anything, which is how sites
accumulate thousands of orphaned cron entries.

---

## Custom Intervals

Built-in schedules are `hourly`, `twicedaily`, `daily`, and `weekly`. Anything else must be
registered before it can be used:

```php
add_filter( 'cron_schedules', function ( array $schedules ) {
	$schedules['acme_fifteen_minutes'] = array(
		'interval' => 15 * MINUTE_IN_SECONDS,
		'display'  => __( 'Every 15 minutes', 'acme-events' ),
	);
	return $schedules;
} );
```

Register the filter before scheduling the event; an unknown interval makes
`wp_schedule_event()` return `false`.

---

## Writing a Safe Callback

Cron callbacks run without a user, without a nonce, and possibly twice. Three properties make
them safe:

```php
function acme_run_daily_cleanup(): void {
	// 1. Guard against concurrent runs — two visitors can trigger the same event.
	if ( ! acme_acquire_lock( 'acme_daily_cleanup', 10 * MINUTE_IN_SECONDS ) ) {
		return;
	}

	try {
		// 2. Bound the work. Never "process everything" in one execution.
		$expired = get_posts( array(
			'post_type'      => 'acme_signup',
			'post_status'    => 'pending',
			'posts_per_page' => 100,
			'fields'         => 'ids',
			'date_query'     => array( array( 'before' => '30 days ago' ) ),
		) );

		foreach ( $expired as $id ) {
			wp_delete_post( $id, true );
		}

		// 3. If more remain, schedule the next batch rather than looping.
		if ( count( $expired ) === 100 ) {
			wp_schedule_single_event( time() + MINUTE_IN_SECONDS, 'acme_daily_cleanup' );
		}
	} finally {
		acme_release_lock( 'acme_daily_cleanup' );
	}
}

function acme_acquire_lock( string $key, int $ttl ): bool {
	// add_option() with autoload 'no' is atomic: it fails if the row already exists.
	return add_option( $key . '_lock', time(), '', 'no' );
}

function acme_release_lock( string $key ): void {
	delete_option( $key . '_lock' );
}
```

A cron callback should also assume **no user context**: `current_user_can()` returns false for
everything, so capability checks belong at the point where the job was created, not inside the
job.

---

## Long-Running Jobs

PHP has a `max_execution_time`, and cron requests are subject to it. A job that processes
50,000 rows in one call will be killed partway through, leaving inconsistent state.

Two viable approaches:

**Batch with self-rescheduling** — the pattern above: process a bounded chunk, schedule the
next.

**Action Scheduler** — the queue library that ships with WooCommerce, designed for exactly
this. It stores actions in its own tables, processes them in batches with concurrency control,
and provides an admin UI for failures:

```php
if ( function_exists( 'as_schedule_single_action' ) ) {
	as_schedule_single_action( time() + 60, 'acme_process_export', array( 'export_id' => $id ), 'acme' );
}
add_action( 'acme_process_export', 'acme_process_export_batch' );
```

On a WooCommerce site it is already installed, and it is the better choice for anything
resembling a queue.

For genuinely heavy work — video processing, large imports, third-party sync — the right
answer is usually outside WordPress entirely: a dedicated worker consuming a queue, with
WordPress only enqueuing and displaying status.

---

## Inspecting and Debugging

```bash
wp cron event list                       # everything scheduled, with next-run times
wp cron event run acme_daily_cleanup     # run one event now
wp cron event run --due-now              # run everything currently due
wp cron event delete acme_daily_cleanup  # remove a stuck event
wp cron test                             # verify WP-Cron can spawn its own request
```

Common findings and what they mean:

- **Hundreds of duplicate events** — something schedules on `init` without checking
  `wp_next_scheduled()`.
- **An event with a timestamp in the past that never runs** — no traffic, cron disabled with
  no system cron, or a fatal error in the callback killing the run.
- **An event that no longer has a callback** — a removed plugin whose events were never
  cleared.

Add logging rather than guessing:

```php
add_action( 'acme_daily_cleanup', function () {
	error_log( '[acme] cleanup started ' . gmdate( 'c' ) );
}, 1 );
```

---

## Examples

**Good Example** — a real scheduler, an idempotent callback, a lock

```php
// wp-config.php — stop traffic from triggering cron; a system scheduler owns it.
define( 'DISABLE_WP_CRON', true );
```

```bash
# crontab — deterministic timing, independent of visitors and full-page caching.
*/5 * * * * cd /var/www/app && wp cron event run --due-now --quiet
```

```php
add_action( 'myplugin_send_reminders', 'myplugin_send_reminders' );

function myplugin_send_reminders() {
	// Two overlapping runs would email everyone twice. wp_cache_add() is atomic
	// across processes ONLY with a persistent object cache (Redis, Memcached).
	// WordPress's default cache is per-request, so without one this guard does
	// nothing — see below.
	if ( ! wp_cache_add( 'myplugin_reminders_lock', 1, 'myplugin', 5 * MINUTE_IN_SECONDS ) ) {
		return;
	}

	$pending = get_posts(
		array(
			'post_type'      => 'myplugin_signup',
			'posts_per_page' => 100,          // one bounded batch per run
			'meta_key'       => '_reminder_sent',
			'meta_compare'   => 'NOT EXISTS',
			'fields'         => 'ids',
		)
	);

	foreach ( $pending as $signup_id ) {
		myplugin_send_reminder( $signup_id );
		// Mark immediately: a crash mid-batch must not re-send what already went out.
		update_post_meta( $signup_id, '_reminder_sent', time() );
	}

	wp_cache_delete( 'myplugin_reminders_lock', 'myplugin' );
}
```

Without a persistent object cache, use a database-level lock instead — `GET_LOCK()` is atomic
across connections and releases itself when the connection closes:

```php
$got_lock = (int) $GLOBALS['wpdb']->get_var(
	$GLOBALS['wpdb']->prepare( 'SELECT GET_LOCK(%s, 0)', 'myplugin_reminders' )
);

if ( 1 !== $got_lock ) {
	return;               // another run holds it
}

// ... work ...

$GLOBALS['wpdb']->query( $GLOBALS['wpdb']->prepare( 'SELECT RELEASE_LOCK(%s)', 'myplugin_reminders' ) );
```

The idempotency marker (`_reminder_sent`) is what actually prevents duplicate emails; the lock
only stops two runs from doing the same work at the same time. Keep both.

**Bad Example** — scheduled on every request, unbounded, and not idempotent

```php
// Runs on init, so a new event is scheduled on every single page load.
add_action( 'init', function () {
	wp_schedule_event( time(), 'hourly', 'myplugin_send_reminders' );
} );

add_action( 'myplugin_send_reminders', function () {
	// Every signup, forever — the job gets slower every day and eventually times out
	// halfway through, having sent an arbitrary prefix of the emails.
	$all = get_posts( array( 'post_type' => 'myplugin_signup', 'posts_per_page' => -1 ) );

	foreach ( $all as $signup ) {
		myplugin_send_reminder( $signup->ID );   // no record of what was sent
	}
} );
```

`wp_schedule_event()` belongs in an activation hook, or behind a
`! wp_next_scheduled( $hook )` guard. Without one, the cron table fills with duplicates and
the job runs many times per hour.

---

## Common Mistakes

- **Scheduling on `init` without `wp_next_scheduled()`**, creating a duplicate on every
  request.
- **Registering the `add_action()` only on activation**, so the callback does not exist when
  cron fires.
- **Unscheduling with different arguments** than were used to schedule.
- **Not clearing events on deactivation**, leaving orphans behind.
- **Assuming punctuality** on a low-traffic or fully cached site.
- **Unbounded work in one execution**, killed by `max_execution_time`.
- **No concurrency guard**, so a job runs twice on a busy site.
- **Capability checks inside a cron callback**, which always fail — there is no user.
- **`DISABLE_WP_CRON` set with no system cron configured**, so nothing runs at all.
- **Using WP-Cron as a queue** where Action Scheduler or a real worker belongs.

---

## Verification Checklist

- Is the callback registered unconditionally on every request?
- Is the event scheduled once, guarded by `wp_next_scheduled()`?
- Are the same arguments used for scheduling and unscheduling?
- Are events cleared on deactivation?
- Is the work bounded per run, with the next batch scheduled if more remains?
- Is there a lock preventing overlapping executions?
- Does the callback avoid depending on a current user?
- In production, is `DISABLE_WP_CRON` set **and** a system cron configured?

---

## Summary

WP-Cron is a schedule, not a scheduler: traffic triggers it, so production sites should
disable that trigger and drive `wp cron event run --due-now` from the system cron. Register
callbacks always, schedule once, cancel with identical arguments, bound every run, and reach
for Action Scheduler when the work is really a queue.

## Related


- `knowledge/wordpress/15-plugin-development.md`
- `knowledge/wordpress/26-wp-cli.md`
- `knowledge/wordpress/27-deployment.md`
- `knowledge/wordpress/28-debugging.md`
- `knowledge/wordpress/05-performance.md`
- `knowledge/wordpress/29-maintenance.md`
