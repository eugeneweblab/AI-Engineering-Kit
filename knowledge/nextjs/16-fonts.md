# Next.js Fonts

## Purpose

This document defines the engineering standards for working with fonts in Next.js applications.

The objective is to deliver fast-loading, accessible, and visually consistent typography while minimizing layout shifts and improving Core Web Vitals.

Fonts should be considered a critical part of application performance rather than a purely visual asset.

---

# Core Principle

Load only the fonts that users need.

Optimize typography without sacrificing performance.

---

# Typography Goals

Every application should strive for:

- fast font loading;
- minimal layout shifts;
- readable typography;
- consistent rendering;
- accessible text;
- efficient caching.

---

# Font Loading

Prefer the built-in Next.js font optimization.

Benefits include:

- automatic self-hosting;
- improved privacy;
- reduced external requests;
- optimized loading behavior.

Avoid loading fonts directly from external CDNs unless required.

---

# Local Fonts

Use local fonts when:

- branding requires custom typography;
- commercial licenses prohibit redistribution;
- offline availability is required.

Store font files in a predictable directory.

Example:

```
public/

    fonts/

        Inter/

        Roboto/

        BrandFont/
```

---

# Google Fonts

Use the Next.js font integration for Google Fonts.

Benefits include:

- automatic optimization;
- self-hosting;
- preload support;
- improved performance.

Avoid importing fonts using CSS `@import`.

---

# Font Variants

Load only the required:

- font weights;
- font styles;
- subsets.

Avoid downloading unused font variants.

---

# Font Subsets

Configure only the language subsets required by the application.

Examples:

- latin;
- latin-ext;
- cyrillic;
- greek;
- vietnamese.

Smaller subsets improve loading performance.

---

# Font Display

Use an appropriate font display strategy.

Prefer behavior that minimizes invisible text while reducing layout shifts.

Typography should remain readable during loading.

---

# Font Preloading

Preload critical fonts used above the fold.

Avoid preloading fonts that are only used on specific pages.

---

# Font Fallbacks

Always define appropriate fallback fonts.

Example:

```
Inter

↓

Arial

↓

sans-serif
```

Fallback fonts should closely match the primary font to reduce layout shifts.

---

# Layout Stability

Typography should not introduce unexpected layout movement.

Verify:

- line height;
- font metrics;
- fallback compatibility;
- responsive scaling.

Minimize Cumulative Layout Shift (CLS).

---

# Responsive Typography

Typography should adapt to different screen sizes.

Review:

- font size;
- line height;
- spacing;
- readability.

Avoid fixed typography that performs poorly on mobile devices.

---

# Accessibility

Ensure typography supports:

- sufficient contrast;
- readable font sizes;
- scalable text;
- predictable spacing.

Users should be able to zoom content without losing readability.

---

# Variable Fonts

Prefer variable fonts when they replace multiple static font files.

Benefits include:

- fewer network requests;
- smaller total payload;
- greater design flexibility.

Avoid using variable fonts if browser compatibility requirements prohibit them.

---

# Caching

Fonts should be cached aggressively.

Version font assets to support long cache lifetimes without serving outdated files.

---

# Performance

Review:

- font file size;
- number of variants;
- preload usage;
- caching strategy;
- layout stability.

Typography should contribute positively to Core Web Vitals.

---

# Organization

Keep font configuration centralized.

Example:

```
src/

    styles/

        fonts.ts

        typography.ts
```

Avoid scattering font configuration throughout the application.

---

# Security

Load fonts only from trusted sources.

Avoid introducing unnecessary third-party font providers.

---

# AI Execution Checklist

## Investigation

☐ Review typography requirements.

☐ Identify required font families.

☐ Review language support.

☐ Review performance goals.

---

## Planning

☐ Optimize font loading.

☐ Minimize variants.

☐ Configure fallbacks.

☐ Enable caching.

---

## Verification

☐ Fonts load efficiently.

☐ Layout shifts minimized.

☐ Typography accessible.

☐ Responsive behavior verified.

☐ Caching configured.

☐ Performance reviewed.

---

# Common Mistakes

Avoid:

Loading unnecessary font weights.

Using CSS `@import` for fonts.

Missing fallback fonts.

Loading fonts from multiple providers.

Ignoring layout shifts.

Preloading every font.

Using decorative fonts for body text.

Duplicating font configuration.

---

# Completion Criteria

Font implementation is complete when:

- fonts load efficiently;
- only required variants are included;
- layout shifts are minimized;
- typography remains accessible;
- caching is configured appropriately;
- performance objectives are satisfied.

---

# Summary

Typography directly affects usability, accessibility, and performance.

By using Next.js font optimization, minimizing downloaded variants, configuring appropriate fallbacks, and preventing layout shifts, applications provide a faster and more consistent user experience across all devices.