#!/usr/bin/env python3
"""Render 'PARIS body-recomposition.md' to PDF via reportlab.

CJK-capable (WQY Zen Hei) so the Chinese food names render instead of tofu boxes.
pandoc/weasyprint/chromium are unavailable in this env.
"""
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, KeepTogether,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

HERE = Path(__file__).parent
SRC = HERE / "PARIS body-recomposition.md"
OUT = HERE / "PARIS body-recomposition.pdf"

WQY = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
pdfmetrics.registerFont(TTFont("WQY", WQY, subfontIndex=0))
pdfmetrics.registerFontFamily("WQY", normal="WQY", bold="WQY", italic="WQY", boldItalic="WQY")
FONT = "WQY"

INK = colors.HexColor("#1c1c1e")
TEAL = colors.HexColor("#0f6466")
TEAL_D = colors.HexColor("#0a4749")
CLAY = colors.HexColor("#a8552f")
GREY = colors.HexColor("#6b6b70")
RULE = colors.HexColor("#d8d8dc")
BAND = colors.HexColor("#f2f4f4")

# WQY lacks the emoji block; map to glyphs it does carry.
GLYPH_FIX = {"⭐": "★", "⚠️": "▲", "⚠": "▲", "️": ""}

PW, PH = A4
MARGIN = 1.5 * cm
USABLE = PW - 2 * MARGIN


def S(name, **kw):
    kw.setdefault("fontName", FONT)
    kw.setdefault("textColor", INK)
    kw.setdefault("wordWrap", "CJK")  # required for Chinese to wrap
    return ParagraphStyle(name, **kw)


ST = {
    "title": S("title", fontSize=23, leading=28, textColor=TEAL_D, spaceAfter=2),
    "sub": S("sub", fontSize=12, leading=17, textColor=CLAY, spaceAfter=10),
    "h2": S("h2", fontSize=15.5, leading=20, textColor=TEAL_D, spaceBefore=16, spaceAfter=7),
    "h3": S("h3", fontSize=12.5, leading=16.5, textColor=TEAL, spaceBefore=12, spaceAfter=5),
    "h4": S("h4", fontSize=11, leading=15, textColor=CLAY, spaceBefore=9, spaceAfter=4),
    "p": S("p", fontSize=9.8, leading=14.6, spaceAfter=6),
    "meta": S("meta", fontSize=9.5, leading=14, textColor=GREY, spaceAfter=2),
    "li": S("li", fontSize=9.8, leading=14.4, leftIndent=14, firstLineIndent=-9, spaceAfter=3.5),
    "quote": S("quote", fontSize=9.6, leading=14.4, leftIndent=10, rightIndent=6,
               textColor=TEAL_D, spaceBefore=4, spaceAfter=6),
    "cell": S("cell", fontSize=8.7, leading=12.2),
    "cellh": S("cellh", fontSize=8.7, leading=12.2, textColor=colors.white),
    "foot": S("foot", fontSize=8, leading=10, textColor=GREY, alignment=1),
}


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(t):
    """Markdown inline -> reportlab mini-HTML."""
    for bad, good in GLYPH_FIX.items():
        t = t.replace(bad, good)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)      # links -> label
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\*\w])\*([^*\n]+?)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`([^`]+?)`", r'<font color="#a8552f">\1</font>', t)
    return t


def col_widths(rows):
    """Proportional widths from the longest cell per column, CJK counted double."""
    n = max(len(r) for r in rows)
    weights = []
    for i in range(n):
        longest = 0
        for r in rows:
            if i < len(r):
                txt = re.sub(r"[*`\[\]()]", "", r[i])
                w = sum(2 if ord(c) > 0x2E80 else 1 for c in txt)
                longest = max(longest, w)
        weights.append(max(longest, 6) ** 0.72)  # damp so wide columns don't dominate
    total = sum(weights)
    return [USABLE * w / total for w in weights]


def make_table(rows):
    head, body = rows[0], rows[1:]
    data = [[Paragraph(inline(c), ST["cellh"]) for c in head]]
    for r in body:
        r = r + [""] * (len(head) - len(r))
        data.append([Paragraph(inline(c), ST["cell"]) for c in r[:len(head)]])
    t = Table(data, colWidths=col_widths(rows), repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
        ("BOX", (0, 0), (-1, -1), 0.6, RULE),
    ]
    for i in range(2, len(data), 2):
        style.append(("BACKGROUND", (0, i), (-1, i), BAND))
    t.setStyle(TableStyle(style))
    return t


def parse(md):
    """Markdown -> flowables. Handles the subset this document actually uses."""
    flow = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        if not s or s.startswith('<a name='):
            i += 1
            continue

        # table: a header row followed by a |---|---| separator
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw = lines[i].strip()
                if not re.match(r"^\|[\s:|-]+\|$", raw):
                    rows.append([c.strip() for c in raw.strip("|").split("|")])
                i += 1
            flow.append(Spacer(1, 3))
            flow.append(make_table(rows))
            flow.append(Spacer(1, 8))
            continue

        if s.startswith("# "):
            flow.append(Paragraph(inline(s[2:]), ST["title"]))
        elif s.startswith("## "):
            flow.append(Spacer(1, 2))
            flow.append(Paragraph(inline(s[3:]), ST["h2"]))
            flow.append(HRFlowable(width="100%", thickness=0.7, color=RULE,
                                   spaceBefore=1, spaceAfter=7))
        elif s.startswith("### "):
            flow.append(Paragraph(inline(s[4:]), ST["h3"]))
        elif s.startswith("#### "):
            flow.append(Paragraph(inline(s[5:]), ST["h4"]))
        elif s == "---":
            flow.append(HRFlowable(width="100%", thickness=0.7, color=RULE,
                                   spaceBefore=8, spaceAfter=8))
        elif s.startswith("> "):
            block = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                block.append(lines[i].strip().lstrip(">").strip())
                i += 1
            para = Paragraph(inline(" ".join(block)), ST["quote"])
            tb = Table([[para]], colWidths=[USABLE], hAlign="LEFT")
            tb.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), BAND),
                ("LINEBEFORE", (0, 0), (0, -1), 2.5, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            flow.append(tb)
            flow.append(Spacer(1, 7))
            continue
        elif re.match(r"^[-*] ", s) or re.match(r"^\d+\. ", s):
            # gather the item plus any indented continuation lines
            bullet = "•" if re.match(r"^[-*] ", s) else s.split(".")[0] + "."
            body = re.sub(r"^([-*]|\d+\.) ", "", s)
            i += 1
            while i < len(lines) and lines[i].startswith("  ") and lines[i].strip() \
                    and not re.match(r"^\s*([-*]|\d+\.) ", lines[i]):
                body += " " + lines[i].strip()
                i += 1
            flow.append(Paragraph(f"{bullet}  {inline(body)}", ST["li"]))
            continue
        else:
            # merge soft-wrapped paragraph lines
            body = s
            i += 1
            while i < len(lines):
                nxt = lines[i].strip()
                if (not nxt or nxt.startswith(("#", "|", ">", "---", "<a name="))
                        or re.match(r"^([-*]|\d+\.) ", nxt)):
                    break
                body += " " + nxt
                i += 1
            style = ST["meta"] if body.startswith("**Created:") or body.startswith("**Profile:") else ST["p"]
            flow.append(Paragraph(inline(body), style))
            continue

        i += 1
    return flow


def decorate(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 8)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(PW / 2, 0.85 * cm, str(canvas.getPageNumber()))
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN, PH - 1.05 * cm, PW - MARGIN, PH - 1.05 * cm)
    canvas.drawRightString(PW - MARGIN, PH - 0.85 * cm, "PARIS — Body Recomposition Plan")
    canvas.restoreState()


def main():
    if not SRC.exists():
        sys.exit(f"missing source: {SRC}")
    doc = BaseDocTemplate(str(OUT), pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=1.5 * cm, bottomMargin=1.3 * cm,
                          title="PARIS — Body Recomposition Plan", author="")
    frame = Frame(MARGIN, 1.3 * cm, USABLE, PH - 2.8 * cm, id="body")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=decorate)])
    doc.build(parse(SRC.read_text(encoding="utf-8")))
    print(f"wrote {OUT}  ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
