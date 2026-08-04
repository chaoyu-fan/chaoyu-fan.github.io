from __future__ import annotations

import html
import re
import unicodedata
import argparse
from pathlib import Path
import hashlib

# The system Python's OpenSSL wrapper does not accept the newer
# ``usedforsecurity`` keyword that ReportLab passes when creating its PDF
# object. Keep ReportLab compatible without changing the global interpreter.
_md5 = hashlib.md5
def _md5_compat(data=b"", *args, **kwargs):
    kwargs.pop("usedforsecurity", None)
    return _md5(data, *args, **kwargs)
hashlib.md5 = _md5_compat

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
)

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent
SOURCE = ROOT / "17560" / "2607.17560v1_zh_hybrid.md"
OUT = ROOT / "pdf" / "2607.17560v1_中文阅读版.pdf"

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
FONT = "STSong-Light"
UNICODE_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
pdfmetrics.registerFont(TTFont("ArialUnicode", UNICODE_FONT_PATH))
FORMULA_FONT = "ArialUnicode"


def esc(text: str) -> str:
    return html.escape(normalize_symbols(text), quote=False)


def normalize_symbols(text: str) -> str:
    """Keep common extracted symbols visible in the CJK PDF font."""
    text = unicodedata.normalize("NFKC", text)
    return (text.replace("©", "(C)")
                .replace("·", " - ")
                .replace("•", "*")
                .replace("‐", "-")
                .replace("‑", "-")
                .replace("‒", "-")
                .replace("–", "-")
                .replace("—", "--")
                .replace("□", "")
                .replace("ϵ", "epsilon")
                .replace("ȷ", "j")
                .replace("ı", "i")
                .replace("ż", "z")
                .replace("ř", "r")
                .replace("„", '"')
                .replace("ˆ", "^")
                .replace("ˇ", "v")
                .replace("˙", ".")
                .replace("\ue077", "")
                .replace("⊺", "^T")
                .replace("⋺", "")
                .replace("\u0301", "'"))


def parse_pages(source: Path = SOURCE) -> list[tuple[int, str]]:
    text = source.read_text(encoding="utf-8")
    parts = re.split(r"(?m)^### 原文第 (\d+) 页\n", text)
    pages: list[tuple[int, str]] = []
    for i in range(1, len(parts), 2):
        n = int(parts[i])
        body = parts[i + 1].split("\n---\n", 1)[0].strip()
        pages.append((n, body))
    return pages


class ReadingDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="normal",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates([PageTemplate(id="reading", frames=[frame], onPage=draw_header_footer)])


def draw_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.setFont(FONT, 8)
    canvas.drawString(doc.leftMargin, 12 * mm, "强化学习：从算法到基础模型 - 中文阅读版")
    canvas.drawRightString(A4[0] - doc.rightMargin, 12 * mm, f"{doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "TitleCN", parent=styles["Title"], fontName=FONT, fontSize=25, leading=34,
    alignment=TA_CENTER, textColor=colors.HexColor("#111827"), spaceAfter=18,
)
SUBTITLE = ParagraphStyle(
    "SubtitleCN", parent=styles["Normal"], fontName=FONT, fontSize=12, leading=20,
    alignment=TA_CENTER, textColor=colors.HexColor("#4b5563"), spaceAfter=12,
)
NOTE = ParagraphStyle(
    "NoteCN", parent=styles["Normal"], fontName=FONT, fontSize=9.5, leading=15,
    textColor=colors.HexColor("#374151"), leftIndent=12, rightIndent=12,
    borderColor=colors.HexColor("#d1d5db"), borderWidth=0.5, borderPadding=8,
    spaceBefore=10, spaceAfter=14,
)
PAGE_HEAD = ParagraphStyle(
    "PageHead", parent=styles["Heading3"], fontName=FONT, fontSize=10,
    leading=14, textColor=colors.HexColor("#6b7280"), spaceAfter=9,
)
H1 = ParagraphStyle(
    "H1CN", parent=styles["Heading1"], fontName=FONT, fontSize=16, leading=22,
    textColor=colors.HexColor("#111827"), spaceBefore=8, spaceAfter=8,
)
H2 = ParagraphStyle(
    "H2CN", parent=styles["Heading2"], fontName=FONT, fontSize=13, leading=18,
    textColor=colors.HexColor("#1f2937"), spaceBefore=5, spaceAfter=5,
)
BODY = ParagraphStyle(
    "BodyCN", parent=styles["BodyText"], fontName=FONT, fontSize=9.3, leading=14.2,
    alignment=TA_LEFT, wordWrap="CJK", spaceAfter=6,
)
CAPTION = ParagraphStyle(
    "CaptionCN", parent=BODY, fontSize=8.7, leading=12, textColor=colors.HexColor("#4b5563"),
    leftIndent=8, rightIndent=8,
)
FORMULA = ParagraphStyle(
    "FormulaCN", parent=BODY, fontSize=8, leading=10.5, fontName=FORMULA_FONT,
    wordWrap="LTR", leftIndent=10, rightIndent=4, textColor=colors.HexColor("#111827"),
)


def is_formula(line: str) -> bool:
    s = line.strip()
    symbols = "πθ∇µϵλγσΩΣ∫∑√∞≤≥≈≠∈∉⊂⊃→←↔ˆˇż˝˙´˚¯˘"
    n = sum(c in symbols for c in s)
    return n >= 2 or (n and len(re.findall(r"[A-Za-z]", s)) < 8)


def page_flow(n: int, body: str):
    flow = [Paragraph(f"原文第 {n} 页", PAGE_HEAD)]
    # Render source lines as paragraphs while retaining extracted equation lines
    # in a compact monospace block; this keeps formulas legible after reflow.
    paragraph: list[str] = []

    def flush():
        if paragraph:
            text = normalize_symbols(" ".join(x.strip() for x in paragraph).strip())
            if text:
                flow.append(Paragraph(esc(text), BODY))
            paragraph.clear()

    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        if line.startswith("# "):
            flush(); flow.append(Paragraph(esc(normalize_symbols(line[2:].strip())), H1)); continue
        if line.startswith("## "):
            flush(); flow.append(Paragraph(esc(normalize_symbols(line[3:].strip())), H2)); continue
        if line.startswith("### "):
            flush(); flow.append(Paragraph(esc(normalize_symbols(line[4:].strip())), H2)); continue
        if is_formula(line):
            flush(); flow.append(Preformatted(normalize_symbols(line), FORMULA)); continue
        if re.match(r"^(图|图表|Figure|Fig\.?|表|Table)\b", line, re.I):
            flush(); flow.append(Paragraph(esc(normalize_symbols(line)), CAPTION)); continue
        if line.startswith("> "):
            flush(); flow.append(Paragraph(esc(normalize_symbols(line[2:])), NOTE)); continue
        # Preserve list markers while allowing CJK line wrapping.
        paragraph.append(line)
    flush()
    flow.append(PageBreak())
    return flow


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a page-aware Chinese reading PDF")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    pages = parse_pages(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc = ReadingDocTemplate(
        str(args.output), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=20 * mm,
        title="强化学习：从算法到基础模型（中文阅读版）",
        author="Zihan Ding; machine-translated reading draft",
    )
    story = [
        Spacer(1, 35 * mm),
        Paragraph("强化学习：从算法到基础模型", TITLE),
        Paragraph("Reinforcement Learning: From Algorithms To Foundation Models", SUBTITLE),
        Spacer(1, 4 * mm),
        Paragraph("作者：Zihan Ding - arXiv:2607.17560v1 - 2026 年 7 月", SUBTITLE),
        Spacer(1, 16 * mm),
        Paragraph(
            "本 PDF 是基于公开 arXiv 源文件的中文机器翻译阅读版。正文页序与源文档对齐，数学表达式按文本抽取结果尽量保留，图表以占位标记表示；页 290-319 的参考文献保留英文。该稿已完成自动页标记、文本完整性和渲染检查，但未经过人工逐句学术校对。",
            NOTE,
        ),
        Spacer(1, 8 * mm),
        Paragraph("源文件：2607.17560v1.pdf (319 页)", SUBTITLE),
        PageBreak(),
    ]
    for n, body in pages:
        story.extend(page_flow(n, body))
    # Remove the final empty page break generated by the last page.
    if story and isinstance(story[-1], PageBreak):
        story.pop()
    doc.build(story)
    print(f"wrote {args.output} pages={doc.page}")


if __name__ == "__main__":
    main()
