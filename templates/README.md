# HTML Template

Use `brief.html` as the fixed visual template for generated briefs.

Agents should copy the template and replace only the `{{PLACEHOLDER}}` blocks with current content. Keep the CSS, layout, class names, and overall structure stable unless the user explicitly asks for design changes.

Common replacements:

- `{{TLDR_CARDS}}`: 3-4 `<div class="tile">...</div>` blocks
- `{{TOP_STORY_CARDS}}`: 5-8 `<article class="story ...">...</article>` blocks
- `{{TODAYS_SHAPE_ITEMS}}`: short `<li>...</li>` bullets
- `{{SIGNAL_QUALITY_ITEMS}}`: short `<li>...</li>` bullets
- `{{ALSO_NOTED_CARDS}}`: 2-4 `<div class="note">...</div>` blocks
- `{{WATCH_NEXT_ITEMS}}`: 3-5 `<li>...</li>` bullets

Top story cards should be one row each and use `Source`, `Signal`, and `Potential impact`.
