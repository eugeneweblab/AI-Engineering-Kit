# Knowledge Base Structure v1.0

Status: APPROVED

This document defines the complete folder and file structure of the Engineering Knowledge Base.

After approval this structure becomes frozen until Knowledge Base v2.

---

# Root

knowledge/

├── README.md

├── ai/
├── engineering/
├── workflows/
├── figma/

├── architecture/
├── backend/
├── frontend/

├── html/
├── css/
├── javascript/
├── typescript/
├── react/
├── nextjs/

├── nodejs/
├── nestjs/

├── php/
├── wordpress/
├── woocommerce/
├── divi/

├── databases/
├── sql/
├── mysql/
├── postgresql/
├── prisma/
├── redis/

├── rest-api/
├── graphql/

├── docker/
├── kubernetes/
├── nginx/
├── linux/
├── devops/
├── cicd/
├── aws/

├── git/
├── github/

├── testing/
├── security/
├── performance/
├── accessibility/
├── seo/
├── tailwind/

├── tools/

├── examples/
├── templates/
├── checklists/
├── playbooks/
├── prompts/
└── snippets/

---

# Standard Structure

Every technical section follows the same layout.

README.md

00-overview.md

01-...

02-...

...

30-...

98-production-checklist.md

99-ai-review-checklist.md

100-common-antipatterns.md

---

Numbering

The numeric prefix is the document's `order`, and it must be unique within a topic.

`01`–`30` is the standard range. A topic may extend past `30` when the subject genuinely
needs another document — `aws/31-high-availability.md` is the only such case today. Reusing
a prefix that is already taken is not permitted; `scripts/check-knowledge.py` fails the build
on a duplicate `order`, on a gap in `01`–`30`, and on a missing `README`/`00`/`98`/`99`/`100`.

Every filename is listed in [`canonical-file-list.md`](canonical-file-list.md).

---

Exceptions

The following directories use their own custom structure:

AI

Engineering

Workflows

Figma

Examples

Templates

Prompts

Playbooks

Checklists

Snippets

These ten have no `00-overview`, no `98`/`99`/`100`, and no obligation to reach `30`. Their
complete file lists are in [`canonical-file-list.md`](canonical-file-list.md), parts 30–33
and 45–50. Do not "fix" them to match the standard layout.

---

Amendments

The structure itself is unchanged and remains frozen until v2. The entries below record
corrections that brought this document in line with what it already described elsewhere.

**2026-08-05**

- `figma/` added to the root tree. It was listed under Exceptions from the start but was
  missing from the directory listing above, so the two halves of this document disagreed.
- Numbering section added, recording that `order` must be unique within a topic and that
  `aws/31-high-availability.md` extends past `30`. Both were already true on disk; neither
  was written down.
- `canonical-file-list.md` extended from 28 topics to all 49, so every file the structure
  produces is now named. Verified against the tree: 1,439 files listed, 1,439 on disk, no
  difference in either direction.