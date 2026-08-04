#!/usr/bin/env python3
"""Turn pdftotext -layout output into a readable, page-aware Markdown draft."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PAGE_NUMBER = re.compile(r"^\s*\d+\s*$")
SECTION = re.compile(
    r"^(?:[IVX]+\s+|\d+(?:\.\d+)*\.?\s+|Appendix\s+|Abstract\s*$|Acknowledgements\s*$|Contents\s*$|References\s*$|Conclusion\s*$)",
    re.IGNORECASE,
)


def clean_line(line: str) -> str:
    line = line.replace("\u00a0", " ").replace("\u2009", " ")
    return re.sub(r"[ \t]+", " ", line).strip()


def heading_level(text: str) -> int | None:
    if text in {"Abstract", "Acknowledgements", "Contents", "References", "Conclusion"}:
        return 1
    m = re.match(r"^(\d+(?:\.\d+)*)\.?\s+", text)
    if m:
        return min(4, m.group(1).count(".") + 1)
    if re.match(r"^[IVX]+\s+", text):
        return 1
    if text.startswith("Appendix "):
        return 1
    return None


def page_to_blocks(page: str) -> list[str]:
    lines = [clean_line(line) for line in page.splitlines()]
    lines = [line for line in lines if line and not PAGE_NUMBER.fullmatch(line)]
    if not lines:
        return []

    blocks: list[str] = []
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        if current:
            text = " ".join(current).strip()
            if text:
                blocks.append(text)
            current = []

    for line in lines:
        # Captions, display equations, table rows, and short all-caps labels are
        # easier to read as standalone Markdown blocks.
        is_caption = bool(re.match(r"^(Figure|Table|Algorithm|Equation)\s+", line, re.I))
        is_heading = bool(SECTION.match(line)) and len(line) < 180
        is_short_display = len(line) < 90 and ("=" in line or "≤" in line or "≥" in line)
        if is_heading or is_caption or is_short_display:
            flush()
            blocks.append(line)
        else:
            current.append(line)
    flush()
    return blocks


def convert(source: Path, destination: Path) -> None:
    pages = source.read_text(encoding="utf-8", errors="replace").split("\f")
    out: list[str] = [
        f"<!-- Source text extracted from {source.name} with pdftotext -layout. -->",
        "<!-- Page markers are retained to support source-PDF proofreading. -->",
        "",
    ]
    for page_no, page in enumerate(pages, start=1):
        blocks = page_to_blocks(page)
        if not blocks:
            continue
        out.append(f"<!-- Page {page_no} -->")
        for block in blocks:
            level = heading_level(block)
            if level is not None:
                out.append("#" * level + " " + block)
            elif block.startswith(("Figure ", "Table ", "Algorithm ", "Equation ")):
                out.append(f"*{block}*")
            else:
                out.append(block)
            out.append("")
        out.append("---")
        out.append("")
    destination.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    convert(args.source, args.destination)
