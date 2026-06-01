#!/usr/bin/env python3
"""Convert the interview-prep HTML (single source of truth) into a CJK-capable PDF
using reportlab. libreoffice/chromium/weasyprint are unavailable in this env."""
import re, sys
from html.parser import HTMLParser
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Preformatted, HRFlowable, PageBreak)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT = "WQY"
pdfmetrics.registerFont(TTFont(FONT, "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", subfontIndex=0))
pdfmetrics.registerFontFamily(FONT, normal=FONT, bold=FONT, italic=FONT, boldItalic=FONT)

BLUE = colors.HexColor("#0a4d8c")
BLUE2 = colors.HexColor("#14598a")
ORANGE = colors.HexColor("#b3471a")
GREY = colors.HexColor("#777777")

styles = {
    "h1": ParagraphStyle("h1", fontName=FONT, fontSize=21, leading=26, textColor=BLUE, spaceAfter=4),
    "h2": ParagraphStyle("h2", fontName=FONT, fontSize=15, leading=20, textColor=BLUE, spaceBefore=4, spaceAfter=8, borderColor=colors.HexColor("#c9d6e5"), borderWidth=0, leftIndent=0),
    "h3": ParagraphStyle("h3", fontName=FONT, fontSize=12.5, leading=16, textColor=BLUE2, spaceBefore=12, spaceAfter=4),
    "q": ParagraphStyle("q", fontName=FONT, fontSize=12, leading=16, textColor=ORANGE, spaceBefore=14, spaceAfter=3),
    "p": ParagraphStyle("p", fontName=FONT, fontSize=10.5, leading=15.5, textColor=colors.HexColor("#1a1a1a"), spaceAfter=5),
    "subtitle": ParagraphStyle("subtitle", fontName=FONT, fontSize=11, leading=15, textColor=GREY, spaceAfter=3),
    "meta": ParagraphStyle("meta", fontName=FONT, fontSize=10, leading=15, textColor=GREY, spaceAfter=2),
    "box": ParagraphStyle("box", fontName=FONT, fontSize=10, leading=15, textColor=colors.HexColor("#1a1a1a")),
    "cell": ParagraphStyle("cell", fontName=FONT, fontSize=9, leading=12.5, textColor=colors.HexColor("#1a1a1a")),
    "cellh": ParagraphStyle("cellh", fontName=FONT, fontSize=9, leading=12.5, textColor=colors.white),
    "li": ParagraphStyle("li", fontName=FONT, fontSize=10.5, leading=15, textColor=colors.HexColor("#1a1a1a"), leftIndent=16, firstLineIndent=-12, spaceAfter=3),
    "pre": ParagraphStyle("pre", fontName=FONT, fontSize=8.5, leading=11.5, textColor=colors.HexColor("#222222")),
    "footer": ParagraphStyle("footer", fontName=FONT, fontSize=9, leading=12, textColor=GREY, alignment=1, spaceBefore=10),
}

INLINE = {"b", "strong", "code", "span", "font", "i", "em"}
BLOCK = {"h1", "h2", "h3", "p", "pre", "div", "li"}
SKIP = {"style", "script", "head", "title"}

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

class Conv(HTMLParser):
    def __init__(self, width):
        super().__init__(convert_charrefs=True)
        self.width = width
        self.flow = []
        self.buf = []
        self.cap = None          # dict for current block or None
        self.skip = 0
        self.closes = []         # inline close-tag stack
        self.table = None
        self.row = None
        self.cell = None
        self.cellh = False
        self.in_cell = False
        self.list_type = None
        self.li_n = 0

    def target_append(self, s):
        if self.in_cell:
            self.cell.append(s)
        elif self.cap is not None:
            self.buf.append(s)

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        a = dict(attrs)
        cls = a.get("class", "")
        if tag == "br":
            self.target_append("<br/>")
        elif tag == "hr":
            self.flow.append(Spacer(1, 6))
            self.flow.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#dddddd")))
            self.flow.append(Spacer(1, 4))
        elif tag == "table":
            self.table = []
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.in_cell = True
            self.cell = []
            self.cellh = (tag == "th")
        elif tag in ("ul", "ol"):
            self.list_type = tag
            self.li_n = 0
        elif tag in INLINE:
            if tag in ("b", "strong"):
                self.target_append("<b>"); self.closes.append("</b>")
            elif tag in ("i", "em"):
                self.target_append("<i>"); self.closes.append("</i>")
            elif tag == "code":
                self.target_append('<font face="Courier" backColor="#eeeeee">'); self.closes.append("</font>")
            elif tag == "span":
                if "label-cn" in cls:
                    self.target_append('<font color="#777777"><b>'); self.closes.append("</b></font>")
                elif "label" in cls:
                    self.target_append('<font color="#0a4d8c"><b>'); self.closes.append("</b></font>")
                elif "red" in cls:
                    self.target_append('<font color="#b3471a"><b>'); self.closes.append("</b></font>")
                else:
                    self.closes.append("")
            else:
                self.closes.append("")
        elif tag in BLOCK:
            self.cap = {"tag": tag, "cls": cls, "style": a.get("style", "")}
            self.buf = []
            if tag == "li":
                self.li_n += 1

    def handle_endtag(self, tag):
        if tag in SKIP:
            if self.skip:
                self.skip -= 1
            return
        if self.skip:
            return
        if tag in INLINE:
            if self.closes:
                self.target_append(self.closes.pop())
        elif tag in ("td", "th"):
            self.in_cell = False
            self.row.append((self.cellh, "".join(self.cell).strip()))
            self.cell = None
        elif tag == "tr":
            if self.row is not None:
                self.table.append(self.row); self.row = None
        elif tag == "table":
            self.emit_table(); self.table = None
        elif tag in ("ul", "ol"):
            self.list_type = None
        elif tag in BLOCK:
            self.emit_block()
            self.cap = None

    def handle_data(self, data):
        if self.skip or (self.cap is None and not self.in_cell):
            return
        if self.cap and self.cap["tag"] == "pre":
            self.target_append(esc(data))
        else:
            txt = re.sub(r"\s+", " ", data)
            if txt:
                self.target_append(esc(txt))

    def emit_block(self):
        tag, cls = self.cap["tag"], self.cap["cls"]
        markup = "".join(self.buf).strip()
        if tag == "pre":
            inner = Preformatted("".join(self.buf).strip("\n"), styles["pre"])
            self.flow.append(self.boxify(inner, colors.HexColor("#f3f3f3"), border=colors.HexColor("#dddddd")))
            self.flow.append(Spacer(1, 4)); return
        if not markup:
            return
        if tag == "h1":
            self.flow.append(Paragraph(markup, styles["h1"]))
            self.flow.append(HRFlowable(width="100%", thickness=2.5, color=BLUE, spaceAfter=6))
        elif tag == "h2":
            self.flow.append(PageBreak())
            self.flow.append(Paragraph(markup, styles["h2"]))
            self.flow.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c9d6e5"), spaceAfter=8))
        elif tag == "h3":
            self.flow.append(Paragraph(markup, styles["h3"]))
        elif tag == "li":
            bullet = f"{self.li_n}. " if self.list_type == "ol" else "•  "
            self.flow.append(Paragraph(bullet + markup, styles["li"]))
        elif tag == "div":
            if "en" in cls.split():
                self.flow.append(self.boxify(Paragraph(markup, styles["box"]), colors.HexColor("#eef4fb"), bar=BLUE))
                self.flow.append(Spacer(1, 4))
            elif "cn" in cls.split():
                self.flow.append(self.boxify(Paragraph(markup, styles["box"]), colors.HexColor("#f7f6f2"), bar=colors.HexColor("#a0a0a0")))
                self.flow.append(Spacer(1, 6))
            elif "note" in cls.split():
                self.flow.append(self.boxify(Paragraph(markup, styles["box"]), colors.HexColor("#fff8e6"), border=colors.HexColor("#f0d894")))
                self.flow.append(Spacer(1, 6))
            elif "tip" in cls.split():
                self.flow.append(self.boxify(Paragraph(markup, styles["box"]), colors.HexColor("#ecf7ee"), bar=colors.HexColor("#3c9d54")))
                self.flow.append(Spacer(1, 6))
            elif "q" in cls.split():
                self.flow.append(Paragraph(markup, styles["q"]))
            elif "subtitle" in cls.split():
                self.flow.append(Paragraph(markup, styles["subtitle"]))
            elif "cover-meta" in cls.split() or "meta" in cls.split():
                self.flow.append(Paragraph(markup, styles["meta"]))
            elif "footer" in (cls.split() if cls else []) or "text-align:center" in self.cap["style"]:
                self.flow.append(Paragraph(markup, styles["footer"]))
            else:
                self.flow.append(Paragraph(markup, styles["p"]))
        else:  # p
            self.flow.append(Paragraph(markup, styles["p"]))

    def boxify(self, inner, bg, bar=None, border=None):
        t = Table([[inner]], colWidths=[self.width])
        ts = [("BACKGROUND", (0, 0), (-1, -1), bg),
              ("LEFTPADDING", (0, 0), (-1, -1), 9),
              ("RIGHTPADDING", (0, 0), (-1, -1), 9),
              ("TOPPADDING", (0, 0), (-1, -1), 7),
              ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]
        if bar:
            ts.append(("LINEBEFORE", (0, 0), (0, -1), 3, bar))
        if border:
            ts.append(("BOX", (0, 0), (-1, -1), 0.6, border))
        t.setStyle(TableStyle(ts))
        return t

    def emit_table(self):
        if not self.table:
            return
        ncols = max(len(r) for r in self.table)
        cw = self.width / ncols
        data = []
        for r in self.table:
            row = []
            for is_h, cellmarkup in r:
                st = styles["cellh"] if is_h else styles["cell"]
                row.append(Paragraph(cellmarkup, st))
            while len(row) < ncols:
                row.append(Paragraph("", styles["cell"]))
            data.append(row)
        t = Table(data, colWidths=[cw] * ncols, repeatRows=1)
        ts = [("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c0c0c0")),
              ("BACKGROUND", (0, 0), (-1, 0), BLUE),
              ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("LEFTPADDING", (0, 0), (-1, -1), 6),
              ("RIGHTPADDING", (0, 0), (-1, -1), 6),
              ("TOPPADDING", (0, 0), (-1, -1), 5),
              ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]
        for i in range(1, len(data)):
            if i % 2 == 0:
                ts.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f4f7fb")))
        t.setStyle(TableStyle(ts))
        self.flow.append(Spacer(1, 4))
        self.flow.append(t)
        self.flow.append(Spacer(1, 6))


def main():
    src = open("/home/user/Claude-Code/haitong-interview-prep/Haitong_Interview_Prep.html", encoding="utf-8").read()
    # Replace emoji / glyphs the CJK font lacks, with clean text equivalents
    reps = {"🔴": "[必背] ", "🟡": "[重点] ", "🟢": "[熟悉] ", "☐": "[ ] ",
            "✅": "✓ ", "⚠️": "注意：", "⚠": "注意："}
    for k, v in reps.items():
        src = src.replace(k, v)

    doc = SimpleDocTemplate("/home/user/Claude-Code/haitong-interview-prep/Haitong_Interview_Prep.pdf",
                            pagesize=A4, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            leftMargin=1.9 * cm, rightMargin=1.9 * cm,
                            title="Haitong Interview Prep")
    c = Conv(doc.width)
    c.feed(src)
    doc.build(c.flow)
    print("PDF built, flowables:", len(c.flow))


if __name__ == "__main__":
    main()
