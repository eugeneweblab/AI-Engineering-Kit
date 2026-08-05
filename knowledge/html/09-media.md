---
id: html/09-media
topic: html
slug: media
title: "HTML Media"
type: doc
order: 9
status: ready
tags: [html, media]
related: [html/05-images, html/11-accessibility, html/18-performance, html/16-svg]
when_to_use: "Read before embedding audio, video, or captions on a page."
---
# HTML Media

## Purpose

This document defines how to embed **audio and video** with the native `<audio>` and
`<video>` elements, provide multiple source formats, and make time-based media
accessible with captions and descriptions. It covers `<picture>` only insofar as it
relates to responsive media; still images are covered in the images guide. The goal is
media that plays across browsers, respects bandwidth, and is usable without sound or sight.

## Why It Matters

Media is heavy and time-based, which creates two failure modes ordinary content does not
have. First, bandwidth: an unoptimised autoplaying video can burn a user's mobile data
and jank the page. Second, access: a video with no captions is invisible to deaf users
and unusable in sound-off environments (offices, transit), which is where most video is
watched. Autoplaying sound is also hostile and blocked by browsers. Native elements solve
codec negotiation, controls, and keyboard access for free — a custom player must
re-earn all of it.

## Core Principles

- **Use native `<video>`/`<audio>`, not plugins or bare files.** They give keyboard
  controls, captions, and picture-in-picture without custom code.
- **Offer multiple `<source>` formats.** Provide modern codecs (WebM/AV1, MP4/H.264) so
  the browser picks the first it supports; fall back gracefully.
- **Captions are mandatory for video with speech.** Add a `<track kind="captions">`
  (WebVTT). Without them, deaf and sound-off users get nothing.
- **Never autoplay with sound.** Browsers block it; it startles users and wastes data.
  Autoplay is only acceptable when `muted` and usually decorative.
- **Give the browser sizing and loading hints.** Set `width`/`height` (or aspect ratio),
  `poster`, and `preload` to avoid layout shift and needless downloads.

## Best Practices

- Always include `controls` unless you build a fully accessible custom control set; users
  must be able to pause, seek, and adjust volume with the keyboard.
- List `<source>` elements from most to least preferred and include a `type` with codec
  string so the browser can skip unsupported formats without downloading them.
- Set `preload="metadata"` (or `none`) for below-the-fold or optional media to avoid
  downloading the whole file before the user asks.
- Provide a `poster` image for `<video>` so a meaningful frame shows before playback and
  the box does not appear empty.
- Add `<track kind="captions">` for dialogue and `kind="descriptions"` for key visuals;
  set `default` on the caption track for the primary language.
- Reserve space with `width`/`height` or `aspect-ratio` CSS to prevent cumulative layout
  shift when media loads.
- For responsive art-directed images use `<picture>` with `<source media>`; keep an
  `<img>` with `alt` as the required fallback.

## Examples

**Good Example** — multiple formats, poster, captions, no autoplay

```html
<video
  controls                 <!-- keyboard-operable native controls -->
  width="1280" height="720" <!-- reserves space, prevents layout shift -->
  poster="/media/talk-poster.jpg"
  preload="metadata">       <!-- fetch only metadata until the user plays -->
  <!-- Most-preferred codec first; browser picks the first it supports -->
  <source src="/media/talk.webm" type="video/webm; codecs=av01" />
  <source src="/media/talk.mp4"  type="video/mp4; codecs=avc1" />
  <!-- Captions make speech usable without sound and for deaf users -->
  <track kind="captions" src="/media/talk.en.vtt" srclang="en" label="English" default />
  <p>Your browser can't play this video. <a href="/media/talk.mp4">Download it</a>.</p>
</video>
```

**Bad Example** — autoplaying sound, single format, no captions

```html
<!-- Autoplay with sound is blocked by browsers and hostile to users;
     one MP4 source means no fallback; no <track> means deaf and sound-off
     users get nothing; no dimensions cause layout shift on load. -->
<video src="/media/talk.mp4" autoplay></video>
```

## Common Mistakes

- Autoplaying with audio (browsers block it and users hate it).
- Shipping a single format with no fallback `<source>` or download link.
- Omitting captions/`<track>` for spoken video, excluding deaf and sound-off users.
- No `poster` and no dimensions, causing an empty box and layout shift.
- `preload="auto"` on optional media, wasting bandwidth before any interaction.
- Rebuilding a custom player that loses keyboard control, captions, and PiP.
- Using `<img>` where art direction is needed instead of `<picture>`.

## Production Tips

- Serve adaptive streaming (HLS/DASH) for long-form video rather than one large file.
- Compress and cap resolution to the display size; a hero video rarely needs 4K.
- Respect `prefers-reduced-motion` — pause or avoid autoplaying background video for
  users who opted out of motion.
- Host captions as versioned `.vtt` files and review them; auto-generated captions need
  human correction before shipping.

## AI Review Checklist

- Are `<audio>`/`<video>` native elements with `controls` (or an accessible custom UI)?
- Are multiple `<source>` formats provided with `type`/codec hints?
- Does spoken video include a `<track kind="captions">`?
- Is autoplay avoided, or at least `muted` when used?
- Are `width`/`height` (or aspect ratio) and a `poster` set to prevent layout shift?
- Is `preload` tuned so optional media does not download eagerly?
- Is `prefers-reduced-motion` honoured for autoplaying motion?

## Related

- `knowledge/html/05-images.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/16-svg.md`
- `knowledge/html/18-performance.md`
