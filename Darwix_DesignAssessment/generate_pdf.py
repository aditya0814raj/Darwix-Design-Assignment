from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float
    title: str
    subtitle: str | None = None


def _title(c: canvas.Canvas, text: str) -> None:
    w, h = LETTER
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, h - 0.85 * inch, text)
    c.setStrokeColor(colors.HexColor("#111827"))
    c.setLineWidth(1)
    c.line(0.75 * inch, h - 0.92 * inch, w - 0.75 * inch, h - 0.92 * inch)


def _footer(c: canvas.Canvas, left: str, page_num: int) -> None:
    w, _h = LETTER
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(0.75 * inch, 0.55 * inch, left)
    right = f"Page {page_num}"
    c.drawRightString(w - 0.75 * inch, 0.55 * inch, right)
    c.setFillColor(colors.black)


def _pill(c: canvas.Canvas, x: float, y: float, text: str, fill: colors.Color) -> None:
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(fill)
    c.roundRect(x, y, stringWidth(text, "Helvetica", 9) + 14, 16, 8, stroke=1, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 9)
    c.drawString(x + 7, y + 4, text)
    c.restoreState()


def _box(c: canvas.Canvas, b: Box, *, header_fill=colors.HexColor("#F3F4F6")) -> None:
    c.saveState()
    c.setStrokeColor(colors.HexColor("#111827"))
    c.setLineWidth(1)
    c.roundRect(b.x, b.y, b.w, b.h, 10, stroke=1, fill=0)

    # header
    c.setFillColor(header_fill)
    c.roundRect(b.x, b.y + b.h - 26, b.w, 26, 10, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(b.x + 10, b.y + b.h - 18, b.title)

    if b.subtitle:
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#374151"))
        c.drawString(b.x + 10, b.y + b.h - 38, b.subtitle)
        c.setFillColor(colors.black)
    c.restoreState()


def _arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float) -> None:
    # simple arrow with triangle head
    c.saveState()
    c.setStrokeColor(colors.HexColor("#374151"))
    c.setLineWidth(1.2)
    c.line(x1, y1, x2, y2)
    # head
    import math

    angle = math.atan2(y2 - y1, x2 - x1)
    head_len = 8
    head_ang = math.radians(24)
    x3 = x2 - head_len * math.cos(angle - head_ang)
    y3 = y2 - head_len * math.sin(angle - head_ang)
    x4 = x2 - head_len * math.cos(angle + head_ang)
    y4 = y2 - head_len * math.sin(angle + head_ang)
    c.setFillColor(colors.HexColor("#374151"))
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x3, y3)
    p.lineTo(x4, y4)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()


def _bullets(c: canvas.Canvas, x: float, y: float, lines: Iterable[str], *, leading: float = 14) -> None:
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#111827"))
    yy = y
    for line in lines:
        c.drawString(x, yy, "•")
        c.drawString(x + 12, yy, line)
        yy -= leading


def page_cover(c: canvas.Canvas, page_num: int, *, candidate: str) -> None:
    w, h = LETTER
    _title(c, "Darwix AI — Sales Performance Analytics Dashboard")

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor("#374151"))
    c.drawString(0.75 * inch, h - 1.35 * inch, "UI/UX Assessment Deliverable (User Flow + Wireframes + Rationale)")
    c.setFillColor(colors.black)

    # meta card
    meta = Box(0.75 * inch, h - 3.05 * inch, w - 1.5 * inch, 1.4 * inch, "Submission Details")
    _box(c, meta)
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(meta.x + 14, meta.y + meta.h - 54, f"Candidate: {candidate}")
    c.drawString(meta.x + 14, meta.y + meta.h - 74, f"Date: {date.today().isoformat()}")
    c.drawString(meta.x + 14, meta.y + meta.h - 94, "Audience: Sales Manager (daily operational use)")
    c.setFillColor(colors.black)

    # quick scope
    scope = Box(0.75 * inch, h - 5.7 * inch, w - 1.5 * inch, 2.3 * inch, "Scope (what this dashboard supports)")
    _box(c, scope)
    _bullets(
        c,
        scope.x + 14,
        scope.y + scope.h - 54,
        [
            "Scan team health in < 60 seconds (quality, conversion, nudge success).",
            "Spot agents needing coaching / follow-up with explainable drivers.",
            "Drill into an agent: trends + call-level insights + coaching history.",
            "Take action: assign nudge/coaching module and export weekly report.",
        ],
    )

    _footer(c, "Darwix Design Assessment — Sales Performance Analytics", page_num)


def page_user_flow(c: canvas.Canvas, page_num: int) -> None:
    w, h = LETTER
    _title(c, "1) User Flow / Sitemap (Sales Manager daily loop)")

    # flow boxes
    left = 0.75 * inch
    top = h - 1.55 * inch
    bw = 2.45 * inch
    bh = 0.95 * inch
    gapx = 0.55 * inch
    gapy = 0.45 * inch

    b1 = Box(left, top - bh, bw, bh, "Landing", "Sales Performance Analytics")
    b2 = Box(left + bw + gapx, top - bh, bw, bh, "Dashboard Scan", "KPIs + exceptions")
    b3 = Box(left + 2 * (bw + gapx), top - bh, bw, bh, "Filter / Slice", "date • region • agent")

    b4 = Box(left, top - bh - (bh + gapy), bw, bh, "Agent List", "ranking + flags")
    b5 = Box(left + bw + gapx, top - bh - (bh + gapy), bw, bh, "Agent Drill-down", "trends + drivers")
    b6 = Box(left + 2 * (bw + gapx), top - bh - (bh + gapy), bw, bh, "Action Panel", "assign • follow-up • export")

    b7 = Box(left + bw + gapx, top - bh - 2 * (bh + gapy), bw, bh, "Report Export", "weekly PDF/CSV + summary")

    for b in [b1, b2, b3, b4, b5, b6, b7]:
        _box(c, b)

    # arrows (top row)
    _arrow(c, b1.x + b1.w, b1.y + b1.h / 2, b2.x, b2.y + b2.h / 2)
    _arrow(c, b2.x + b2.w, b2.y + b2.h / 2, b3.x, b3.y + b3.h / 2)
    # down to second row
    _arrow(c, b2.x + b2.w / 2, b2.y, b5.x + b5.w / 2, b5.y + b5.h)
    _arrow(c, b1.x + b1.w / 2, b1.y, b4.x + b4.w / 2, b4.y + b4.h)
    _arrow(c, b3.x + b3.w / 2, b3.y, b6.x + b6.w / 2, b6.y + b6.h)
    # second row progression
    _arrow(c, b4.x + b4.w, b4.y + b4.h / 2, b5.x, b5.y + b5.h / 2)
    _arrow(c, b5.x + b5.w, b5.y + b5.h / 2, b6.x, b6.y + b6.h / 2)
    # export
    _arrow(c, b6.x + b6.w / 2, b6.y, b7.x + b7.w / 2, b7.y + b7.h)

    # legend / assumptions
    legend = Box(0.75 * inch, 1.35 * inch, w - 1.5 * inch, 2.15 * inch, "Key Assumptions (to keep the UX fast)")
    _box(c, legend)

    _pill(c, legend.x + 14, legend.y + legend.h - 62, "Default: last 7 days", colors.HexColor("#2563EB"))
    _pill(c, legend.x + 162, legend.y + legend.h - 62, "3‑click action", colors.HexColor("#16A34A"))
    _pill(c, legend.x + 266, legend.y + legend.h - 62, "Explainability", colors.HexColor("#7C3AED"))

    _bullets(
        c,
        legend.x + 14,
        legend.y + legend.h - 88,
        [
            "Managers start from exceptions: flags + outliers, not raw tables.",
            "Filters are sticky across pages; drill-down preserves context.",
            "Every recommendation includes a short driver (why) to build trust.",
            "Bulk actions supported from agent list (assign coaching in batches).",
        ],
    )

    _footer(c, "Darwix Design Assessment — Sales Performance Analytics", page_num)


def page_wireframe_dashboard(c: canvas.Canvas, page_num: int) -> None:
    w, h = LETTER
    _title(c, "2) Wireframe — Main Dashboard (daily overview)")

    # layout frame
    chrome = Box(0.75 * inch, 0.95 * inch, w - 1.5 * inch, h - 2.05 * inch, "Layout", "Left nav + main content")
    _box(c, chrome, header_fill=colors.HexColor("#E5E7EB"))

    # left nav
    nav = Box(chrome.x + 10, chrome.y + 10, 1.65 * inch, chrome.h - 20, "Nav", "Analytics • Coaching • Reports")
    _box(c, nav)

    # top bar (filters + export)
    topbar = Box(nav.x + nav.w + 12, chrome.y + chrome.h - 88, chrome.w - nav.w - 34, 78, "Top Bar", "Date range • Region • Agent • Export")
    _box(c, topbar)
    _pill(c, topbar.x + 14, topbar.y + 14, "Date: Last 7 days", colors.HexColor("#2563EB"))
    _pill(c, topbar.x + 140, topbar.y + 14, "Region: All", colors.HexColor("#0EA5E9"))
    _pill(c, topbar.x + 234, topbar.y + 14, "Agent: All", colors.HexColor("#0EA5E9"))
    _pill(c, topbar.x + topbar.w - 132, topbar.y + 14, "Download report", colors.HexColor("#111827"))

    # KPI row
    kpi_y = topbar.y - 86
    kpi_w = (topbar.w - 20) / 3
    k1 = Box(topbar.x, kpi_y, kpi_w, 78, "Call Quality", "Avg score • % high risk")
    k2 = Box(topbar.x + kpi_w + 10, kpi_y, kpi_w, 78, "Conversion", "Win rate • stage drop-offs")
    k3 = Box(topbar.x + 2 * (kpi_w + 10), kpi_y, kpi_w, 78, "Nudge Success", "% adopted • lift")
    for b in [k1, k2, k3]:
        _box(c, b)

    # charts row
    charts_y = kpi_y - 190
    ch_w = (topbar.w - 10) / 2
    ch1 = Box(topbar.x, charts_y, ch_w, 180, "Trends", "team score vs conversion (spark lines)")
    ch2 = Box(topbar.x + ch_w + 10, charts_y, ch_w, 180, "Win/Loss Drivers", "top reasons + sentiment themes")
    for b in [ch1, ch2]:
        _box(c, b)

    # agent table + action rail
    table_y = chrome.y + 10
    table_h = charts_y - table_y - 12
    table_w = topbar.w - 1.8 * inch - 10
    table = Box(topbar.x, table_y, table_w, table_h, "Agents (ranked)", "flags: ↓trend • low conversion • low nudge adoption")
    rail = Box(topbar.x + table_w + 10, table_y, 1.8 * inch, table_h, "Exception Queue", "agents needing attention")
    _box(c, table)
    _box(c, rail)

    # table columns sketch
    c.saveState()
    c.setStrokeColor(colors.HexColor("#D1D5DB"))
    c.setLineWidth(1)
    cols = ["Agent", "Call score", "Conv%", "Nudge%", "Risk", "Action"]
    col_x = [table.x + 12, table.x + 150, table.x + 250, table.x + 330, table.x + 410, table.x + table.w - 80]
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#374151"))
    yy = table.y + table.h - 52
    for i, name in enumerate(cols):
        c.drawString(col_x[i], yy, name)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    for r in range(6):
        y = yy - 18 - r * 18
        c.line(table.x + 10, y - 6, table.x + table.w - 10, y - 6)
        c.setFillColor(colors.HexColor("#111827"))
        c.drawString(col_x[0], y, f"Agent {r+1}")
        c.setFillColor(colors.HexColor("#111827"))
        c.drawString(col_x[1], y, f"{78 - r*3}")
        c.drawString(col_x[2], y, f"{24 - r}%")
        c.drawString(col_x[3], y, f"{62 - r*4}%")
        c.setFillColor(colors.HexColor("#DC2626") if r >= 3 else colors.HexColor("#16A34A"))
        c.drawString(col_x[4], y, "High" if r >= 3 else "OK")
        c.setFillColor(colors.HexColor("#2563EB"))
        c.drawString(col_x[5], y, "View →")
    c.restoreState()

    _footer(c, "Darwix Design Assessment — Sales Performance Analytics", page_num)


def page_wireframe_agent_drilldown(c: canvas.Canvas, page_num: int) -> None:
    w, h = LETTER
    _title(c, "2) Wireframe — Agent Drill-down (performance + drivers)")

    frame = Box(0.75 * inch, 0.95 * inch, w - 1.5 * inch, h - 2.05 * inch, "Agent Profile View", "Context preserved from dashboard filters")
    _box(c, frame, header_fill=colors.HexColor("#E5E7EB"))

    # header strip
    header = Box(frame.x + 10, frame.y + frame.h - 90, frame.w - 20, 80, "Agent Header", "Name • Role • Region • Current flags • Assign action")
    _box(c, header)
    _pill(c, header.x + 14, header.y + 14, "Flag: ↓call score trend", colors.HexColor("#DC2626"))
    _pill(c, header.x + 170, header.y + 14, "Flag: low nudge adoption", colors.HexColor("#DC2626"))
    _pill(c, header.x + header.w - 160, header.y + 14, "Assign coaching", colors.HexColor("#111827"))

    # left column charts
    left_col_w = (frame.w - 30) * 0.62
    right_col_w = (frame.w - 30) - left_col_w
    lc_x = frame.x + 10
    rc_x = lc_x + left_col_w + 10

    trends = Box(lc_x, header.y - 200, left_col_w, 190, "Trend Cards", "score • conversion • nudge adoption (12 weeks)")
    calls = Box(lc_x, frame.y + 10, left_col_w, trends.y - (frame.y + 22), "Calls / Deals", "sortable list with AI highlights")
    _box(c, trends)
    _box(c, calls)

    # right column: drivers + coaching history
    drivers = Box(rc_x, header.y - 150, right_col_w, 140, "Top Drivers (Explainability)", "why the agent is underperforming")
    history = Box(rc_x, frame.y + 10, right_col_w, drivers.y - (frame.y + 22), "Coaching & Nudges", "assigned modules • completion • impact")
    _box(c, drivers)
    _box(c, history)

    # drivers bullets
    c.saveState()
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#111827"))
    _bullets(
        c,
        drivers.x + 14,
        drivers.y + drivers.h - 54,
        [
            "Low objection-handling score in pricing conversations.",
            "High talk-to-listen ratio (customer interruptions ↑).",
            "Nudge “ask-next-step” shown 18×, adopted 5× (↓).",
        ],
        leading=13,
    )
    c.restoreState()

    # calls list sketch
    c.saveState()
    c.setStrokeColor(colors.HexColor("#D1D5DB"))
    c.setLineWidth(1)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#374151"))
    c.drawString(calls.x + 12, calls.y + calls.h - 52, "Recent interactions")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#111827"))
    for i in range(7):
        y = calls.y + calls.h - 72 - i * 18
        c.line(calls.x + 10, y - 6, calls.x + calls.w - 10, y - 6)
        c.drawString(calls.x + 12, y, f"{'Call' if i % 2 == 0 else 'Deal'} • {['Won','Lost','In progress'][i % 3]} • AI risk: {['Low','Med','High'][i % 3]}")
        c.setFillColor(colors.HexColor("#2563EB"))
        c.drawRightString(calls.x + calls.w - 12, y, "Open →")
        c.setFillColor(colors.HexColor("#111827"))
    c.restoreState()

    _footer(c, "Darwix Design Assessment — Sales Performance Analytics", page_num)


def page_wireframe_action_panel_and_rationale(c: canvas.Canvas, page_num: int) -> None:
    w, h = LETTER
    _title(c, "2–3) Action Panel + Design Rationale (1 page)")

    # action panel wireframe (left)
    left_w = (w - 1.5 * inch) * 0.52
    right_w = (w - 1.5 * inch) - left_w - 12
    x0 = 0.75 * inch

    action = Box(x0, 1.0 * inch, left_w, h - 2.2 * inch, "Action Panel (slide-over)", "assign nudges • coaching • follow-ups • export")
    _box(c, action, header_fill=colors.HexColor("#E5E7EB"))

    # action sections
    sec1 = Box(action.x + 10, action.y + action.h - 150, action.w - 20, 110, "Assign Module", "template-based, quick + consistent")
    sec2 = Box(action.x + 10, sec1.y - 120, action.w - 20, 110, "Follow-up Task", "create task + due date + reason")
    sec3 = Box(action.x + 10, sec2.y - 120, action.w - 20, 110, "Export", "weekly summary PDF/CSV")
    for s in [sec1, sec2, sec3]:
        _box(c, s)
    _pill(c, sec1.x + 14, sec1.y + 14, "Assign to agent", colors.HexColor("#111827"))
    _pill(c, sec3.x + 14, sec3.y + 14, "Download weekly report", colors.HexColor("#111827"))

    # rationale (right)
    rationale = Box(x0 + left_w + 12, 1.0 * inch, right_w, h - 2.2 * inch, "Design Rationale (max 1 page)", None)
    _box(c, rationale, header_fill=colors.HexColor("#E5E7EB"))

    c.saveState()
    tx = rationale.x + 14
    ty = rationale.y + rationale.h - 52
    c.setFont("Helvetica", 10.5)
    c.setFillColor(colors.HexColor("#111827"))
    paragraphs = [
        "Goal: Enable a Sales Manager to diagnose team health fast, then take corrective action with high confidence.",
        "1) Speed under pressure: The main dashboard is exception-first (flags + outliers) with KPIs and trends placed above the agent table so a manager can scan in <60 seconds. Filters are sticky and always visible.",
        "2) Clarity + trust: Drill-down surfaces explainable drivers (talk ratio, objection handling, nudge adoption) next to trends. This answers “why is performance down?” before asking the manager to act.",
        "3) Actionability: The action panel is a slide-over that keeps context (no page loss) and supports one-tap templates for nudges/coaching plus a lightweight follow-up task. Bulk assignment is supported from the agent list.",
        "4) Reporting: Export is available globally (top bar) and locally (action panel) to match both planned weekly routines and reactive coaching moments.",
        "Assumptions: Call scoring + nudge events are near-real-time; managers oversee multiple regions; AI outputs provide confidence + short explanations; permissions allow assigning coaching modules and exporting reports.",
    ]

    max_width = rationale.w - 28
    leading = 13
    for p in paragraphs:
        # simple manual wrapping
        words = p.split()
        line = ""
        for w0 in words:
            candidate = (line + " " + w0).strip()
            if stringWidth(candidate, "Helvetica", 10.5) <= max_width:
                line = candidate
            else:
                c.drawString(tx, ty, line)
                ty -= leading
                line = w0
        if line:
            c.drawString(tx, ty, line)
            ty -= leading
        ty -= 6

    c.restoreState()

    _footer(c, "Darwix Design Assessment — Sales Performance Analytics", page_num)


def build_pdf(output_path: str, *, candidate: str) -> None:
    c = canvas.Canvas(output_path, pagesize=LETTER)
    page_cover(c, 1, candidate=candidate)
    c.showPage()
    page_user_flow(c, 2)
    c.showPage()
    page_wireframe_dashboard(c, 3)
    c.showPage()
    page_wireframe_agent_drilldown(c, 4)
    c.showPage()
    page_wireframe_action_panel_and_rationale(c, 5)
    c.save()


if __name__ == "__main__":
    # Update this string if you want your exact submission filename.
    candidate = "Adity_Lastname"
    output = f"{candidate}_Darwix_DesignAssessment.pdf"
    build_pdf(output, candidate=candidate)
    print(f"Wrote: {output}")

