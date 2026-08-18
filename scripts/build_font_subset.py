#!/usr/bin/env python3
"""Build the CJK webfont from every character currently used by the site."""

from __future__ import annotations

import argparse
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FONT = ROOT / "static" / "fonts" / "SourceHanSerifSC-Regular.otf"
OUTPUT_FONT = ROOT / "assets" / "fonts" / "SourceHanSerifSC-Regular-subset.woff2"
TEXT_ROOTS = (
    ROOT / "assets",
    ROOT / "config",
    ROOT / "content",
    ROOT / "data",
    ROOT / "layouts",
)
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".md", ".toml", ".yaml", ".yml"}
CJK_RANGES = (
    (0x2E80, 0x2EFF),
    (0x2F00, 0x2FDF),
    (0x3000, 0x30FF),
    (0x3100, 0x312F),
    (0x3130, 0x318F),
    (0x31C0, 0x31EF),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0xFE10, 0xFE1F),
    (0xFE30, 0xFE4F),
    (0xFF00, 0xFFEF),
    (0x20000, 0x2FA1F),
)


def site_characters() -> set[str]:
    characters: set[str] = set()
    for root in TEXT_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                characters.update(path.read_text(encoding="utf-8", errors="ignore"))
    return characters


def is_cjk_codepoint(codepoint: int) -> bool:
    return any(start <= codepoint <= end for start, end in CJK_RANGES)


def build_subset(source: Path, destination: Path) -> tuple[int, int]:
    font = TTFont(source, recalcTimestamp=False)
    available = {
        codepoint
        for table in font["cmap"].tables
        for codepoint in table.cmap
    }
    requested = {
        ord(character)
        for character in site_characters()
        if is_cjk_codepoint(ord(character))
    }
    selected = requested & available

    options = subset.Options()
    options.flavor = "woff2"
    options.recalc_timestamp = False
    options.layout_features = ["*"]
    options.name_IDs = [0, 1, 2, 3, 4, 5, 6]
    options.name_languages = [0x409, 0x804]

    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=selected)
    subsetter.subset(font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    font.flavor = "woff2"
    font.save(destination, reorderTables=False)
    return len(selected), len(requested - available)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--output", type=Path, default=OUTPUT_FONT)
    args = parser.parse_args()

    included, unsupported = build_subset(args.font, args.output)
    print(f"Built {args.output} with {included} supported characters")
    if unsupported:
        print(f"Skipped {unsupported} characters not provided by Source Han Serif SC")


if __name__ == "__main__":
    main()
