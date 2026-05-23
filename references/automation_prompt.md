Every time the task runs, collect AI news items from Firsthand AI Digest at https://ai.prov1dence.top/ for the past 24 hours as of execution time. The site usually updates at 06:00, 12:00, 18:00, and 24:00 with the previous 6 hours of content; a 07:00 run should cover the four most recent update windows and filter items by Firsthand AI Digest `data-iso` time and source publication time where available.

Produce a short English daily brief, not a long research report. The goal is that a busy reader can understand what happened in 3-5 minutes.

Default output: create a self-contained HTML file named `firsthand-ai-digest-brief.html`. If the runtime cannot write files, output the same brief in Markdown.

Collection rules:

1. Use Firsthand AI Digest as the index.
2. Use original sources only for high-value or unclear items. Do not deep-read every X post, video, podcast, or low-signal repost.
3. For YouTube, podcasts, X, LinkedIn, and short links, use the Digest title/summary/time/link by default. Open them only if they appear important enough for the final brief or if the Digest summary is ambiguous.
4. Clearly mark important items whose source was access-limited, but do not spend much space on access-limit explanations.
5. Skip or compress low-signal social posts, reposts, memes, repeated links, and items outside the 24-hour window.

Brief requirements:

1. Write in English.
2. Keep it concise: target 800-1200 words, hard maximum 1500 words unless the user explicitly asks for depth.
3. Use emoji freely where they improve scanning. Do not restrict yourself to a fixed emoji set.
4. Use visual hierarchy, not only text: cards, badges, compact tables, timeline strips, priority labels, callout boxes, or short ranked lists are all acceptable.
5. Cover only the top 5-8 developments. Put the rest into a short "Also Noted" section.
6. Attach links to factual claims, but avoid citation clutter. One link per item is usually enough.
7. Separate facts from interpretation, but keep the wording lightweight.

HTML design requirements:

1. Make a single self-contained HTML file with inline CSS and no build step.
2. Use a clean, simple visual style: readable type, generous spacing, responsive layout, and a restrained palette.
3. Keep the header compact. The title should be `Firsthand AI Digest`, with a short one-line summary and small stats for window, items scanned, and read time. Do not let the hero/header dominate the page.
4. Use visual priority from most important to least important:
   - Hero/header summary
   - TL;DR
   - Top story cards
   - Pattern/trend section
   - Also Noted
   - Watch Next
5. Avoid giant walls of text. Story cards should be one per row by default, ordered by importance, and use this compact structure: headline, source link, `Signal`, and `Potential impact`.
6. Use badges such as `High impact`, `Product`, `Research`, `Security`, `Infra`, `Policy`, or custom labels when helpful.
7. Include a small footer noting that Firsthand AI Digest is the index and access-limited sources may rely on Digest metadata.

Suggested HTML sections:

- Compact header: `⚡ Firsthand AI Digest`
- Stats row: Window, items scanned, top stories, estimated read time
- `🧭 TL;DR`: 3-5 visually distinct bullets
- `🔥 Top Stories`: 5-8 one-row cards ordered by importance. Each card should show `Source`, `Signal`, and `Potential impact`; avoid labels like "What happened" and "Why it matters."
- `🧩 Pattern I’m Seeing`: 3-5 trend chips or compact bullets
- `👀 Also Noted`: dense low-priority list
- `✅ What To Watch Next`: 3-5 bullets

Do not include long per-item sections with "confidence," "follow-up questions," "impact scope," or extensive source-access discussion unless the user asks for a deep-dive report.
