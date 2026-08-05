---
id: accessibility/15-media
topic: accessibility
slug: media
title: "Accessibility Media"
type: doc
order: 15
status: ready
tags: [accessibility, media, readers, muted, aria-label]
related: [accessibility/14-motion-and-animation, accessibility/09-images, accessibility/04-keyboard-navigation, accessibility/07-aria, accessibility/23-wcag]
when_to_use: "Read before embedding audio, video, players, or auto-playing media."
---
# Accessibility Media

## Purpose

This document defines how to make audio and video usable by people who cannot hear it,
cannot see it, or cannot use a mouse. Every piece of information carried in a media file
must have a text or alternative-modality path so that no user is locked out of it.

It maps to WCAG **1.2.1–1.2.5** (captions, audio description, transcripts), **1.4.2
Audio Control**, and **2.1.1 Keyboard**, and is written so an agent embedding a player
provides the required alternatives rather than assuming the video "speaks for itself".

## Why It Matters

Media is dense with information and hostile to alternatives by default. A deaf user gets
nothing from an uncaptioned tutorial. A blind user gets nothing from a video whose key
action happens silently on screen. A user in an open office, on a train, or with a broken
speaker is in the same position situationally. Auto-playing audio is worse than useless:
it talks over a screen reader, making the entire page unnavigable until the user finds
the source and silences it.

These are not edge cases — captions alone benefit the large population of people who
watch with sound off. The alternatives you add for the disabled user improve the product
for everyone.

## Core Principles

- **Captions for all pre-recorded audio content** (WCAG 1.2.2). Captions carry speech
  *and* meaningful non-speech sound ("[door slams]"). They are synchronized, not a bare
  transcript.
- **Audio description for visual information** (WCAG 1.2.5). If the video shows something
  the soundtrack does not describe, a described track or an extended description must
  cover it.
- **A transcript for audio-only and as a fallback for video.** A full text transcript is
  the most robust, most searchable alternative and helps everyone.
- **Never auto-play sound.** If media plays automatically for more than 3 seconds, the
  user must be able to pause or stop it, or control volume independently (WCAG 1.4.2).
  Prefer no auto-play at all.
- **The player must be fully keyboard-operable.** Every control — play, pause, seek,
  volume, captions, fullscreen — reachable and operable without a mouse.

## Best Practices

- Use the native `<video>`/`<audio>` element with `<track kind="captions">`; native
  controls are keyboard- and screen-reader-accessible out of the box. If you build a
  custom player, replicate that: labelled buttons, focusable slider, visible focus.
- Provide captions as WebVTT (`.vtt`) `kind="captions"` (includes non-speech sound), not
  `kind="subtitles"` (translation of dialogue only), when the goal is accessibility.
- Publish a text transcript adjacent to the media, linked and in the DOM (not only inside
  the player), so it is searchable and screen-reader-navigable.
- Do not set `autoplay`. If a background video is decorative, mark it `muted`, give it no
  meaningful audio, and provide a pause control; treat its motion under
  [reduced motion](14-motion-and-animation.md).
- Label the media region: give the player an accessible name (e.g., `aria-label` on the
  container or a visible caption) describing what it contains.
- Ensure caption and control contrast meets the same thresholds as the rest of the UI.

## Examples

**Good Example** — captions track, no autoplay, keyboard-native controls

```html
<figure>
  <video controls preload="metadata" width="640">
    <source src="/onboarding.mp4" type="video/mp4">
    <!-- kind="captions" includes non-speech sounds; screen readers and
         deaf users get the full audio content. Native controls are already
         keyboard- and AT-accessible, so we do not reinvent them. -->
    <track kind="captions" src="/onboarding.en.vtt" srclang="en" label="English" default>
    <track kind="descriptions" src="/onboarding.desc.vtt" srclang="en" label="Description">
  </video>
  <figcaption>
    Onboarding walkthrough. <a href="/onboarding-transcript">Read the transcript</a>.
  </figcaption>
</figure>
```

**Bad Example** — autoplaying sound, no captions, no transcript

```html
<!-- autoplay with sound talks over screen readers (WCAG 1.4.2 failure);
     no <track> means deaf users get nothing; no transcript means the
     content is unreachable by text. -->
<video src="/promo.mp4" autoplay loop></video>
```

## Common Mistakes

- Auto-playing media with sound, drowning out the screen reader.
- No captions, or "subtitles" that translate dialogue but omit non-speech sound.
- Auto-generated captions shipped without human correction (names, jargon, and timing
  are frequently wrong).
- No audio description for information shown only on screen.
- No text transcript, so the content cannot be searched, skimmed, or read.
- A custom player whose controls are unlabelled `<div>`s that keyboard users cannot reach.

## Production Tips

- Treat captions and transcripts as release blockers for any content-bearing video, the
  same way you would treat missing copy.
- Store transcripts as real HTML pages — they double as SEO-indexable content and are the
  cheapest, most durable alternative.

## AI Review Checklist

- Does every pre-recorded video have synchronized captions covering speech and key sounds?
- Is a text transcript provided and reachable in the DOM (not only inside the player)?
- Is audio description provided when meaningful information is shown but not spoken?
- Is `autoplay` absent, or is the user able to pause/stop/adjust volume independently?
- Are all player controls reachable and operable by keyboard with a visible focus ring?
- Do captions use `kind="captions"` (not `subtitles`) and have they been human-verified?

## Related

- `knowledge/accessibility/14-motion-and-animation.md`
- `knowledge/accessibility/09-images.md`
- `knowledge/accessibility/04-keyboard-navigation.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/23-wcag.md`
