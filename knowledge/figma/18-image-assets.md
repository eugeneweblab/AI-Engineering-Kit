---
id: figma/18-image-assets
topic: figma
slug: image-assets
title: "Image Assets"
type: doc
order: 18
status: ready
tags: [figma, image-assets]
related: []
when_to_use: ""
---
# Image Assets

## Purpose

This document defines the standard process for identifying, exporting, optimizing, and implementing image assets from Figma.

The objective is to ensure that all visual assets are production-ready, responsive, performant, and maintainable.

Image assets should support both visual quality and frontend performance.

---

## Core Principle

Export only what cannot be created with code.

Before exporting any asset, determine whether it should instead be implemented using:

- HTML;
- CSS;
- SVG;
- existing icon libraries;
- reusable components.

Do not export images that represent simple UI elements.

---

## Asset Review Workflow

Follow this sequence for every design.

```
Identify Assets
        ↓
Classify Assets
        ↓
Determine Export Format
        ↓
Optimize Assets
        ↓
Plan Responsive Images
        ↓
Define Naming
        ↓
Implement
        ↓
Verify
```

---

## Step 1 — Identify Assets

Review the entire design.

Identify:

- photographs;
- illustrations;
- logos;
- icons;
- backgrounds;
- decorative graphics;
- product images;
- team photos;
- partner logos;
- marketing graphics.

Document every required asset before implementation.

---

## Step 2 — Classify Assets

Every asset should belong to one category.

## Content Images

Examples:

- blog images;
- product photos;
- author photos;
- team members.

Usually managed through the CMS.

---

## UI Assets

Examples:

- icons;
- logos;
- decorative elements;
- backgrounds.

Usually part of the frontend codebase.

---

## Generated Assets

Examples:

- Open Graph images;
- charts;
- QR codes;
- dynamic graphics.

Usually generated programmatically.

---

## Step 3 — Choose the Correct Format

Preferred formats:

## SVG

Use for:

- icons;
- logos;
- simple illustrations;
- diagrams.

Advantages:

- scalable;
- lightweight;
- editable.

---

## WebP

Use for:

- photographs;
- marketing graphics;
- product images.

Preferred default raster format.

---

## PNG

Use only when:

- transparency is required;
- SVG is not suitable.

Avoid PNG for large photographs.

---

## JPEG

Use only when:

- compatibility requires it;
- WebP or AVIF are unavailable.

Prefer modern formats whenever possible.

---

## AVIF

Use when supported by the project and infrastructure.

Ideal for high-quality photographic content with minimal file size.

---

## Step 4 — Responsive Images

Plan responsive behavior.

Review:

- desktop image;
- tablet image;
- mobile image;
- aspect ratio;
- cropping;
- focal point.

Images should remain visually effective across all breakpoints.

---

## Step 5 — Image Optimization

Verify:

- dimensions;
- compression;
- unnecessary metadata removed;
- correct format;
- quality level;
- loading strategy.

Avoid exporting oversized assets.

---

## Step 6 — Naming Convention

Use descriptive filenames.

Good examples:

```
hero-background.webp

team-member-john-smith.webp

product-card-placeholder.svg

company-logo.svg

pricing-illustration.webp
```

Avoid:

```
image1.png

export-final.png

design-new.jpg

rectangle-copy.png

asset-final-final.png
```

Names should describe purpose rather than origin.

---

## Step 7 — WordPress Guidelines

For WordPress projects:

- store content images in the Media Library;
- use Featured Images where appropriate;
- avoid hardcoded image URLs;
- use responsive image functions;
- allow editors to replace images.

Content should remain editable.

---

## Step 8 — Divi Guidelines

For Divi projects:

- use native image modules where appropriate;
- avoid duplicate uploads;
- reuse shared assets;
- optimize large background images.

Large hero backgrounds should be carefully evaluated for performance.

---

## Step 9 — Accessibility

Review every image.

Determine:

- informative;
- decorative;
- functional.

Verify:

- alternative text;
- empty alt attributes for decorative images;
- accessible labels for linked images.

Accessibility requirements depend on the purpose of the image.

---

## Step 10 — Performance

Verify:

- lazy loading;
- responsive images;
- correct dimensions;
- modern formats;
- duplicate assets;
- unused images.

Every image should justify its network cost.

---

## AI Execution Checklist

## Investigation

☐ Every required asset identified.

☐ Asset category determined.

☐ Export format selected.

☐ Responsive behavior reviewed.

☐ Accessibility reviewed.

---

## Planning

☐ Naming convention applied.

☐ Optimization strategy defined.

☐ CMS integration planned.

☐ Existing assets reviewed.

---

## Verification

☐ Assets exported correctly.

☐ Images optimized.

☐ Responsive behavior verified.

☐ Accessibility requirements satisfied.

☐ No duplicate assets introduced.

---

## Common Mistakes

Avoid:

Exporting text as images.

Exporting icons as PNG files.

Using raster graphics instead of SVG.

Uploading oversized images.

Hardcoding image URLs.

Ignoring responsive image support.

Keeping unused exported assets.

Using generic filenames.

---

## Completion Criteria

Image asset preparation is complete when:

- every required asset has been identified;
- appropriate file formats have been selected;
- assets have been optimized;
- responsive behavior has been planned;
- accessibility requirements have been considered;
- assets are ready for production.

---

## Summary

Well-managed image assets improve frontend performance, accessibility, maintainability, and editor experience.

A structured asset workflow prevents unnecessary exports, duplicate files, and performance regressions while ensuring visual consistency across the project.