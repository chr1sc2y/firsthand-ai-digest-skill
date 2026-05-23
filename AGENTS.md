# Firsthand AI Digest Agent Instructions

Use this repository to run a daily Firsthand AI Digest workflow from <https://ai.prov1dence.top/>.

## Capabilities

- Run once: execute `python3 scripts/run_once.py --hours 24 --output firsthand-ai-digest-source-pack.md`, then inspect the source pack and open only the highest-value original sources before writing the final brief.
- Schedule daily: if the host agent supports scheduled tasks, create a daily 07:00 task using `references/automation_prompt.md` as the task body.
- Portable fallback: if native scheduling is unavailable, explain how to run the one-time command and use the prompt in `references/automation_prompt.md` with the user's scheduler or agent runtime.

## Reporting Rules

- Write the final brief in English.
- Prefer a self-contained HTML file named `firsthand-ai-digest-brief.html`; use Markdown only if HTML/file output is unavailable.
- Optimize for a 3-5 minute read, not a comprehensive research report.
- Use emoji freely, compact bullets, one-row story cards, badges, tables, callouts, or other lightweight visual structures. For top stories, prefer `Source`, `Signal`, and `Potential impact`.
- Use `templates/brief.html` as the fixed HTML template when available. Replace placeholders and keep the CSS/layout stable.
- Use ai.prov1dence.top as an index, not as the only source.
- Follow only high-value or ambiguous items into original sources: blogs, papers, product announcements, videos, podcasts, and X posts or threads.
- Mark inaccessible sources clearly, including login gates, paywalls, anti-bot failures, deleted posts, and missing transcripts.
- Cite clickable links for factual claims.
- Separate facts, inference, and analysis.

## One-Time Run

```bash
python3 scripts/run_once.py --hours 24 --output firsthand-ai-digest-source-pack.md
```

Then read `firsthand-ai-digest-source-pack.md`, open important source links directly, and write the brief using `references/automation_prompt.md`.

The helper filters Firsthand AI Digest cards by their `data-iso` timestamps before fetching original sources.

The helper fetches ordinary pages in parallel and keeps YouTube, X, LinkedIn, short-link, and major podcast hosts metadata-only by default. Use browser or platform-specific access for high-value items from those hosts.

## Scheduling

Target schedule: every day at 07:00 in the user's locale.

If the agent exposes its own automation API, create a native scheduled task. If it does not, do not invent a fake automation; provide the user with a concrete scheduler command or platform-specific next step.
