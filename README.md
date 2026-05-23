# Firsthand AI Digest Skill

A small agent skill for turning [Firsthand AI Digest](https://ai.prov1dence.top/) into a visual daily AI news brief.

It scans the last 24 hours of AI news, picks the most important signals, and asks your agent to produce a clean HTML page that you can read in a few minutes.

![Firsthand AI Digest preview](assets/preview.png)

## Quick Start

Just copy this sentence to your agent:

```text
Import and use https://github.com/chr1sc2y/firsthand-ai-digest-skill to create a daily 7 AM Firsthand AI Digest automation, and run it once now as a short visual HTML brief.
```

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
- Uses a fixed HTML template at `templates/brief.html`, so each daily brief keeps the same visual style

## Output Style

The preferred output is a single HTML file with no build step and no external dependencies.

The visual style is fixed in `templates/brief.html`. Agents should copy that template and replace the `{{PLACEHOLDER}}` blocks with current content, instead of inventing a new layout each day.

The page should be short, visual, and easy to scan:

- compact header
- TL;DR cards
- one-row story cards
- `Source`, `Signal`, and `Potential impact`
- low-priority notes at the bottom
