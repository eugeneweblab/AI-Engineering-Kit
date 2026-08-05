---
id: nextjs/16-images
topic: nextjs
slug: images
title: "Next.js Images"
type: doc
order: 16
status: ready
tags: [nextjs, images]
related: [nextjs/20-performance, performance/11-images, accessibility/09-images]
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

`next/image` works in both Server and Client Components. It renders a plain `<img>` on the server, so no `"use client"` directive is required to use it.

Good:

```tsx
import Image from "next/image";

export default function ProductCard() {
    return (
        <Image
            src="/images/products/chair.jpg"
            alt="Ergonomic office chair in charcoal fabric"
            width={480}
            height={480}
        />
    );
}
```

Bad:

```tsx
// No dimensions -> cumulative layout shift, no optimization.
export default function ProductCard() {
    return <img src="/images/products/chair.jpg" alt="Chair" />;
}
```

For a raw `<img>`, Next.js cannot infer intrinsic size, cannot generate `srcset`, and cannot reserve layout space, which harms both CLS and LCP.

---

## Responsive Images

Images should adapt to different viewport sizes.

Provide:

- responsive dimensions;
- appropriate breakpoints;
- correct `sizes` attribute.

When an image must fill its container rather than use fixed dimensions, use the `fill` prop with a positioned parent and a `sizes` value. Without `sizes`, a `fill` image defaults to `100vw`, which downloads a full-viewport-width source even inside a small column.

Good:

```tsx
import Image from "next/image";

export default function Hero() {
    return (
        <div style={{ position: "relative", aspectRatio: "16 / 9" }}>
            <Image
                src="/images/blog/cover.jpg"
                alt="Team collaborating around a whiteboard"
                fill
                sizes="(max-width: 768px) 100vw, 66vw"
                style={{ objectFit: "cover" }}
                priority
            />
        </div>
    );
}
```

Bad:

```tsx
// fill without sizes -> always requests a 100vw source, even in a narrow column.
<div style={{ position: "relative" }}>
    <Image src="/images/blog/cover.jpg" alt="Cover" fill />
</div>
```

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

Configure the negotiated formats in `next.config.ts`. The optimizer serves the first format the browser accepts, falling back to the original source.

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    images: {
        // Preference order; AVIF first, then WebP.
        formats: ["image/avif", "image/webp"],
    },
};

export default nextConfig;
```

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

Set `priority` on the LCP image. It disables lazy loading, adds a high-priority preload, and removes it from the browser's lazy queue.

Good:

```tsx
<Image
    src="/images/blog/cover.jpg"
    alt="Article cover"
    width={1200}
    height={630}
    priority
/>
```

Bad:

```tsx
// Lazy by default -> the LCP image is discovered late and paints slowly.
<Image src="/images/blog/cover.jpg" alt="Article cover" width={1200} height={630} />
```

Only prioritize a small number of critical images. Marking many images `priority` floods the preload queue and negates the benefit.

---

## Remote Images

Configure trusted remote image sources.

Review:

- allowed domains;
- caching;
- security;
- optimization support.

Never allow unrestricted image sources.

Allowlist remote hosts with `images.remotePatterns` in `next.config.ts`. A remote `src` from a host that is not listed throws at render time. Prefer `remotePatterns` over the older `domains` array, which is deprecated and cannot restrict by path.

Good:

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    images: {
        remotePatterns: [
            {
                protocol: "https",
                hostname: "images.example.com",
                pathname: "/uploads/**",
            },
        ],
    },
};

export default nextConfig;
```

Bad:

```ts
// Wildcard hostname allows any origin to be proxied and optimized.
const nextConfig = {
    images: {
        remotePatterns: [{ protocol: "https", hostname: "**" }],
    },
};
```

Remote images require explicit `width` and `height` (or `fill`) because Next.js cannot read their intrinsic size at build time.

---

## Local Images

Prefer storing application assets locally when practical.

Examples:

- logos;
- icons;
- illustrations;
- marketing assets.

Import local files as static imports. Next.js reads the real dimensions at build time, so `width`/`height` are inferred and `placeholder="blur"` generates an automatic blur without a manual `blurDataURL`.

```tsx
import Image from "next/image";
import hero from "@/public/images/hero.png";

export default function Landing() {
    return (
        <Image
            src={hero}
            alt="Product dashboard on a laptop"
            placeholder="blur"
            priority
        />
    );
}
```

Static imports are also fingerprinted, so they can be served with long-term immutable caching. Version static assets to support long-term caching.

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

Decorative images should use empty alternative text. `alt` is a required prop on `next/image`; for a purely decorative image pass `alt=""` so assistive technology skips it.

```tsx
// Meaningful image: describe it.
<Image src="/images/team/ana.jpg" alt="Ana Ruiz, Head of Design" width={96} height={96} />

// Decorative image: empty alt, skipped by screen readers.
<Image src="/images/textures/divider.png" alt="" width={800} height={2} />
```

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

For inline vector icons, prefer rendering the SVG as a component rather than routing it through `next/image` — the optimizer offers no benefit for vectors. The image optimizer refuses to process SVGs unless `images.dangerouslyAllowSVG` is enabled; leave it disabled unless the SVG source is fully trusted, since optimized SVGs can carry scripts.

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

## Examples

**Good Example** — dimensions declared, priority on the LCP image, `sizes` that match the CSS

```tsx
import Image from 'next/image';
import hero from '@/public/hero.jpg';          // static import: dimensions inferred

export function Hero() {
  return (
    <Image
      src={hero}
      alt="Two engineers reviewing a deployment dashboard"
      priority                                  // the LCP image: preload, do not lazy-load
      placeholder="blur"                        // blurDataURL generated at build time
      sizes="100vw"
      className="w-full h-auto"
    />
  );
}

export function ProductThumb({ product }: { product: Product }) {
  return (
    <Image
      src={product.imageUrl}                    // remote: dimensions must be explicit
      alt={product.name}
      width={320}
      height={240}
      // Tells the browser which candidate to pick; must match the rendered width.
      sizes="(max-width: 640px) 50vw, 320px"
      loading="lazy"
    />
  );
}
```

```ts
// next.config.ts — only these hosts may be optimised, so the endpoint cannot be
// used as an open image proxy.
export default {
  images: {
    remotePatterns: [{ protocol: 'https', hostname: 'cdn.example.com', pathname: '/products/**' }],
    formats: ['image/avif', 'image/webp'],
  },
};
```

**Bad Example** — no dimensions, the hero lazy-loaded, `fill` without a sized parent

```tsx
export function Hero() {
  return (
    <>
      {/* A plain img with no width/height: the page reflows when it loads (CLS),
          and no format negotiation or resizing happens at all. */}
      <img src="/hero.jpg" />

      {/* Lazy-loading the LCP image delays it by a full round trip — the single
          most common cause of a poor LCP score on a Next.js site. */}
      <Image src="/hero.jpg" alt="" width={1600} height={900} loading="lazy" />

      {/* `fill` requires a positioned, sized parent. Without one the image
          collapses to zero height and renders nothing. */}
      <div>
        <Image src="/banner.jpg" alt="Banner" fill />
      </div>

      {/* sizes="100vw" on a 320px thumbnail downloads the largest candidate. */}
      <Image src="/thumb.jpg" alt="Thumb" width={320} height={240} sizes="100vw" />
    </>
  );
}
```

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

## Related

- `knowledge/nextjs/20-performance.md`
- `knowledge/performance/11-images.md`
- `knowledge/accessibility/09-images.md`
