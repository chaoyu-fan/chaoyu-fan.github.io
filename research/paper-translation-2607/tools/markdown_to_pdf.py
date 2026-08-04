#!/usr/bin/env python3
"""Render a Chinese Markdown translation as a searchable, readable PDF.

This deliberately produces a clean reading edition rather than pretending to
reproduce the source PDF's two-column/figure layout. Source-page markers remain
in the text so the result can be checked against the original page by page.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from xml.sax.saxutils import escape

# The system Python/OpenSSL combination on this Mac lacks the optional
# `usedforsecurity` keyword that newer ReportLab passes to hashlib.md5.
_real_md5 = hashlib.md5


def _compat_md5(data=b"", *args, **kwargs):
    return _real_md5(data)


hashlib.md5 = _compat_md5

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


FONT_REGULAR = "/System/Library/Fonts/Supplemental/Songti.ttc"
FONT_SANS = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_SANS_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_UNICODE = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("SongtiCN", FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("HeitiCN", FONT_SANS))
    pdfmetrics.registerFont(TTFont("HeitiCN-Bold", FONT_SANS_BOLD))
    pdfmetrics.registerFont(TTFont("ArialUnicode", FONT_UNICODE))


def clean_markdown(text: str) -> str:
    # ReportLab Paragraph uses a small XML-like markup language. Escape source
    # text first, then restore the few Markdown emphasis markers we support.
    text = escape(text, entities={"'": "&apos;", '"': "&quot;"})
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", text)
    text = text.replace("  ", " ")
    return text


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "cn-title", parent=base["Title"], fontName="HeitiCN-Bold", fontSize=21,
            leading=28, alignment=TA_CENTER, textColor=colors.HexColor("#17324D"),
            spaceAfter=10 * mm,
        ),
        "h1": ParagraphStyle(
            "cn-h1", parent=base["Heading1"], fontName="HeitiCN-Bold", fontSize=16,
            leading=22, textColor=colors.HexColor("#17324D"), spaceBefore=9 * mm,
            spaceAfter=4 * mm, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "cn-h2", parent=base["Heading2"], fontName="HeitiCN-Bold", fontSize=13,
            leading=18, textColor=colors.HexColor("#255B7A"), spaceBefore=6 * mm,
            spaceAfter=3 * mm, keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "cn-h3", parent=base["Heading3"], fontName="HeitiCN-Bold", fontSize=11,
            leading=15, textColor=colors.HexColor("#3D6F83"), spaceBefore=4 * mm,
            spaceAfter=2 * mm, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "cn-body", parent=base["BodyText"], fontName="SongtiCN", fontSize=9.3,
            leading=14, alignment=TA_JUSTIFY, firstLineIndent=0, spaceAfter=3.2 * mm,
            wordWrap="CJK",
        ),
        "bullet": ParagraphStyle(
            "cn-bullet", parent=base["BodyText"], fontName="SongtiCN", fontSize=9.3,
            leading=14, leftIndent=7 * mm, firstLineIndent=-4 * mm, spaceAfter=1.5 * mm,
            wordWrap="CJK",
        ),
        "quote": ParagraphStyle(
            "cn-quote", parent=base["BodyText"], fontName="SongtiCN", fontSize=9,
            leading=13, leftIndent=7 * mm, rightIndent=4 * mm, borderPadding=3 * mm,
            borderColor=colors.HexColor("#B7C8D4"), borderWidth=0.5,
            textColor=colors.HexColor("#455A64"), spaceAfter=3 * mm, wordWrap="CJK",
        ),
        "marker": ParagraphStyle(
            "cn-marker", parent=base["BodyText"], fontName="HeitiCN", fontSize=7.5,
            leading=10, textColor=colors.HexColor("#7A8790"), spaceBefore=2 * mm,
            spaceAfter=2 * mm,
        ),
        "note": ParagraphStyle(
            "cn-note", parent=base["BodyText"], fontName="HeitiCN", fontSize=8,
            leading=12, textColor=colors.HexColor("#55636E"), spaceAfter=4 * mm,
        ),
    }


def parse_markdown(path: Path, styles) -> list:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    story: list = []
    in_code = False
    code_lines: list[str] = []
    seen_title = False

    def flush_code() -> None:
        nonlocal code_lines
        if code_lines:
            story.append(Preformatted("\n".join(code_lines), ParagraphStyle(
                "code", fontName="ArialUnicode", fontSize=7.4, leading=9,
                leftIndent=6 * mm, rightIndent=4 * mm, spaceAfter=3 * mm,
            ), maxLineLength=92, newLineChars="    "))
        code_lines = []

    for raw in lines:
        line = raw.strip()
        # Page anchors must be handled before code blocks.  The source
        # extraction can place a trailing page marker immediately after a
        # fenced code block; treating it as code would make the marker
        # disappear from the searchable PDF and break page-level QA.
        if line.startswith("<!--") and re.search(r"page\s*:", line, flags=re.IGNORECASE):
            if in_code:
                flush_code()
                in_code = False
            marker = re.sub(r"<!--\s*", "", line).replace("-->", "").strip()
            page_match = re.search(r"page\s*:\s*(\d+)", marker, flags=re.IGNORECASE)
            if page_match:
                marker = f"原文第 {page_match.group(1)} 页"
            story.append(Paragraph(escape(marker), styles["marker"]))
            continue
        if line.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(raw.rstrip())
            continue
        if not line:
            continue
        if line.startswith("<!--") or line.startswith("---"):
            if line.startswith("---"):
                story.append(HRFlowable(width="100%", thickness=0.35, color=colors.HexColor("#C9D3D9"), spaceBefore=2 * mm, spaceAfter=2 * mm))
            continue
        if line.startswith("#"):
            hashes, text = re.match(r"^(#+)\s*(.*)$", line).groups()
            if not seen_title and len(hashes) == 1:
                story.append(Paragraph(clean_markdown(text), styles["title"]))
                seen_title = True
            else:
                style = styles["h1"] if len(hashes) == 1 else styles["h2"] if len(hashes) == 2 else styles["h3"]
                story.append(Paragraph(clean_markdown(text), style))
            continue
        if line.startswith(">"):
            story.append(Paragraph(clean_markdown(line[1:].strip()), styles["quote"]))
            continue
        if re.match(r"^(?:[-*•])\s+", line):
            item = re.sub(r"^(?:[-*•])\s+", "• ", line)
            story.append(Paragraph(clean_markdown(item), styles["bullet"]))
            continue
        if line.startswith("!") and "](" in line:
            # Image links cannot be reconstructed from plain pdftotext. Keep a
            # visible marker rather than silently dropping a figure reference.
            story.append(Paragraph(clean_markdown("[原文图示：请对照源 PDF]"), styles["note"]))
            continue
        story.append(Paragraph(clean_markdown(line), styles["body"]))
    if in_code:
        flush_code()
    return story


def decorate(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("HeitiCN", 7.5)
    canvas.setFillColor(colors.HexColor("#71808A"))
    canvas.drawString(doc.leftMargin, 10 * mm, "中文阅读版 · 由源 PDF 转录并翻译")
    canvas.drawRightString(A4[0] - doc.rightMargin, 10 * mm, f"{doc.page}")
    canvas.restoreState()


def render(source: Path, output: Path, title: str) -> None:
    register_fonts()
    styles = build_styles()
    story = [
        Paragraph(clean_markdown("本文件为源 PDF 的中文阅读版：保留原文页码标记，正文与图注经过机器翻译后排版。公式、图表和参考文献请结合源 PDF 逐页核对。"), styles["note"]),
    ]
    story.extend(parse_markdown(source, styles))
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=17 * mm, leftMargin=17 * mm,
        topMargin=17 * mm, bottomMargin=16 * mm, title=title,
        author="Chinese translation reading edition",
    )
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    render(args.source, args.output, args.title)
