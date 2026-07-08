---
id: nextjs/16-images
topic: nextjs
slug: images
title: "Next.js Images"
type: doc
order: 16
status: ready
tags: [nextjs, images]
related: []
when_to_use: "Read before adding or optimizing images in a Next.js app."
---
# Next.js Images

## Purpose

This document defines the engineering standards for working with images in Next.js applications.

The objective is to deliver fast-loading, responsive, accessible, and optimized images while minimizing bandwidth usage and improving Core Web Vitals.

Images should be treated as performance-critical resources rather than simple visual assets.

---

## Core Principle

Optimize every image.

Never serve larger images than necessary.

---

## Image Optimization Goals

Every application should strive for:

- fast loading;
- responsive sizing;
- minimal bandwidth usage;
- modern image formats;
- accessibility;
- stable layouts.

---

## Image Component

Prefer the Next.js `Image` component over the native `img` element.

Benefits include:

- automatic optimization;
- responsive sizing;
- lazy loading;
- optimized formats;
- layout stability.

Use native `img` only when the `Image` component cannot satisfy the requirements.

---

## Responsive Images

Images should adapt to different viewport sizes.

Provide:

- responsive dimensions;
- appropriate breakpoints;
- correct `sizes` attribute.

Avoid serving desktop-sized images to mobile devices.

---

## Image Formats

Prefer modern formats.

Recommended order:

- AVIF;
- WebP;
- PNG;
- JPEG;
- SVG (vector graphics).

Choose the format that best matches the image content.

---

## Image Dimensions

Always define image dimensions.

Specify:

- width;
- height;
- aspect ratio.

Avoid layout shifts caused by unknown image sizes.

---

## Lazy Loading

Lazy load images that are not immediately visible.

Typical examples:

- galleries;
- blog images;
- product listings;
- user avatars below the fold.

Do not lazy load critical above-the-fold images.

---

## Priority Images

Prioritize images that contribute to the Largest Contentful Paint (LCP).

Examples:

- hero banners;
- product hero images;
- article cover images.

Only prioritize a small number of critical images.

---

## Remote Images

Configure trusted remote image sources.

Review:

- allowed domains;
- caching;
- security;
- optimization support.

Never allow unrestricted image sources.

---

## Local Images

Prefer storing application assets locally when practical.

Examples:

- logos;
- icons;
- illustrations;
- marketing assets.

Version static assets to support long-term caching.

---

## Image Compression

Balance:

- image quality;
- file size;
- loading speed.

Avoid visually lossless images that consume unnecessary bandwidth.

---

## Accessibility

Every meaningful image should include descriptive alternative text.

Decorative images should use empty alternative text.

Avoid:

- redundant descriptions;
- keyword stuffing;
- generic alternatives such as "image".

---

## SVG

Use SVG for:

- logos;
- icons;
- simple illustrations;
- diagrams.

Avoid embedding excessively complex SVGs that increase bundle size.

---

## Background Images

Use CSS background images only when the image is purely decorative.

Content images should remain semantic HTML elements.

---

## Image Organization

Organize assets consistently.

Example:

```
public/

    images/

        products/

        avatars/

        blog/

        icons/

        logos/
```

Keep naming predictable and descriptive.

---

## CDN

Serve images through a CDN whenever appropriate.

Benefits include:

- global distribution;
- faster delivery;
- reduced server load.

---

## Security

Validate remote image sources.

Avoid rendering images from untrusted origins without appropriate controls.

---

## Performance

Review:

- image size;
- compression;
- responsive behavior;
- lazy loading;
- caching.

Images often represent the largest assets on a page.

---

## AI Execution Checklist

## Investigation

☐ Identify image purpose.

☐ Determine responsive requirements.

☐ Review accessibility.

☐ Review performance impact.

---

## Planning

☐ Use the `Image` component.

☐ Optimize dimensions.

☐ Select appropriate format.

☐ Configure lazy loading.

---

## Verification

☐ Images optimized.

☐ Layout shifts avoided.

☐ Accessibility verified.

☐ Responsive behavior confirmed.

☐ Caching configured.

☐ Performance reviewed.

---

## Common Mistakes

Avoid:

Using oversized images.

Serving desktop images to mobile devices.

Omitting dimensions.

Using `img` instead of `Image` without justification.

Missing alternative text.

Lazy loading LCP images.

Loading untrusted remote images.

Ignoring image compression.

---

## Completion Criteria

Image implementation is complete when:

- images are optimized;
- responsive behavior is implemented;
- accessibility requirements are satisfied;
- layout shifts are eliminated;
- caching is configured appropriately;
- performance objectives are met.

---

## Summary

Images have a significant impact on application performance and user experience.

By using the Next.js `Image` component, optimizing formats and dimensions, providing accessible alternative text, and leveraging responsive loading strategies, applications become faster, more accessible, and easier to maintain.