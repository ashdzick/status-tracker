#!/usr/bin/env python3
"""Build a printable HTML weekly status report from markdown + config.json.

Usage:
  python3 build.py                 # weekly-status.md + config.json beside this script
  python3 build.py path/to.md      # config.json looked up beside the markdown file
  python3 build.py path/to.md path/to/config.json

No dependencies beyond the Python standard library.
Open the HTML in a browser and print to PDF.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys

HISTORY = ".status-history.json"
SPECIAL = {"On Hold", "Closed"}

DEFAULT_SHORT = {
    "Not Started": "Not started",
    "In Progress": "In progress",
    "Complete": "Complete",
    "On Hold": "On hold",
    "Outreach Sent": "Outreach",
    "Scheduled": "Scheduled",
    "Interviewed": "Interviewed",
    "Current State Mapped": "Current state",
    "Future State & Impact": "Future state",
    "Backlog": "Backlog",
    "Doing": "Doing",
    "Blocked": "Blocked",
    "Done": "Done",
}

NAVY, BODY, MUTED, FOOTER = "#1C3645", "#17242B", "#49585F", "#49585F"
GREEN_L, GREEN_S, BRICK, HAIR, SAGE = "#157F3D", "#209D50", "#8C3222", "#C4C8C6", "#A3C4AA"

DEFAULT_CONFIG = {
    "output_prefix": "Weekly_Status",
    "eyebrow": "Weekly Status",
    "footer": "Weekly Status",
    "board_heading": "Progress",
    "asks_heading": "What I need from you",
    "needs_heading": "Blocked / needs resolution",
    "summary_heading": "This week",
    "tbd_heading": "Not started",
    "tbd_note": "Exact sequencing and tasks to be determined.",
    "vocabularies": [
        {
            "id": "default",
            "label": "Kanban",
            "stages": ["Not Started", "In Progress", "Complete"],
            "short_labels": {
                "Not Started": "Not started",
                "In Progress": "In progress",
                "Complete": "Complete",
                "On Hold": "On hold",
            },
            "wave_prefix": None,
        }
    ],
    "stats": [
        {"id": "week", "label": "Engagement week<br>of {span}", "style": ""},
        {"id": "units", "label": "Items<br>in scope", "style": ""},
        {"id": "in_progress", "label": "In<br>progress", "style": "win"},
        {"id": "complete", "label": "Complete", "style": "win"},
        {"id": "decisions", "label": "Decisions<br>pending", "style": ""},
    ],
}


def load_config(path: str) -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep-ish copy via json
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            user = json.load(f)
        cfg.update({k: v for k, v in user.items() if k != "vocabularies" and k != "stats"})
        if "vocabularies" in user:
            cfg["vocabularies"] = user["vocabularies"]
        if "stats" in user:
            cfg["stats"] = user["stats"]
    return cfg


def parse(path: str):
    text = open(path, encoding="utf-8").read()
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    meta, summary, asks, needs, units = {}, [], [], [], []
    section, cur = None, None

    for raw in text.splitlines():
        line = raw.rstrip()
        s = line.strip()

        m = re.match(r"^##\s+(BU|Workstream):\s*(.+)$", s)
        if m:
            cur = {
                "kind": m.group(1),
                "name": m.group(2).strip(),
                "tasks": [],
                "prefix": "",
                "wave": "",
                "stage": "Not Started",
                "contacts": "",
                "note": "",
            }
            units.append(cur)
            section = "unit"
            continue
        if re.match(r"^##\s+Summary\s*$", s):
            section, cur = "summary", None
            continue
        if re.match(r"^##\s+Asks\s*$", s):
            section, cur = "asks", None
            continue
        if re.match(r"^##\s+Needs Resolution\s*$", s):
            section, cur = "needs", None
            continue
        if s.startswith("# "):
            meta["title"] = s[2:].strip()
            continue

        km = re.match(
            r"^(week_of|prepared_by|recipients|engagement_week|engagement_span):\s*(.*)$",
            s,
        )
        if km and section is None:
            meta[km.group(1)] = km.group(2).strip()
            continue

        if section == "summary" and s:
            summary.append(s)
        elif section in ("asks", "needs") and s.startswith("- "):
            item = s[2:]
            owner = ""
            if "|" in item:
                item, owner = [p.strip() for p in item.rsplit("|", 1)]
            (asks if section == "asks" else needs).append((item, owner))
        elif section == "unit" and cur is not None:
            fm = re.match(r"^(prefix|wave|stage|contacts|note):\s*(.*)$", s)
            if fm:
                cur[fm.group(1)] = fm.group(2).strip()
            elif s.startswith("- ["):
                mark = s[3]
                cur["tasks"].append((mark, s[6:].strip() if len(s) > 6 else ""))

    meta["summary"] = " ".join(summary)
    return meta, asks, needs, units


def vocabs(cfg: dict) -> list:
    return cfg.get("vocabularies") or DEFAULT_CONFIG["vocabularies"]


def short_label(stage: str, vocab: dict) -> str:
    labels = vocab.get("short_labels") or {}
    if stage in labels:
        return labels[stage]
    return DEFAULT_SHORT.get(stage, stage)


def resolve_vocab(cfg: dict, unit: dict) -> dict:
    vs = vocabs(cfg)
    wave = (unit.get("wave") or "").strip().lower()
    for v in vs:
        prefix = v.get("wave_prefix")
        if prefix and wave.startswith(str(prefix).strip().lower()):
            return v
    for v in vs:
        if v.get("id") == "default" or not v.get("wave_prefix"):
            return v
    return vs[0]


def allowed_stages(cfg: dict) -> set:
    names = set(SPECIAL)
    for v in vocabs(cfg):
        names.update(v.get("stages") or [])
    return names


def warn_stages(cfg: dict, units: list) -> list:
    allowed = allowed_stages(cfg)
    out = []
    for u in units:
        if u["stage"] not in allowed:
            out.append(
                'Unit "%s" has unknown stage "%s" (will render as first stage).'
                % (u["name"], u["stage"])
            )
    return out


def is_tbd(u: dict) -> bool:
    return (u.get("wave") or "").strip().upper() == "TBD"


def rail(stage: str, vocab: dict) -> str:
    stages = vocab.get("stages") or ["Not Started", "In Progress", "Complete"]
    on_hold = stage == "On Hold"
    idx = -1 if on_hold else (stages.index(stage) if stage in stages else 0)
    nodes = []
    for i, st in enumerate(stages):
        done = (not on_hold) and i < idx
        here = (not on_hold) and i == idx
        cls = "done" if done else ("here" if here else "todo")
        if on_hold:
            cls = "hold"
        seg = '<span class="seg %s"></span>' % cls if i else ""
        nodes.append(
            '%s<span class="node %s" title="%s"></span>'
            % (seg, cls, html.escape(st))
        )
    label = "On hold" if on_hold else short_label(stage, vocab)
    lcls = "hold" if on_hold else ("stage-label" if idx > 0 else "stage-label dim")
    short_cls = " short" if len(stages) <= 3 else ""
    return '<div class="rail%s">%s</div><div class="%s">%s</div>' % (
        short_cls,
        "".join(nodes),
        lcls,
        html.escape(label),
    )


def snapshot(units: list) -> dict:
    return {
        u["name"]: {
            "stage": u["stage"],
            "done": sum(1 for m, _ in u["tasks"] if m == "x"),
        }
        for u in units
    }


def load_history(folder: str) -> dict:
    try:
        with open(os.path.join(folder, HISTORY), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_history(folder: str, hist: dict) -> None:
    with open(os.path.join(folder, HISTORY), "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=1, sort_keys=True)


def diff(prev: dict, snap: dict, cfg: dict) -> tuple:
    marks, moved, added = {}, [], []
    vocab = vocabs(cfg)[0]
    for name, cur in snap.items():
        was = prev.get(name)
        if was is None:
            marks[name] = "New this week"
            added.append(name)
        elif was["stage"] != cur["stage"]:
            marks[name] = "Moved from %s" % short_label(was["stage"], vocab)
            moved.append(
                "%s moved to %s" % (name, short_label(cur["stage"], vocab))
            )
        elif cur["done"] > was["done"]:
            n = cur["done"] - was["done"]
            marks[name] = "%d step%s done" % (n, "" if n == 1 else "s")
    lines = moved[:]
    if added:
        lines.append(
            "%s added to the board"
            % (added[0] if len(added) == 1 else "%d lines" % len(added))
        )
    return marks, lines


def closed_strip(closed: list) -> str:
    if not closed:
        return ""
    items = "".join(
        '<li><span class="cl-name">%s</span><span class="cl-note">%s</span></li>'
        % (html.escape(u["name"]), html.escape(u["note"]))
        for u in closed
    )
    return (
        '<div class="closed"><div class="cl-head">Closed</div>'
        '<ul class="cl-list">%s</ul></div>' % items
    )


def compute_stat(stat_id, meta, units, blockers, needs_count, cfg):
    default_vocab = resolve_vocab(cfg, units[0] if units else {"wave": ""})
    stages = default_vocab.get("stages") or []

    if stat_id == "week":
        return str(meta.get("engagement_week", "1"))
    if stat_id == "units":
        return str(len(units))
    if stat_id == "in_progress":
        if "In Progress" in stages:
            return str(sum(1 for u in units if u["stage"] == "In Progress"))
        if "Doing" in stages:
            return str(sum(1 for u in units if u["stage"] == "Doing"))
        if len(stages) >= 2:
            first, last = stages[0], stages[-1]
            return str(
                sum(
                    1
                    for u in units
                    if u["stage"] in stages
                    and u["stage"] not in (first, last, "On Hold")
                )
            )
        return "0"
    if stat_id == "complete":
        if "Complete" in stages:
            return str(sum(1 for u in units if u["stage"] == "Complete"))
        if "Done" in stages:
            return str(sum(1 for u in units if u["stage"] == "Done"))
        if stages:
            return str(sum(1 for u in units if u["stage"] == stages[-1]))
        return "0"
    if stat_id == "decisions":
        return str(len(blockers) + needs_count)
    if stat_id == "wave1":
        return str(
            sum(
                1
                for u in units
                if (u.get("wave") or "").strip().lower().startswith("wave 1")
            )
        )
    if stat_id == "scheduled_or_later":
        if "Scheduled" in stages:
            threshold = stages.index("Scheduled")
            return str(
                sum(
                    1
                    for u in units
                    if u["stage"] in stages and stages.index(u["stage"]) >= threshold
                )
            )
        return "0"
    return "0"


def format_label(label: str, meta: dict) -> str:
    return (
        label.replace("{span}", str(meta.get("engagement_span", "")))
        .replace("{week}", str(meta.get("engagement_week", "")))
    )


def build(src: str, config_path: str) -> str:
    cfg = load_config(config_path)
    meta, asks, needs, all_units = parse(src)
    warnings = warn_stages(cfg, all_units)
    for w in warnings:
        print("WARNING:", w, file=sys.stderr)

    closed = [u for u in all_units if u["stage"] == "Closed"]
    units = [u for u in all_units if u["stage"] != "Closed"]
    blockers = [(u["name"], t) for u in units for m, t in u["tasks"] if m == "!"]

    folder = os.path.dirname(os.path.abspath(src))
    week = meta.get("week_of", "current")
    hist = load_history(folder)
    snap = snapshot(units)
    prior_weeks = sorted(k for k in hist if k != week)
    marks, delta_lines = (
        diff(hist[prior_weeks[-1]], snap, cfg) if prior_weeks else ({}, [])
    )

    rows = []
    tbd_header_done = False
    for u in units:
        if is_tbd(u) and not tbd_header_done:
            tbd_header_done = True
            rows.append(
                '<div class="group"><hr class="thick">'
                '<h3 class="section-head">%s</h3>'
                '<div class="group-note">%s</div></div>'
                % (
                    html.escape(cfg.get("tbd_heading", "Not started")),
                    html.escape(cfg.get("tbd_note", "")),
                )
            )
        vocab = resolve_vocab(cfg, u)
        tasks = []
        for m, t in u["tasks"]:
            cls = {"x": "t-done", "!": "t-block", " ": "t-open"}.get(m, "t-open")
            glyph = "✓" if m == "x" else ("!" if m == "!" else "○")
            tasks.append(
                '<li class="%s"><span class="g">%s</span>%s</li>'
                % (cls, glyph, html.escape(t))
            )
        prefix_html = (
            '<span class="prefix">%s</span>' % html.escape(u["prefix"])
            if u["prefix"]
            else ""
        )
        contacts_html = (
            '<div class="contacts">%s</div>' % html.escape(u["contacts"])
            if u["contacts"]
            else ""
        )
        note_html = (
            '<div class="note">%s</div>' % html.escape(u["note"]) if u["note"] else ""
        )
        wave_html = (
            '<div class="eyebrow">%s</div>' % html.escape(u["wave"]) if u["wave"] else ""
        )
        delta_html = (
            '<div class="delta">%s</div>' % html.escape(marks[u["name"]])
            if u["name"] in marks
            else ""
        )
        rows.append(
            """
    <div class="row">
      <div class="col-bu">
        %s
        <div class="bu-name">%s%s</div>
        %s
      </div>
      <div class="col-stage">%s%s</div>
      <div class="col-detail">
        %s
        <ul class="tasks">%s</ul>
      </div>
    </div>"""
            % (
                wave_html,
                html.escape(u["name"]),
                prefix_html,
                contacts_html,
                rail(u["stage"], vocab),
                delta_html,
                note_html,
                "".join(tasks),
            )
        )

    def bullet(text, who):
        who_s = (" (%s)" % html.escape(who)) if who else ""
        return "<li>%s%s</li>" % (html.escape(text), who_s)

    ask_rows = "".join(bullet(a, o) for a, o in asks) or (
        '<li class="none">None this week.</li>'
    )
    block_rows = "".join(bullet(t, b) for b, t in blockers)
    block_rows += "".join(bullet(t, o) for t, o in needs)
    block_rows = block_rows or '<li class="none">Nothing outstanding.</li>'

    stat_parts = []
    for s in cfg.get("stats") or DEFAULT_CONFIG["stats"]:
        value = compute_stat(
            s.get("id", ""), meta, units, blockers, len(needs), cfg
        )
        style = s.get("style") or ""
        n_class = "n" + (" " + style if style else "")
        label = format_label(s.get("label", ""), meta)
        stat_parts.append(
            '<div class="stat"><div class="%s">%s</div><div class="c">%s</div></div>'
            % (n_class, html.escape(value), label)
        )

    delta_block = (
        '<div class="delta-line"><span class="lbl">Since last week</span>%s</div>'
        % html.escape("; ".join(delta_lines) + ".")
        if delta_lines
        else ""
    )

    recipients = meta.get("recipients", "")
    prepared_by = meta.get("prepared_by", "")
    if prepared_by and recipients:
        byline = "Prepared by %s for %s" % (
            html.escape(prepared_by),
            html.escape(recipients),
        )
    elif prepared_by:
        byline = "Prepared by %s" % html.escape(prepared_by)
    elif recipients:
        byline = "For %s" % html.escape(recipients)
    else:
        byline = ""

    title = meta.get("title", "Weekly Status")
    eyebrow = cfg.get("eyebrow") or title
    footer = cfg.get("footer") or title

    doc = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>%(title)s — %(week)s</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; }
  body { margin:0; background:#fff; color:%(BODY)s;
         font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
         font-size:13.5px; line-height:1.5; -webkit-font-smoothing:antialiased; }
  .page { max-width:1080px; margin:0 auto; padding:44px 52px 60px; }

  .eyebrow { font-size:9.5px; font-weight:600; letter-spacing:.13em; text-transform:uppercase;
              color:%(GREEN_L)s; }
  h1 { font-size:27px; font-weight:800; color:%(NAVY)s; margin:8px 0 6px; letter-spacing:-.015em; }
  .subhead { color:%(MUTED)s; font-size:13px; margin-bottom:26px; }
  hr { border:0; border-top:1px solid %(HAIR)s; margin:26px 0; }
  hr.thick { border-top:2px solid %(NAVY)s; margin:22px 0 26px; }

  .stats { display:flex; gap:56px; margin:0 0 26px; flex-wrap:wrap; }
  .stat .n { font-size:30px; font-weight:800; color:%(NAVY)s; line-height:1; letter-spacing:-.02em; }
  .stat .n.win { color:%(GREEN_S)s; }
  .stat .n.pain { color:%(BRICK)s; }
  .stat .c { font-size:10.5px; color:%(MUTED)s; margin-top:7px; letter-spacing:.02em;
              line-height:1.4; }

  h2 { font-size:14.5px; font-weight:800; letter-spacing:-.01em; text-transform:none;
        color:%(NAVY)s; margin:0 0 11px; line-height:1.3; }
  .summary { font-size:14px; color:%(BODY)s; }

  .twocol { display:flex; gap:56px; align-items:flex-start; }
  .twocol > div { flex:1; }
  ul.plain { list-style:disc; margin:0; padding:0 0 0 18px; }
  ul.plain li { padding:4px 0; font-size:13px; line-height:1.5; }
  li.none { color:%(MUTED)s; font-style:italic; list-style:none; margin-left:-18px; }

  .row { display:flex; gap:34px; padding:19px 0 23px;
          align-items:flex-start; page-break-inside:avoid; }
  .row:first-of-type { padding-top:0; }
  .col-bu { width:210px; flex:none; }
  .col-stage { width:230px; flex:none; padding-top:14px; }
  .col-detail { flex:1; }
  .bu-name { font-size:15px; font-weight:800; color:%(NAVY)s; margin-top:3px; letter-spacing:-.01em; }
  .prefix { font-size:10px; font-weight:600; color:%(FOOTER)s; margin-left:8px; letter-spacing:.06em; }
  .contacts { font-size:11px; color:%(MUTED)s; margin-top:5px; }

  .rail { display:flex; align-items:center; }
  .node { width:9px; height:9px; border-radius:50%%; flex:none;
           border:1.5px solid %(SAGE)s; background:#fff; }
  .node.done { background:%(GREEN_S)s; border-color:%(GREEN_S)s; }
  .node.here { background:#fff; border:2.5px solid %(GREEN_S)s; width:11px; height:11px; }
  .node.hold { border-color:%(HAIR)s; background:#fff; }
  .seg { height:1.5px; flex:1; background:%(HAIR)s; }
  .seg.done { background:%(GREEN_S)s; }
  .stage-label { font-size:10.5px; font-weight:600; color:%(GREEN_L)s; margin-top:9px;
                  letter-spacing:.05em; text-transform:uppercase; }
  .stage-label.dim { color:%(FOOTER)s; }
  .hold { font-size:10.5px; font-weight:600; color:%(FOOTER)s; margin-top:9px;
           letter-spacing:.05em; text-transform:uppercase; }

  .section-head { font-size:19px; font-weight:800; color:%(NAVY)s; letter-spacing:-.015em;
                   text-transform:none; margin:0 0 16px; line-height:1.25; }
  h3.section-head { margin:0 0 5px; }

  .group { padding:14px 0 10px; }
  .group hr.thick { margin:0 0 22px; }
  .group-note { font-size:12.5px; color:%(MUTED)s; }

  .delta { font-size:10px; font-weight:800; color:%(GREEN_L)s; margin-top:6px;
            letter-spacing:.04em; }
  .delta::before { content:"\\2191"; margin-right:5px; }
  .delta-line { margin-top:14px; font-size:13px; color:%(BODY)s; }
  .delta-line .lbl { font-weight:800; color:%(GREEN_L)s; margin-right:9px;
                      letter-spacing:.02em; }

  .note { font-size:12.5px; color:%(MUTED)s; max-width:70ch; }
  ul.tasks { list-style:none; margin:10px 0 0; padding:0; }
  ul.tasks li { font-size:12.5px; padding:2.5px 0; display:flex; gap:9px; align-items:baseline; }
  .g { font-size:10px; width:11px; flex:none; }
  .t-done { color:%(FOOTER)s; } .t-done .g { color:%(GREEN_S)s; }
  .t-open .g { color:%(MUTED)s; }
  .t-block { color:%(BRICK)s; font-weight:600; } .t-block .g { color:%(BRICK)s; }

  .closed { margin-top:26px; padding-top:13px; border-top:1px solid %(HAIR)s; }
  .cl-head { font-size:9.5px; font-weight:800; letter-spacing:.14em; text-transform:uppercase;
              color:%(FOOTER)s; margin-bottom:8px; }
  .cl-list { list-style:none; margin:0; padding:0; }
  .cl-list li { display:flex; gap:12px; align-items:baseline; font-size:11.5px;
                 color:%(MUTED)s; padding:2px 0; }
  .cl-name { font-weight:800; color:%(GREEN_L)s; white-space:nowrap; }
  .cl-name::before { content:"\\2713"; margin-right:6px; }

  footer { margin-top:34px; padding-top:14px; border-top:1px solid %(HAIR)s;
            font-size:10.5px; color:%(FOOTER)s; display:flex; justify-content:space-between; }
  @media print { .page { padding:22px 26px; } body { font-size:11.5px; } }
</style></head><body><div class="page">

  <div class="eyebrow">%(eyebrow)s</div>
  <h1>%(title_esc)s</h1>
  <div class="subhead">Week of %(week)s%(byline_sep)s%(byline)s</div>
  <hr class="thick">

  <div class="stats">
    %(stats)s
  </div>

  <h2>%(summary_heading)s</h2>
  <div class="summary">%(summary)s</div>
  %(delta_block)s
  <hr>

  <div class="twocol">
    <div><h2>%(needs_heading)s</h2><ul class="plain">%(block_rows)s</ul></div>
    <div><h2>%(asks_heading)s</h2><ul class="plain">%(ask_rows)s</ul></div>
  </div>
  <hr class="thick">

  <h2 class="section-head">%(board_heading)s</h2>
  %(rows)s
  %(closed)s

  <footer><span>%(footer)s</span>
    <span>Week of %(week)s</span></footer>
</div>
</body></html>""" % {
        "title": html.escape(title),
        "title_esc": html.escape(title),
        "week": html.escape(week),
        "BODY": BODY,
        "NAVY": NAVY,
        "MUTED": MUTED,
        "FOOTER": FOOTER,
        "GREEN_L": GREEN_L,
        "GREEN_S": GREEN_S,
        "BRICK": BRICK,
        "HAIR": HAIR,
        "SAGE": SAGE,
        "eyebrow": html.escape(eyebrow),
        "byline_sep": " &nbsp;·&nbsp; " if byline else "",
        "byline": byline,
        "stats": "".join(stat_parts),
        "summary_heading": html.escape(cfg.get("summary_heading", "This week")),
        "summary": html.escape(meta.get("summary", "")),
        "delta_block": delta_block,
        "needs_heading": html.escape(cfg.get("needs_heading", "Blocked / needs resolution")),
        "asks_heading": html.escape(cfg.get("asks_heading", "What I need from you")),
        "block_rows": block_rows,
        "ask_rows": ask_rows,
        "board_heading": html.escape(cfg.get("board_heading", "Progress")),
        "rows": "".join(rows),
        "closed": closed_strip(closed),
        "footer": html.escape(footer),
    }

    prefix = cfg.get("output_prefix") or "Weekly_Status"
    out = os.path.join(folder, "%s_%s.html" % (prefix, week))
    open(out, "w", encoding="utf-8").write(doc)
    hist[week] = snap
    save_history(folder, hist)
    print("Wrote", out)
    if delta_lines:
        print("Since %s: %s" % (prior_weeks[-1], "; ".join(delta_lines)))
    elif not prior_weeks:
        print("No prior week on file; deltas start next edition.")
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "weekly-status.md")
    if len(sys.argv) > 2:
        config_path = sys.argv[2]
    else:
        config_path = os.path.join(os.path.dirname(os.path.abspath(src)), "config.json")
        if not os.path.isfile(config_path):
            alt = os.path.join(here, "config.json")
            config_path = alt if os.path.isfile(alt) else config_path
    if not os.path.isfile(src):
        print("Source not found:", src, file=sys.stderr)
        print("Copy template.md to weekly-status.md (or pass a path).", file=sys.stderr)
        sys.exit(1)
    build(src, config_path)


if __name__ == "__main__":
    main()
