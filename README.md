# Status Tracker

A polished weekly status report template you can fork and make yours — without building the layout, stage rails, and PDF-ready HTML from scratch.

Aimed at **builders, freelancers, consultants, and anyone** who needs a clean client-facing status update and would rather customize a working starter than invent one.

```
Fork → edit config.json → AI (or you) update weekly-status.md → python3 build.py → print PDF
```

## Why this exists

Status decks and trackers eat time. You already know what’s in flight; you shouldn’t also have to design a report every week.

This gives you:

- A consulting-grade HTML page that prints cleanly to PDF
- Stage rails, blockers, asks, and week-over-week deltas built in
- A simple markdown file you (or ChatGPT / Grok / Claude) can update
- Config you can reshape for kanban, assessment-style stages, or your own vocabulary

Open source: **fork it, edit it, use it on client work.** Don’t sell this template (or a thin reskin of it) as a product.

## How to use

1. **Fork or clone** this repo.
2. **Configure once** — edit [`config.json`](config.json) (branding, stages, stats). Start from [`config.example.json`](config.example.json) or the [setup prompt](prompts/README.md).
3. **Fill your engagement** — replace [`weekly-status.md`](weekly-status.md) with your units and week-1 content (or copy [`template.md`](template.md) and fill it in).
4. **Each week** — update `weekly-status.md` by hand or with the [weekly AI prompt](prompts/README.md), then run `python3 build.py`.
5. **Send** — open the HTML in a browser → Cmd-P / Ctrl-P → save as PDF.

Vibecoders: open the folder in Cursor (or similar) and ask the agent to apply your notes and run the build.

## Quick start

```bash
git clone https://github.com/ashdzick/status-tracker.git
cd status-tracker
python3 build.py
```

Open the HTML file it prints (e.g. `northwind_Weekly_Status_2026-07-15.html`) in a browser to see the demo. Then swap in your config and markdown.

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

Free to fork, modify, and use for your own work (including client deliverables).  
**Not** free to sell this template — or a thinly modified version of it — as a product.

See [LICENSE](LICENSE).
