# Next.js Performance

## Purpose

This document defines the engineering standards for optimizing performance in Next.js applications.

The objective is to deliver fast, responsive, scalable applications by making performance an architectural concern rather than a post-release optimization effort.

Every performance optimization should be measurable.

---

# Core Principle

Measure first.

Optimize second.

Every optimization should solve a verified performance problem.

---

# Performance Goals

Every application should optimize for:

- fast initial load;
- responsive interactions;
- smooth navigation;
- efficient rendering;
- minimal JavaScript;
- efficient network usage.

Performance should improve user experience rather than benchmark scores alone.

---

# Core Web Vitals

Optimize the following metrics:

- Largest Contentful Paint (LCP)
- Interaction to Next Paint (INP)
- Cumulative Layout Shift (CLS)

These metrics should guide architectural decisions.

---

# Server-First Rendering

Prefer Server Components whenever possible.

Benefits include:

- reduced JavaScript;
- faster rendering;
- improved SEO;
- smaller bundles.

Avoid converting Server Components into Client Components without necessity.

---

# Minimize Client JavaScript

Every Client Component increases:

- bundle size;
- hydration cost;
- JavaScript execution time.

Keep interactive boundaries as small as possible.

---

# Bundle Optimization

Review every dependency.

Ask:

- Is it necessary?
- Is there a smaller alternative?
- Can it run on the server?
- Can it be lazy loaded?

Avoid adding large libraries for small tasks.

---

# Code Splitting

Split JavaScript by feature.

Examples:

- dashboard;
- editor;
- charts;
- administration.

Users should only download code required for the current page.

---

# Dynamic Imports

Use dynamic imports for:

- large editors;
- charting libraries;
- maps;
- media players;
- rarely used components.

Load code only when it becomes necessary.

---

# Lazy Loading

Lazy load:

- heavy components;
- dialogs;
- image galleries;
- analytics dashboards;
- administrative features.

Avoid delaying critical content.

---

# Images

Optimize images by:

- serving responsive sizes;
- using modern formats;
- lazy loading below-the-fold images;
- avoiding oversized assets.

Prefer the Next.js `Image` component.

---

# Fonts

Optimize fonts by:

- self-hosting;
- subsetting;
- preloading critical fonts;
- minimizing font variants.

Avoid layout shifts caused by late font loading.

---

# Data Fetching

Reduce unnecessary requests.

Prefer:

- server-side fetching;
- parallel requests;
- request memoization;
- caching.

Avoid request waterfalls.

---

# Caching

Use caching intentionally.

Review:

- browser cache;
- CDN cache;
- Data Cache;
- Route Cache;
- revalidation.

Avoid disabling caches without justification.

---

# Streaming

Stream slow or independent content.

Examples:

- analytics;
- recommendations;
- reports;
- dashboards.

Streaming improves perceived performance.

---

# Partial Prerendering

When supported by the project, prefer Partial Prerendering (PPR) over fully dynamic rendering when only small sections require personalization.

---

# Hydration

Hydrate only interactive components.

Avoid hydrating:

- static content;
- marketing pages;
- documentation;
- read-only views.

Hydration is one of the largest client-side performance costs.

---

# Rendering

Avoid unnecessary rerenders.

Review:

- component boundaries;
- state ownership;
- memoization;
- prop changes.

Optimize only after identifying real bottlenecks.

---

# Third-Party Scripts

Review every third-party script.

Examples:

- analytics;
- chat widgets;
- marketing tools;
- advertisements.

Load scripts only when required.

---

# Network Performance

Reduce:

- request count;
- payload size;
- duplicate requests.

Compress assets and enable HTTP caching.

---

# Database Performance

Optimize:

- query count;
- indexes;
- pagination;
- selected columns.

Avoid N+1 query problems.

---

# Monitoring

Continuously monitor:

- Core Web Vitals;
- server response times;
- bundle size;
- cache hit ratio;
- rendering performance.

Performance should be continuously measured.

---

# Profiling

Use profiling tools before optimizing.

Examples:

- React DevTools Profiler;
- Chrome DevTools;
- Lighthouse;
- Next.js bundle analyzer.

Avoid premature optimization.

---

# Accessibility

Performance improvements must never reduce accessibility.

Verify:

- loading indicators;
- keyboard navigation;
- focus management;
- semantic HTML.

Accessibility and performance should improve together.

---

# Security

Performance optimizations must never weaken security.

Examples:

- disabling validation;
- exposing private data;
- bypassing authorization.

Security always takes priority.

---

# AI Execution Checklist

## Investigation

☐ Measure current performance.

☐ Identify bottlenecks.

☐ Review bundle size.

☐ Review rendering strategy.

---

## Planning

☐ Minimize client JavaScript.

☐ Optimize loading strategy.

☐ Improve caching.

☐ Reduce network requests.

---

## Verification

☐ Core Web Vitals improved.

☐ Bundle size reviewed.

☐ Caching configured.

☐ Accessibility preserved.

☐ Security maintained.

☐ Performance measurable.

---

# Common Mistakes

Avoid:

Optimizing without measurement.

Making entire pages Client Components.

Disabling caching.

Loading unnecessary JavaScript.

Adding oversized dependencies.

Creating request waterfalls.

Hydrating static content.

Ignoring bundle growth.

---

# Completion Criteria

A performance optimization is complete when:

- measurable improvements have been achieved;
- rendering strategy has been reviewed;
- client JavaScript has been minimized;
- caching is appropriate;
- Core Web Vitals meet project targets;
- accessibility and security remain unaffected.

---

# Summary

Performance is a continuous engineering practice rather than a one-time task.

By prioritizing server rendering, minimizing client-side JavaScript, optimizing bundles, leveraging caching, and continuously measuring results, Next.js applications remain fast, scalable, and maintainable throughout their lifecycle.