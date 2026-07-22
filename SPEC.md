# Format and design spec

Markdown source + `config.json` → printable HTML. Read alongside `build.py`.

## Files

| File | Role |
|---|---|
| `weekly-status.md` | Weekly content (AI- or hand-edited) |
| `config.json` | Stages, branding, stats (set once per engagement) |
| `.status-history.json` | Auto-written snapshots for deltas |
| `build.py` | Parser + renderer (stdlib only) |

## Markdown grammar

Line-oriented. HTML comments are stripped before parsing. Units render in source order (except `wave: TBD` grouping).

### Metadata

Bare `key: value` lines before the first `##` heading:

```
week_of           2026-07-22
prepared_by       Alex Rivera
recipients        Pat, Jordan
engagement_week   2
engagement_span   6
```

The `# Title` H1 becomes the page title and headline.

### Prose sections

```
## Summary            One paragraph (newlines joined with spaces)
## Needs Resolution   Bullets: - text | owner
## Asks               Bullets: - text | owner
```

Owner is optional; without `|` the bullet renders bare.

### Units

```
## BU: Name                  (or ## Workstream: Name)
prefix: CODE
wave: Wave 1
stage: In Progress           Must match config (or On Hold / Closed)
contacts: Name (role)
note: One line of context
- [x] done
- [ ] open
- [!] blocked
```

Field lines must come before the first task line. Unknown fields are ignored.

## config.json

```
output_prefix      Filename prefix before _<week_of>.html
eyebrow            Small label above the title
footer             Footer left text
board_heading      Heading above the unit board
asks_heading       Right band title
needs_heading      Left band title
summary_heading    Heading above the summary
tbd_heading        Divider title for wave: TBD
tbd_note           Divider caption
vocabularies[]     Stage lists (see below)
stats[]            Stats band entries
```

### Vocabularies

```
id             "default" or any id
label          Human label
stages[]       Ordered progress stages
short_labels   Map of stage → compact rail caption
wave_prefix    If set, units whose wave starts with this (case-insensitive) use this vocab
```

**Specials (always):**

- `On Hold` — inert gray rail
- `Closed` — unit moved to the bottom strip

Unknown stage strings print a WARNING and render as index 0.

### Stats

Each entry: `{ "id", "label", "style" }` where `style` is `""` | `win` | `pain`.  
`label` may include `<br>` and `{span}` / `{week}`.

| id | Value |
|---|---|
| `week` | `engagement_week` |
| `units` | Non-closed unit count |
| `in_progress` | Units at `In Progress` or `Doing`, else between first and last stage |
| `complete` | Units at `Complete` or `Done`, else at last stage |
| `decisions` | Blocked tasks + needs bullets |
| `wave1` | Units whose wave starts with `wave 1` |
| `scheduled_or_later` | Units at `Scheduled` or later in default vocab |

## Grouping

Units render in source order until the first `wave: TBD`. Then a divider (`tbd_heading` / `tbd_note`) is emitted. No sorting.

## History and deltas

`.status-history.json` maps `week_of` → `{ unit name: { stage, done } }`. Written after every successful build.

Baseline is the most recent key that is **not** the current `week_of`. Markers: new unit → stage change → more tasks done. Stage changes and additions also compose “Since last week” under the summary.

## Design tokens

```
Navy      #1C3645
Body      #17242B
Muted     #49585F
Green     #157F3D / #209D50
Brick     #8C3222
Hairline  #C4C8C6
Sage      #A3C4AA
```

Report type: Inter. Green = progress, brick = blocked, navy = neutral. No card grids or drop shadows on the report.
