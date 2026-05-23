# Firsthand AI Digest Skill

A small agent skill for turning [Firsthand AI Digest](https://ai.prov1dence.top/) into a visual daily AI news brief.

It scans the last 24 hours of AI news, picks the most important signals, and asks your agent to produce a clean HTML page that you can read in a few minutes.

![Firsthand AI Digest preview](assets/preview.png)

## Quick Start

Just copy this sentence into your agent. It will generate a scheduled task and run it immediately once.

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
