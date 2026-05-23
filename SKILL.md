---
name: ai-providence-daily
description: Build and run a daily Firsthand AI Digest workflow for https://ai.prov1dence.top/. Use when the user wants to create a recurring 7 AM automation, run the workflow once, collect the last 24 hours of AI news from Firsthand AI Digest, check high-value original sources when needed, then produce a concise English visual daily brief, preferably as a self-contained HTML page with emoji, cards, badges, links, and a 3-5 minute reading time.
---

# Firsthand AI Digest

## Overview

Use this skill to turn Firsthand AI Digest into a repeatable AI daily brief. The workflow has two modes:

- Create a scheduled automation that runs every day at 07:00 in the user's locale.
- Run the workflow once immediately and produce a concise English 24-hour visual daily brief.

## Quick Start

1. For scheduled runs, create a Codex automation with the prompt in `references/automation_prompt.md`.
2. For one-time runs, execute `scripts/run_once.py` to generate a source pack, then inspect only the highest-value original sources.
3. Use Firsthand AI Digest summaries as the fast scan layer; open original sources when a top story needs verification or context.
4. Clearly mark inaccessible, login-gated, deleted, paywalled, or anti-bot-limited sources.

## Create The Automation

When the user asks to create the daily task, use Codex automation support rather than writing cron files by hand.

Use these automation settings:

- Name: `Firsthand AI Digest Daily Brief`
- Schedule: every day at 07:00 in the user's locale
- Kind: cron/workspace automation
- Reasoning: high
- Prompt: load and use `references/automation_prompt.md`

If the user's environment exposes `automation_update`, create:

```json
{
  "kind": "cron",
  "name": "Firsthand AI Digest Daily Brief",
  "rrule": "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR,SA,SU;BYHOUR=7;BYMINUTE=0",
  "status": "ACTIVE",
  "reasoningEffort": "high"
}
```

Add the current workspace directory as the automation working directory when available. Preserve the prompt text exactly unless the user asks to customize coverage, report language, or schedule.

## Run Once

Run the bundled source collector from the skill directory:

```bash
python3 scripts/run_once.py --hours 24 --output ai-providence-source-pack.md
```

Useful options:

```bash
python3 scripts/run_once.py --hours 24 --max-detail-pages 20 --max-original-sources 80 --output report-source-pack.md
python3 scripts/run_once.py --site https://ai.prov1dence.top/ --hours 48 --output source-pack.md
```

The script intentionally creates a source pack, not a final brief. It filters Firsthand AI Digest cards by timestamp, fetches ordinary article/blog pages in parallel, and keeps slow or anti-bot-prone hosts such as YouTube, X, LinkedIn, t.co, and podcast platforms as metadata-only by default. Then open only high-value sources directly with browser or platform-specific access, especially:

- Official product/company blogs and docs
- Papers and technical reports
- YouTube/video pages, descriptions, chapters, captions or transcripts when available
- Podcast pages, show notes, transcripts or episode metadata
- X posts and threads, using accessible public text or logged-in browser context if the user provides it

Use `--fetch-heavy-hosts` only when the user explicitly wants raw HTML fetching for slow/anti-bot-prone hosts and accepts longer runtimes.

## Brief Requirements

Write the final brief in English. Make it useful at a glance, not exhaustive. Default to a self-contained HTML file named `firsthand-ai-digest-brief.html`; use Markdown only when file output is unavailable or the user asks for Markdown.

Include:

1. A short header with coverage window, items scanned, number of top stories, and estimated read time.
2. A prominent TL;DR section with 3-5 bullets.
3. A top stories section with only the top 5-8 items, ordered by importance.
4. For each top story: a short headline, source link, `Signal`, and `Potential impact`.
5. A pattern/trend section with 3-5 compact insights.
6. A compact also-noted section for lower-signal items.
7. A watch-next section with 3-5 bullets.

Target 800-1200 words, hard maximum 1500 words unless the user explicitly asks for a deep dive. Use emoji freely and naturally; do not restrict the emoji set. Use visual signposts such as cards, badges, priority labels, compact tables, timeline strips, or callout boxes. Avoid long per-item confidence/impact/follow-up blocks.

For HTML output, keep the page simple and self-contained with inline CSS. Use a clean responsive layout, readable type, generous spacing, and visual priority from most important to least important. Use `Firsthand AI Digest` as the page title. Keep the header compact so attention flows quickly to TL;DR and top stories. Render top-story cards as one row each by default; two-column cards can feel noisy for news scanning. Do not use external JS or a build step.

## Source Handling Rules

- Prefer primary sources for top stories; use Firsthand AI Digest metadata for low-signal items.
- Use ai.prov1dence.top as an index and context layer, not as the sole source of truth.
- If a source cannot be fully fetched, mark it briefly as access-limited only when the item is important.
- For videos and podcasts without transcripts, use accessible titles, descriptions, chapters, show notes, or Digest excerpts.
- For X posts, use Digest excerpts by default; open thread context only for important stories.
