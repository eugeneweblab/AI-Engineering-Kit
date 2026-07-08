---
id: tailwind/25-debugging
topic: tailwind
slug: debugging
title: "Debugging"
type: doc
order: 25
status: ready
tags: [tailwind, debugging]
related: [tailwind/29-tooling, tailwind/19-performance, tailwind/24-react, tailwind/11-responsive-design, tailwind/100-common-antipatterns]
when_to_use: "Read when a Tailwind class is not applying, an override is losing, or styles differ between dev and production."
---
# Debugging

## Purpose

This document defines a systematic way to diagnose why Tailwind styles are not
behaving as expected: a class that never applies, an override that loses to a base
utility, a style that works in dev but disappears in a production build, or a
variant that silently does nothing. It is written so an agent can find the root
cause quickly instead of adding `!important` and moving on.

Most Tailwind "bugs" are not CSS bugs. They are content-detection, specificity, or
class-order problems. Knowing which of the three you are looking at is most of the
fix.

## Why It Matters

Tailwind failures are quiet. The build succeeds, the type checker passes, and the
app renders — just with the wrong padding or a missing color. Because nothing
errors, developers reach for `!important` or inline styles, which masks the real
cause (a purged class, a merge conflict) and leaves a landmine for the next
change. Diagnosing the actual mechanism — did the class ship? did it lose on
order? — turns a recurring mystery into a one-line fix and keeps the codebase from
accumulating specificity hacks.

## Core Principles

- **First ask: did the class ship?** Search the generated CSS for the exact class.
  If it is absent, this is a content-detection problem, not a CSS problem.
- **Second ask: is it in the DOM but overridden?** Inspect the element; if the rule
  is struck through in devtools, it is a specificity or source-order conflict.
- **Reproduce in a production build.** Many bugs exist only after the scanner runs;
  a dev server or CDN build hides them. `NODE_ENV=production` before you conclude.
- **Change one thing at a time.** Add a single known-good utility (`bg-red-500`) to
  confirm Tailwind is wired up before debugging the real class.
- **Read the generated CSS, not just the class attribute.** The source of truth is
  the compiled stylesheet, not what you wrote in JSX.

## Best Practices

- Grep the built CSS for the class name: if missing, the source string is dynamic
  (interpolated) or the file is outside the scanned paths — make the class static.
- Use browser devtools to see which rule wins; a line-through means another rule of
  equal-or-higher specificity later in source order overrode it — use
  `tailwind-merge` to collapse the conflict.
- Verify responsive and state prefixes are on the same element as the base
  (`md:flex` needs the element to be the one that becomes flex, not its parent).
- Confirm dark mode: check whether `dark` is toggled by `class` or `media`, and
  that the `dark` class actually lands on `<html>` when using the class strategy.
- Check arbitrary values for syntax: `w-[32px]` needs no space and units;
  `bg-[#1da1f2]` needs the hash — a malformed bracket value emits nothing.
- Install the Tailwind IntelliSense extension; it flags unknown classes and shows
  the resolved CSS on hover, catching typos before runtime.
- When a plugin utility is missing, confirm the plugin is registered and the build
  was restarted — config changes require a dev-server restart.

## Examples

**Good Example** — make the class static so the scanner emits it

```tsx
// The scanner sees complete strings, so both classes are guaranteed to ship.
const tone = danger ? "text-red-600" : "text-green-600";
return <span className={tone}>{status}</span>;

// Verify from the terminal that the class is actually in the output:
//   grep -R "text-red-600" dist/assets/*.css
```

**Bad Example** — interpolated class the scanner cannot see

```tsx
// `text-${hue}-600` is never a complete token in source, so Tailwind emits
// nothing for it. It works with the dev CDN (which JITs on the fly) and then
// silently breaks in the production build — the hardest kind of bug to catch.
const hue = danger ? "red" : "green";
return <span className={`text-${hue}-600`}>{status}</span>;
// Adding !important would not help: the rule does not exist in the CSS at all.
```

## Common Mistakes

- Debugging a dev/CDN build and concluding it works, when the class is purged only
  in the production build.
- Reaching for `!important` on an override that is actually a `tailwind-merge`
  conflict — the fix is to merge, not to escalate specificity.
- Assuming a responsive prefix failed when the breakpoint simply is not active at
  the current viewport width.
- Editing `tailwind.config` / `@theme` and not restarting the dev server, so the
  new token never compiles.
- Putting `dark:` variants everywhere but never toggling the `dark` class on the
  root element, so none of them activate.
- Blaming Tailwind for a class typo that IntelliSense would have flagged instantly.

## Production Tips

- Add a smoke check in CI that greps the built CSS for a handful of critical
  dynamic classes (chart colors, status badges) so a purged class fails the build,
  not the customer.
- When a style regresses only in prod, diff the generated CSS between the last good
  build and the current one — the missing rule points straight at the cause.
- Keep a scratch route with `bg-red-500`/`p-8` to instantly confirm the pipeline is
  alive when a whole stylesheet appears to be missing.

## AI Review Checklist

- Was the class confirmed present in the generated production CSS, not just the dev
  build?
- If overridden, was the cause identified as source-order/specificity and fixed
  with `tailwind-merge` rather than `!important`?
- Are any failing classes actually dynamic interpolations that need to be made
  static or safelisted?
- After a config/`@theme` change, was the dev server restarted before concluding it
  did not work?
- For dark-mode issues, is the `dark` class (or media strategy) actually active on
  the root?
- Were arbitrary values checked for correct bracket syntax and units?

## Related

- `knowledge/tailwind/29-tooling.md`
- `knowledge/tailwind/19-performance.md`
- `knowledge/tailwind/24-react.md`
- `knowledge/tailwind/11-responsive-design.md`
- `knowledge/tailwind/100-common-antipatterns.md`
