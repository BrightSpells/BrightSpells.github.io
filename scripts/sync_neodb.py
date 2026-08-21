#!/usr/bin/env python3
"""Sync NeoDB ratings and comments into Hugo data.

With ``NEODB_TOKEN`` this imports the complete shelf through NeoDB's official
API. Without a token it keeps the page useful by falling back to the latest 20
public RSS activities.
"""

from __future__ import annotations

import email.utils
import html
import json
import os
import re
import ssl
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "neodb.json"
FEED_URL = os.environ.get(
    "NEODB_FEED_URL",
    "https://neodb.social/@MinskyMoment@neodb.social/rss/",
)
API_URL = "https://neodb.social/api/me/shelf/complete"
NEODB_ORIGIN = "https://neodb.social"
TOKEN_FILE = ROOT / ".neodb-token"
NEODB_TOKEN = os.environ.get("NEODB_TOKEN", "").strip()
if not NEODB_TOKEN and TOKEN_FILE.exists():
    NEODB_TOKEN = TOKEN_FILE.read_text(encoding="utf-8").strip()
START_DATE = os.environ.get("NEODB_START_DATE", "").strip()
DETAIL_START_YEAR = int(os.environ.get("NEODB_DETAIL_START_YEAR", "2023"))
TITLE_METADATA_VERSION = 2
TIMEZONE = ZoneInfo(os.environ.get("NEODB_TIMEZONE", "America/Chicago"))
REFRESH_METADATA = os.environ.get("NEODB_REFRESH_METADATA") == "1"
USER_AGENT = "BrightSpells-NeoDB-Sync/1.0 (+https://brightspells.github.io/)"
SSL_CONTEXT = ssl.create_default_context()
MACOS_CA_FILE = Path("/etc/ssl/cert.pem")
if sys.platform == "darwin" and MACOS_CA_FILE.exists():
    SSL_CONTEXT = ssl.create_default_context(cafile=str(MACOS_CA_FILE))

MOON_VALUES = {
    "🌕": 1,
    "🌖": 0.75,
    "🌗": 0.5,
    "🌘": 0.25,
    "🌑": 0,
    "🌔": 0.75,
    "🌓": 0.5,
    "🌒": 0.25,
}


def fetch_text(url: str, headers: dict[str, str] | None = None) -> str:
    request_headers = {"User-Agent": USER_AGENT, **(headers or {})}
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
        return response.read().decode("utf-8")


def fetch_json(url: str, headers: dict[str, str] | None = None) -> dict:
    return json.loads(fetch_text(url, headers=headers))


class DescriptionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.item_url = ""
        self.item_title = ""
        self._inside_item_link = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "br":
            self.parts.append("\n")
        elif tag == "p" and self.parts:
            self.parts.append("\n")
        elif tag == "a":
            href = attributes.get("href") or ""
            if "/~neodb~/" in href:
                self.item_url = href.replace("/~neodb~/", "/")
                self._inside_item_link = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self._inside_item_link = False

    def handle_data(self, data: str) -> None:
        self.parts.append(data)
        if self._inside_item_link:
            self.item_title += data


class JsonLdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[str] = []
        self._capturing = False
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self._capturing = True
            self._parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._capturing:
            self.blocks.append("".join(self._parts))
            self._capturing = False

    def handle_data(self, data: str) -> None:
        if self._capturing:
            self._parts.append(data)


def clean_text(value: str) -> str:
    value = html.unescape(html.unescape(value))
    lines = [re.sub(r"\s+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line)


def score_from_title(title: str) -> int | float | None:
    moons = re.findall("[🌕🌖🌗🌘🌑🌔🌓🌒]", title)
    if not moons:
        return None
    score = round(sum(MOON_VALUES[moon] for moon in moons), 2)
    return int(score) if score == int(score) else score


def item_type_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path.strip("/").split("/")
    if not path:
        return "other"
    if path[0] == "tv":
        return "series"
    if path[0] == "movie":
        return "film"
    return path[0]


def parse_feed_item(item: ET.Element) -> dict | None:
    feed_title = item.findtext("title", default="")
    score = score_from_title(feed_title)
    if score is None:
        return None

    description = html.unescape(item.findtext("description", default=""))
    parser = DescriptionParser()
    parser.feed(description)
    if not parser.item_url:
        return None

    text_lines = clean_text("".join(parser.parts)).splitlines()
    comment = "\n".join(text_lines[1:]).strip() if len(text_lines) > 1 else ""
    published = email.utils.parsedate_to_datetime(item.findtext("pubDate", default=""))
    local_time = published.astimezone(TIMEZONE)
    guid = item.findtext("guid", default="") or item.findtext("link", default="")

    return {
        "id": parser.item_url.rstrip("/").split("/")[-1],
        "guid": guid,
        "type": item_type_from_url(parser.item_url),
        "feed_title": clean_text(parser.item_title),
        "score": score,
        "date": local_time.date().isoformat(),
        "timestamp": published.isoformat(),
        "comment": comment,
        "url": parser.item_url,
        "post_url": item.findtext("link", default=""),
    }


def json_ld_objects(value: object) -> list[dict]:
    if isinstance(value, dict):
        objects = [value]
        graph = value.get("@graph")
        if isinstance(graph, list):
            objects.extend(item for item in graph if isinstance(item, dict))
        return objects
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def fetch_item_metadata(url: str) -> dict:
    parser = JsonLdParser()
    parser.feed(fetch_text(url))
    for block in parser.blocks:
        try:
            candidates = json_ld_objects(json.loads(block))
        except json.JSONDecodeError:
            continue
        for candidate in candidates:
            if candidate.get("name") and candidate.get("image"):
                image = candidate["image"]
                if isinstance(image, dict):
                    image = image.get("url", "")
                return {
                    "title": clean_text(str(candidate["name"])),
                    "cover": str(image),
                    "language": str(candidate.get("inLanguage", "")),
                    "url": str(candidate.get("url", url)),
                }
    return {}


def load_existing() -> dict:
    if not DATA_FILE.exists():
        return {"source": FEED_URL, "entries": []}
    with DATA_FILE.open(encoding="utf-8") as handle:
        return json.load(handle)


def api_score(rating_grade: int | float | None) -> int | float | None:
    if rating_grade is None:
        return None
    score = rating_grade / 2
    return int(score) if score == int(score) else score


def absolute_neodb_url(url: str) -> str:
    return urllib.parse.urljoin(f"{NEODB_ORIGIN}/", url)


def first_localized_title(labels: list[dict], languages: tuple[str, ...]) -> str:
    for language in languages:
        for label in labels:
            if str(label.get("lang", "")).lower() == language and label.get("text"):
                return clean_text(str(label["text"]))
    return ""


def format_item_title(item: dict, detail: dict | None = None) -> dict:
    """Return an original-language title with a Simplified Chinese label."""
    detail = detail or {}
    labels = detail.get("localized_title") or item.get("localized_title") or []
    chinese = first_localized_title(labels, ("zh-cn", "zh-hans", "zh"))
    raw_title = clean_text(str(item.get("title") or item.get("display_title") or "未命名"))
    languages = detail.get("language") or item.get("language") or []
    if isinstance(languages, str):
        languages = [languages]
    languages = [str(language).lower() for language in languages]
    label_languages = {str(label.get("lang", "")).lower() for label in labels}
    # Season/edition suffixes often live only in the shelf title. Preserve them
    # for English items; use orig_title for Japanese and other source languages.
    prefer_shelf_title = any(language.startswith("en") for language in languages)
    prefer_shelf_title = prefer_shelf_title or (not languages and "en" in label_languages)
    original = clean_text(
        str(
            raw_title
            if prefer_shelf_title
            else detail.get("orig_title") or item.get("orig_title") or raw_title
        )
    )

    # NeoDB sometimes includes the Chinese label in its English-facing title.
    # Strip that suffix before composing the consistent bilingual form.
    for opening, closing in ((" (", ")"), ("（", "）")):
        suffix = f"{opening}{chinese}{closing}" if chinese else ""
        if suffix and original.endswith(suffix):
            original = original[:-len(suffix)].rstrip()

    is_chinese_original = any(language.startswith("zh") for language in languages)
    same_title = chinese and re.sub(r"\s+", "", original).casefold() == re.sub(r"\s+", "", chinese).casefold()
    display_title = original
    if chinese and not is_chinese_original and not same_title:
        display_title = f"{original} ({chinese})"

    return {
        "title": display_title,
        "original_title": original,
        "chinese_title": chinese,
        "languages": languages,
        "title_metadata_version": TITLE_METADATA_VERSION,
    }


def api_entry(mark: dict) -> dict | None:
    item = mark.get("item") or {}
    category = item.get("category")
    type_map = {"book": "book", "movie": "film", "tv": "series", "game": "game"}
    if category not in type_map:
        return None

    created = datetime.fromisoformat(mark["created_time"].replace("Z", "+00:00"))
    local_time = created.astimezone(TIMEZONE)
    item_url = absolute_neodb_url(
        item.get("url") or f"/{category}/{item.get('uuid', '')}"
    )
    post_id = mark.get("post_id")
    entry = {
        "id": item.get("uuid") or item.get("id"),
        "guid": f"neodb:{item.get('uuid') or item.get('id')}",
        "type": type_map[category],
        "title": clean_text(item.get("title") or item.get("display_title") or "未命名"),
        "score": api_score(mark.get("rating_grade")),
        "date": local_time.date().isoformat(),
        "timestamp": created.isoformat(),
        "comment": clean_text(mark.get("comment_text") or ""),
        "url": item_url,
        "post_url": (
            f"https://neodb.social/@MinskyMoment/posts/{post_id}/"
            if post_id else item_url
        ),
        "cover": item.get("cover_image_url") or "",
        "category": category,
        "_api_url": absolute_neodb_url(item.get("api_url") or ""),
        "_item": item,
    }
    return entry


def print_comment_history(entries: list[dict]) -> None:
    """Print aggregate yearly writing stats used to choose a clean cutoff."""
    by_year: dict[str, list[int]] = defaultdict(list)
    totals: dict[str, int] = defaultdict(int)
    for entry in entries:
        year = entry["date"][:4]
        totals[year] += 1
        if entry.get("comment"):
            by_year[year].append(len(entry["comment"]))

    print("NeoDB comment history by year:")
    for year in sorted(totals, reverse=True):
        lengths = by_year[year]
        commented = len(lengths)
        average = round(sum(lengths) / commented) if commented else 0
        middle = round(median(lengths)) if commented else 0
        long_comments = sum(length >= 100 for length in lengths)
        print(
            f"  {year}: {totals[year]} completed, {commented} commented, "
            f"median {middle} chars, average {average} chars, {long_comments} at 100+ chars"
        )


def sync_api_entries() -> list[dict]:
    headers = {
        "Authorization": f"Bearer {NEODB_TOKEN}",
        "Accept": "application/json",
        # NeoDB falls back to an item's native title when no English label
        # exists, while English-language editions keep their English titles.
        "Accept-Language": "en",
    }
    marks: list[dict] = []
    page = 1
    pages = 1
    while page <= pages:
        query = urllib.parse.urlencode({"page": page, "page_size": 100})
        payload = fetch_json(f"{API_URL}?{query}", headers=headers)
        marks.extend(payload.get("data", []))
        pages = int(payload.get("pages", 1))
        page += 1

    existing_entries = {
        entry["guid"]: entry
        for entry in load_existing().get("entries", [])
        if entry.get("guid")
    }
    entries = [entry for mark in marks if (entry := api_entry(mark))]

    metadata_needed: list[dict] = []
    for entry in entries:
        cached = existing_entries.get(entry["guid"], {})
        if cached.get("original_title"):
            cached_labels = list(entry["_item"].get("localized_title") or [])
            if cached.get("chinese_title") and not any(
                str(label.get("lang", "")).lower() == "zh-cn"
                and label.get("text") == cached.get("chinese_title")
                for label in cached_labels
            ):
                cached_labels.insert(0, {
                    "lang": "zh-cn",
                    "text": cached.get("chinese_title"),
                })
            cached_detail = {
                "orig_title": cached.get("original_title"),
                "language": cached.get("languages") or [],
                "localized_title": cached_labels,
            }
            entry.update(format_item_title(entry["_item"], cached_detail))
        elif entry.get("_api_url"):
            metadata_needed.append(entry)
        else:
            entry.update(format_item_title(entry["_item"]))

    if metadata_needed:
        print(f"fetching original-language metadata for {len(metadata_needed)} items")
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = {
                executor.submit(fetch_json, entry["_api_url"], headers): entry
                for entry in metadata_needed
            }
            completed = 0
            for future in as_completed(futures):
                entry = futures[future]
                try:
                    entry.update(format_item_title(entry["_item"], future.result()))
                except Exception as error:
                    entry.update(format_item_title(entry["_item"]))
                    entry.pop("title_metadata_version", None)
                    print(f"warning: title metadata failed for {entry['url']}: {error}", file=sys.stderr)
                completed += 1
                if completed % 50 == 0 or completed == len(metadata_needed):
                    print(f"  title metadata: {completed}/{len(metadata_needed)}")

    for entry in entries:
        entry.pop("_api_url", None)
        entry.pop("_item", None)

    print_comment_history(entries)
    if START_DATE:
        datetime.strptime(START_DATE, "%Y-%m-%d")
        entries = [entry for entry in entries if entry["date"] >= START_DATE]
    return sorted(entries, key=lambda entry: entry.get("timestamp", ""), reverse=True)


def sync_rss_entries() -> list[dict]:
    existing_data = load_existing()
    existing_entries = {
        entry["guid"]: entry
        for entry in existing_data.get("entries", [])
        if entry.get("guid") and not str(entry["guid"]).startswith("neodb:")
    }

    root = ET.fromstring(fetch_text(FEED_URL))
    feed_entries = [entry for item in root.findall("./channel/item") if (entry := parse_feed_item(item))]

    metadata_needed = [
        entry for entry in feed_entries
        if REFRESH_METADATA
        or not existing_entries.get(entry["guid"], {}).get("cover")
        or not existing_entries.get(entry["guid"], {}).get("title")
    ]
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_item_metadata, entry["url"]): entry for entry in metadata_needed}
        for future in as_completed(futures):
            entry = futures[future]
            try:
                entry.update(future.result())
            except Exception as error:  # Keep the feed usable if one item page is unavailable.
                print(f"warning: metadata fetch failed for {entry['url']}: {error}", file=sys.stderr)

    for entry in feed_entries:
        old_entry = existing_entries.get(entry["guid"], {})
        if not entry.get("title") and not old_entry.get("title"):
            entry["title"] = entry["feed_title"]
        merged = {**old_entry, **entry}
        if old_entry.get("cover") and not merged.get("cover"):
            merged["cover"] = old_entry["cover"]
        existing_entries[entry["guid"]] = merged

    return sorted(
        existing_entries.values(),
        key=lambda entry: entry.get("timestamp", ""),
        reverse=True,
    )


def build_output(entries: list[dict], source_mode: str) -> dict:
    counts = {
        entry_type: sum(entry.get("type") == entry_type for entry in entries)
        for entry_type in ("series", "film", "book", "game")
    }
    archive_years = sorted({entry["date"][:4] for entry in entries if entry.get("date")}, reverse=True)
    years = [year for year in archive_years if int(year) >= DETAIL_START_YEAR]
    return {
        "source": API_URL if source_mode == "api" else FEED_URL,
        "source_mode": source_mode,
        "limited": source_mode == "rss",
        "start_date": START_DATE or None,
        "counts": counts,
        "years": years,
        "archive_years": archive_years,
        "detail_start_year": DETAIL_START_YEAR,
        "entries": entries,
    }


def main() -> int:
    source_mode = "api" if NEODB_TOKEN else "rss"
    entries = sync_api_entries() if NEODB_TOKEN else sync_rss_entries()
    output = build_output(entries, source_mode)
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if not DATA_FILE.exists() or DATA_FILE.read_text(encoding="utf-8") != rendered:
        DATA_FILE.write_text(rendered, encoding="utf-8")
        print(f"updated {DATA_FILE.relative_to(ROOT)} with {len(entries)} entries")
    else:
        print(f"no changes ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
