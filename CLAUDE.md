# Claude Code Instructions

This repository defines a Firsthand AI Digest workflow.

When the user asks to use this repo:

1. Read `references/agent_contract.md`.
2. For a one-time run, execute:

```bash
python3 scripts/run_once.py --hours 24 --output firsthand-ai-digest-source-pack.md
```

3. Read the generated source pack.
4. Open and verify only the most important original sources, especially official blogs, papers, videos, podcasts, and X threads.
5. Write the final brief in English using `references/automation_prompt.md`, preferably as `firsthand-ai-digest-brief.html`, by copying `templates/brief.html` and filling the placeholders. Keep the visual style stable.
6. For scheduling, use Claude Code's available scheduling/automation mechanism if present. If no native scheduler is available, give the user a host-specific option such as cron, GitHub Actions, or their agent runtime's scheduler.

Do not treat the source pack as the final report. It is only the collection layer.
