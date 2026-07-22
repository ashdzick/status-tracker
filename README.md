# Status Tracker

A **forkable starter template** for consulting-style weekly status reports.

You customize it once, then update each week with ChatGPT, Grok, Claude, or any AI — or by hand. One Python command builds a print-ready HTML page (Cmd-P → PDF). No server, no accounts, no npm.

```
Fork → edit config.json → AI updates weekly-status.md → python3 build.py → print PDF
```

## Quick start

```bash
git clone <this-repo>
cd status-tracker   # or whatever you named the folder
python3 build.py
```

Open the HTML file it prints (e.g. `northwind_Weekly_Status_2026-07-15.html`) in a browser.

For your own engagement: edit `config.json` and replace `weekly-status.md` (or use the [setup prompt](prompts/README.md)). Blank starter: [`template.md`](template.md).

## How weekly updates work (AI)

1. Copy your current `weekly-status.md` and this week’s rough notes.
2. Paste them into ChatGPT / Grok / Claude using the **Weekly update** prompt in [`prompts/README.md`](prompts/README.md).
3. Replace `weekly-status.md` with the AI output.
4. Run `python3 build.py`.
5. Open the HTML → print → save as PDF.

Vibecoders: open the folder in Cursor and ask the agent to apply your notes and run the build.

First-time setup prompt is in the same file.

## Suggested configuration options

Edit `config.json` (start from [`config.example.json`](config.example.json)). Stage names on units must match **exactly**. `On Hold` and `Closed` are always allowed specials (park a row / retire to the bottom strip).

### 1. Kanban (default)

```json
"vocabularies": [{
  "id": "default",
  "label": "Kanban",
  "stages": ["Not Started", "In Progress", "Complete"],
  "short_labels": {
    "Not Started": "Not started",
    "In Progress": "In progress",
    "Complete": "Complete",
    "On Hold": "On hold"
  },
  "wave_prefix": null
}]
```

Good stats: `week`, `units`, `in_progress`, `complete`, `decisions`.

### 2. Consulting assessment

Discovery / current-state-to-impact style:

```json
"vocabularies": [{
  "id": "default",
  "label": "Assessment",
  "stages": [
    "Not Started",
    "Outreach Sent",
    "Scheduled",
    "Interviewed",
    "Current State Mapped",
    "Future State & Impact"
  ],
  "short_labels": {
    "Not Started": "Not started",
    "Outreach Sent": "Outreach",
    "Scheduled": "Scheduled",
    "Interviewed": "Interviewed",
    "Current State Mapped": "Current state",
    "Future State & Impact": "Future state",
    "On Hold": "On hold"
  },
  "wave_prefix": null
}]
```

Optional second vocabulary for foundation rows (used when a unit’s `wave` starts with `wave 0`):

```json
{
  "id": "foundation",
  "label": "Foundation",
  "stages": ["Not Started", "In Progress", "Complete"],
  "short_labels": {
    "Not Started": "Not started",
    "In Progress": "In progress",
    "Complete": "Complete"
  },
  "wave_prefix": "wave 0"
}
```

Assessment-oriented stats: `week`, `units`, `wave1`, `scheduled_or_later`, `decisions`.

### 3. Simple delivery

```json
"vocabularies": [{
  "id": "default",
  "label": "Delivery",
  "stages": ["Backlog", "Doing", "Done"],
  "short_labels": {
    "Backlog": "Backlog",
    "Doing": "Doing",
    "Done": "Done",
    "On Hold": "On hold"
  },
  "wave_prefix": null
}]
```

Use `On Hold` for parked work (or add `"Blocked"` as its own stage if you want it on the rail).

### 4. Custom stages

Any ordered list works. Rules:

- Put progress stages in `vocabularies[].stages`.
- Add compact captions in `short_labels`.
- Use extra vocabularies with `wave_prefix` when different workstreams need different rails.
- Keep `On Hold` / `Closed` as specials; unknown stage names print a **WARNING** and fall back to the first stage.

Also customize branding in `config.json`:

| Field | Purpose |
|---|---|
| `eyebrow` | Small green label above the title |
| `footer` | Footer left text |
| `output_prefix` | HTML filename prefix |
| `board_heading` | Section title above the unit list |
| `stats` | Array of `{ id, label, style }` — see [SPEC.md](SPEC.md) |

## Markdown cheat sheet

```
week_of: 2026-07-22
prepared_by: Your Name
recipients: Stakeholders
engagement_week: 1
engagement_span: 6

## Summary
## Needs Resolution     # - text | owner
## Asks                 # - text | owner

## BU: Name             # or ## Workstream: Name
prefix: CODE
wave: Wave 1            # use TBD for the “not started” group
stage: In Progress
contacts: …
note: …
- [x] done
- [ ] open
- [!] blocked
```

Full grammar: [SPEC.md](SPEC.md).

## What the build does

- Renders the stage rail from your config
- Rolls blocked `[!]` tasks into the left band
- Groups `wave: TBD` under a divider
- Moves `Closed` units to a bottom strip
- Tracks week-over-week deltas in `.status-history.json`

```bash
python3 build.py
python3 build.py path/to/other.md
python3 build.py path/to/other.md path/to/config.json
```

## Privacy

Everything stays in your clone. No cloud. Google Fonts load when you open the HTML in a browser.

## License

MIT — see [LICENSE](LICENSE).
