# AI prompts

Copy-paste these into ChatGPT, Grok, Claude, or similar. Attach or paste the referenced files.

## Setup (first time)

```
I forked a weekly status tracker template. Help me create my engagement files.

Here is config.example.json:
---
[paste config.example.json]
---

Here is template.md:
---
[paste template.md]
---

My engagement:
- Client / engagement name:
- My name:
- Recipients:
- Length in weeks:
- Stage preset: kanban  (or: consulting assessment / simple delivery / custom — if custom, list stages)
- Work items (units/workstreams), with optional codes and contacts:

Return ONLY:
1) A complete config.json
2) A complete weekly-status.md for week 1

Keep the exact markdown field format from the template (week_of, stage lines, - [ ] tasks, etc.).
Do not invent units I did not list. Use On Hold / Closed only if I said so.
```

## Weekly update

```
Update my weekly status markdown. Keep the exact file format. Do not invent units I did not mention.

Current weekly-status.md:
---
[paste weekly-status.md]
---

This week’s rough notes:
---
[paste notes: what happened, stage changes, task updates, new asks/blockers, next week]
---

Rules:
- Bump week_of to this week’s date (ISO YYYY-MM-DD) if I gave one; otherwise ask me for it in one line then wait.
- Rewrite ## Summary as one clear paragraph.
- Update ## Needs Resolution and ## Asks as "- text | owner" bullets (owner optional).
- Update stage: values using ONLY stages from my config (plus On Hold / Closed).
- Task marks: [ ] open, [x] done, [!] blocked.
- Preserve unit names unless I renamed one.
- Return the FULL weekly-status.md only, no commentary.
```

## Vibecoder (Cursor / Claude Code)

Open this folder in your agent and say something like:

```
Apply these weekly notes to weekly-status.md, then run python3 build.py and tell me the HTML path.
Notes: …
```
