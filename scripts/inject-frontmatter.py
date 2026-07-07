#!/usr/bin/env python3
"""Inject idempotent YAML frontmatter into every topic doc under knowledge/*/*.md."""
import os, re, sys

KB = "/Users/devrocketteam2/Downloads/active_projects/AI-Engineering-Kit/knowledge"

def title_from_slug(slug):
    return " ".join(w.capitalize() for w in slug.split("-")) if slug else "Overview"

def first_h1(text):
    for line in text.splitlines():
        m = re.match(r"^#\s+(.*\S)\s*$", line)
        if m:
            return m.group(1).strip()
    return None

processed, skipped = 0, 0
for topic in sorted(os.listdir(KB)):
    tdir = os.path.join(KB, topic)
    if not os.path.isdir(tdir):
        continue
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(tdir, fn)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if text.lstrip().startswith("---"):
            skipped += 1
            continue

        base = fn[:-3]  # strip .md
        num_m = re.match(r"^(\d+)-(.*)$", base)
        if fn == "README.md":
            slug, order, doctype = "readme", -1, "index"
        elif num_m:
            order = int(num_m.group(1))
            slug = num_m.group(2)
            doctype = "doc"
        else:
            order = 999
            slug = base.lower().replace("_", "-")
            doctype = "doc"

        h1 = first_h1(text)
        title = h1 if h1 else title_from_slug(slug)
        # Draft = empty scaffold: nothing beyond the H1 (or a leftover TODO marker).
        body_wo_h1 = re.sub(r"^#\s+.*$", "", text, count=1, flags=re.M).strip()
        is_empty = body_wo_h1 == "" or "TODO: Document pending" in body_wo_h1
        status = "draft" if is_empty else "ready"

        if fn == "README.md":
            doc_id = f"{topic}/readme"
            tags = [topic]
        else:
            doc_id = f"{topic}/{base}"
            tags = [topic] if slug in ("", "readme") else [topic, slug]

        # Build frontmatter (double-quote title to be safe)
        safe_title = title.replace('"', '\\"')
        tags_str = ", ".join(tags)
        fm = ["---",
              f"id: {doc_id}",
              f"topic: {topic}",
              f"slug: {slug}",
              f'title: "{safe_title}"',
              f"type: {doctype}",
              f"order: {order}",
              f"status: {status}",
              f"tags: [{tags_str}]",
              "related: []",
              'when_to_use: ""',
              "---",
              ""]
        new_text = "\n".join(fm) + "\n" + text.lstrip("\n") if not text.startswith("\n") else "\n".join(fm) + text
        # Ensure single blank line between frontmatter and body
        new_text = "\n".join(fm) + text.lstrip("\n")
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)
        processed += 1

print(f"processed={processed} skipped(existing FM)={skipped}")
