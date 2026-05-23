# Firsthand AI Digest Skill

A small agent skill for turning [Firsthand AI Digest](https://ai.prov1dence.top/) into a visual daily AI news brief.

It scans the last 24 hours of AI news, picks the most important signals, and asks your agent to produce a clean HTML page that you can read in a few minutes.

![Firsthand AI Digest preview](assets/preview.png)

## What It Does

- Collects the latest 24 hours from Firsthand AI Digest
- Filters items by the site's timestamp data
- Avoids slow raw fetching for X, YouTube, LinkedIn, podcasts, and short links
- Uses original sources only when they are important enough
- Produces a simple visual HTML brief with:
  - TL;DR
  - ranked top stories
  - source links
  - signal and potential impact
  - patterns and watchlist

## Install In Codex

Import this GitHub repository as a Skill:

```text
git@github.com:chr1sc2y/firsthand-ai-digest-skill.git
```

Then ask Codex:

```text
Use $ai-providence-daily to create the daily 7 AM automation and run today's Firsthand AI Digest brief once.
```

Codex will create a daily automation and generate a self-contained HTML brief named:

```text
firsthand-ai-digest-brief.html
```

## Use With Claude Code Or OpenClaw

This repo also includes portable agent instructions:

- `AGENTS.md` for general agents
- `CLAUDE.md` for Claude Code
- `references/agent_contract.md` for a platform-neutral workflow
- `references/automation_prompt.md` for the actual brief-generation prompt

Point your agent at this repository and say:

```text
Follow this repo's instructions and generate today's Firsthand AI Digest HTML brief.
```

If your agent supports scheduled jobs, ask it to schedule the task for every day at 7 AM.

## Run Once Manually

From the repo root:

```bash
python3 scripts/run_once.py --hours 24 --output firsthand-ai-digest-source-pack.md
```

This creates a source pack. The source pack is not the final brief; it is the input your agent uses to write the final HTML page.

## Output Style

The preferred output is a single HTML file with no build step and no external dependencies.

The page should be short, visual, and easy to scan:

- compact header
- TL;DR cards
- one-row story cards
- `Source`, `Signal`, and `Potential impact`
- low-priority notes at the bottom

## Notes

The script is intentionally lightweight. It does not try to fully crawl X, YouTube, LinkedIn, podcasts, or short-link services because those pages are often slow, login-gated, or anti-bot protected. Instead, it uses Firsthand AI Digest metadata by default and lets the agent open only the most important sources when needed.
