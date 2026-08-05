---
id: github/05-discussions
topic: github
slug: discussions
title: "Discussions"
type: doc
order: 5
status: ready
tags: [github, discussions, SECURITY.md, GitHub]
related: [github/03-issues, github/04-projects, github/02-repositories, github/13-security, github/19-organizations]
when_to_use: "Read before deciding where open-ended Q&A, proposals, or announcements should live, versus filing an Issue."
---
# Discussions

## Purpose

GitHub Discussions is a forum built into a repository or organization for
conversations that do not have a single, closeable outcome: questions, ideas,
design proposals, announcements, and community Q&A. This document defines when to
use a Discussion instead of an [Issue](03-issues.md), and how to structure
Discussions so knowledge accumulates and stays findable.

## Why It Matters

The most common GitHub organizational mistake is putting conversation in the wrong
container. Open-ended questions filed as Issues clutter the backlog and never close;
concrete tasks buried in Discussions never get tracked or shipped. Discussions exist
precisely so that "how should we approach X?" and "is this a bug?" have a home that
does not pollute the task ledger. Used well, Discussions become a searchable
knowledge base that turns repeated questions into a single answered thread — reducing
the same question being asked ten times as ten Issues.

## Core Principles

- **Discussions are open-ended; Issues are closeable.** If there is a definable
  "done," it is an Issue. If it is a question, idea, or conversation, it is a
  Discussion.
- **Q&A discussions have accepted answers.** The Q&A format lets one reply be marked
  as the answer, so future readers get the resolution immediately.
- **Categories are the taxonomy.** Announcements, Q&A, Ideas, and Show-and-tell are
  distinct formats; choose the category that matches the conversation's shape.
- **Promote, do not duplicate.** When a Discussion produces a concrete task, convert
  it into an Issue — GitHub preserves the link — rather than copy-pasting.
- **Discussions are a knowledge asset.** They are searchable and permanent; write
  them so a stranger six months later can find and understand the answer.

## Best Practices

- Enable Discussions and define a lean category set with clear descriptions so
  people post in the right place. Use the Q&A format for support categories.
- Pin canonical Discussions (roadmap, FAQ, contribution norms) so newcomers find
  them first.
- Mark an answer on every resolved Q&A thread; an unanswered question is invisible
  value lost.
- Convert a Discussion to an Issue the moment it yields an actionable task, keeping
  the origin link for context.
- Use announcement categories (restricted to maintainers) for releases and policy
  changes, so signal is not drowned by replies.
- Moderate: lock resolved or off-topic threads, and set a code of conduct for public
  repos to keep the space usable.

## Examples

**Good Example** — routing a question correctly and capturing the answer

```text
User posts in the "Q&A" category:
  "What's the recommended way to configure connection pooling in v4?"

A maintainer replies with the approach and MARKS IT AS THE ANSWER.
→ The thread now surfaces the resolution at the top and is searchable, so the
  next person who asks finds it instead of opening a duplicate.

Later the thread reveals the docs are missing this. A maintainer converts it to
an Issue "Document connection-pool config for v4" — GitHub keeps the link back to
the Discussion, so the rationale travels with the task.
```

**Bad Example** — open-ended question filed as an Issue

```markdown
### Issue #613: "How do I configure pooling?"
<!-- WRONG container. This has no closeable outcome, so it will sit open forever
     cluttering the bug/feature backlog, or be closed unanswered and lost.
     It also can't be marked as an "accepted answer", so the resolution—if it
     ever comes—won't surface for the next person. This belongs in Q&A Discussions. -->
labels: question
```

## Common Mistakes

- Filing open-ended questions as Issues, cluttering the backlog with items that
  never close.
- Burying an actionable task inside a Discussion instead of converting it to an Issue.
- Leaving Q&A threads without a marked answer, so the resolution is unfindable.
- Too many overlapping categories, so nobody knows where to post.
- Using Discussions where a design decision should be an [ADR](02-repositories.md)
  or Issue with tracked acceptance.

## Production Tips

- Automate with the GraphQL API (Discussions is GraphQL-first) to auto-label,
  cross-post releases, or nudge unanswered Q&A after N days.
- Redirect misfiled Issues with a saved comment and convert them, rather than just
  closing — preserve the asker's effort.
- For public projects, pair Discussions with a `SECURITY.md` so vulnerability reports
  go to a private channel, never a public thread.

## AI Review Checklist

- Does this content lack a closeable outcome, making it a Discussion not an Issue?
- Is it posted in the category matching its shape (Q&A, Idea, Announcement)?
- For Q&A: is an accepted answer marked once resolved?
- When a task emerged, was it converted to a linked Issue rather than duplicated?
- Are categories few and clearly described enough to route posts correctly?

## Related

- `knowledge/github/03-issues.md`
- `knowledge/github/04-projects.md`
- `knowledge/github/02-repositories.md`
- `knowledge/github/13-security.md`
- `knowledge/github/19-organizations.md`
