# Agent-Neutral Workflow Contract

This file describes the workflow independently of Codex, Claude Code, OpenClaw, or any specific agent runtime.

## Inputs

- Index site: Firsthand AI Digest at `https://ai.prov1dence.top/`
- Lookback window: past 24 hours from task execution time
- Preferred schedule: daily at 07:00 in the user's locale
- Output language: English
- Output style: concise visual daily brief, 3-5 minute read
- Preferred artifact: self-contained HTML file named `firsthand-ai-digest-brief.html`

## Required Workflow

1. Fetch the ai.prov1dence.top index page.
2. Identify items published or surfaced within the requested lookback window.
3. Follow only high-value or ambiguous items to original sources. Include blogs, papers, announcements, videos, podcasts, and X posts or threads when they matter for the brief.
4. Fetch or inspect accessible original content for top stories.
5. Mark access limitations explicitly.
6. Write the final brief using `references/automation_prompt.md`, preferably as self-contained HTML.

## Optional Helper

Run:

```bash
python3 scripts/run_once.py --hours 24 --output firsthand-ai-digest-source-pack.md
```

The helper produces a source pack with discovered links and excerpts. It does not replace original-source verification or analysis.

The helper filters Firsthand AI Digest cards by their `data-iso` timestamps before fetching original sources.

The helper should not be treated as a full crawler. It fetches ordinary web pages in parallel and leaves slow or anti-bot-prone platforms to browser/platform-specific inspection when they matter for the final report.

## Scheduling Contract

An agent implementation may satisfy scheduling through any native mechanism:

- Codex automation
- Claude Code-compatible scheduler, if available
- OpenClaw scheduler, if available
- GitHub Actions
- system cron
- another trusted recurring job runner

If the runtime cannot create scheduled tasks, the agent should say so clearly and provide a manual or platform-specific setup path.

## Output Contract

The final brief must include:

- Execution time and coverage window
- Count of index items and selected top stories
- TL;DR
- Top Stories
- Pattern/Trend section
- Also Noted
- What To Watch Next

Prefer HTML with visual hierarchy: hero/header, stats row, one-row story cards, badges, compact lists, and clear source links. Top-story cards should use `Source`, `Signal`, and `Potential impact` rather than long prose labels. If HTML output is impossible, use Markdown with rich visual signposts and emoji.

Target 800-1200 words, hard maximum 1500 words unless the user asks for a deep dive.
